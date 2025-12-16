import os
import inspect

from pytestifyx.driver.api import BaseRequest
from pytestifyx.driver.web import BasePage
from pytestifyx.config import pytestifyx_str
from pytestifyx.utils.requests.requests_config import Config


class TestCase:
    _config_instances = {}

    # 不同方法的配置实例是隔离的 同一个方法的配置实例是共享的
    def get_config_instance(self, method_name):
        if method_name not in self._config_instances:
            self._config_instances[method_name] = Config()
        return self._config_instances[method_name]

    def __getattribute__(self, name):
        if name == 'config':
            # 获取当前正在执行的方法的名称
            current_method = inspect.currentframe().f_back.f_code.co_name
            return self.get_config_instance(current_method)
        else:
            return super().__getattribute__(name)

    @classmethod
    def setup_class(cls):
        print(pytestifyx_str)
        print('------------------------------用例测试启动🚀🚀🚀------------------------------')

    @staticmethod
    def page(play: object, name: str = None):
        print('首次运行会下载浏览器驱动⏬，请耐心等待⌛️')
        os.system('python -m playwright install')
        return BasePage(play, name=name)

    def api(self, path, func_name, config, params, **kwargs):
        return BaseRequest().base(path, func_name, config, params, **kwargs)
