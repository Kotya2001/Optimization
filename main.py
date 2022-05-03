import numpy as np
import random
import ray
from ray import tune
import ray.rllib.agents.ppo as ppo
from ray.tune.logger import pretty_print
import gym
import json

from ray.rllib.agents.callbacks import DefaultCallbacks
from ray.rllib.policy.sample_batch import SampleBatch
from ray.rllib.env import BaseEnv
from ray.rllib.evaluation import Episode, RolloutWorker
from ray.rllib.utils.typing import AgentID, PolicyID
from typing import Dict, Optional, TYPE_CHECKING
from ray.rllib.policy import Policy

from ray.rllib.models.tf.tf_modelv2 import TFModelV2
from ray.rllib.models import ModelCatalog
from ray.rllib.models.tf.fcnet import FullyConnectedNetwork as fcn
from ray.rllib.models.tf.recurrent_net import RecurrentNetwork as rnn
import tensorflow as tf

m = 5000  # num vars
n = 811  # num constraints
ubound = 16  # upper bound of constraints
steps_per_forward = 31
bound = 466

# data simpling
rand = np.random.RandomState(3)
p = np.round(rand.random_sample(m) * 5, 1)  # goal koef
c = np.round(rand.random_sample((n, m)) * 10 * (rand.random_sample(m) * (p / 5) * 0.3 + 1), 1)  # constrants
b = np.round(c.sum(axis=1) * (rand.random_sample(n) * 0.5 + 0.3), 0)

act_space = gym.spaces.Discrete(ubound + 1)
n_acts = act_space.n

obs_spc = gym.spaces.Dict({
    'rem': gym.spaces.Box(low=np.zeros(n), high=b, dtype=np.float64),
    'j': gym.spaces.Discrete(m + 1),
    'mask': gym.spaces.MultiBinary(n_acts)})

ray.shutdown()
ray.init()
config = ppo.DEFAULT_CONFIG.copy()


def register_env(env, env_name, env_config={}):
    tune.register_env(env_name, lambda env_name: env(env_config=env_config))


class SampleCallback(DefaultCallbacks):

    def __init__(self, legacy_callbacks_dict: Dict[str, callable] = None):
        self.best_reward = -666666666
        self.best_actions = []
        self.legacy_callbacks = legacy_callbacks_dict or {}

    def on_postprocess_trajectory(
            self, *, worker: "RolloutWorker", episode: Episode,
            agent_id: AgentID, policy_id: PolicyID,
            policies: Dict[PolicyID, Policy], postprocessed_batch: SampleBatch,
            original_batches: Dict[AgentID, SampleBatch], **kwargs) -> None:
        sample_obj = original_batches[agent_id][1]
        rewards = sample_obj.columns(['rewards'])[0]
        total_reward = np.sum(rewards)
        actions = sample_obj.columns(['actions'])[0]
        print(len(actions[rewards >= 0]))

        if total_reward > self.best_reward and len(actions[rewards >= 0]) >= bound:
            # print('ku', total_reward, rewards, actions)
            actions = actions[rewards >= 0]
            total_reward = np.sum(actions * p[:len(actions)])
            self.best_actions = actions
            self.best_reward = total_reward
            episode.hist_data["best_actions"] = [actions]
            episode.hist_data["best_reward"] = [total_reward]


class MyEnv(gym.Env):
    def __init__(self, env_config):
        self.action_space = gym.spaces.Discrete(ubound + 1)
        self.observation_space = gym.spaces.Dict({
            'rem': gym.spaces.Box(low=np.zeros(n), high=b, dtype=np.float64),
            'j': gym.spaces.Discrete(m + 1),
            'mask': gym.spaces.MultiBinary(n_acts)})
        self.state = {'rem': np.array(b), 'j': 0, 'mask': gym.spaces.MultiBinary(n_acts).sample()}
        self.done = False

    def reset(self):
        self.state = {'rem': np.array(b), 'j': 0, 'mask': gym.spaces.MultiBinary(n_acts).sample()}
        self.done = False
        return self.state

    def step(self, action):
        # print('current state:', self.state)
        # print('action taken:', action)
        j = self.state['j']
        mask = self.state['mask']
        rem = self.state['rem'] - c[:, j] * action
        if np.any(rem < 0):
            self.reward = -1
        else:
            self.reward = action * p[j]
            j += 1
            self.state = {'rem': rem, 'j': j, 'mask': gym.spaces.MultiBinary(n_acts).sample()}

        # print('reward:', self.reward)
        # print('next state:', self.state)

        if j == m:
            self.done = True
            # print(rem)
        else:
            self.done = False

        return self.state, self.reward, self.done, {}


class Agent(TFModelV2):
    def __init__(self, obs_space, action_space, num_outputs, model_config, name, true_obs_shape=n,
                 action_vec_size=n_acts, *args, **kwargs):
        super(Agent, self).__init__(obs_space, action_space, num_outputs, model_config, name, *args, **kwargs)
        self.action_vec_model = fcn(
            gym.spaces.Box(-1, 1, shape=(true_obs_shape,), dtype=int),
            action_space, action_vec_size, model_config, name + '_action_vec'
        )

    def forward(self, input_dict, state, seg_lens):
        action_mask = input_dict['obs']['mask']

        action_embed, _ = self.action_vec_model({
            'obs': input_dict['obs']['rem']})

        res = tf.multiply(action_embed, action_mask)

        return res, state

    def value_function(self):
        return self.action_vec_model.value_function()


config["num_gpus"] = 0
config["num_workers"] = 1
config["framework"] = "torch"
config["env_config"] = {}


ModelCatalog.register_custom_model('custom_agent', Agent)
register_env(MyEnv, 'custom_env', env_config={})
trainer_config = {
    "model": {
        "custom_model": "custom_agent"
    },
    "env_config": config,
    'gamma': 0.99,
    'train_batch_size': m,
    'vf_clip_param': 2190,
    'lr': 0.0003,
    'callbacks': SampleCallback

}

model = ppo.PPOTrainer(env='custom_env', config=trainer_config)

best_g = 0
best_actions = []

for i in range(steps_per_forward):
    result = model.train()

    if 'best_reward' in result['hist_stats'] and len(result['hist_stats']['best_reward']) > 0 and (
            best_g < result['hist_stats']['best_reward'][-1] or best_actions == []):
        best_g = result['hist_stats']['best_reward'][-1]
        best_actions = result['hist_stats']['best_actions'][-1]

    if i % 10 == 0:
        print('i: ', i)
        print('mean episode length:', result['episode_len_mean'])
        print('max episode reward:', result['episode_reward_max'])
        print('mean episode reward:', result['episode_reward_mean'])
        print('min episode reward:', result['episode_reward_min'])
        print('total episodes:', result['episodes_total'])
        print('solution:', best_g, best_actions)
    checkpoint = model.save()
