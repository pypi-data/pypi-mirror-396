import functools
import time
import traceback
import inspect
from datetime import datetime
from functools import wraps

from pytestifyx.utils.logs.core import log


def retry(max_attempts=5, delay=1):
    """
    装饰器，用于在函数执行失败时自动重试。
    max_attempts: 最大重试次数。
    delay: 每次重试之间的延迟（秒）。
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            attempts = 0
            while attempts < max_attempts:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    attempts += 1
                    print(f"异常：{e}，正在尝试第 {attempts} 次重试...")
                    time.sleep(delay)
            return None

        return wrapper

    return decorator


def run_time_locate(func):
    def wrapper(*args, **kwargs):
        start = datetime.now()
        _func = func(*args, **kwargs)
        end = datetime.now()
        wait_time = (end - start).microseconds / 1000
        log.info(f'元素定位+操作共耗时: {wait_time} ms')
        return _func

    return wrapper


def run_many_times(times=1):
    """把函数运行times次的装饰器
    :param times:运行次数
    没有捕获错误，出错误就中断运行，可以配合handle_exception装饰器不管是否错误都运行n次。
    """

    def _run_many_times(func):
        @wraps(func)
        def __run_many_times(*args, **kwargs):
            for i in range(times):
                log.debug('* ' * 50 + '当前是第 {} 次运行[ {} ]函数'.format(i + 1, func.__name__))
                func(*args, **kwargs)

        return __run_many_times

    return _run_many_times


def handle_exception(retry_times=0, error_detail_level=0, is_throw_error=True, time_sleep=0):
    """捕获函数错误的装饰器,重试并打印日志
    :param time_sleep:
    :param retry_times : 重试次数
    :param error_detail_level :为0打印exception提示，为1打印3层深度的错误堆栈，为2打印所有深度层次的错误堆栈
    :param is_throw_error : 在达到最大次数时候是否重新抛出错误
    :type error_detail_level: int
    """

    if error_detail_level not in [0, 1, 2]:
        raise Exception('error_detail_level参数必须设置为0 、1 、2')

    def _handle_exception(func):
        @wraps(func)
        def __handle_exception(*args, **kwargs):
            for i in range(0, retry_times + 1):
                try:
                    result = func(*args, **kwargs)
                    if i:
                        log.debug(u'%s\n调用成功，调用方法--> [  %s  ] 第  %s  次重试成功' % ('# ' * 40, func.__name__, i))
                    return result

                except Exception as e:
                    error_info = ''
                    if error_detail_level == 0:
                        error_info = '错误类型是：' + str(e.__class__) + '  ' + str(e)
                    elif error_detail_level == 1:
                        error_info = '错误类型是：' + str(e.__class__) + '  ' + traceback.format_exc(limit=3)
                    elif error_detail_level == 2:
                        error_info = '错误类型是：' + str(e.__class__) + '  ' + traceback.format_exc()
                    log.error(u'%s\n记录错误日志，调用方法--> [  %s  ] 第  %s  次错误重试， %s\n' % ('- ' * 40, func.__name__, i, error_info))
                    if i == retry_times and is_throw_error:  # 达到最大错误次数后，重新抛出错误
                        raise e
                time.sleep(time_sleep)

        return __handle_exception

    return _handle_exception


def cost_time(func):
    def wrapper(*args, **kwargs):
        t1 = time.time()
        result = func(*args, **kwargs)
        t2 = time.time()
        log.info(f"{func.__name__} running time: {t2 - t1} secs.")
        return result

    return wrapper


def type_assert(fn):
    def wrapper(*args, **kwargs):
        sig = inspect.signature(fn)
        params = sig.parameters
        va = list(params.values())
        for arg, param in zip(args, va):
            if param.annotation != inspect._empty and not isinstance(arg, param.annotation):
                raise TypeError("you must input {}".format(param.annotation))
        for k, v in kwargs.items():
            if params[k].annotation != inspect._empty and not isinstance(v, params[k].annotation):
                raise TypeError("you must input {}".format(params[k].annotation))
        cc = fn(*args, **kwargs)
        return cc

    return wrapper
