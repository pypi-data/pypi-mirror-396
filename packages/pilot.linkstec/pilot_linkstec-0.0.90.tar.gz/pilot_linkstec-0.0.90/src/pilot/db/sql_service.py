from typing import Dict, Any
from db.db_util import exec_insert, exec_select, exec_update, exec_delete


# insert文を呼出
def insert_sql_info(key:str, params: Dict[str, Any]):
    exec_insert(key, params)

# select文を呼出
def select_sql_info(key:str, params: Dict[str, Any]):
    result_rows = exec_select(key, params)

    if not result_rows:
        return []
    return [row_to_dict(r) for r in result_rows]

# update文を呼出
def update_sql_info(key:str, params: Dict[str, Any]):
    exec_update(key, params)

# delete文を呼出
def delete_sql_info(key:str, params: Dict[str, Any]):
    exec_delete(key, params)

def row_to_dict(row: Any) -> Dict[str, Any]:
    """
    把数据库返回的“行对象”统一转换为普通 dict。
    支持：
      - sqlite3.Row               -> dict(row)
      - SQLAlchemy RowProxy       -> dict(row._mapping)   (SQLA >=1.4)
      - SQLAlchemy legacy RowProxy-> row._asdict()
      - MyBatis‑Python ResultSet  -> dict(row)
    如有其它库，只需在这里补充对应的转换方式。
    """
    # sqlite3.Row 直接可迭代 (key, value) 对
    if isinstance(row, dict):
        return row                     # 已经是 dict，直接返回

    try:
        # SQLAlchemy 1.4+ Row (has ._mapping)
        return dict(row._mapping)      # type: ignore[attr-defined]
    except AttributeError:
        pass

    try:
        # SQLAlchemy 1.3‑ RowProxy (has ._asdict())
        return row._asdict()           # type: ignore[attr-defined]
    except AttributeError:
        pass

    try:
        # 任何实现了 __iter__ 且返回 (key, value) 的对象（如 sqlite3.Row）
        return dict(row)
    except Exception as exc:
        raise TypeError(f"Cannot convert row of type {type(row)} to dict") from exc
