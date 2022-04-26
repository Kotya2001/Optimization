import numpy as np
from GenJSON.PrepData import ubound, m, n, b, c, p, number_bound, array
import ray
from ray import tune
import ray.rllib.agents.ppo as ppo
from ray.tune.logger import pretty_print
import gym
import json
import datetime

from ray.rllib.agents.callbacks import DefaultCallbacks
from ray.rllib.policy.sample_batch import SampleBatch
from ray.rllib.env import BaseEnv
from ray.rllib.evaluation import Episode, RolloutWorker
from ray.rllib.utils.typing import AgentID, PolicyID
from typing import Dict, Optional, TYPE_CHECKING
from ray.rllib.policy import Policy

steps_per_forward = 121
rews, all_actions = [], []

# m = 10935  # num vars
# n = 253  # num constraints
# ubound = 11  # upper bound of constraints
#
# rand = np.random.RandomState(3)
# p = np.round(rand.random_sample(m) * 5, 1)  # goal koef
# c = np.round(rand.random_sample((n, m)) * 10 * (rand.random_sample(m) * (p / 5) * 0.3 + 1), 1)  # constrants
# b = np.round(c.sum(axis=1) * (rand.random_sample(n) * 0.5 + 0.3), 0)

ray.shutdown()
ray.init()


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
        # print(f'len actions {len(actions[rewards >= 0])} total_reward {total_reward} actions {actions[rewards >= 0]}')

        if total_reward > self.best_reward and len(actions[rewards >= 0]) == number_bound:
            # print('ku', total_reward, rewards, actions)
            actions = actions[rewards >= 0]
            total_reward = np.sum(rewards[rewards >= 0])
            self.best_actions = actions
            self.best_reward = total_reward
            episode.hist_data["best_actions"] = [actions]
            episode.hist_data["best_reward"] = [total_reward]


class MyEnv(gym.Env):
    def __init__(self, env_config):
        self.action_space = gym.spaces.Discrete(ubound + 1)
        self.observation_space = gym.spaces.Dict({
            'rem': gym.spaces.Box(low=np.zeros(n), high=b, dtype=np.float64),
            'j': gym.spaces.Discrete(m + 1)})
        self.state = {'rem': np.array(b), 'j': 0}
        self.done = False

    def reset(self):
        self.state = {'rem': np.array(b), 'j': 0}
        self.done = False
        return self.state

    def step(self, action):
        # print('current state:', self.state)
        # print('action taken:', action)
        j = self.state['j']
        rem = self.state['rem'] - c[:, j] * action
        if np.any(rem < 0):
            self.reward = -1
        else:
            self.reward = action * p[j]
            j += 1
            self.state = {'rem': rem, 'j': j}

        # print('reward:', self.reward)
        # print('next state:', self.state)

        if j == m:
            self.done = True
        else:
            self.done = False

        return self.state, self.reward, self.done, {}


config = ppo.DEFAULT_CONFIG.copy()
config["num_gpus"] = 1
config["num_workers"] = 4
config["framework"] = "torch"
config["callbacks"] = SampleCallback
config["env_config"] = {}
config["log_level"] = "ERROR"
config['lr'] = 0.001
# config['model']['use_attention'] = True
config['gamma'] = 0.99

model = ppo.PPOTrainer(config=config, env=MyEnv)
env = MyEnv(config)

print(datetime.datetime.now())
for ind in range(len(array) - 1):
    p = p[array[ind]:array[ind + 1]]
    c = c[:, array[ind]:array[ind + 1]]

    best_g = 0
    best_actions = []

    for i in range(steps_per_forward):
        result = model.train()

        if 'best_reward' in result['hist_stats'] and len(result['hist_stats']['best_reward']) > 0 and \
                (best_g < result['hist_stats']['best_reward'][-1] or best_actions == []):
            best_g = result['hist_stats']['best_reward'][-1]
            best_actions = result['hist_stats']['best_actions'][-1]
            rews.append((best_g, ind))
            all_actions.append((best_actions, ind))

        if i % 10 == 0:
            print('i: ', i)
            print('mean episode length:', result['episode_len_mean'])
            print('max episode reward:', result['episode_reward_max'])
            print('mean episode reward:', result['episode_reward_mean'])
            print('min episode reward:', result['episode_reward_min'])
            print('total episodes:', result['episodes_total'])
            print('solution:', best_g, best_actions)

        checkpoint = model.save()
    if array[ind] == 1750:
        break
        # print("checkpoint saved at", checkpoint)

print(datetime.datetime.now())
print(rews, all_actions)