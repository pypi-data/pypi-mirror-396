import inspect
from pytestifyx.utils.parse.config import parse_yaml_config


class RequestConfig:
    is_cover_header = True  # 同名字段是否覆盖原有请求头
    encrypt_type = 'Single'  # 加密方式，Single单字段加密，Multi多字段加密
    sign_type = 'Header'  # 加签方式，Header存放签名，Body体存放签名
    request_type = 'HTTP'  # 请求方式，HTTP/DUBBO/MQ
    request_method = 'POST'  # 请求方法，POST/GET
    content_type = 'json'  # 请求头Content-Type
    is_json_dumps = True  # 是否对请求体进行json.dumps
    delete_key = []  # 删除请求参数中的某些字段
    concurrent_number = 1  # 并发数量


class TemplateConfig:
    is_body_reload = True  # 是否重新加载body模版
    is_header_reload = True  # 是否重新加载header模版


class EncryptConfig:
    encrypt_flag = True  # 是否加密
    encrypt_method = 'RSA'  # 加密方式，RSA/AES/DES


class SignConfig:
    sign_flag = True  # 是否加签
    sign_method = 'RSA'  # 加签方式，RSA/MD5/SHA256/SHA512


class EnvConfig:
    env_name = 'test'  # 环境环境，test/dev/pre/prod


class AssertConfig:
    assert_db = True  # 是否校验响应结果


class LogConfig:
    is_request_log = True  # 是否打印请求日志
    is_request_log_json_dumps = True  # 是否对请求日志进行json.dumps
    is_response_log = True  # 是否打印返回日志
    is_sql_log = True  # 是否打印sql日志


class TenantIdConfig:
    tenant_id = ''  # 租户ID


class Config(RequestConfig, TemplateConfig, EncryptConfig, SignConfig, EnvConfig, AssertConfig, LogConfig, TenantIdConfig):
    def __init__(self):
        super().__init__()
        self.load_from_config_file()

    def load_from_config_file(self):
        config = parse_yaml_config('config.yaml')['config']
        for key, value in config.items():
            setattr(self, key, value)

    def set_attr(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def get_attr(self, attr):
        return getattr(self, attr)

    def get_all_attr(self):
        attributes = [i for i in inspect.getmembers(self) if not inspect.isroutine(i[1])]
        attribute = {}
        for a in attributes:
            if not a[0].startswith('__'):
                attribute[a[0]] = a[1]
        return attribute

    def merge_configs(self, other_config):
        new_config = Config()
        for attr, value in other_config.get_all_attr().items():
            setattr(new_config, attr, value)
        return new_config


if __name__ == '__main__':
    config = Config()
    print(config.get_all_attr())
    config.set_attr(**{'is_cover_header': False})
    print(config.get_all_attr())
