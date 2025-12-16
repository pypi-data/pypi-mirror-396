import json
import os.path
from pathlib import Path

from typing import List, Dict, Any
from venv import logger

from base.get_file_encoding import get_file_encoding

#
def read_file_lines(file_path):
    if not os.path.exists(file_path):
        logger.error(f"ファイルが存在しない。{file_path}")
        return None
    file_encoding = get_file_encoding(file_path)
    with open(file_path, 'r', encoding=file_encoding) as f:
        _lines = f.readlines()
    return _lines

def read_json_file_lines(json_file_path):
    if not os.path.exists(json_file_path):
        logger.error(f"JSONファイルが存在しない。{json_file_path}")
        return None

    json_file_encoding = get_file_encoding(json_file_path)
    with open(json_file_path, 'r', encoding=json_file_encoding) as fp:
        return json.load(fp)  # -> List[Dict]

def write_file_line(file_path, file_content):
    path = Path(file_path)
    os.makedirs(str(path.parent), exist_ok=True)
    with path.open('w', encoding="utf-8") as f:
        f.write(file_content)

def write_json_file(data: List[Dict[str, Any]], json_file_path) -> None:
    """把列表写回 JSON 文件，使用 4 空格缩进，保证可读性。"""
    path = Path(json_file_path)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def write_java_files(file_path, code):
    real_code = code.replace(r'\n', '\n')
    with file_path.open("w", encoding="utf-8") as f:
        f.write(real_code.rstrip()+ '\n')