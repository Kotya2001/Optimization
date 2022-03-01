import numpy as np
import random
import json


class GenerateJSON:

    def __init__(self, numberOfRegs, typesOfPlaces, T, upperBound, totalBudget, totalProjPerYear):
        """

        :param numberOfRegs: -> int, number of regions
        :param typesOfPlaces: -> int, number of basketball courts types
        :param T: -> int, total number of years
        :param upperBound: -> int, maximum number of projects for each regions
        :param totalBudget: -> int, total budget for building courts in regions
        :param totalProjPerYear: -> int, total number of basketball court for each region per year
        """
        self.numberOfRegs = numberOfRegs
        self.typesOfPlaces = typesOfPlaces
        self.namesOfRegs = ['Region' + '_' + str(i) for i in range(1, numberOfRegs + 1)]
        self.w = np.zeros((self.numberOfRegs, self.typesOfPlaces)).astype(np.int64)
        self.b = np.zeros((self.numberOfRegs,)).astype(np.int64)
        self.T = T
        self.upperBound = upperBound
        self.totalBudget = totalBudget
        self.totalProjPerYear = totalProjPerYear

    def gap(self):

        # Зполняем матрицу приоритетностей площадок
        for i in range(self.numberOfRegs):
            for j in range(self.typesOfPlaces):
                self.w[i][j] = int(np.random.randint(1, 18, (1, 1))[0][0])

        # Заполняем матрицу количесвта баскетболистов
        for i in range(self.numberOfRegs):
            self.b[i] = int(np.random.randint(3245, 10001, (1, 1))[0][0])

        # Словарь стоимостей типов площадок
        _cost = {'Type of basketball court' + '_' + str(i): random.randint(12000000, 20000000) for i in
                 range(1, self.typesOfPlaces + 1)}

        # Словарь рагов регионов
        _p = {self.namesOfRegs[j]: {'Rank': random.randint(1, 11)} for j in range(len(self.namesOfRegs))}

        # Словарь вмещаемости количества людей для каждого типа площадки
        _e = {'Type of basketball court' + '_' + str(e): random.randint(51, 142) for e in range(1, self.typesOfPlaces + 1)}

        # Словарь приориттностей для каждого региона
        _w = {name: {'Priority of basketball court': {}} for name in self.namesOfRegs}
        w_keys = list(_w.keys())
        squared = ['Type of basketball court' + '_' + str(j) for j in range(1, self.typesOfPlaces + 1)]

        for i in range(len(w_keys)):
            for j in range(len(squared)):
                _w[w_keys[i]]['Priority of basketball court'][squared[j]] = int(self.w[i][j])

        # Словарь количества баскетболистов для каждого региона
        _b = {name: {'Number of players': None} for name in self.namesOfRegs}
        b_keys = list(_b.keys())
        for ind in range(len(b_keys)):
            _b[b_keys[ind]]['Number of players'] = int(self.b[ind])

        for key in list(_w.keys()):
            _w[key].update(_b[key])
            _w[key].update(_p[key])

        cost_and_capacity = {i: {"Cost": _cost[i], "Capacity": _e[i]} for i in list(_cost.keys())}

        data = {'Periods': self.T,
                'Limit on the number of projects per year': self.totalProjPerYear,
                'Total budget': self.totalBudget,
                'The maximum number of basketball courts in the region per year': self.upperBound,
                'Regions': _w,
                'Types of basketball courts': cost_and_capacity}

        with open('data.json', 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=4, ensure_ascii=False)


numberOfRegs = 37
typesOfPlaces = 3
T = 3
upperBound, totalBudget, totalProjPerYear = 7, 160000000, 3

obj = GenerateJSON(numberOfRegs, typesOfPlaces, T, upperBound, totalBudget, totalProjPerYear)
obj.gap()
