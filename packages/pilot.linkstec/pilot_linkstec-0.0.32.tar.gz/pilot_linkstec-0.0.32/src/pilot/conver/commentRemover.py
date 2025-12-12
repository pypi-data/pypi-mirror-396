import re
from pathlib import Path
import sys

class CommentRemover:
    """
    ColdFusion (.cfm, .cfc) と JavaScript (.js) のコメント削除クラス
    """

    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
        self.text = ''
        self.cleaned_text = ''

    def load(self, encoding='utf-8'):
        try:
            with self.file_path.open('r', encoding=encoding) as f:
                self.text = f.read()
        except Exception as e:
            print(f"Failed to load file {self.file_path}: {e}", file=sys.stderr)
            raise

    def save(self, output_path: str, encoding='utf-8'):
        try:
            with open(output_path, 'w', encoding=encoding) as f:
                f.write(self.cleaned_text)
        except Exception as e:
            print(f"Failed to save file {output_path}: {e}", file=sys.stderr)
            raise

    def remove_comments(self):
        ext = self.file_path.suffix.lower()
        if ext in ['.cfm', '.cfc']:
            self.cleaned_text = self.remove_coldfusion_comments(self.text)
        elif ext == '.js':
            self.cleaned_text = self.remove_js_comments(self.text)
        elif ext in ['.cbl', '.cob', '.cobol']:
            self.cleaned_text = self.remove_cobol_comments(self.text)
        else:
            print(f"Unsupported file extension: {ext}, no comment removal applied.", file=sys.stderr)
            self.cleaned_text = self.text

    def remove_coldfusion_comments(self, text: str) -> str:
        pattern_cftag = r'<!---(?:.|\n)*?--->'
        pattern_block = r'/\*(?:.|\n)*?\*/'
        pattern_line = r'//.*?$'

        text = re.sub(pattern_cftag, '', text, flags=re.MULTILINE)
        text = re.sub(pattern_block, '', text, flags=re.MULTILINE)
        text = re.sub(pattern_line, '', text, flags=re.MULTILINE)
        return text

    def remove_js_comments(self, text: str) -> str:
        pattern_block = r'/\*(?:.|\n)*?\*/'
        pattern_line = r'//.*?$'

        text = re.sub(pattern_block, '', text, flags=re.MULTILINE)
        text = re.sub(pattern_line, '', text, flags=re.MULTILINE)
        return text

    def remove_cobol_comments(self, text: str) -> str:
        """
        COBOLのコメント行、および方言の行内コメント *>以降を削除

        ・固定形式コメント行
          行頭が '*'（先頭1文字目が*）の行はコメント → 削除
          または7文字目が '*'の行もコメント → 削除

        ・行内コメント (方言)
          '*> '以降はコメント → 削除
        """

        lines = text.splitlines()
        cleaned_lines = []

        for line in lines:
            # 固定長形式にあわせて7文字目 (index 6)を判定
            # 行長が7未満でも対応 (存在しなければFalse)
            is_comment_line = False

            if line.startswith('*'):
                is_comment_line = True
            elif len(line) >= 7 and line[6] == '*':
                is_comment_line = True

            if is_comment_line:
                # コメント行なのでスキップ
                continue

            # 行内コメント *> の扱い
            # 行の途中に '*> ' (*>に続く空白も含む) があればその位置で切り捨てる
            comment_pos = line.find('*>')
            if comment_pos != -1:
                # 行内コメント開始位置でカット（空白も含め全部削除）
                # 例えば 'MOVE X TO Y *> このコメント' => 'MOVE X TO Y '
                line = line[:comment_pos].rstrip()

            cleaned_lines.append(line)

        return '\n'.join(cleaned_lines)