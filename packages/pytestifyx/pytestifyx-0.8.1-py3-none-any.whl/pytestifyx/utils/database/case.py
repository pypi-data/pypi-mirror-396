import importlib
import os
import sqlite3
import inspect
import json
import ast
import textwrap
from pytestifyx.utils.public.get_project_path import get_project_path


class DatabaseWriter:
    def __init__(self):
        db_name = f"{get_project_path()}/param.sqlite"
        self.conn = sqlite3.connect(db_name)
        self.c = self.conn.cursor()
        self.c.execute(
            """
                    CREATE TABLE IF NOT EXISTS param_info
                    (
                        class_name text,
                        method_name text,
                        case_name text,
                        case_params text,
                        version text DEFAULT 'V1',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        PRIMARY KEY (class_name, method_name, case_name)
                    )
                """
        )

    def scan_directory_and_write_to_db(self, directory):
        # 遍历目录下的所有文件
        for filename in os.listdir(directory):
            # 检查文件是否是Python文件
            if filename.endswith(".py"):
                # 获取文件的完整路径
                file_path = os.path.join(directory, filename)
                # 加载模块
                spec = importlib.util.spec_from_file_location("module.name", file_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                # 获取模块中的所有类
                for name, obj in inspect.getmembers(module):
                    # 检查类名是否以"Flow"或"Busi"开头
                    if inspect.isclass(obj) and (name.startswith("Flow") or name.startswith("Busi")):
                        # 实例化类并调用write_to_db方法
                        self.write_to_db(obj)

    def write_to_db(self, class_obj):
        class_name = class_obj.__name__
        obj = class_obj()
        methods = inspect.getmembers(obj, predicate=inspect.ismethod)
        for method_name, method in methods:
            if method_name.startswith("__"):
                continue
            # 获取方法的源代码
            source_code = inspect.getsource(method)
            # 移除源代码的首行的缩进
            source_code = textwrap.dedent(source_code)
            # 解析源代码，获取装饰器中的数据
            module = ast.parse(source_code)
            function_def = module.body[0]
            decorator = function_def.decorator_list[0]
            # 获取装饰器的keywords属性
            keywords = decorator.keywords
            # 检查keywords[0].value是否是字面量结构
            if self.is_literal(keywords[0].value):
                data = ast.literal_eval(keywords[0].value)
                # 拆解data成一条条记录，写入数据库
                for record in data:
                    case_name = list(record.keys())[0]
                    case_params = json.dumps(list(record.values())[0], ensure_ascii=False)
                    self.c.execute("SELECT version, case_params FROM param_info WHERE class_name = ? AND method_name = ? AND case_name = ?", (class_name, method_name, case_name))
                    version_row = self.c.fetchone()
                    if version_row is None:
                        version = "V1"
                        self.c.execute("INSERT INTO param_info (class_name, method_name, case_name, case_params, version) VALUES (?, ?, ?, ?, ?)", (class_name, method_name, case_name, case_params, version))
                    else:
                        old_case_params, old_version = version_row[1], version_row[0]
                        if old_case_params != case_params:
                            version_number = int(old_version[1:]) + 1
                            version = "V" + str(version_number)
                            self.c.execute("UPDATE param_info SET case_params = ?, version = ?, updated_at = CURRENT_TIMESTAMP WHERE class_name = ? AND method_name = ? AND case_name = ?", (case_params, version, class_name, method_name, case_name))
            else:
                print("Not a literal structure, skipping...")
        self.conn.commit()

    def get_case_info(self, class_name, method_name):
        self.c.execute("SELECT * FROM param_info WHERE class_name = ? AND method_name = ?", (class_name, method_name))
        rows = self.c.fetchall()
        return self.restore_records(rows)

    @staticmethod
    def is_literal(node):
        return isinstance(node, (ast.Str, ast.Bytes, ast.Num, ast.Tuple, ast.List, ast.Dict, ast.Set, ast.NameConstant))

    @staticmethod
    def restore_records(records):
        restored_records = []
        for record in records:
            case_name = record[2]
            case_params = json.loads(record[3])
            restored_records.append({case_name: case_params})
        return tuple(restored_records)

    def close(self):
        self.conn.close()


db_writer = DatabaseWriter()

if __name__ == "__main__":
    pass
    # from api_test.cooperating.catalog.catalog_info.test_data.busi import BusiCatalogInfo

    # 使用示例
    # db_writer = DatabaseWriter()
    # db_writer.scan_directory_and_write_to_db('/Users/jaylu/PycharmProjects/onekautotest/api_test/cooperating/catalog/catalog_info/test_data')
    # print(db_writer.get_case_info("BusiCatalogInfo", "busi_tree_global_org"))
    # db_writer.close()
