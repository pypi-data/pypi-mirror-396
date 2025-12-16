class BaseProvider:
    __provider__ = 'base'

    def __init__(self, generator):
        self.generator = generator

    def random_int(self, min, max):
        return self.generator.random.randint(min, max)

    def random_digit(self):
        return self.generator.random.randint(0, 9)

    def random_digit_not_null(self):
        return self.generator.random.randint(1, 9)

    def random_elements(self, elements=('a', 'b', 'c'), length=None):
        if isinstance(elements, dict):
            if not hasattr(elements, "_key_cache"):
                elements._key_cache = tuple(elements.keys())
            choices = elements._key_cache
        else:
            choices = elements
        return [self.generator.random.choice(choices)] if length == 1 else self.generator.random.choices(choices,
                                                                                                         k=length)

    def random_element(self, elements=('a', 'b', 'c')):
        return self.random_elements(elements, length=1)[0]
