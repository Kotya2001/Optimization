from ortools.linear_solver import pywraplp
import numpy as np


def LinearProgrammingExample(w, b, cost, p, e, T, w_dict, upperBound, totalBudget, totalProjPerYear, numberOfRegs,
                             typesOfPlaces):
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
        solver.Add(var <= upperBound)

    # Ограничения на количесвто объектов в год
    for i in range(numberOfRegs):
        for j in range(0, len(variables[i::numberOfRegs]), typesOfPlaces):
            solver.Add(sum(variables[i::numberOfRegs][j:j + typesOfPlaces]) <= totalProjPerYear)

    # Ограничения на стоиммость объектов за T лет
    for i in range(numberOfRegs):
        ex = []
        for j in range(0, len(variables[i::numberOfRegs]), typesOfPlaces):
            ex.append(variables[i::numberOfRegs][j:j + typesOfPlaces])

        ex = np.array(ex).T

        solver.Add(sum([cost[k] * sum(ex[k, :].tolist()) for k in range(len(ex))]) <= totalBudget)

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
