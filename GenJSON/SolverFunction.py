from ortools.linear_solver import pywraplp


def LinearProgrammingExample(w, b, cost, p, e, T, w_dict, a, u, upperBound, totalBudget, totalProjPerYear, numberOfRegs,
                             typesOfPlaces, maxNumberCourts):
    years = ['year' + '_' + str(i) for i in range(1, T + 1)]
    res = []

    solver = pywraplp.Solver.CreateSolver('SCIP')
    solver.EnableOutput()
    variables = []

    # Создаем переменные
    for t in range(1, T + 1):
        for key in list(w_dict.keys()):
            for k in list(w_dict[key].keys()):
                variables.append(solver.IntVar(0, upperBound, (key + '.' + k + '.' + years[t - 1])))

    # Ограничения на количесвто объектов в год
    for i in range(0, len(variables), numberOfRegs * typesOfPlaces):
        solver.Add(sum(variables[i:i + (numberOfRegs * typesOfPlaces)]) <= totalProjPerYear)

    # Ограничения на стоиммость объектов за T лет
    tot = []
    for i in range(0, len(variables), typesOfPlaces):
        l = variables[i: i + typesOfPlaces]
        for j in range(len(l)):
            tot.append(l[j] * cost[int(i / typesOfPlaces) % numberOfRegs][j])

    solver.Add(sum(tot) <= totalBudget)

    vars = dict(sorted({str(var): var for var in variables}.items(), key=lambda x: x[0]))

    # Ограничение на максимальное количесвто площадок в каждом регионе
    for i in range(0, len(list(vars.values())), T * typesOfPlaces):
        solver.Add(sum(list(vars.values())[i: i + (T * typesOfPlaces)]) <= maxNumberCourts)

    # Ограничение на колиество баскетболистов
    for i in range(0, len(list(vars.values())), T * typesOfPlaces):
        regs = []
        v = list(vars.values())[i: i + (T * typesOfPlaces)]
        for j in range(0, len(v), T):
            regs.append(sum(v[j:j + T]) * e[int(j / T) % T])

        solver.Add(sum(regs) <= b[int(i / (T * typesOfPlaces))])

    # Ограничение на затраты регионов
    for i in range(0, len(list(vars.values())), T * typesOfPlaces):
        regs = []
        v = list(vars.values())[i: i + (T * typesOfPlaces)]
        for j in range(0, len(v), T):
            regs.append(sum(v[j:j + T]) * u[int(i / (T * typesOfPlaces) % (T * typesOfPlaces))][int(j / T)])

        solver.Add(sum(regs) <= a[int(i / (T * typesOfPlaces))])

    obj = []

    for i in range(0, len(list(vars.values())), T * typesOfPlaces):
        v = list(vars.values())[i: i + (T * typesOfPlaces)]
        for j in range(0, len(v), T):
            coef = (w[int(i / (T * typesOfPlaces))][int(j / T) % T] + p[int(i / (T * typesOfPlaces))])
            for t in range(T):
                obj.append(coef * v[j:j + T][t] * ((T + 1 - (t + 1)) / T))

    solver.Maximize(sum(obj))
    status = solver.Solve()

    if status == pywraplp.Solver.OPTIMAL:
        for key in list(vars.keys()):
            if int(vars[key].solution_value()) > 0:
                reg, court, year = tuple(key.split('.'))
                res.append((reg, court, year, int(vars[key].solution_value())))

        ans = {i[0]: {i[1]: {i[2]: i[3]}} for i in res}
        print('Objective value =', solver.Objective().Value())

    return ans
