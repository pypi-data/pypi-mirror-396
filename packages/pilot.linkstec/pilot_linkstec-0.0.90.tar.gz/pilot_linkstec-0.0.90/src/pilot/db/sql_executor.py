# sql_executor.py
import sqlite3
from typing import Any, Mapping, Tuple, List, Union

from db.db_connect import get_connection
from db.sql_loader import load_sql


# -----------------------------------------------------------------
# 1️⃣ DDL（CREATE / ALTER / DROP …）统一执行函数
# -----------------------------------------------------------------
def exec_ddl(relative_path: str, params: Union[Mapping[str, Any], Tuple[Any, ...]] = None) -> None:
    """
    执行 DDL 脚本（如建表、建索引等）。
    - `relative_path` 为相对于 sql/ 目录的路径，例如 'ddl/create_user_table.sql'。
    - 如果脚本里有占位符，可通过 `params` 传入 dict（命名）或 tuple（位置）。
    """
    sql, args = load_sql(relative_path, params)

    # 只需要一次 execute，DDL 不返回结果集
    with get_connection() as conn:
        conn.execute(sql, args)


# -----------------------------------------------------------------
# 2️⃣ DML（SELECT / INSERT / UPDATE / DELETE）统一执行函数
# -----------------------------------------------------------------
def exec_dml(relative_path: str,
             params: Union[Mapping[str, Any], Tuple[Any, ...]] = None
             ) -> Union[List[Tuple[Any, ...]], int]:
    """
    执行 DML 脚本。

    - 对 SELECT：返回 `List[Tuple]`（查询结果）。
    - 对 INSERT / UPDATE / DELETE：返回受影响的行数 (`cursor.rowcount`)。
    """
    sql, args = load_sql(relative_path, params)

    with get_connection() as conn:
        cur: sqlite3.Cursor = conn.execute(sql, args)

        # 判断是否是查询语句（首个非空字符为 SELECT）
        if sql.lstrip().upper().startswith("SELECT") or sql.lstrip().upper().startswith("WITH") :
            result = cur.fetchall()          # 读取全部结果后返回 list
        else:
            # 对非查询语句，事务已在 get_connection() 的 __exit__ 中提交
            result = cur.rowcount           # 受影响的行数

        cur.close()
        return result

def exec_multiple_dml(relative_path: str,
             params: Union[Mapping[str, Any], Tuple[Any, ...]] = None
             ):
    try:
        sql, args = load_sql(relative_path, params)
        with get_connection() as conn:
            cur = conn.cursor()
            cur.executescript(sql)
        # cur.close()
    except sqlite3.Error as e:
        raise  # 需要時可重新拋出讓上層捕獲