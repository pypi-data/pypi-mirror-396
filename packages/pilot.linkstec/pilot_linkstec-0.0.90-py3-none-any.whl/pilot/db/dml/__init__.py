import importlib.resources as pkg_resources
from pathlib import Path
from typing import Union

def load_dml_sql(name: Union[str, Path]) -> str:
    """
    读取 dml/ 目录下的 .sql 文件并返回其内容。
    参数 ``name`` 可以是文件名（不含后缀）或完整路径对象。
    示例:
        sql = dml.load_sql("create_user_table")
    """
    # 兼容传入 "create_user_table.sql" 或不带后缀的名字
    filename = str(name)
    if not filename.lower().endswith('.sql'):
        filename += '.sql'
    # pkg_resources 会在包内部查找资源文件
    with pkg_resources.open_text(__package__, filename) as f:
        return f.read()