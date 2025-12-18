import json
from clarifai.runners.utils import data_utils
from clarifai.runners.models.model_class import ModelClass

import inspect

def log_stack():
    for frame_info in inspect.stack():
        print(f"{frame_info.filename}:{frame_info.lineno} in {frame_info.function}")


default = 27

x = json.dumps(default)

print(x, type(x))

x = json.loads(x)

print(x, type(x))

param = data_utils.Param(default)

print(param, type(param))

print(param.default)

param_json = json.dumps(param)

print(param_json, type(param_json))

param_json = json.loads(param_json)

print(param_json, type(param_json))

# param_json = json.loads(param_json)

# print(param_json, type(param_json))

def test_int(default: int = data_utils.Param(default=27)):
    print(default, type(default))

test_int()





class Test(ModelClass):
    
    @ModelClass.method
    def test(self, max_tokens: int = data_utils.Param(default=27)) -> int:
        print(max_tokens, type(max_tokens))
        return max_tokens

test = Test()

test.test()

