import json


def json_update(data, target_data: dict):
    for key, value in list(target_data.items()):
        if key.startswith('@'):  # 如果key以@开头，则表示该key为替换报文中的key
            path = key[1:].split('.')  # 去掉@，分割path
            current_data = data
            for p in path[:-1]:  # 遍历到倒数第二个元素，定位到最终的字典
                if p.isdigit():
                    p = int(p)  # 如果是数字，转换为整数
                current_data = current_data[p]
            final_key = path[-1]
            if final_key in current_data:
                current_data[final_key] = value  # 只更新精确匹配的键
        else:
            update_allvalues(data, {key: value})  # 对于非@开头的键，递归更新


def update_allvalues(data, kw: dict):
    if isinstance(data, dict):
        for k, v in data.items():
            if k in kw:
                data[k] = kw[k]
            else:
                data[k] = update_allvalues(v, kw)
        return data
    elif isinstance(data, list):
        for k, item in enumerate(data):
            data[k] = update_allvalues(item, kw)
        return data
    elif isinstance(data, str):
        try:  # 兼容报文格式为序列化后的字典："{'name':'lyh'}"
            if data.startswith('{') and data.endswith('}'):
                d = eval(data)
                if isinstance(d, dict):
                    return json.dumps(update_allvalues(d, kw))
                else:
                    return data
            else:
                return data
        except NameError:  # 未定义
            return data
        except SyntaxError:  # 'api_version': 'V1.0',
            return data
    else:
        return data


def remove_keys(data, keys: list):
    if isinstance(data, dict):
        for k, v in data.copy().items():  # RuntimeError: dictionary changed size during iteration
            if k in keys:
                data.pop(k)
            else:
                remove_keys(v, keys)
        return data
    elif isinstance(data, list):
        for k, item in enumerate(data):
            data[k] = remove_keys(item, keys)
        return data


if __name__ == '__main__':
    param = {}
    # param['@id'] = "1739669853902065661"
    param['@graph.cells.0.id'] = "1739669853902065661"
    data = {
        "id": "1739669853902065666",
        "graph": {
            "graphName": "default",
            "cells": [
                {"id": "1739669853902065666"}
            ]
        }
    }
    json_update(data, param)
    print(data)
