import os
import yaml
import configparser

from pytestifyx.utils.public.get_project_path import get_project_path


def parse_ini_config(file_path):
    config = configparser.ConfigParser()
    base_path = get_project_path()
    full_path = os.path.join(str(base_path), file_path)
    config.read(full_path, encoding='utf-8')
    return config


# 读取 YAML 配置文件
def parse_yaml_config(file_name='config.yaml'):
    base_path = get_project_path()
    file_path = os.path.join(base_path, file_name)
    with open(file_path, 'r', encoding='utf-8') as file:
        return yaml.safe_load(file)
