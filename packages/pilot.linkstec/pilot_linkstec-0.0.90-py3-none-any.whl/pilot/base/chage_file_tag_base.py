import re
from pathlib import Path
from pilot.job.impl.base_job import BaseJob
from base.file_operation import read_file_lines, write_json_file, write_file_line

class ChangeFile(BaseJob):

    @staticmethod
    def escape_sql_text(text):
        """只转义SQL中的 < 和 >"""
        text = text.replace('<', '&lt;')
        text = text.replace('>', '&gt;')
        return text

    def change_mybatis_tag(self, content):
        """处理MyBatis标签内容"""
        # 处理所有动态标签
        tags = ['select', 'update', 'insert', 'delete', 'where', 'if', 'foreach', 'choose', 'otherwise', 'set']

        for tag in tags:
            pattern = re.compile(rf'<{tag}([^>]*?)>([\s\S]*?)</{tag}>', re.IGNORECASE)

            def _single(m):
                attrs, body = m.groups()
                body_fixed = self.process_tag_text(body)
                return f'<{tag}{attrs}>{body_fixed}</{tag}>'

            content = pattern.sub(_single, content)

        return content

    def process_tag_text(self, tag_body):
        """处理标签内容，只转义普通文本中的 < 和 >"""
        parts = re.split(r'(<!--.*?-->|<[^>]+?>)', tag_body, flags=re.DOTALL)
        out = ""
        for i, part in enumerate(parts):
            if i % 2 == 0:
                # 偶数索引是普通文本，需要转义
                out += self.escape_sql_text(part)
            else:
                # 奇数索引是标签，原样保留
                out += part
        return out

    def backup_file(self):

        file_name = Path(self.file_path).name

        file_path = Path(self.file_path)

        backup_file_path = file_path.with_name(file_name + '.back')

        file_path.rename(backup_file_path)


    def run(self):
        try:
            lines = read_file_lines(self.file_path)
            str_code = ''.join(lines)
            remove_file_type = self.__getattribute__('file_type')
            match remove_file_type:
                case 'mybatis':
                    self.backup_file()
                    _split_result = self.change_mybatis_tag(str_code)
                    write_file_line(self.file_path, _split_result)
                case _:
                    _split_result =None

        except Exception as e:
            self.logger.error(f"{__name__}異常終了. {e}")
            return

        super().run()