import copy
from pathlib import Path
from typing import List, Dict

from lxml import etree as ET

from pilot.job.impl.base_job import BaseJob

from base.file_operation import read_file_lines
from db.sql_service import delete_sql_info, insert_sql_info


class DeleteComment(BaseJob):

    @staticmethod
    def _remove_java_comments(java_code: str):
        """
        用状态机把 Java 代码中的注释全部去掉。

        参数
            java_code: 完整的 Java 源码（字符串）

        返回
            去掉注释后的源码
        """
        NORMAL = 0  # 普通代码
        LINE_COMMENT = 1  # // 注释
        BLOCK_COMMENT = 2  # /* … */ 或 /** … */
        STRING_LITERAL = 3  # "…"（包括转义字符）

        state = NORMAL
        i = 0
        n = len(java_code)
        out: List[str] = []

        while i < n:
            ch = java_code[i]

            # ---------- 普通代码 ----------
            if state == NORMAL:
                if ch == '/' and i + 1 < n:  # 可能是注释的起始
                    nxt = java_code[i + 1]
                    if nxt == '/':  # // 单行注释
                        state = LINE_COMMENT
                        i += 2
                        continue
                    elif nxt == '*':  # /* 块注释（包括 /**）
                        state = BLOCK_COMMENT
                        i += 2
                        continue
                    else:
                        out.append(ch)
                elif ch == '"':  # 字符串开始
                    state = STRING_LITERAL
                    out.append(ch)
                else:
                    out.append(ch)

            # ---------- 行注释 ----------
            elif state == LINE_COMMENT:
                if ch == '\n':  # 行结束，回到普通状态
                    out.append(ch)  # 保留换行，使代码行号不变
                    state = NORMAL
                # 其余字符直接丢弃（注释内容）

            # ---------- 块注释 ----------
            elif state == BLOCK_COMMENT:
                if ch == '*' and i + 1 < n and java_code[i + 1] == '/':
                    state = NORMAL
                    i += 2  # 跳过结束符 */
                    continue
                # 块注释内部全部丢弃，遇到换行仍保留，以免影响后续行号
                if ch == '\n':
                    out.append('\n')

            # ---------- 字符串 ----------
            elif state == STRING_LITERAL:
                out.append(ch)
                if ch == '\\' and i + 1 < n:  # 转义字符，跳过下一个字符
                    out.append(java_code[i + 1])
                    i += 2
                    continue
                if ch == '"':  # 字符串结束（未被转义）
                    state = NORMAL

            i += 1

        return ''.join(out)

    def _remove_sql_comments(self, xml_path: Path) -> tuple[ET.Element, List[Dict[str, str]]]:
        """
        读取 MyBatis XML，完成三件事：
            1️⃣ 展开所有 <include>（递归）。
            2️⃣ 删除已展开的 <sql id="…"> 片段（可选）。
            3️⃣ **删除所有 XML 注释**，确保输出文件中不再出现 <!-- … -->。
        返回:
            - expanded_root : 已展开且已删除注释/无用 <sql> 的 Element。
            - statements    : List[{'id','type','sql'}] 已展开的完整 SQL 文本。
        """
        parser = ET.XMLParser(remove_blank_text=False)   # 保留原始换行、缩进
        tree = ET.parse(str(xml_path), parser=parser)
        root = tree.getroot()

        # 1️⃣ 收集 <sql> 片段
        fragments = self.build_sql_fragments(root)

        # 2️⃣ 展开 <include>
        self._expand_node(root, fragments)

        # 3️⃣ 删除已经展开的 <sql>（如果你想保留，只需注释掉下面这行）
        self._remove_unused_sql(root)

        # 4️⃣ **删除所有 XML 注释**
        self._remove_all_comments(root)

        # 5️⃣（可选）写回文件，使用 pretty_print 保持缩进
        expanded_xml = ET.tostring(
            root,
            encoding="utf-8",
            xml_declaration=True,   # 与原文件保持 <?xml …?> 头部
            pretty_print=True       # 美化缩进，便于阅读或打印
        )

        return expanded_xml

    # -------------------------------------------------
    # 3️⃣ 收集 <sql id="…"> 片段
    # -------------------------------------------------
    @staticmethod
    def build_sql_fragments(root: ET.Element) -> Dict[str, ET.Element]:
        """返回 {id : deepcopy(<sql …>)}，防止后续修改原片段。"""
        fragments = {}
        for sql_el in root.findall(".//sql"):
            sid = sql_el.get("id")
            if not sid:
                continue
            fragments[sid] = copy.deepcopy(sql_el)

        for sql_el in root.findall(".//select"):
            sid = sql_el.get("id")
            if not sid:
                continue
            fragments[sid] = copy.deepcopy(sql_el)

        return fragments

    @staticmethod
    def _strip_text(text: str) -> str:
        """去掉首尾空白，保留内部换行与缩进。"""
        if text is None:
            return ""
        lines = text.splitlines()
        # 去掉全空行，右侧空格保留左侧缩进
        lines = [ln.rstrip() for ln in lines if ln.strip() != ""]
        return "\n".join(lines)

    # -------------------------------------------------
    # 4️⃣ 展开 <include>（递归）
    # -------------------------------------------------
    def _expand_node(self, node: ET.Element, fragments: Dict[str, ET.Element]) -> None:
        """
        递归遍历 node 子树，遇到 <include> 用对应 fragment 替换。
        """
        for child in list(node):  # 复制列表，遍历时可增删
            if child.tag == "include":
                refid = child.get("refid")
                if not refid:
                    raise ValueError("<include> without refid attribute")

                fragment = fragments.get(refid)
                if fragment is None:
                    raise KeyError(f"SQL fragment id='{refid}' not found")

                # 复制并递归展开（防止 fragment 本身还有 <include>）
                frag_copy = copy.deepcopy(fragment)
                self._expand_node(frag_copy, fragments)

                # ---- 替换过程 ----
                parent = child.getparent()
                idx = parent.index(child)

                # 把 <include> 原本的 tail（如果有）拼到 fragment 最后一个节点的 tail
                after = child.tail or ""

                if len(frag_copy) == 0:  # 纯文本片段
                    txt = self._strip_text(frag_copy.text or "")
                    if idx == 0:
                        parent.text = (parent.text or "") + txt + after
                    else:
                        prev = parent[idx - 1]
                        prev.tail = (prev.tail or "") + txt + after
                    parent.remove(child)
                else:
                    # 把子元素逐个插入到原来的位置
                    for sub in list(frag_copy):
                        parent.insert(idx, sub)
                        idx += 1

                    # 把 fragment.text（如果有）挂到第一个子节点的 .text
                    if frag_copy.text:
                        first = parent[idx - len(list(frag_copy))]
                        first.text = (first.text or "") + frag_copy.text

                    # 把 after（原 <include> 的 tail）挂到最后一个插入节点的 tail
                    if after:
                        last = parent[idx - 1]
                        last.tail = (last.tail or "") + after

                    # 删除原 <include>
                    parent.remove(child)

            else:
                self._expand_node(child, fragments)

    # -------------------------------------------------
    # 5️⃣ 删除已经展开的 <sql> 片段（可选）
    # -------------------------------------------------
    @staticmethod
    def _remove_unused_sql(root: ET.Element) -> None:
        """在展开完后把所有 <sql id="…"> 元素从文档中删除。"""
        for sql_el in root.findall(".//sql"):
            parent = sql_el.getparent()
            if parent is not None:
                parent.remove(sql_el)

    def _remove_comment(self, comment: ET._Comment) -> None:
        """安全删除注释节点并保留它的 tail。"""
        parent = comment.getparent()
        if parent is None:
            return
        self._splice_tail_before(comment, comment.tail)  # 先搬走 tail
        parent.remove(comment)  # 再删节点

    def _remove_all_comments(self, root: ET._Element) -> None:
        """
        递归遍历整棵树，删除所有 Comment 节点，同时保留它们的 tail（即注释后面的 SQL）。
        """
        for child in list(root):  # 用 list() 复制，防止遍历时结构被修改
            if child.tag is ET.Comment:  # ✅ 这里使用 tag 比较，安全可靠
                self._remove_comment(child)
            else:
                self._remove_all_comments(child)

    # -------------------------------------------------
    # 6️⃣ 删除所有 XML 注释（<!-- … -->）
    # -------------------------------------------------
    def _splice_tail_before(self, node: ET._Element, tail: str) -> None:
        """把 node.tail 合并到前一个兄弟的 tail（或父节点的 text）中。"""
        if not tail:
            return

        prev = node.getprevious()
        if prev is not None:  # 有前一个兄弟元素
            prev.tail = (prev.tail or "") + tail
        else:  # 没有前一个兄弟，说明 node 是父节点的第一个子元素
            parent = node.getparent()
            if parent is not None:
                parent.text = (parent.text or "") + tail

    @staticmethod
    def _insert_sql_file_info(file_name, file_path, file_out_path_str):

        params_delete_file_info = {
            "mapper_file_name": file_name.split('.')[0]
        }
        delete_sql_info('delete_sql_file_info', params_delete_file_info)

        params_file_info = {
            "mapper_file_name": file_name.split('.')[0],
            "original_file_path": file_path,
            "no_comment_file_path": file_out_path_str

        }
        insert_sql_info('sql_file_info', params_file_info)

    def run(self):
        try:

            lines = read_file_lines(self.file_path)
            str_code = ''.join(lines)

            remove_file_type = self.__getattribute__('file_type')
            output_file_path = self.__getattribute__('target_file_path')

            match remove_file_type:
                case 'Java':
                    del_comment_code = self._remove_java_comments(str_code)

                    with open(output_file_path, "w", encoding="utf-8") as fp:
                        fp.write(del_comment_code)
                case 'mybatis':
                    del_comment_code = self._remove_sql_comments(Path(self.file_path))
                    output_file_path.write_bytes(del_comment_code)
                    file_name = Path(self.file_path).name.split('.')[0]
                    self._insert_sql_file_info(file_name,self.file_path , str(output_file_path))

                case _:
                    del_comment_code =''



        except Exception as e:
            self.logger.error(f"{__name__}異常終了. {e}")
            return

        super().run()