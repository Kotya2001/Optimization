from ortools.sat.python import cp_model


def LinearProgrammingExample(w, b, cost, p, e, T, w_dict, upperBound, totalBudget, totalProjPerYear, numberOfRegs,
                             typesOfPlaces, maxNumberCourts):
    years = ['year' + '_' + str(i) for i in range(1, T + 1)]
    res = []

    model = cp_model.CpModel()
    variables = []

    # Создаем переменные
    for t in range(1, T + 1):
        for key in list(w_dict.keys()):
            for k in list(w_dict[key].keys()):
                variables.append(model.NewIntVar(0, 10, (key + '.' + k + '.' + years[t - 1])))

    # Верхняя граница
    for var in variables:
        model.Add(var <= upperBound)

    # Ограничения на количесвто объектов в год
    for i in range(0, len(variables), numberOfRegs * typesOfPlaces):
        model.Add(sum(variables[i:i + (numberOfRegs * typesOfPlaces)]) <= totalProjPerYear)

    # Ограничения на стоиммость объектов за T лет
    tot = []
    for i in range(0, len(variables), typesOfPlaces):
        l = variables[i: i + typesOfPlaces]
        # print(l)
        for j in range(len(l)):
            tot.append(l[j] * cost[int(i / typesOfPlaces) % numberOfRegs][j])
    # print(cost)

    model.Add(sum(tot) <= totalBudget)

    vars = dict(sorted({str(var): var for var in variables}.items(), key=lambda x: x[0]))

    # Ограничение на максимальное количесвто площадок в каждом регионе
    for i in range(0, len(list(vars.values())), T * typesOfPlaces):
        model.Add(sum(list(vars.values())[i: i + (T * typesOfPlaces)]) <= maxNumberCourts)

    # Ограничение на колиество баскетболистов
    for i in range(0, len(list(vars.values())), T * typesOfPlaces):
        regs = []
        v = list(vars.values())[i: i + (T * typesOfPlaces)]
        for j in range(0, len(v), T):
            regs.append(sum(v[j:j + T]) * e[int(j / T) % T])

        model.Add(sum(regs) <= b[int(i / (T * typesOfPlaces))])

    obj = []

    for i in range(0, len(list(vars.values())), T * typesOfPlaces):
        v = list(vars.values())[i: i + (T * typesOfPlaces)]
        for j in range(0, len(v), T):
            coef = (w[int(i / (T * typesOfPlaces))][int(j / T) % T] + p[int(i / (T * typesOfPlaces))])
            for t in range(T):
                obj.append(coef * v[j:j + T][t] * ((T + 1 - (t + 1)) / T))

    model.Maximize(sum(obj))
    solver = cp_model.CpSolver()
    solver.parameters.log_search_progress = True
    status = solver.Solve(model)

    if status == cp_model.OPTIMAL:
        for key in list(vars.keys()):
            if int(solver.Value(vars[key])) > 0:
                reg, court, year = tuple(key.split('.'))
                res.append((reg, court, year, int(solver.Value(vars[key]))))

        ans = {i[0]: {i[1]: {i[2]: i[3]}} for i in res}
        print('Objective value =', solver.ObjectiveValue())

    return ans
