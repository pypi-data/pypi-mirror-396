import os
from pathlib import Path

from base.ai_info import call_ai

def call_ai_main(prompt_file_path, out_file_path):

    lines = read_file_lines_with_path(prompt_file_path)

    prompt_str = ''.join(lines)

    result_content = call_ai(prompt_str)

    file_name = Path(prompt_file_path).name.split('.')[0] + '.json'

    os.makedirs(out_file_path, exist_ok=True)

    method_info_file = os.path.join(out_file_path, file_name)

    with open(method_info_file, 'w', encoding='utf-8') as f:
        f.write(result_content)

    return method_info_file

def read_file_lines_with_path(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        _lines = f.readlines()
    return _lines

def remove_markdown_code_block(content):
    content = content.strip()
    if content.startswith('```') and content.endswith('```'):
        lines = content.split('\n')
        if len(lines) >= 3:
            return '\n'.join(lines[1:-1])
        else:
            return '\n'.join(lines[1:-1]) if len(lines) > 2 else ''
    return content