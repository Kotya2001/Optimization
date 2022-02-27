from GenJSON.SolverFunction import LinearProgrammingExample
import json


def get_data(json_path):
    with open(json_path) as file:
        data = json.load(file)

    T = data["Периоды"]

    w_dict = {i: data["Регионы"][i]["Приоритетность площадки"] for i in
              list(data["Регионы"].keys())}
    b = {i: data["Регионы"][i]["Количество баскетболистов"] for i in
         list(data["Регионы"].keys())}
    cost = {i: data["Типы площадок"][i]["Стоимость"] for i in list(data["Типы площадок"].keys())}
    e = {i: data["Типы площадок"][i]["Вместимость"] for i in list(data["Типы площадок"].keys())}
    p = {i: data["Регионы"][i]["Ранг"] for i in
         list(data["Регионы"].keys())}

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
    upperBound, totalBudget, totalProjPerYear = data['Максимальное количество площадок в регионе в год'], data[
        'Общий бюджет'], data['Ограничение на количество проектов в год']
    numberOfRegs, typesOfPlaces = data['Количество регионов'], data['Количество типов площадок']

    return w, b, cost, p, e, T, w_dict, upperBound, totalBudget, totalProjPerYear, numberOfRegs, typesOfPlaces


path = 'GenJSON/data.json'

transformFunction = get_data(path)
solverFunction = LinearProgrammingExample(*transformFunction)
print(json.dumps(solverFunction, indent=4, ensure_ascii=False))
