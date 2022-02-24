import json

from GenJSON.CreateJSON import GenerateJSON
from ortools.linear_solver import pywraplp
import numpy as np

numberOfRegs = 12
typesOfPlaces = 3
T = 3
files_paths = (
    'GenJSON/b.json', 'GenJSON/cost.json', 'GenJSON/e.json', 'GenJSON/info.json', 'GenJSON/p.json', 'GenJSON/w.json')

obj = GenerateJSON(numberOfRegs, typesOfPlaces, T)
obj.gap()
obj.info()


def get_data(json_paths):
    """

    :param json_paths: tuple путей к json  файлам
    :return: list для задачи оптимизации
    """
    b, cost, e, info, p, w = files_paths

    with open(b) as file:
        b = json.load(file)
    with open(cost) as file:
        cost = json.load(file)
    with open(e) as file:
        e = json.load(file)
    with open(info) as file:
        info = json.load(file)
    with open(p) as file:
        p = json.load(file)
    with open(w) as file:
        w = json.load(file)

    cost = [cost[i] for i in list(cost.keys())]
    w = [[*list((list(w[key].values())[0].values()))] for key in list(w.keys())]
    e = [e[i] for i in list(e.keys())]
    p = [p[i] for i in list(p.keys())]
    b = [b[i]['Количество баскетболистов'] for i in list(b.keys())]

    numberOfRegs, typesOfPlaces, T = info['Количество регионов'], info['Количесвто типов площадок'], info['Число лет']

    return w, b, cost, p, e, numberOfRegs, typesOfPlaces, T


def LinearProgrammingExample(w, b, cost, p, e, numberOfRegs, typesOfPlaces, T, const=5):
    """

    :param w: матрица приоритетностей площадок
    :param b: вектор количества спортсменов
    :param cost: стоимость площадок
    :param p: ранг регионов
    :param e: вместимость площадок
    :param numberOfRegs: сколько регионов
    :param typesOfPlaces: сколько типов площадок
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
        for j in range(1, typesOfPlaces + 1):
            for i in range(1, numberOfRegs + 1):
                variables.append(solver.IntVar(0, 20, ('x_' + str(i) + '_' + str(j) + '_' + str(t))))

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


print(LinearProgrammingExample(*get_data(files_paths), const=5))
