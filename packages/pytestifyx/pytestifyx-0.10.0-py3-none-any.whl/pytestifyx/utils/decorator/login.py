import functools
import pytest
import inspect


def auto_login(func):
    @functools.wraps(func)
    def wrapper(self, param=None, request=None, **kwargs):
        # 如果 param 是 None，就创建一个新的字典
        if param is None:
            param = {}
        # 获取当前测试函数的所有 fixture
        fixturenames = kwargs.keys()
        # 遍历所有的 fixture，找出那些以 "login" 开头的 fixture
        for fixture_name in fixturenames:
            if fixture_name.startswith("login"):
                login_fixture_value = kwargs.get(fixture_name)
                # 将这个 fixture 的值赋给 param["_headers"]
                param["_headers"] = login_fixture_value

        # 调用原始的测试函数
        return func(self, param, **kwargs)

    return wrapper
