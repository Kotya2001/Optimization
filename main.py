import json

from GenJSON.CreateJSON import GenerateJSON
from ortools.linear_solver import pywraplp
import numpy as np

numberOfRegs = 3
typesOfPlaces = 3
T = 3
path = 'GenJSON/data.json'

obj = GenerateJSON(numberOfRegs, typesOfPlaces, T)
obj.gap()


def get_data(json_path):
    """

    :param json_path: путь к файлу json
    :return: list для задачи оптимизации
    """

    with open(json_path) as file:
        data = json.load(file)

    info = data["Общая информация"]

    w_dict = {i: data["Информация регионов"][i]["Приоритетность площадки"] for i in
              list(data["Информация регионов"].keys())}
    b = {i: data["Информация регионов"][i]["Количество баскетболистов"] for i in
         list(data["Информация регионов"].keys())}
    cost = data["Стоимость площадок"]
    p = data["Ранги регионов"]
    e = data["Вместимость площадок"]

    # Сортируем ключи json, чтобы учесть неупорядоченность введенных данных
    b = dict(sorted(b.items(), key=lambda x: x[0]))
    cost = dict(sorted(cost.items(), key=lambda x: x[0]))
    p = dict(sorted(p.items(), key=lambda x: x[0]))
    e = dict(sorted(e.items(), key=lambda x: x[0]))
    w_dict = dict(sorted({i: dict(sorted(w_dict[i].items(), key=lambda x: x[0])) for i in list(w_dict.keys())}.items(),
                         key=lambda x: x[0]))

    cost = [cost[i] for i in list(cost.keys())]
    w = [[*list((list(w_dict[key].values())))] for key in list(w_dict.keys())]
    e = [e[i] for i in list(e.keys())]
    p = [p[i] for i in list(p.keys())]
    b = [b[i] for i in list(b.keys())]
    T = info['Число лет']

    return w, b, cost, p, e, T, w_dict,


# print(get_data('GenJSON/data.json'))


def LinearProgrammingExample(w, b, cost, p, e, T, w_dict, numberOfRegs, typesOfPlaces, const=5):
    """

    :param w: матрица приоритетностей площадок
    :param b: вектор количества спортсменов
    :param cost: стоимость площадок
    :param p: ранг регионов
    :param e: вместимость площадок
    :param T: на какое количество лет
    :param const: верхнее ограничение на количесвто площадок
    :return: dict количесва площадок для каждого региона, конкретного типа в конктретный год
    """
    result = {}

    count = 0
    solver = pywraplp.Solver.CreateSolver('SCIP')
    variables = []

    # Создаем переменные
    for t in range(1, T + 1):
        for key in list(w_dict.keys()):
            for k in list(w_dict[key].keys()):
                variables.append(solver.IntVar(0, 10, (key + '_' + k + '_' + 'год' + '_' + str(t))))

    # Верхняя граница
    for var in variables:
        solver.Add(var <= const)

    # Ограничения на количесвто объектов в год
    for i in range(numberOfRegs):
        for j in range(0, len(variables[i::numberOfRegs]), typesOfPlaces):
            solver.Add(sum(variables[i::numberOfRegs][j:j + typesOfPlaces]) <= 3)

    # Ограничения на стоиммость объектов за 3 года
    for i in range(numberOfRegs):
        ex = []
        for j in range(0, len(variables[i::numberOfRegs]), typesOfPlaces):
            ex.append(variables[i::numberOfRegs][j:j + typesOfPlaces])

        ex = np.array(ex).T

        solver.Add(sum([cost[k] * sum(ex[k, :].tolist()) for k in range(len(ex))]) <= 160000000)

    ex = []
    for i in range(numberOfRegs):
        for j in range(0, len(variables[i::numberOfRegs]), typesOfPlaces):
            ex.append(variables[i::numberOfRegs][j:j + typesOfPlaces])

    ex = np.array(ex)

    # Ограничение на колиество баскетболистов

    for y in range(0, len(ex), T):
        arr = ex[y:T + y, :]

        for i in range(0, len(arr.T.ravel().tolist()), T):
            res = [e[c] * sum(arr.T.ravel().tolist()[i:i + T]) for c in range(len(e))]

        solver.Add(sum(res) <= b[count])
        count += 1

    objective = solver.Objective()
    count = 0

    for y in range(0, len(ex), T):
        arr = ex[y:T + y, :]
        for t in range(1, T + 1):
            for j in range(typesOfPlaces):
                objective.SetCoefficient(arr[t - 1][j], int((w[count][j] + p[count]) * (T + 1 - t) / T))
        count += 1
    objective.SetMaximization()

    status = solver.Solve()
    count = 0

    if status == pywraplp.Solver.OPTIMAL or status == pywraplp.Solver.FEASIBLE:

        for y in range(0, len(ex), T):
            arr = ex[y:T + y, :].T
            for i in range(typesOfPlaces):
                for t in range(T):
                    if arr[i, t].solution_value() > 0:
                        result[str(arr[i, t])] = arr[i, t].solution_value()

            count += 1
    return result


print(LinearProgrammingExample(*get_data(path), numberOfRegs, typesOfPlaces, const=4))
