from random import Random


class Generator:
    def __init__(self):
        self.providers = []
        self.__random = Random()

    def add_provider(self, provider):

        if isinstance(provider, type):
            provider = provider(self)
        self.providers.insert(0, provider)
        for method_name in dir(provider):
            if method_name.startswith('_'):
                continue
            faker_function = getattr(provider, method_name)
            if callable(faker_function):
                self.set_formatter(method_name, faker_function)

    @property
    def random(self):
        return self.__random

    def set_formatter(self, name, method):
        setattr(self, name, method)
