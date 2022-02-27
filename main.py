from GenJSON.DataTransform import get_data
from GenJSON.SolverFunction import LinearProgrammingExample
import json

solverFunction = LinearProgrammingExample(*get_data('GenJSON/data.json'))
print(json.dumps(solverFunction, indent=4, ensure_ascii=False))
