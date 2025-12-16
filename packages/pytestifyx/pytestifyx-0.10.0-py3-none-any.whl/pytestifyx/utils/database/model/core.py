import datetime
from decimal import Decimal

from pytestifyx.utils.logs.core import log
from prettytable import PrettyTable


class BaseDict:

    def as_dict(self, is_sql_log=True):
        x = PrettyTable()
        dict_ = {}
        x.field_names = [i.name for i in self.__table__.columns]
        for i in self.__table__.columns:
            value = getattr(self, i.name, None)
            if isinstance(value, str):
                try:
                    t = eval(value)
                    if isinstance(t, (list, dict)):  # 如果是列表或字典，则转换为json格式
                        value = t
                except NameError:
                    pass
                except SyntaxError:
                    pass
            if isinstance(value, datetime.datetime):
                value = str(value)
            if isinstance(value, datetime.date):
                value = str(value)
            if isinstance(value, Decimal):  # TypeError: Decimal('10') is not JSON serializable
                value = float(value)
            dict_[i.name] = value
        x.add_row(dict_.values())
        if is_sql_log:
            log.info('\n' + str(x))
        return dict_
