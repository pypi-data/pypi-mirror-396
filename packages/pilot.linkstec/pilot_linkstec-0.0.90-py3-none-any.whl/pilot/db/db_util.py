# -*- coding: utf-8 -*-
"""
db_util.py
通用的 INSERT 工具，根據「INSERT_MAP」把傳入的 dict 轉成
   (sql_file_path, dml_params) 並呼叫 exec_dml()
"""
import pathlib
import re
import sqlite3
from typing import Callable, Dict, Any, List

from db.sql_executor import exec_dml

# -------------------------------------------------
# 2️⃣ INSERT_MAP
#   key   : 給外部呼叫的函式名稱（或任何自訂代號）
#   value : {
#       "sql_path"  : r'ddl\INSERT_XXXXX.sql',
#       # 必要欄位的清單（若有額外固定值，可直接寫在 dict 內）
#       "fields"    : ["package_name", "file_name", ...],
#       # 需要額外固定值時（例如 comment_file_path），寫在這裡
#       "defaults"  : {"comment_file_path": "XXXX"},
#   }
# -------------------------------------------------
INSERT_MAP: Dict[str, Dict[str, Any]] = {
    # ------------------- method 系列 -------------------
    "method_file_info": {
        "sql_path": r"dml\INSERT_METHOD_FILE_INFO.sql",
        "fields": [
            "package_name", "class_name","file_name","original_file_path",
            "no_comment_file_path"
        ],
    },
    "method_class_info": {
        "sql_path": r"dml\INSERT_METHOD_CLASS_INFO.sql",
        "fields": [
            "package_name", "file_name", "class_name", "class_type",
            "full_class_name", "import_object_name"
        ],
    },
    "method_info": {
        "sql_path": r"dml\INSERT_METHOD_INFO.sql",
        "fields": [
            "package_name", "file_name", "class_name", "method_name",
            "full_method_signature", "return_type", "remaining_class_code"
        ],
    },
    "method_parameter_info": {
        "sql_path": r"dml\INSERT_METHOD_PARAMETER_INFO.sql",
        "fields": [
            "package_name", "file_name", "class_name", "method_name",
            "parameter_type", "parameter_name"
        ],
    },
    "sub_method_info": {
        "sql_path": r"dml\INSERT_METHOD_SUB_METHOD_INFO.sql",
        "fields": [
            "package_name", "file_name", "class_name", "method_name",
            "sub_method_name", "called_method_full_signature", "called_method_class"
        ],
    },
    "method_parsing_info": {
        "sql_path": r"dml\INSERT_METHOD_PARSING_INFO.sql",
        "fields": [
            "package_name", "class_name", "method_name", "method_description",
            "input_parameter_info", "return_value_info", "code_with_comment_info",
            "parsing_method_info_file_path"
        ],
    },

    # ------------------- sql 系列 -------------------
    "sql_file_info": {
        "sql_path": r"dml\INSERT_SQL_FILE_INFO.sql",
        "fields": [
            "mapper_file_name","original_file_path","no_comment_file_path"
        ],
    },
    "sql_content_info": {
        "sql_path": r"dml\INSERT_SQL_CONTENT_INFO.sql",
        "fields": ["sql_mapper_name","sql_id","sql_content"],
    },
    "sql_table_info": {
        "sql_path": r"dml\INSERT_SQL_TABLE_INFO.sql",
        "fields": ["sql_mapper_name","sql_id","sql_style","mapper_file_name","table_name","table_alias"],
    },
    "sql_condition_info": {
        "sql_path": r"dml\INSERT_SQL_CONDITION_INFO.sql",
        "fields": ["sql_mapper_name","sql_id","sql_style","mapper_file_name","condition_content"],
    },
    "sql_parameter_info": {
        "sql_path": r"dml\INSERT_SQL_PARAMETER_INFO.sql",
        "fields": ["sql_mapper_name","sql_id","sql_style","mapper_file_name",
                   "parameter_name","parameter_column_name","parameter_table_name","parameter_table_alias"],
    },
    "sql_column_info": {
        "sql_path": r"dml\INSERT_SQL_COLUMN_INFO.sql",
        "fields": ["sql_mapper_name","sql_id","sql_style","mapper_file_name","table_name",
                   "table_alias","sql_type","column_name","column_alias"],
    },
    "sql_parsing_info": {
        "sql_path": r"dml\INSERT_SQL_PARSING_INFO.sql",
        "fields": ["sql_mapper_name","sql_id","in_parameter_info","output_info","sql_description",
                   "sql_content","parsing_file_path"],
    },
    "table_info": {
            "sql_path": r"dml\INSERT_TABLE_INFO.sql",
            "fields": ["table_id","table_name"],
    },
    "table_column_info": {
            "sql_path": r"dml\INSERT_TABLE_COLUMN_INFO.sql",
            "fields": ["table_id","column_id","column_name"],
    },
}

SELECT_MAP: Dict[str, Dict[str, Any]] = {
    # ------------------- method 系列 -------------------
    "method_file_info": {
        "sql_path": r"dml\SELECT_METHOD_FILE_INFO.sql",
        "fields": [
            "file_name"
        ],
    },
    "method_class_info": {
        "sql_path": r"dml\SELECT_METHOD_CLASS_INFO.sql",
        "fields": [
            "package_name",
            "class_name",
        ],
    },
    "method_info": {
        "sql_path": r"dml\SELECT_METHOD_INFO_BY_KEY.sql",
        "fields": [
            "package_name",
            "class_name",
            "method_name",
        ],
    },
    "method_parameter_info": {
        "sql_path": r"dml\SELECT_METHOD_PARAMETER_INFO.sql",
        "fields": [
            "package_name",
            "class_name",
            "method_name",
        ],
    },
    "method_sub_method_info": {
        "sql_path": r"dml\SELECT_METHOD_SUB_METHOD_INFO.sql",
        "fields": [
            "package_name",
            "class_name",
            "method_name",
        ],
    },
    # ------------------- sql 系列 -------------------
    "sql_file_info": {
        "sql_path": r"dml\SELECT_SQL_FILE_INFO.sql",
        "fields": [
            "sql_id"
        ],
    },
    "sql_table_info": {
        "sql_path": r"dml\SELECT_SQL_TABLE_INFO.sql",
        "fields": [
            "sql_mapper_name",
            "sql_id"
        ],
    },
    "sql_condition_info": {
        "sql_path": r"dml\SELECT_SQL_CONDITION_INFO.sql",
        "fields": [
            "sql_mapper_name",
            "sql_id"
        ],
    },
    "sql_content_info_list": {
        "sql_path": r"dml\SELECT_SQL_CONTENT_INFO_LIST.sql",
        "fields": [
            None
        ],
    },
    "sql_parameter_info": {
        "sql_path": r"dml\SELECT_SQL_PARAMETER_INFO.sql",
        "fields": [
            "sql_mapper_name",
            "sql_id"
        ],
    },
    "sql_column_info": {
        "sql_path": r"dml\SELECT_SQL_COLUMN_INFO.sql",
        "fields": [
            "sql_mapper_name",
            "sql_id"
        ],
    },
    "sql_content_info": {
        "sql_path": r"dml\SELECT_SQL_CONTENT_INFO.sql",
        "fields": [
            "sql_mapper_name",
            "sql_id"
        ],
    },
    "sql_get_parsing_sql_info_list": {
        "sql_path": r"dml\SELECT_SQL_PARSING_INFO.sql",
        "fields": [
            "package_name",
            "class_name",
            "method_name",
        ],
    },
    # ------------------- method 系列 -------------------
    "sql_no_sub_method_info": {
        "sql_path": r"dml\SELECT_METHOD_NO_SUB_METHOD_INFO.sql",
        "fields": [
            None
        ],
    },
    "sql_get_sub_method_info_all_list": {
        "sql_path": r"dml\SELECT_METHOD_SUB_METHOD_INFO_ALL_LIST.sql",
        "fields": [
            "values_str"
        ],
    },
    "sql_get_dao_method_info": {
        "sql_path": r"dml\SELECT_METHOD_INFO_BY_KEY.sql",
        "fields": [
            "package_name",
            "class_name",
            "method_name",
        ],
    },
    "sql_get_sub_method_info_list": {
        "sql_path": r"dml\SELECT_METHOD_SUB_METHOD_INFO.sql",
        "fields": [
            "package_name",
            "class_name",
            "method_name",
        ],
    },
    "sql_get_parsing_java_info_list": {
        "sql_path": r"dml\SELECT_METHOD_PARSING_INFO.sql",
        "fields": [
            "package_name",
            "class_name",
            "method_name",
        ],
    },
    # ------------------------SQL PROMPT INFO -------------
    "get_table_info_list": {
        "sql_path": r"dml\SELECT_TABLE_INFO.sql",
        "fields": [
            "sql_mapper_name",
            "sql_id",
        ],
    },
    "get_table_column_info_list": {
        "sql_path": r"dml\SELECT_TABLE_COLUMN_INFO.sql",
        "fields": [
            "sql_mapper_name",
            "sql_id",
        ],
    },
    "get_count_sub_method_info":{
        "sql_path":r"dml\SELECT_COUNT_METHOD_SUB_METHOD_INFO.sql",
        "fields": [
            "sub_method_name",
            "called_method_class",
        ]
    }
}

UPDATE_MAP: Dict[str, Dict[str, Any]] = {
    "update_sql_table_content_info": {
        "sql_path": r"dml\UPDATE_SQL_CONTENT_INFO.sql",
        "fields": [
            "sql_style",
            "sql_mapper_name",
            "sql_id",
        ],
    },
    "update_method_info": {
        "sql_path": r"dml\UPDATE_METHOD_INFO.sql",
        "fields": [
            "package_name",
            "class_name",
            "method_name",
            "return_type"
        ],
    },

}

DELETE_MAP: Dict[str, Dict[str, Any]] = {
    "delete_method_file_info": {
        "sql_path": r"dml\DELETE_METHOD_FILE_INFO.sql",
        "fields": [
            "package_name",
            "class_name"
        ],
    },
    "delete_method_class_info": {
        "sql_path": r"dml\DELETE_METHOD_CLASS_INFO.sql",
        "fields": [
            "package_name",
            "class_name"
        ],
    },
    "delete_method_info": {
        "sql_path": r"dml\DELETE_METHOD_INFO.sql",
        "fields": [
            "package_name",
            "class_name",
            "method_name"
        ],
    },
    "delete_method_parameter_info":{
        "sql_path": r"dml\DELETE_METHOD_PARAMETER_INFO.sql",
        "fields": [
            "package_name",
            "class_name",
            "method_name"
        ],
    },
    "delete_method_sub_method_info":{
        "sql_path": r"dml\DELETE_METHOD_SUB_METHOD_INFO.sql",
        "fields": [
            "package_name",
            "class_name",
            "method_name"
        ],
    },
    "delete_method_parsing_info":{
        "sql_path": r"dml\DELETE_METHOD_PARSING_INFO.sql",
        "fields": [
            "package_name",
            "class_name",
            "method_name"
        ],
    },
    "delete_sql_content_info":{
        "sql_path": r'dml\DELETE_SQL_CONTENT_INFO.sql',
        "fields": [
            "sql_mapper_name",
            "sql_id"
        ]
    },
    "delete_sql_file_info":{
        "sql_path": r'dml\DELETE_SQL_FILE_INFO.sql',
        "fields": [
            "mapper_file_name"
        ]
    },
    "delete_sql_table_info":{
        "sql_path": r'dml\DELETE_SQL_TABLE_INFO.sql',
        "fields": [
            "sql_mapper_name",
            "sql_id"
        ]
    },
    "delete_sql_condition_info": {
        "sql_path": r'dml\DELETE_SQL_CONDITION_INFO.sql',
        "fields": [
            "sql_mapper_name",
            "sql_id"
        ]
    },
    "delete_sql_column_info_info": {
        "sql_path": r'dml\DELETE_SQL_COLUMN_INFO.sql',
        "fields": [
            "sql_mapper_name",
            "sql_id"
        ]
    },
    "delete_sql_parameter_info": {
        "sql_path": r'dml\DELETE_SQL_PARAMETER_INFO.sql',
        "fields": [
            "sql_mapper_name",
            "sql_id"
        ]
    },
    "delete_sql_parsing_info": {
        "sql_path": r'dml\DELETE_SQL_PARSING_INFO.sql',
        "fields": [
            "sql_mapper_name",
            "sql_id"
        ]
    }
}

# -------------------------------------------------
# 1 通用執行函式
# -------------------------------------------------
def exec_insert(key: str, raw_params: Dict[str, Any]) -> None:
    """
    依照 INSERT_MAP[key] 把 raw_params 轉成正確的 dml_params，
    再呼叫 exec_dml()。

    Parameters
    ----------
    key : str
        INSERT_MAP 中的鍵，例如 "file_info"、"class_info" …
    raw_params : dict
        呼叫端傳入的參數（可能多於或少於 fields）。
    """
    if key not in INSERT_MAP:
        raise KeyError(f"Insert key '{key}' is not defined in INSERT_MAP")

    cfg = INSERT_MAP[key]
    sql_path: str = cfg["sql_path"]
    fields: list[str] = cfg.get("fields", [])
    defaults: dict = cfg.get("defaults", {})

    # 只挑出需要的欄位，缺少的會以 None 填充
    dml_params: dict = {f: raw_params.get(f) for f in fields}
    # 合併固定值（例如 comment_file_path = "XXXX"）
    dml_params.update(defaults)

    exec_dml(sql_path, dml_params)

# -------------------------------------------------
# 2 通用執行函式
# -------------------------------------------------
def exec_select(key:str, sel_params: Dict[str, Any]):
    """
        依照 SELECT_MAP[key] 把 sel_params 轉成正確的 dml_params，
        再呼叫 exec_dml()。

        Parameters
        ----------
        key : str
            SELECT_MAP 中的鍵，例如 "file_info"、"class_info" …
        sel_params : dict
            呼叫端傳入的參數（可能多於或少於 fields）。
        """
    if key not in SELECT_MAP:
        raise KeyError(f"Select key '{key}' is not defined in SELECT_MAP")

    cfg = SELECT_MAP[key]
    sql_path: str = cfg["sql_path"]
    fields: list[str] = cfg.get("fields", [])

    # 只挑出需要的欄位，缺少的會以 None 填充
    if sel_params:
        dml_params: dict = {f: sel_params.get(f) for f in fields}
    else:
        dml_params = {}

    result = exec_dml(sql_path, dml_params)

    return result

# -------------------------------------------------
# 3 通用執行函式
# -------------------------------------------------
def exec_update(key: str, raw_params: Dict[str, Any]) -> None:
    """
    依照 UPDATE_MAP[key] 把 raw_params 轉成正確的 dml_params，
    再呼叫 exec_dml()。

    Parameters
    ----------
    key : str
        UPDATE_MAP 中的鍵，例如 "file_info"、"class_info" …
    raw_params : dict
        呼叫端傳入的參數（可能多於或少於 fields）。
    """
    if key not in UPDATE_MAP:
        raise KeyError(f"Update key '{key}' is not defined in UPDATE_MAP")

    cfg = UPDATE_MAP[key]
    sql_path: str = cfg["sql_path"]
    fields: list[str] = cfg.get("fields", [])
    defaults: dict = cfg.get("defaults", {})

    # 只挑出需要的欄位，缺少的會以 None 填充
    dml_params: dict = {f: raw_params.get(f) for f in fields}
    # 合併固定值（例如 comment_file_path = "XXXX"）
    dml_params.update(defaults)

    exec_dml(sql_path, dml_params)

# -------------------------------------------------
# 4 通用執行函式
# -------------------------------------------------
def exec_delete(key: str, raw_params: Dict[str, Any]) -> None:
    """
    依照 DELETE_MAP[key] 把 raw_params 轉成正確的 dml_params，
    再呼叫 exec_dml()。

    Parameters
    ----------
    key : str
        DELETE_MAP 中的鍵，例如 "file_info"、"class_info" …
    raw_params : dict
        呼叫端傳入的參數（可能多於或少於 fields）。
    """
    if key not in DELETE_MAP:
        raise KeyError(f"Delete key '{key}' is not defined in UPDATE_MAP")

    cfg = DELETE_MAP[key]
    sql_path: str = cfg["sql_path"]
    fields: list[str] = cfg.get("fields", [])
    defaults: dict = cfg.get("defaults", {})

    # 只挑出需要的欄位，缺少的會以 None 填充
    dml_params: dict = {f: raw_params.get(f) for f in fields}

    exec_dml(sql_path, dml_params)

