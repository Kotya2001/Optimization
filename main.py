from GenJSON.SolverFunction import LinearProgrammingExample
import json


def get_data(json_path):
    with open(json_path) as file:
        data = json.load(file)

    T = data["Periods"]
    maxNumberCourts = data['The maximum number of basketball courts all types for each region']

    w_dict = {i: {
        j: data["Regions"][i]["Type of basketball court"][j]["Priority"]
        for
        j in list(data["Regions"][i]["Type of basketball court"].keys())
    } for i in
        list(data["Regions"].keys())}
    b = {i: data["Regions"][i]["Number of players"] for i in
         list(data["Regions"].keys())}
    a = {i: data["Regions"][i]["Regs budget"] for i in
         list(data["Regions"].keys())}
    u = {
        i: {j: data["Regions"][i]["Type of basketball court"][j]["Regional costs"]
            for
            j in list(data["Regions"][i]["Type of basketball court"].keys())
            } for i in
        list(data["Regions"].keys())}
    cost = {
        i: {j: data["Regions"][i]["Type of basketball court"][j]["cost"]
            for
            j in list(data["Regions"][i]["Type of basketball court"].keys())
            } for i in
        list(data["Regions"].keys())}
    e = {i: data["Types of basketball courts"][i]["Capacity"] for i in list(data["Types of basketball courts"].keys())}
    p = {i: data["Regions"][i]["Rank"] for i in
         list(data["Regions"].keys())}

    # Сортируем ключи json, чтобы учесть неупорядоченность введенных данных
    b = dict(sorted(b.items(), key=lambda x: int(x[0][x[0].index('_') + 1])))
    a = dict(sorted(a.items(), key=lambda x: int(x[0][x[0].index('_') + 1])))
    cost = dict(sorted({i: dict(sorted(cost[i].items(), key=lambda x: int(x[0][x[0].index('_') + 1]))) for i in
                        list(cost.keys())}.items(),
                       key=lambda x: int(x[0][x[0].index('_') + 1])))
    u = dict(sorted({i: dict(sorted(u[i].items(), key=lambda x: int(x[0][x[0].index('_') + 1]))) for i in
                        list(u.keys())}.items(),
                       key=lambda x: int(x[0][x[0].index('_') + 1])))
    p = dict(sorted(p.items(), key=lambda x: int(x[0][x[0].index('_') + 1])))
    e = dict(sorted(e.items(), key=lambda x: int(x[0][x[0].index('_') + 1])))
    w_dict = dict(sorted({i: dict(sorted(w_dict[i].items(), key=lambda x: int(x[0][x[0].index('_') + 1]))) for i in
                          list(w_dict.keys())}.items(),
                         key=lambda x: int(x[0][x[0].index('_') + 1])))

    cost = [[*list((list(cost[key].values())))] for key in list(cost.keys())]
    w = [[*list((list(w_dict[key].values())))] for key in list(w_dict.keys())]
    u = [[*list((list(u[key].values())))] for key in list(u.keys())]
    e = [e[i] for i in list(e.keys())]
    p = [p[i] for i in list(p.keys())]
    b = [b[i] for i in list(b.keys())]
    a = [a[i] for i in list(a.keys())]
    upperBound, totalBudget, totalProjPerYear = data["The maximum number of basketball courts in the region per year"], \
                                                data["Total budget"], data["Limit on the number of projects per year"]

    numberOfRegs, typesOfPlaces = len(data["Regions"]), len(data["Types of basketball courts"])

    return w, b, cost, p, e, T, w_dict, a, u, upperBound, totalBudget, totalProjPerYear, numberOfRegs, typesOfPlaces, maxNumberCourts


path = 'GenJSON/data.json'

transformFunction = get_data(path)
solverFunction = LinearProgrammingExample(*transformFunction)
print(json.dumps(solverFunction, indent=4, ensure_ascii=False))
