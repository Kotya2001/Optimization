from GenJSON.CreateJSON import GenerateJSON
from ortools.linear_solver import pywraplp
import numpy as np


def get_data(numberOfObjects, numberOfFeatures, namesOfCrits, rankCrits, numberOfTypes, intCrits, bnCrits):
    """

    :param numberOfObjects: int - Количесвто городов
    :param numberOfFeatures: int - Количесвто критериев
    :param namesOfCrits: List - Названия криетриев для оптимизации
    :param rankCrits:  List - спикок ранговых критериев (Приеоретиность)
    :param numberOfTypes: int - Колчиесвто типов площадок
    :param intCrits: List - сипсок челочисленных критериев
    :param bnCrits: list - список бинарных критериев
    :return:
    """
    obj = GenerateJSON(numberOfObjects, numberOfFeatures, namesOfCrits, rankCrits, numberOfTypes, intCrits, bnCrits)

    obj.gap_matrix_no_rk()
    obj.gap_matrix_rk()

    general, w, cost, p, e = obj.get_json()

    return general, w, cost, p, e


def LinearProgrammingExample(general, w, costs, p, e, years, T, const):
    typesOfplaces = len(w[list(w.keys())[0]]['Приоритетность площадки'])
    numberOfRegs = len(w)

    cost = [costs[i] for i in list(costs.keys())]

    w = [[*list((list(w[key].values())[0].values()))] for key in list(w.keys())]
    result = {}

    e = [e[i] for i in list(e.keys())]
    p = [p[i] for i in list(p.keys())]
    b = [general[i]['Количество баскетболистов'] for i in list(general.keys())]

    count = 0
    solver = pywraplp.Solver.CreateSolver('SCIP')
    variables = []

    # Создаем переменные
    for t in range(1, years + 1):
        for j in range(1, typesOfplaces + 1):
            for i in range(1, numberOfRegs + 1):
                variables.append(solver.IntVar(0, 20, ('x_' + str(i) + '_' + str(j) + '_' + str(t))))

    # Ограничение на каждую переменную(верхняя граница)
    for var in variables:
        solver.Add(var <= const)

    # Ограничения на количесвто объектов в год
    for i in range(numberOfRegs):
        for j in range(0, len(variables[i::numberOfRegs]), typesOfplaces):
            solver.Add(sum(variables[i::numberOfRegs][j:j + typesOfplaces]) <= 3)

    # Ограничения на стоиммость объектов за 3 года
    for i in range(numberOfRegs):
        ex = []
        for j in range(0, len(variables[i::numberOfRegs]), typesOfplaces):
            ex.append(variables[i::numberOfRegs][j:j + typesOfplaces])

        ex = np.array(ex).T

        solver.Add(sum([cost[k] * sum(ex[k, :].tolist()) for k in range(len(ex))]) <= 160000000)

    ex = []
    for i in range(numberOfRegs):
        for j in range(0, len(variables[i::numberOfRegs]), typesOfplaces):
            ex.append(variables[i::numberOfRegs][j:j + typesOfplaces])

    ex = np.array(ex)

    # Ограничение на колиество баскетболистов

    for y in range(0, len(ex), years):
        arr = ex[y:years + y, :]

        for i in range(0, len(arr.T.ravel().tolist()), years):
            res = [e[c] * sum(arr.T.ravel().tolist()[i:i + years]) for c in range(len(e))]

        solver.Add(sum(res) <= b[count])
        count += 1

    objective = solver.Objective()
    count = 0

    for y in range(0, len(ex), years):
        arr = ex[y:years + y, :]
        for t in range(1, years + 1):
            for j in range(typesOfplaces):
                objective.SetCoefficient(arr[t - 1][j], int((w[count][j] + p[count]) * (T + 1 - t) / T))
        count += 1
    objective.SetMaximization()

    status = solver.Solve()
    count = 0

    if status == pywraplp.Solver.OPTIMAL or status == pywraplp.Solver.FEASIBLE:

        for y in range(0, len(ex), years):
            arr = ex[y:years + y, :].T
            for i in range(typesOfplaces):
                for t in range(years):
                    if arr[i, t].solution_value() > 0:
                        result[str(arr[i, t])] = arr[i, t].solution_value()

            count += 1
        # print('Objective value =', solver.Objective().Value())

    return result


general, w, cost, p, e = get_data(
    19, 6, ['Количество баскетболистов',
            'количестве существующих спортивных инфраструктурных объектов',
            'количество ресурсов',
            'возможность выделения в городе необходимого земельного участка',
            'финансовая самообеспеченность',
            'наличие представительства ПСБ'], ['Приоритетность площадки'], 3, [
        'количестве существующих спортивных инфраструктурных объектов',
    ], ['наличие представительства ПСБ', 'возможность выделения в городе необходимого земельного участка']
)

print(LinearProgrammingExample(general, w, cost, p, e, 3, 3, 5))