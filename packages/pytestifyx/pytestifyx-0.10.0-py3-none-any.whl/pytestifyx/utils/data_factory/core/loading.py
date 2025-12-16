import pkgutil
from pathlib import Path
from types import ModuleType
from typing import List


def get_path(module: ModuleType) -> str:
    path = Path(module.__file__).parent
    return str(path)


def list_module(module: ModuleType) -> List[str]:
    path = get_path(module)
    return [name for _, name, is_pkg in pkgutil.iter_modules([str(path)]) if is_pkg]


def find_available_providers(modules: List[ModuleType]) -> List[str]:
    available_providers = set()
    for providers_mod in modules:
        if providers_mod.__package__:
            providers = ['.'.join([providers_mod.__package__, mod]) for mod in list_module(providers_mod)]
            available_providers.update(providers)
    return sorted(available_providers)
