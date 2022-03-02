# from ortools.linear_solver import pywraplp
from ortools.sat.python import cp_model
import numpy as np


def LinearProgrammingExample(w, b, cost, p, e, T, w_dict, upperBound, totalBudget, totalProjPerYear, numberOfRegs,
                             typesOfPlaces):
    years = ['year' + '_' + str(i) for i in range(1, T + 1)]
    ans = {reg: {court: {year: None for year in years} for court in list(w_dict[reg].keys())} for reg in
           list(w_dict.keys())}

    # solver = pywraplp.Solver.CreateSolver('SCIP')
    model = cp_model.CpModel()
    variables = []

    # Создаем переменные
    for t in range(1, T + 1):
        for key in list(w_dict.keys()):
            for k in list(w_dict[key].keys()):
                # variables.append(solver.IntVar(0, 10, (key + '.' + k + '.' + years[t - 1])))
                variables.append(model.NewIntVar(0, 10, (key + '.' + k + '.' + years[t - 1])))

    # Верхняя граница
    for var in variables:
        model.Add(var <= upperBound)
        # solver.Add(var <= upperBound)


    # Ограничения на количесвто объектов в год
    for i in range(numberOfRegs):
        for j in range(0, len(variables[i::numberOfRegs]), typesOfPlaces):
            model.Add(sum(variables[i::numberOfRegs][j:j + typesOfPlaces]) <= totalProjPerYear)
            # solver.Add(sum(variables[i::numberOfRegs][j:j + typesOfPlaces]) <= totalProjPerYear)

    # Ограничения на стоиммость объектов за T лет
    for i in range(numberOfRegs):
        ex = []
        for j in range(0, len(variables[i::numberOfRegs]), typesOfPlaces):
            ex.append(variables[i::numberOfRegs][j:j + typesOfPlaces])

        ex = np.array(ex).T
        model.Add(sum([cost[k] * sum(ex[k, :].tolist()) for k in range(len(ex))]) <= totalBudget)
        # solver.Add(sum([cost[k] * sum(ex[k, :].tolist()) for k in range(len(ex))]) <= totalBudget)

    ex = []
    for i in range(numberOfRegs):
        for j in range(0, len(variables[i::numberOfRegs]), typesOfPlaces):
            ex.append(variables[i::numberOfRegs][j:j + typesOfPlaces])

    ex = np.array(ex)

    # Ограничение на максимальное количесвто площадок в каждом регионе
    for i in range(0, len(ex.T.ravel()), T * typesOfPlaces):
        model.Add(sum(ex.T.ravel()[i:(T * typesOfPlaces) + i]) <= 6)
        # solver.Add(sum(ex.T.ravel()[i:(T * typesOfPlaces) + i]) <= 6)

    # Ограничение на колиество баскетболистов
    for y in range(0, len(ex), T):
        arr = ex[y:T + y, :]

        for i in range(0, len(arr.T.ravel().tolist()), T):
            res = [e[c] * sum(arr.T.ravel().tolist()[i:i + T]) for c in range(len(e))]

        model.Add(sum(res) <= b[int(y / T)])
        # solver.Add(sum(res) <= b[int(y / T)])

    obj = []

    for y in range(0, len(ex), T):
        arr = ex[y:T + y, :]
        for t in range(1, T + 1):
            for j in range(typesOfPlaces):
                obj.append(int((w[int(y / T)][j] + p[int(y / T)]) * (T + 1 - t) / T) * arr[t - 1][j])

    model.Maximize(sum(obj))
    solver = cp_model.CpSolver()
    solver.parameters.log_search_progress = True
    status = solver.Solve(model)

    if status == cp_model.OPTIMAL:

        for y in range(0, len(ex), T):
            arr = ex[y:T + y, :].T
            for i in range(typesOfPlaces):
                for t in range(T):
                    reg, court, year = tuple(str(arr[i, t]).split('.'))
                    # ans[reg][court][year] = int(arr[i, t].solution_value())
                    ans[reg][court][year] = int(solver.Value(arr[i, t]))

        print('Objective value =', solver.ObjectiveValue())
    # print('Problem solved in %d iterations' % solver.)
    print('Problem solved in %f milliseconds' % solver.WallTime())

    return ans
