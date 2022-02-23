import numpy as np
import random


class GenerateJSON():

    def __init__(self, number_of_object, number_of_criterions, names_of_crits, rK_crits, rk_obj, int_crits, bn_crits,
                 random_state=42):

        '''
        number_of_object - Количесвто объектов
        number_of_criterions - Количесвто критериев
        names_of_crits - Имена критериев --> list
        rK_crits - ранговые критергии --> list
        rK_obj - количесвто типов категорий --> list
        int_crits - Имена целочисленных критериев (Кроме количесвта баскетболистов) --> list
        bn_crits - Имена бинарных критериев --> list

        '''

        self.number_of_object = number_of_object
        self.number_of_criterions = number_of_criterions
        self.names_of_obj = ['Регион' + '_' + str(i) for i in range(1, number_of_object + 1)]
        self.names_of_crits = names_of_crits
        self.rK_crits = rK_crits
        self.random_state = random_state
        self.int_crits = int_crits
        self.rk_obj = rk_obj
        self.bn_crits = bn_crits

        self.matrix = np.zeros((self.number_of_object, self.number_of_criterions)).astype(np.int64)
        self.rk_matrix = np.zeros((self.number_of_object, self.rk_obj)).astype(np.int64)

    def gap_matrix_no_rk(self):

        for i in range(len(self.names_of_obj)):
            for j in range(len(self.names_of_crits)):
                if self.names_of_crits[j] not in self.int_crits and self.names_of_crits[j] not in self.bn_crits and \
                        self.names_of_crits[j] != 'Количесвто баскетболистов':
                    self.matrix[i][j] = int(random.randint(20000, 10000043994))
                elif self.names_of_crits[j] == 'Количесвто баскетболистов':
                    self.matrix[i][j] = int(np.random.randint(1, 5000, (1, 1))[0][0])
                elif self.names_of_crits in self.int_crits:
                    self.matrix[i][j] = int(np.random.randint(1, 10000, (1, 1))[0][0])
                elif self.names_of_crits[j] in self.bn_crits:
                    self.matrix[i][j] = int(np.random.randint(0, 2, (1, 1))[0][0])

    def gap_matrix_rk(self):

        for k in range(len(self.names_of_obj)):
            for t in range(self.rk_obj):
                self.rk_matrix[k][t] = int(np.random.randint(1, 6, (1, 1))[0][0])

    def get_json(self):
        _json = {name: {} for name in self.names_of_obj}

        arr = list(_json.keys())

        for i in range(len(arr)):
            for j in range(len(self.names_of_crits)):
                _json[arr[i]][self.names_of_crits[j]] = self.matrix[i][j]

        _w = {name: {self.rK_crits[0]: {}} for name in self.names_of_obj}

        arr1 = list(_w.keys())
        squared = ['Тип площадки' + '_' + str(j) for j in range(1, self.rk_obj + 1)]

        for i in range(len(arr1)):
            for j in range(len(squared)):
                _w[arr1[i]][self.rK_crits[0]][squared[j]] = int(self.rk_matrix[i][j])

        _cost = {'Стоимость площадки типа' + str(o): random.randint(12000000, 20000000) for o in
                 range(1, self.rk_obj + 1)}
        _p = {'Ранг региона' + str(u): random.randint(0, 8) for u in range(1, self.number_of_object + 1)}
        _e = {'Тип площадки' + '_' + str(e): random.randint(50, 82) for e in range(1, self.rk_obj + 1)}

        return _json, _w, _cost, _p, _e
