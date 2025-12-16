def pytest_collection_modifyitems(items):
    """
    在收集测试用例之后修改测试名称，避免中文乱码。
    """
    for item in items:
        item.name = item.name.encode("utf-8").decode("unicode_escape")
        item._nodeid = item.nodeid.encode("utf-8").decode("unicode_escape")
