import sqlite3
from pathlib import Path
from contextlib import contextmanager
from typing import Generator

# -------------------- 配置 --------------------
DB_FILE = Path(__file__).with_name("app.sqlite3")   # 默认数据库文件
# ------------------------------------------------

def _create_connection(db_path: Path = DB_FILE) -> sqlite3.Connection:
    """
    创建并返回一个 SQLite 连接对象。
    - 自动创建文件（如果不存在）。
    - 开启 WAL 模式，提高并发读取性能。
    """
    conn = sqlite3.connect(db_path, detect_types=sqlite3.PARSE_DECLTYPES)
    # 让查询结果可以像字典一样访问（可选）
    conn.row_factory = sqlite3.Row
    # 开启 Write‑Ahead Logging（一次性设置即可）
    conn.execute("PRAGMA journal_mode=WAL;")
    return conn


@contextmanager
def get_connection(db_path: Path = DB_FILE) -> Generator[sqlite3.Connection, None, None]:
    """
    上下文管理器：自动打开连接、提交事务并在结束时关闭。
    使用方式：
        with get_connection() as conn:
            conn.execute(...)
    """
    conn = _create_connection(db_path)
    try:
        yield conn
        conn.commit()          # 正常退出时提交事务
    except Exception:         # 发生异常则回滚
        conn.rollback()
        raise
    finally:
        conn.close()


def get_raw_connection(db_path: Path = DB_FILE) -> sqlite3.Connection:
    """
    如果你不想使用上下文管理器，而是自行控制生命周期，
    可以直接调用此函数获取一个 Connection 对象。
    注意：使用完后务必手动 `conn.close()`
    """
    return _create_connection(db_path)