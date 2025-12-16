from importlib import import_module

from .loading import find_available_providers

META_PROVIDERS_MODULES = ['pytestifyx.utils.data_factory.providers']

PROVIDERS = find_available_providers([import_module(path) for path in META_PROVIDERS_MODULES])
