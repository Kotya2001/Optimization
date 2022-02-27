from GenJSON.CreateJSON import GenerateJSON
from GenJSON.DataTransform import get_data
from GenJSON.SolverFunction import LinearProgrammingExample

numberOfRegs = 5
typesOfPlaces = 3
T = 3
upperBound, totalBudget, totalProjPerYear = 4, 160000000, 3
path = 'GenJSON/data.json'

obj = GenerateJSON(numberOfRegs, typesOfPlaces, T, upperBound, totalBudget, totalProjPerYear)
obj.gap()

transformFunction = get_data('GenJSON/data.json')
solverFunction = LinearProgrammingExample(*transformFunction)
print(solverFunction)




