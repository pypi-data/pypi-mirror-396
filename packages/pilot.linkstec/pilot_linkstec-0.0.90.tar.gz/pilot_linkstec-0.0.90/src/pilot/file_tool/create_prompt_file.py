import pathlib
import re
from typing import Mapping, Optional


def load_text(file_path: str | pathlib.Path) -> str:
    """讀取檔案內容，返回 Unicode 字串。"""
    path = pathlib.Path(file_path)
    if not path.is_file():
        raise FileNotFoundError(f"File not found: {path}")

    return path.read_text(encoding='utf-8')

def replace_by_map(
    text: str,
    replace_map: Mapping[str, str],
    *,
    use_regex: bool = False,
    case_sensitive: bool = True,
) -> str:

    if not replace_map:
        return text

    # 若使用正則，先把所有 pattern 編譯好，提高效能
    if use_regex:
        flags = 0 if case_sensitive else re.IGNORECASE
        compiled = [(re.compile(p, flags), repl) for p, repl in replace_map.items()]
        for pattern, repl in compiled:
            text = pattern.sub(repl, text)
    else:
        # 直接使用 str.replace，速度最快
        for old, new in replace_map.items():

            text = text.replace(old, new)

    return text

def save_text(
    file_path: str | pathlib.Path,
    text: str,
    *,
    encoding: Optional[str] = None,
) -> None:

    path = pathlib.Path(file_path)
    if not path.parent.exists():
        path.parent.mkdir(parents=True, exist_ok=True)

    enc = encoding or "utf-8"
    path.write_text(text, encoding=enc)

def process_file(
    src_path: str | pathlib.Path,
    dst_path: Optional[str | pathlib.Path] = None,
    replace_map: Optional[Mapping[str, str]] = None,
    *,
    use_regex: bool = False,
    case_sensitive: bool = True,
) -> None:

    original = load_text(src_path)

    if replace_map:
        new_text = replace_by_map(
            original,
            replace_map,
            use_regex=use_regex,
            case_sensitive=case_sensitive,
        )
    else:
        new_text = original

    target = dst_path if dst_path is not None else src_path
    save_text(target, new_text)
