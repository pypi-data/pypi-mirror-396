from prettytable import PrettyTable

from pytestifyx.utils.logs.core import log


def printify_table(data, align='c'):
    """
    以表格形式打印数据
    :param data: dict
    :param align: str
    :return: None
    """
    x = PrettyTable()
    x.field_names = list(data.keys())
    x.align = align
    x.add_row(list(data.values()))
    log.info('\n' + str(x))
