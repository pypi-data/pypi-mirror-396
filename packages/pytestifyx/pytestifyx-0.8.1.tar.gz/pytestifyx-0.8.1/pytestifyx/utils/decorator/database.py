from sqlalchemy.dialects import mysql

from pytestifyx.utils.public.constant import Query_Success, Query_None
from pytestifyx.utils.logs.core import log


def assert_log_table(table_name):
    def assert_log(func):
        def wrapper(*args, **kwargs):
            log.info(f'{table_name}表数据校验开始')
            _func = func(*args, **kwargs)
            log.info(f'{table_name}表数据校验结束')
            return _func

        return wrapper

    return assert_log


# 类方法装饰器
def query_table_as_dict(table_name, db_name=None):
    def query(func):
        def wrapper(self, *args, **kwargs):
            _func = func(self, *args, **kwargs)
            if self.config.is_sql_log:
                log.info(_func.statement.compile(dialect=mysql.dialect(), compile_kwargs={"literal_binds": True}))
            try:
                response = _func.first().as_dict(self.config.is_sql_log)
                log.info(f'{table_name}--{Query_Success}')
                return response
            except AttributeError:
                log.info(f'{table_name}--{Query_None}')
                return None

        return wrapper

    return query
