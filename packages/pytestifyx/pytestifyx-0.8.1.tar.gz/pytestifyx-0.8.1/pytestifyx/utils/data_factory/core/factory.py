from importlib import import_module
from pytestifyx.utils.data_factory.core.config import PROVIDERS
from pytestifyx.utils.data_factory.core.generator import Generator


class Factory:
    @classmethod
    def create(cls):
        faker = Generator()
        for prov_name in PROVIDERS:
            prov_cls = cls._get_provider_class(prov_name)
            provider = prov_cls(faker)
            provider.__provider__ = prov_name
            faker.add_provider(provider)
        return faker

    @classmethod
    def _get_provider_class(cls, provider):
        provider_class = cls._find_provider_class(provider)
        if provider_class:
            return provider_class
        msg = f"Unable to find provider '{provider}'"
        raise ValueError(msg)

    @classmethod
    def _find_provider_class(cls, provider_path):
        provider_module = import_module(provider_path)
        return provider_module.Provider
