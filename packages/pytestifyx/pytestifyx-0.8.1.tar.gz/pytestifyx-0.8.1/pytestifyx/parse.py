import zipfile
import json
import os
from urllib.parse import urlparse, parse_qsl

from pytestifyx.utils.public.get_project_path import get_project_path, ensure_path_sep
from pytestifyx.utils.public.trans_param_style import convert_string


def trans_saz_to_test():
    busi_methods = []
    project = get_project_path()
    file = input("请输入saz文件的路径 🏭")
    application_name = input("请输入生成应用包的名称 💼，将会在项目根目录下的api_test目录下生成该应用包")
    # 打开SAZ文件
    with zipfile.ZipFile(file, 'r') as saz_file:
        # 遍历SAZ文件中的每个文件
        for filename in saz_file.namelist():
            # 如果文件名以'_c.txt'结尾
            if filename.endswith('_c.txt'):
                # 打开每个文件
                with saz_file.open(filename) as files:
                    # 读取文件内容
                    content = files.read().decode('utf-8')
                    # 分割请求行和请求头
                    parts = content.strip().split('\r\n')
                    # 提取请求方法和URL
                    method, url = parts[0].split(' ')[0:2]

                    try:
                        # 找到空字符串的索引
                        index = parts.index('')
                    except ValueError:
                        # 如果列表中没有空字符串，那么整个列表都是请求头
                        headers_block = parts[1:]
                        body = {}
                    else:
                        # 如果列表中有空字符串，那么空字符串前面的部分是请求头，后面的部分是请求体
                        headers_block = parts[1:index]
                        body = json.loads(parts[index + 1]) if index + 1 < len(parts) else {}
                    # 提取请求头
                    headers = {}
                    for line in headers_block:
                        name, value = line.split(': ', 1)
                        headers[name] = value
                    # 提取接口名称
                    parsed_url = urlparse(url)
                    api_name = parsed_url.path.replace('/', '_').lstrip('_')
                    # 提取查询参数
                    query_params = dict(parse_qsl(parsed_url.query))

                    # 创建目录
                    if not os.path.exists(f"{project}{ensure_path_sep(f'/api_test/{application_name}')}"):
                        os.makedirs(f"{project}{ensure_path_sep(f'/api_test/{application_name}')}")
                        open(f"{project}{ensure_path_sep(f'/api_test/{application_name}/__init__.py')}", 'a').close()
                    if not os.path.exists(f"{project}{ensure_path_sep(f'/api_test/{application_name}/template')}"):
                        os.makedirs(f"{project}{ensure_path_sep(f'/api_test/{application_name}/template')}")
                        open(f"{project}{ensure_path_sep(f'/api_test/{application_name}/template/__init__.py')}", 'a').close()
                    if not os.path.exists(f"{project}{ensure_path_sep(f'/api_test/{application_name}/test_case')}"):
                        os.makedirs(f"{project}{ensure_path_sep(f'/api_test/{application_name}/test_case')}")
                        open(f"{project}{ensure_path_sep(f'/api_test/{application_name}/test_case/__init__.py')}", 'a').close()
                    if not os.path.exists(f"{project}{ensure_path_sep(f'/api_test/{application_name}/test_data')}"):
                        os.makedirs(f"{project}{ensure_path_sep(f'/api_test/{application_name}/test_data')}")
                        open(f"{project}{ensure_path_sep(f'/api_test/{application_name}/test_data/__init__.py')}", 'a').close()

                    # 生成core.py文件
                    class_definition = f"""from pytestifyx import TestCase
from pytestifyx.driver.api import APIRequestMeta


# noinspection PyProtectedMember
class {convert_string(application_name)}(TestCase, metaclass=APIRequestMeta):
    \"\"\"
    数据集
    \"\"\"
    """
                    method_definition = f"""
    def {api_name}(self):
        \"\"\"
        api: api中文名
        应用：
        接口：{url}
        :return:
        \"\"\"
    """
                    if not os.path.exists(f"{project}{ensure_path_sep(f'/api_test/{application_name}/template/core.py')}"):
                        with open(f"{project}{ensure_path_sep(f'/api_test/{application_name}/template/core.py')}", 'a', encoding='utf-8') as file:
                            file.write(class_definition)
                    if method_definition not in open(f"{project}{ensure_path_sep(f'/api_test/{application_name}/template/core.py')}", encoding='utf-8').read():
                        with open(f"{project}{ensure_path_sep(f'/api_test/{application_name}/template/core.py')}", 'a', encoding='utf-8') as file:
                            file.write(method_definition)

                    # 生成body.py文件
                    if body is not None:
                        body_definition = f'\n{method.upper()}_{api_name} = {json.dumps(body, indent=4)}\n'
                        if not os.path.exists(f"{project}{ensure_path_sep(f'/api_test/{application_name}/template/body.py')}") or body_definition not in open(
                                f"{project}{ensure_path_sep(f'/api_test/{application_name}/template/body.py')}", encoding='utf-8').read():
                            with open(f"{project}{ensure_path_sep(f'/api_test/{application_name}/template/body.py')}", 'a', encoding='utf-8') as file:
                                file.write(body_definition)

                    # 如果URL中有查询参数，将其添加到body.py文件中
                    if query_params:
                        query_params_definition = f'\n{method.upper()}_{api_name}_query_params = {json.dumps(query_params, indent=4)}\n'
                        if not os.path.exists(f"{project}{ensure_path_sep(f'/api_test/{application_name}/template/body.py')}") or query_params_definition not in open(
                                f"{project}{ensure_path_sep(f'/api_test/{application_name}/template/body.py')}", encoding='utf-8').read():
                            with open(f"{project}{ensure_path_sep(f'/api_test/{application_name}/template/body.py')}", 'a', encoding='utf-8') as file:
                                file.write(query_params_definition)

                    # 生成headers.py文件
                    headers_definition = f'\n{api_name}_headers = {json.dumps(headers, indent=4)}\n'
                    if not os.path.exists(f"{project}{ensure_path_sep(f'/api_test/{application_name}/template/headers.py')}") or headers_definition not in open(
                            f"{project}{ensure_path_sep(f'/api_test/{application_name}/template/headers.py')}", encoding='utf-8').read():
                        with open(f"{project}{ensure_path_sep(f'/api_test/{application_name}/template/headers.py')}", 'a', encoding='utf-8') as file:
                            file.write(headers_definition)

                    # 生成url.py文件
                    parsed_url = urlparse(url)
                    domain = parsed_url.scheme + "://" + parsed_url.netloc  # 提取域名
                    path = parsed_url.path  # 提取路径
                    domain_definition = f'\nurl_prefix_test = "{domain}"\n'
                    path_definition = f'\n{method.upper()}_{api_name} = "{path}"\n'

                    # 检查并写入域名
                    if not os.path.exists(f"{project}{ensure_path_sep(f'/api_test/{application_name}/template/url.py')}") or domain_definition not in open(
                            f"{project}{ensure_path_sep(f'/api_test/{application_name}/template/url.py')}", encoding='utf-8').read():
                        with open(f"{project}{ensure_path_sep(f'/api_test/{application_name}/template/url.py')}", 'a', encoding='utf-8') as file:
                            file.write(domain_definition)

                    # 检查并写入路径
                    if not os.path.exists(f"{project}{ensure_path_sep(f'/api_test/{application_name}/template/url.py')}") or path_definition not in open(
                            f"{project}{ensure_path_sep(f'/api_test/{application_name}/template/url.py')}", encoding='utf-8').read():
                        with open(f"{project}{ensure_path_sep(f'/api_test/{application_name}/template/url.py')}", 'a', encoding='utf-8') as file:
                            file.write(path_definition)

                    # 生成test_case包
                    def generate_test_class_definition(category):
                        return f"""import pytest
from pytestifyx import TestCase
from pytestifyx.utils.database.assertion.core import deep_diff
from pytest_cases import parametrize_with_cases

from api_test.{application_name}.template.core import {convert_string(application_name)}
from api_test.{application_name}.test_data.{category.lower()} import {category}{convert_string(application_name)}


class Test{category.capitalize()}{convert_string(application_name)}(TestCase):
    \"\"\"
    数据集
    \"\"\"
    i = {convert_string(application_name)}()
    """

                    content_type = {headers['Content-Type']} if 'Content-Type' in headers else 'application/json'

                    def generate_test_method_definition(category, concurrent_number=1):
                        return f"""
    @pytest.mark.busi
    @parametrize_with_cases('param', cases={category.capitalize() + convert_string(application_name)}.{category}_{api_name})  # 业务逻辑测试
    def test_{category}_{api_name}(self, param, **conf):
        config = self.ensure_config()
        config.set_attr(concurrent_number={concurrent_number}, content_type="{content_type}", request_method="{method}", **conf)
        response = self.i.{api_name}(param, config)
        if response.status_code == 200:
            param['assertion_res'] = {{'message': 'success'}}
            assert deep_diff(response.json(), param['assertion_res']) is True
        else:
            assert deep_diff(response.json(), param['exception']) is True
        return response
                    """

                    if not os.path.exists(f"{project}{ensure_path_sep(f'/api_test/{application_name}/test_case/busi.py')}"):
                        with open(f"{project}{ensure_path_sep(f'/api_test/{application_name}/test_case/busi.py')}", 'a', encoding='utf-8') as file:
                            file.write(generate_test_class_definition('Busi'))
                    if generate_test_method_definition('busi') not in open(f"{project}{ensure_path_sep(f'/api_test/{application_name}/test_case/busi.py')}", encoding='utf-8').read():
                        with open(f"{project}{ensure_path_sep(f'/api_test/{application_name}/test_case/busi.py')}", 'a', encoding='utf-8') as file:
                            file.write(generate_test_method_definition('busi'))
                    busi_methods.append({
                        'name': api_name,
                    })

                    if not os.path.exists(f"{project}{ensure_path_sep(f'/api_test/{application_name}/test_case/conc.py')}"):
                        with open(f"{project}{ensure_path_sep(f'/api_test/{application_name}/test_case/conc.py')}", 'a', encoding='utf-8') as file:
                            file.write(generate_test_class_definition('Conc'))
                    if generate_test_method_definition('conc', concurrent_number=5) not in open(f"{project}{ensure_path_sep(f'/api_test/{application_name}/test_case/conc.py')}",
                                                                                                encoding='utf-8').read():
                        with open(f"{project}{ensure_path_sep(f'/api_test/{application_name}/test_case/conc.py')}", 'a', encoding='utf-8') as file:
                            file.write(generate_test_method_definition('conc', concurrent_number=5))

                    # 生成test_data包
                    def generate_data_class_definition(category):
                        return f"""from pytest_cases import parametrize


class {category.capitalize()}{convert_string(application_name)}:
    """

                    def generate_data_method_definition(category, flow=None):
                        return f"""
    @parametrize(data=(
            {{"正向测试案例": {{}}}},
    ))
    def {category}_{flow if flow else api_name}(self, data):
        template = {{}}
        template.update(list(data.values())[0])
        return template
"""

                    if not os.path.exists(f"{project}{ensure_path_sep(f'/api_test/{application_name}/test_data/busi.py')}"):
                        with open(f"{project}{ensure_path_sep(f'/api_test/{application_name}/test_data/busi.py')}", 'a', encoding='utf-8') as file:
                            file.write(generate_data_class_definition('Busi'))
                    if generate_data_method_definition('busi') not in open(f"{project}{ensure_path_sep(f'/api_test/{application_name}/test_data/busi.py')}", encoding='utf-8').read():
                        with open(f"{project}{ensure_path_sep(f'/api_test/{application_name}/test_data/busi.py')}", 'a', encoding='utf-8') as file:
                            file.write(generate_data_method_definition('busi'))

                    if not os.path.exists(f"{project}{ensure_path_sep(f'/api_test/{application_name}/test_data/conc.py')}"):
                        with open(f"{project}{ensure_path_sep(f'/api_test/{application_name}/test_data/conc.py')}", 'a', encoding='utf-8') as file:
                            file.write(generate_data_class_definition('Conc'))
                    if generate_data_method_definition('conc') not in open(f"{project}{ensure_path_sep(f'/api_test/{application_name}/test_data/conc.py')}", encoding='utf-8').read():
                        with open(f"{project}{ensure_path_sep(f'/api_test/{application_name}/test_data/conc.py')}", 'a', encoding='utf-8') as file:
                            file.write(generate_data_method_definition('conc'))

                    if not os.path.exists(f"{project}{ensure_path_sep(f'/api_test/{application_name}/test_data/flow.py')}"):
                        with open(f"{project}{ensure_path_sep(f'/api_test/{application_name}/test_data/flow.py')}", 'a', encoding='utf-8') as file:
                            file.write(generate_data_class_definition('Flow'))
                    if generate_data_method_definition('flow') not in open(f"{project}{ensure_path_sep(f'/api_test/{application_name}/test_data/flow.py')}", encoding='utf-8').read():
                        with open(f"{project}{ensure_path_sep(f'/api_test/{application_name}/test_data/flow.py')}", 'a', encoding='utf-8') as file:
                            file.write(generate_data_method_definition('flow', 'all'))

    flow_class_definition = f"""import pytest
from pytestifyx import TestCase
from pytest_cases import parametrize_with_cases

from api_test.{application_name}.test_case.busi import TestBusi{convert_string(application_name)}
from api_test.{application_name}.test_data.flow import Flow{convert_string(application_name)}

class TestFlow{convert_string(application_name)}(TestCase):
    \"\"\"
    数据集
    \"\"\"
    busi = TestBusi{convert_string(application_name)}()
    """

    flow_method_definition = f"""
    @pytest.mark.flow
    @parametrize_with_cases('param', cases=Flow{convert_string(application_name)}.flow_all)
    def test_flow_all(self, params):
    """
    for method in busi_methods:
        name = method['name']
        flow_method_definition += f"""
        {name}_response = self.busi.test_busi_{name}(params)
    """
    flow_method_definition += f"""
        return {name}_response
    """
    if not os.path.exists(f"{project}{ensure_path_sep(f'/api_test/{application_name}/test_case/flow.py')}"):
        with open(f"{project}{ensure_path_sep(f'/api_test/{application_name}/test_case/flow.py')}", 'a', encoding='utf-8') as file:
            file.write(flow_class_definition)
    if flow_method_definition not in open(f"{project}{ensure_path_sep(f'/api_test/{application_name}/test_case/flow.py')}", encoding='utf-8').read():
        with open(f"{project}{ensure_path_sep(f'/api_test/{application_name}/test_case/flow.py')}", 'a', encoding='utf-8') as file:
            file.write(flow_method_definition)


if __name__ == '__main__':
    trans_saz_to_test()
