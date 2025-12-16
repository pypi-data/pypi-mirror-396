from pytestifyx.utils.decorator.public import type_assert
import json
from typing import List


class JsonPathFinder:
    def __init__(self, json_str, mode='key'):
        self.data = json.loads(json_str)
        self.mode = mode

    def iter_node(self, rows, road_step, target):
        if isinstance(rows, dict):
            key_value_iter = (x for x in rows.items())
        elif isinstance(rows, list):
            key_value_iter = (x for x in enumerate(rows))
        else:
            return
        for key, value in key_value_iter:
            current_path = road_step.copy()
            current_path.append(key)
            if self.mode == 'key':
                check = key
            else:
                check = value
            if check == target:
                yield current_path
            if isinstance(value, (dict, list)):
                yield from self.iter_node(value, current_path, target)

    def find_one(self, target: str) -> list:
        path_iter = self.iter_node(self.data, [], target)
        for path in path_iter:
            return path
        return []

    def find_all(self, target) -> List[list]:
        path_iter = self.iter_node(self.data, [], target)
        return list(path_iter)


def flat_dict(data: dict):
    out = {}
    for key, val in data.items():
        if isinstance(val, dict):
            val = [val]
        if isinstance(val, list):
            for subdict in val:
                deeper = flat_dict(subdict).items()
                out.update({key + '.' + key2: val2 for key2, val2 in deeper})
        else:
            out[key] = val
    return out


def data_flatten(val, key='', con_s='.', basic_types=(str, int, float, bool, complex, bytes)):
    """
    数据展开生成器,以键值对为最基础的数据
    param key: 键，默认为基础类型数据，不做进一步分析
    param val: 值，判断值的数据类型，如果为复杂类型就做进一步分析
    param con_s: 拼接符，当前级的键与父级键拼接的连接符，默认为_
    param basic_types: 基础数据类型元组，如果值的类型在元组之内，则可以输出
    return: 键值对元组
    """
    if isinstance(val, dict):
        for ck, cv in val.items():
            yield from data_flatten(cv, con_s.join([key, ck]).lstrip(con_s))
    elif isinstance(val, (list, tuple, set)):
        for index, item in enumerate(val):
            yield from data_flatten(item, con_s.join([key, str(index)]).lstrip(con_s))
    elif isinstance(val, basic_types) or val is None:
        yield str(key).lower(), val


def merge(dst: dict, src: dict):
    for key, value in src.items():
        if key not in dst:
            dst[key] = value
        elif isinstance(dst[key], dict) and isinstance(value, dict):
            merge(dst[key], value)
        else:
            raise Exception('数据格式有误，不能转换为嵌套字典')


@type_assert
def deflat_dict(data: dict):
    def unpack(key: list, value):
        if len(key) == 1:
            return {key[0]: value}
        else:
            prefix = key.pop(0)
            return {prefix: unpack(key, value)}

    result = {}
    for d in [unpack(key.split('.'), value) for key, value in data.items()]:
        merge(result, d)
    return result


def merge_json(dic_a: dict, dic_b: dict):
    """
    1：遍历字典1和字典2的每一个键
    2：如果两个字典的键是一样的，就给新字典的该键赋值为空列表然后空列表依次添加字典1和字典2 的值，然后将最后的值赋值给原字典
    3：如果两个字典的键不同，则分别将键值对加到新列表中
    """
    result_dic = {}
    for k, v in dic_a.items():
        for m, n in dic_b.items():
            if k == m:
                result_dic[k] = []
                result_dic[k].append(dic_a[k])
                result_dic[k].append(dic_b[k])
                dic_a[k] = result_dic[k]
                dic_b[k] = result_dic[k]
            else:
                result_dic[k] = dic_a[k]
                result_dic[m] = dic_b[m]
    return result_dic
