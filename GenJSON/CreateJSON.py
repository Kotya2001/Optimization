import numpy as np
import random
import json


class GenerateJSON:

    def __init__(self, numberOfRegs, typesOfPlaces, T, upperBound, totalBudget, totalProjPerYear):
        """

        :param numberOfRegs: -> int, number of regions
        :param typesOfPlaces: -> int, number of basketball courts types
        :param T:
        :param upperBound:
        :param totalBudget:
        :param totalProjPerYear:
        """
        self.numberOfRegs = numberOfRegs
        self.typesOfPlaces = typesOfPlaces
        self.namesOfRegs = ['Регион' + '_' + str(i) for i in range(1, numberOfRegs + 1)]
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
                self.w[i][j] = int(np.random.randint(1, 6, (1, 1))[0][0])

        # Заполняем матрицу количесвта баскетболистов
        for i in range(self.numberOfRegs):
            self.b[i] = int(np.random.randint(3245, 10001, (1, 1))[0][0])

        # Словарь стоимостей типов площадок
        _cost = {'Тип площадки' + '_' + str(i): random.randint(12000000, 20000000) for i in
                 range(1, self.typesOfPlaces + 1)}

        # Словарь рагов регионов
        _p = {self.namesOfRegs[j]: {'Ранг': random.randint(1, 8)} for j in range(len(self.namesOfRegs))}

        # Словарь вмещаемости количества людей для каждого типа площадки
        _e = {'Тип площадки' + '_' + str(e): random.randint(51, 142) for e in range(1, self.typesOfPlaces + 1)}

        # Словарь приориттностей для каждого региона
        _w = {name: {'Приоритетность площадки': {}} for name in self.namesOfRegs}
        w_keys = list(_w.keys())
        squared = ['Тип площадки' + '_' + str(j) for j in range(1, self.typesOfPlaces + 1)]

        for i in range(len(w_keys)):
            for j in range(len(squared)):
                _w[w_keys[i]]['Приоритетность площадки'][squared[j]] = int(self.w[i][j])

        # Словарь количества баскетболистов для каждого региона
        _b = {name: {'Количество баскетболистов': None} for name in self.namesOfRegs}
        b_keys = list(_b.keys())
        for ind in range(len(b_keys)):
            _b[b_keys[ind]]['Количество баскетболистов'] = int(self.b[ind])

        for key in list(_w.keys()):
            _w[key].update(_b[key])
            _w[key].update(_p[key])

        cost_and_capacity = {i: {"Стоимость": _cost[i], "Вместимость": _e[i]} for i in list(_cost.keys())}

        data = {'Периоды': self.T,
                'Ограничение на количество проектов в год': self.totalProjPerYear,
                'Общий бюджет': self.totalBudget,
                'Максимальное количество площадок в регионе в год': self.upperBound,
                'Количество регионов': self.numberOfRegs,
                'Количество типов площадок': self.typesOfPlaces,
                'Регионы': _w,
                'Типы площадок': cost_and_capacity}

        with open('data.json', 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=4, ensure_ascii=False)


numberOfRegs = 11
typesOfPlaces = 3
T = 3
upperBound, totalBudget, totalProjPerYear = 9, 160000000, 3

obj = GenerateJSON(numberOfRegs, typesOfPlaces, T, upperBound, totalBudget, totalProjPerYear)
obj.gap()
