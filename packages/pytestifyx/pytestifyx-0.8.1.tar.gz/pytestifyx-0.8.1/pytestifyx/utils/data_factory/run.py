from collections import OrderedDict
from pytestifyx.utils.data_factory.core.factory import Factory


class MakeData:

    def __init__(self):
        self._factory_map = OrderedDict()
        self._factory_map['data'] = Factory.create()
        self._factories = list(self._factory_map.values())

    def __getattr__(self, attr):
        return getattr(self._factories[0], attr)


if __name__ == '__main__':
    md = MakeData()
    print(md.basic('汉字', '12', '14'))
    print(md.name('MALE'))
