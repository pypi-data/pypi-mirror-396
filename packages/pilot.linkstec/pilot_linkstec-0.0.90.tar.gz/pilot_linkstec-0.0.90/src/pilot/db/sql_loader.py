# --------------------------------------------------------------
# sql_loader.py – 通用的 SQL 加载 / 参数渲染工具
# --------------------------------------------------------------
import pathlib
import re
from typing import Any, Mapping, Tuple, Union, Iterable, List
import importlib.resources as pkg_resources   # Python 3.7+

# ------------------------------------------------------------------
# 默认根目录：与本文件同级的 “sql” 目录（保持向后兼容）
# ------------------------------------------------------------------
DEFAULT_SQL_ROOT = pathlib.Path(__file__).parent


def _read_from_filesystem(root: pathlib.Path, relative_path: str) -> str:
    """
    从磁盘文件系统读取 SQL。
    参数
    ----
    root : pathlib.Path
        sql 根目录（例如 Path('sql')）
    relative_path : str
        相对于根目录的路径，如 'ddl/create_user_table.sql'
    """
    file_path = root / relative_path
    if not file_path.is_file():
        raise FileNotFoundError(f"SQL file not found: {file_path}")
    return file_path.read_text(encoding="utf-8")


def _read_from_package(package: str, relative_path: str) -> str:
    """
    从 Python 包（资源）读取 SQL。
    参数
    ----
    package : str
        包名，例如 'dml'、'my_project.dml'
    relative_path : str
        包内部的相对路径，如 'ddl/create_user_table.sql'
    """
    # pkg_resources.open_text 会自动处理编码、BOM 等细节
    try:
        with pkg_resources.open_text(package, relative_path,
                                     encoding="utf-8-sig") as f:
            return f.read()
    except FileNotFoundError as exc:
        raise FileNotFoundError(
            f"SQL resource not found: package={package!r}, file={relative_path}"
        ) from exc


def _read_sql_file(relative_path: str,
                   base_path: Union[pathlib.Path, str] = DEFAULT_SQL_ROOT
                   ) -> str:
    """
    统一入口：根据 ``base_path`` 类型决定读取方式。
    * Path   → 从磁盘文件系统读取
    * str    → 当作包名，使用 importlib.resources 读取资源文件
    """
    if isinstance(base_path, pathlib.Path):
        return _read_from_filesystem(base_path, relative_path)
    elif isinstance(base_path, str):
        return _read_from_package(base_path, relative_path)
    else:
        raise TypeError(
            "base_path 必须是 pathlib.Path（文件系统）或 str（包名），"
            f"实际得到 {type(base_path)!r}"
        )


# ----------------------------------------------------------------------
# 1️⃣ 正则：捕获 MyBatis‐style #{name} / ${name}
# ----------------------------------------------------------------------
_RE_PLACEHOLDER = re.compile(r'''
    (?:\#|\$)          # 开头是 # 或 $
    \{                 # 左花括号
    \s*                # 可选空白
    (?P<name>[^}]+?)   # 参数名（非贪婪）
    \s*                # 可选空白
    \}                 # 右花括号
''', re.VERBOSE)


def _replace_mybatis_placeholders(sql: str,
                                 use_named: bool) -> Tuple[str, List[str]]:
    """
    把 ``#{name}`` / ``${name}`` 替换为 SQLite 占位符。

    Parameters
    ----------
    sql : str
        原始 SQL（可能包含 MyBatis 占位符）。
    use_named : bool
        * ``True``  → 使用命名占位符 ``:name``；
        * ``False`` → 使用位置占位符 ``?``.

    Returns
    -------
    Tuple[str, List[str]]
        * 第 1 项：替换后的 SQL。
        * 第 2 项：出现的参数名顺序列表（仅在 ``use_named=False`` 时有意义）。
    """
    if use_named:        # 直接把 #{xxx} 替换为 :xxx
        new_sql = _RE_PLACEHOLDER.sub(lambda m: f":{m.group('name').strip()}", sql)
        return new_sql, []                     # 参数顺序不需要

    else:
        # 把所有占位符统一为 “?”
        names: List[str] = []

        def repl(m: re.Match) -> str:
            names.append(m.group('name').strip())
            return "?"

        new_sql = _RE_PLACEHOLDER.sub(repl, sql)
        return new_sql, names


# ----------------------------------------------------------------------
# 2️⃣ 主函数
# ----------------------------------------------------------------------
def render_sql(
    template: str,
    params: Union[Mapping[str, Any], Iterable[Any], None] = None,
) -> Tuple[
    str,
    Union[Mapping[str, Any], Tuple[Any, ...]]
]:

    # -------------------------------------------------
    # ① 参数为 None → 只做占位符统一（全部转成 ?）
    # -------------------------------------------------
    if params is None:
        new_sql, _ = _replace_mybatis_placeholders(template, use_named=False)
        return new_sql, ()

    # -------------------------------------------------
    # ② 参数为 Mapping → 使用命名占位符
    # -------------------------------------------------
    if isinstance(params, Mapping):
        new_sql, _ = _replace_mybatis_placeholders(template, use_named=True)
        return new_sql, params

    # -------------------------------------------------
    # ③ 参数为 Iterable（但不是 Mapping） → 使用位置占位符
    # -------------------------------------------------
    if isinstance(params, Iterable):
        # 先把模板里的 MyBatis 占位符全部换成 ?
        new_sql, name_order = _replace_mybatis_placeholders(template,
                                                          use_named=False)

        # 1) 如果用户本来就传的是 list/tuple 等，直接转 tuple
        # 2) 如果用户误把 dict 当成 Iterable（dict 本身是 Iterable），
        #    那么我们把它当作 Mapping 处理，以免产生错误的顺序。
        if isinstance(params, Mapping):
            # 把 dict 按 name_order 取值，保持顺序一致
            ordered_vals = tuple(params[name] for name in name_order)
        else:
            ordered_vals = tuple(params)

        # 当模板里没有 MyBatis 占位符时 name_order 为 []，此时
        # ordered_vals 仍然是用户提供的 tuple/list → 正常使用。
        return new_sql, ordered_vals

    # -------------------------------------------------
    # ④ 其它类型（不应该出现） → 抛出友好错误
    # -------------------------------------------------
    raise TypeError(
        "params 必须是 Mapping、Iterable 或 None，"
        f"但收到的是 {type(params)!r}"
    )


# ------------------------------------------------------------------
# 一站式加载 + 渲染
# ------------------------------------------------------------------
def load_sql(relative_path: str,
             params: Union[Mapping[str, Any],
                          Iterable[Any],
                          None] = None,
             base_path: Union[pathlib.Path, str] = DEFAULT_SQL_ROOT
             ) -> Tuple[str,
                        Union[Mapping[str, Any], Tuple[Any, ...]]]:
    """
    读取 SQL →（可选）渲染参数 → 返回 ``(sql, parameters)``。

    参数
    ----
    relative_path : str
        相对于根目录/包的路径，如 ``'ddl/create_user_table.sql'``。
    params        : Mapping / Iterable / None
        传给 ``sqlite3`` 的参数对象，渲染规则同 ``render_sql``。
    base_path     : pathlib.Path | str
        *Path* → 读取磁盘目录（默认 ``DEFAULT_SQL_ROOT``）<br>
        *str*  → 当作 **包名**，使用 ``importlib.resources`` 从包中读取。
    """
    raw_sql = _read_sql_file(relative_path, base_path=base_path)
    # -------------------------------------------------
    # ① 若傳入的 params 含有 `values_str`（pattern‑2 用法）
    # -------------------------------------------------
    if isinstance(params, Mapping) and "values_str" in params:
        # 把傳入的二元組列表渲染成 VALUES‑list
        values_sql = _render_values_str(params["values_str"])
        # 替換模板中預留的佔位符（我們約定使用 /*{values_str}*/）
        raw_sql = raw_sql.replace("/*{values_str}*/", values_sql)

        # 把 `values_str` 從 params 中剔除，避免後續被當成普通參數傳給 sqlite3
        # （如果你想保留其他命名參數，仍然可以放在同一個 dict 中）
        params = {k: v for k, v in params.items() if k != "values_str"}

    return render_sql(raw_sql, params)

# ----------------------------------------------------------------------
# ② 把 values_str 渲染成 VALUES‑list ------------------------------------
# ----------------------------------------------------------------------
def _render_values_str(
    values: Iterable[Tuple[Any, Any]]
) -> str:
    """
    把 [(cls1, sub1), (cls2, sub2), …] 轉成

        ('cls1','sub1'),('cls2','sub2'),...

    只在 pattern‑2 中使用。會自動把單引號轉義為兩個單引號。
    """
    def esc(v: Any) -> str:
        # 只處理字串型別，其他類型直接轉成 str
        if isinstance(v, str):
            return v.replace("'", "''")
        return str(v)

    rows = [f"('{esc(c)}', '{esc(s)}')" for c, s in values]
    return ",\n".join(rows)