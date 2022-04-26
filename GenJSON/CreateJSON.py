import numpy as np
import random
import json
from math import ceil


class GenerateJSON:

    def __init__(self, numberOfRegs, typesOfPlaces, T, upperBound, maxNumberCourts):
        """
        :param numberOfRegs: -> int, number of regions
        :param typesOfPlaces: -> int, number of basketball courts types
        :param T: -> int, total number of years
        :param upperBound: -> int, maximum number of projects for each regions
        :param maxNumberCourts: -> int, maximum number of basketball courts all types for each region
        """
        self.numberOfRegs = numberOfRegs
        self.typesOfPlaces = typesOfPlaces
        self.namesOfRegs = ['Region' + '_' + str(i) for i in range(1, numberOfRegs + 1)]
        self.w = np.zeros((self.numberOfRegs, self.typesOfPlaces)).astype(np.int64)
        self.b = np.zeros((self.numberOfRegs,)).astype(np.int64)
        self.T = T
        self.upperBound = upperBound
        self.totalBudget = random.randint(3, 10)
        self.totalProjPerYear = random.randint(1, 4)
        self.maxNumberCourts = maxNumberCourts

    def gap(self):

        # Зполняем матрицу приоритетностей площадок
        for i in range(self.numberOfRegs):
            for j in range(self.typesOfPlaces):
                self.w[i][j] = int(np.random.randint(1, 18, (1, 1))[0][0])

        # Заполняем матрицу количесвта баскетболистов
        for i in range(self.numberOfRegs):
            self.b[i] = int(np.random.randint(3245, 10001, (1, 1))[0][0])

        # Словарь стоимостей типов площадок
        # _cost = {'Type of basketball court' + '_' + str(i): random.randint(12000000, 20000000) for i in
        #          range(1, self.typesOfPlaces + 1)}

        # Словарь рагов регионов
        _p = {self.namesOfRegs[j]: {'Rank': random.randint(1, 11)} for j in range(len(self.namesOfRegs))}

        # Бюджет региона на строительство объектов
        _a = {self.namesOfRegs[j]: {'Regs budget': random.randint(5000000, 7500000)} for j in
              range(len(self.namesOfRegs))}

        # Словарь вмещаемости количества людей для каждого типа площадки
        _e = {'Type of basketball court' + '_' + str(e): random.randint(51, 142) for e in
              range(1, self.typesOfPlaces + 1)}

        # Словарь приориттностей для каждого региона
        _w = {name: {'Type of basketball court': {}} for name in self.namesOfRegs}
        w_keys = list(_w.keys())
        squared = ['Type of basketball court' + '_' + str(j) for j in range(1, self.typesOfPlaces + 1)]

        for i in range(len(w_keys)):
            for j in range(len(squared)):
                _w[w_keys[i]]['Type of basketball court'][squared[j]] = {'Priority': int(self.w[i][j]),
                                                                         'cost': random.randint(12000000, 20000000),
                                                                         'Regional costs': random.randint(3000000,
                                                                                                          5200000)}

        # Словарь количества баскетболистов для каждого региона
        _b = {name: {'Number of players': None} for name in self.namesOfRegs}
        b_keys = list(_b.keys())
        for ind in range(len(b_keys)):
            _b[b_keys[ind]]['Number of players'] = int(self.b[ind])

        for key in list(_w.keys()):
            _w[key].update(_b[key])
            _w[key].update(_p[key])
            _w[key].update(_a[key])

        cost_and_capacity = {i: {"Capacity": _e[i]} for i in list(_e.keys())}

        mean_cost = []
        for i in list(_w.keys()):
            for j in list(_w[i]["Type of basketball court"].keys()):
                mean_cost.append(_w[i]["Type of basketball court"][j]['cost'])

        mean_cost = sum(mean_cost) / len(mean_cost)
        totalBudget = int(self.upperBound * mean_cost * self.T * (0.4 + self.totalBudget * 0.2))
        totalProjPerYear = int((self.numberOfRegs / self.T) * (0.7 + self.totalProjPerYear * 0.2))

        data = {'Periods': self.T,
                'Limit on the number of projects per year': totalProjPerYear,
                'Total budget': totalBudget,
                'The maximum number of basketball courts in the region per year': self.upperBound,
                'The maximum number of basketball courts all types for each region': self.maxNumberCourts,
                'Regions': _w,
                'Types of basketball courts': cost_and_capacity}

        with open('data.json', 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=4, ensure_ascii=False)


numberOfRegs = 15
typesOfPlaces = 5
T = 5
upperBound, maxNumberCourts = 6, 7

obj = GenerateJSON(numberOfRegs, typesOfPlaces, T, upperBound, maxNumberCourts)
obj.gap()


