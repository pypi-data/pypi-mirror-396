import importlib
import types


def walk_module(module, map):
    if module not in map:
        map[module] = None
        importlib.reload(module)
        for name in dir(module):
            obj = getattr(module, name)
            if isinstance(obj, types.ModuleType):
                walk_module(obj, map)


def reload_all(*modules):
    map = {}
    for module in modules:
        if isinstance(module, types.ModuleType):
            walk_module(module, map)

