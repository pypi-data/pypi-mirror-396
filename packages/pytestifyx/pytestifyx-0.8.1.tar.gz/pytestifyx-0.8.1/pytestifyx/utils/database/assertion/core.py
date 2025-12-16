import json

from deepdiff import DeepDiff
from pytestifyx.utils.logs.core import log


def deep_diff(response, expect, **kwargs):
    """
    :param response: 实际返回报文
    :param expect: 预期值
    :return:
    """
    try:
        if kwargs['is_response_log']:
            log.info('实际返回为' + json.dumps(response, ensure_ascii=False))
    except KeyError:
        log.info('实际返回为' + json.dumps(response, ensure_ascii=False))
    log.info('预期值为' + json.dumps(expect, ensure_ascii=False))
    result = DeepDiff(response, expect)
    log.info(f"数据校验差异详情为{result}")
    if 'values_changed' in result:
        log.error(f"数据校验不通过,内容差异详情为{result['values_changed']}")
    elif 'type_changes' in result:
        log.error(f"数据校验不通过,类型差异详情为{result['type_changes']}")
    elif 'dictionary_item_added' in result:
        log.error(f"数据校验不通过,缺失字段详情为{result['dictionary_item_added']}")
    else:
        if 'dictionary_item_removed' in result:
            log.warning(f"数据校验通过,但实际返回多余字段，详情为{result['dictionary_item_removed']}")
        log.info('数据校验通过')
        return True
