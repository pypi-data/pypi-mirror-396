import json
from pathlib import Path
from typing import List, Dict, Any, Sequence


# -------------------------------------------------
# 读取映射 JSON（返回 list[dict]）
# -------------------------------------------------
def load_mapping(json_path: Path) -> List[Dict[str, str]]:
    """
    参数
    ----
    json_path : Path
        包含 {"table_name": "...", "table_name_jp": "..."} 记录的 JSON 文件

    返回
    ----
    List[Dict[str, str]]
        直接返回 JSON 中的数组对象，后面会用它做查找
    """
    if not json_path.is_file():
        raise FileNotFoundError(f"映射文件不存在: {json_path}")
    return json.loads(json_path.read_text(encoding="utf-8"))

def get_json_items(
    source_keys: List[str],
    json_file_path: str,
    *,
    src_field: str = "key",
    dst_fields: Sequence[str] = ("value",),
    default: Any = None,
    extra_fields: Sequence[str] = (),
    result_key_prefix: str = "",
) -> List[Dict[str, Any]]:
    """
    通用映射函数（支持一次提取多个目标字段）。

    参数
    ----
    source_keys : List[str]
        待映射的键列表（如表名、代码等）。
    mapping_array : List[Dict[str, Any]]
        从 JSON 读取的映射记录，每条记录必须至少包含 ``src_field`` 与
        所有在 ``dst_fields`` 中列出的字段。
    src_field : str, default "key"
        用来匹配 ``source_keys`` 的字段名。
    dst_fields : Sequence[str], default ("value",)
        需要一次性提取的 **一个或多个** 目标字段名。
    default : Any, default None
        当 ``source_keys`` 在映射中找不到时使用的默认值。
    extra_fields : Sequence[str], default ()
        需要把映射记录里额外字段原样复制到结果中的键名列表。
    result_key_prefix : str, default ""
        给返回的字段名前加统一前缀（例如 ``"tbl_"``），防止键冲突。

    返回
    ----
    List[Dict[str, Any]]
        每条记录形如：
        {
            "<prefix><src_field>"   : "...",      # 原始键
            "<prefix><dst1>"        : "...",
            "<prefix><dst2>"        : "...",
            ... extra_fields ...
        }
    """
    # -------------------------------------------------
    # 1️⃣ 把映射数组转成 dict，便于 O(1) 查找
    # -------------------------------------------------

    mapping_array = load_mapping(Path(json_file_path))

    lookup: Dict[Any, Dict[str, Any]] = {}
    for rec in mapping_array:
        key = rec.get(src_field)
        if key is not None:               # 跳过缺失 src_field 的脏数据
            lookup[key] = rec

    # -------------------------------------------------
    # 2️⃣ 构造结果列表
    # -------------------------------------------------
    result: List[Dict[str, Any]] = []
    for k in source_keys:
        rec = lookup.get(k)               # 可能为 None

        # 基础字段（原始键）
        item: Dict[str, Any] = {
            f"{result_key_prefix}{src_field}": k,
        }

        # 目标字段们
        for dst in dst_fields:
            value = rec.get(dst, default) if rec else default
            item[f"{result_key_prefix}{dst}"] = value

        # 额外字段（若有对应记录则复制，否则填 default）
        for extra in extra_fields:
            item[f"{result_key_prefix}{extra}"] = (
                rec.get(extra, default) if rec else default
            )
        result.append(item)

    return result