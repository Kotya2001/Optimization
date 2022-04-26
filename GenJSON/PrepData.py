import random
import numpy as np
import json

path = '/Applications/Developing/Python/Optimization/GenJSON/data.json'
number_bound, start = 250, 0  # number_bound - длина массива actions, где награды >= 0


class PrepData:

    def __init__(self, json_path):
        self.json_path = json_path
        self.vars = []
        self.coefs = []

        with open(self.json_path) as file:
            self.data = json.load(file)
        self.T = self.data["Periods"]
        self.upperBound = self.data["The maximum number of basketball courts in the region per year"]

    def set_goal_coef(self):
        ex = {}
        years = ['year' + '_' + str(i) for i in range(1, self.T + 1)]
        # self.upperBound = self.data["The maximum number of basketball courts in the region per year"]

        w_dict = {i: {
            j: self.data["Regions"][i]["Type of basketball court"][j]["Priority"]
            for
            j in list(self.data["Regions"][i]["Type of basketball court"].keys())
        } for i in
            list(self.data["Regions"].keys())}

        p = {i: self.data["Regions"][i]["Rank"] for i in
             list(self.data["Regions"].keys())}

        # Sorting
        p = dict(sorted(p.items(), key=lambda x: int(x[0][x[0].index('_') + 1])))
        w_dict = dict(sorted({i: dict(sorted(w_dict[i].items(), key=lambda x: int(x[0][x[0].index('_') + 1]))) for i in
                              list(w_dict.keys())}.items(),
                             key=lambda x: int(x[0][x[0].index('_') + 1])))

        # Creating vars
        for t in range(1, self.T + 1):
            for key in list(w_dict.keys()):
                for k in list(w_dict[key].keys()):
                    self.vars.append(key + '.' + k + '.' + years[t - 1])
                    self.coefs.append((p[key] + w_dict[key][k]) * ((self.T + 1 - t) / self.T))
                    ex[key + '.' + k + '.' + years[t - 1]] = (p[key] + w_dict[key][k]) * ((self.T + 1 - t) / self.T)

        return ex

    def get_constraints(self):
        constraits = []
        numberOfRegs, typesOfPlaces = len(self.data["Regions"]), len(self.data["Types of basketball courts"])

        maxNumberCourts = self.data["The maximum number of basketball courts all types for each region"]

        cost = {
            i: {j: self.data["Regions"][i]["Type of basketball court"][j]["cost"]
                for
                j in list(self.data["Regions"][i]["Type of basketball court"].keys())
                } for i in
            list(self.data["Regions"].keys())}

        b = {i: self.data["Regions"][i]["Number of players"] for i in
             list(self.data["Regions"].keys())}

        e = {i: self.data["Types of basketball courts"][i]["Capacity"] for i in
             list(self.data["Types of basketball courts"].keys())}

        u = {
            i: {j: self.data["Regions"][i]["Type of basketball court"][j]["Regional costs"]
                for
                j in list(self.data["Regions"][i]["Type of basketball court"].keys())
                } for i in
            list(self.data["Regions"].keys())}

        a = {i: self.data["Regions"][i]["Regs budget"] for i in
             list(self.data["Regions"].keys())}

        cost = dict(sorted({i: dict(sorted(cost[i].items(), key=lambda x: int(x[0][x[0].index('_') + 1]))) for i in
                            list(cost.keys())}.items(),
                           key=lambda x: int(x[0][x[0].index('_') + 1])))

        b = dict(sorted(b.items(), key=lambda x: int(x[0][x[0].index('_') + 1])))
        e = dict(sorted(e.items(), key=lambda x: int(x[0][x[0].index('_') + 1])))
        a = dict(sorted(a.items(), key=lambda x: int(x[0][x[0].index('_') + 1])))
        u = dict(sorted({i: dict(sorted(u[i].items(), key=lambda x: int(x[0][x[0].index('_') + 1]))) for i in
                         list(u.keys())}.items(),
                        key=lambda x: int(x[0][x[0].index('_') + 1])))

        cost = [[*list((list(cost[key].values())))] for key in list(cost.keys())]
        b = [b[i] for i in list(b.keys())]
        e = [e[i] for i in list(e.keys())]
        u = [[*list((list(u[key].values())))] for key in list(u.keys())]
        a = [a[i] for i in list(a.keys())]

        x, X = {i: 0 for i in self.vars}, []

        totalProjPerYear = self.data["Limit on the number of projects per year"]
        totalBudget = self.data["Total budget"]

        # Ограничения на количесвто объектов в год
        for i in range(0, len(self.vars), numberOfRegs * typesOfPlaces):
            for j in self.vars[i:i + (numberOfRegs * typesOfPlaces)]:
                x[j] = 1
            X.append(x)
            constraits.append(totalProjPerYear)

            x = {i: 0 for i in self.vars}

        # Ограничения на стоиммость объектов за T лет
        for i in range(0, len(self.vars), typesOfPlaces):
            l = self.vars[i: i + typesOfPlaces]
            for j in range(len(l)):
                x[l[j]] = cost[int(i / typesOfPlaces) % numberOfRegs][j]

        X.append(x)
        constraits.append(totalBudget)
        x = {i: 0 for i in self.vars}

        # Ограничение на максимальное количесвто площадок в каждом регионе
        vars = sorted(self.vars)
        for i in range(0, len(vars), self.T * typesOfPlaces):
            for j in vars[i: i + (self.T * typesOfPlaces)]:
                x[j] = 1
            X.append(x)
            constraits.append(maxNumberCourts)

            x = {i: 0 for i in self.vars}

        # Ограничение на колиество баскетболистов
        for i in range(0, len(vars), self.T * typesOfPlaces):
            v = vars[i: i + (self.T * typesOfPlaces)]
            for j in range(0, len(v), self.T):
                for k in v[j:j + self.T]:
                    x[k] = e[int(j / self.T) % self.T]

            X.append(x)
            constraits.append(b[int(i / (self.T * typesOfPlaces))])
            x = {i: 0 for i in self.vars}

        # Ограничение на затраты регионов
        for i in range(0, len(vars), self.T * typesOfPlaces):
            v = vars[i: i + (self.T * typesOfPlaces)]
            for j in range(0, len(v), self.T):
                for k in v[j:j + self.T]:
                    x[k] = u[int(i / (self.T * typesOfPlaces) % (self.T * typesOfPlaces))][int(j / self.T)]

            X.append(x)
            constraits.append(a[int(i / (self.T * typesOfPlaces))])
            x = {i: 0 for i in self.vars}

        result = [list(d.values()) for d in X]

        return X, constraits


ex = PrepData(path)
goal_coef = ex.set_goal_coef()

constraits = ex.get_constraints()[0]
bounds = ex.get_constraints()[1]

p = []
for k in sorted(list(goal_coef.keys())):
    p.append(goal_coef[k])
p = np.array(p)

c = []
for d in constraits:
    r = []
    for k in sorted(list(d.keys())):
        r.append(d[k])
    c.append(r)
c = np.array(c)

b = np.array(bounds).astype(np.float64)

ubound = ex.upperBound

m = len(p)
n = len(c)

array = np.arange(start, m, number_bound) # массив индексов матрицы c (условий), которые по пакетам подаются в RL
