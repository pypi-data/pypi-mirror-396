import copy
import json
import re
from pathlib import Path
from typing import List, Dict, Tuple

from lxml import etree as ET

from pilot.job.impl.base_job import BaseJob

from base.file_operation import read_file_lines, write_json_file


class SplitFile(BaseJob):

    @staticmethod
    def split_java_methods(java_code: str):
        """
        与えられた単一の完全な Java ソースコードから
        1. 各メソッド（コンストラクタ含む）本体（コメント・アノテーション付き）
        2. メソッドを除いた残りのクラスコード
        を抽出し、指示通りの JSON 文字列を返す。

        【前提】
            * 入力は 1 ファイル分だけ。
            * クラスは 1 つ（内部クラス・列挙型があっても OK）。
            * メソッドはネストしない（ローカルクラス・ローカルメソッドは対象外）。
            * 文字列リテラルやコメント中の波括弧は正規表現だけでは完全に安全に扱えないが、
              本ユーティリティは「実務上よく出会う」コードを対象に設計している。
              必要なら JavaParser 等の本格的パーサに差し替えて下さい。

        【出力形式】
            JSON 文字列（UTF‑8）で、質問文に書かれたスキーマ通り。
        """
        # ------------------------------------------------------------------
        # 1️⃣ パッケージ・インポートの取得（無い場合は空文字列）
        # ------------------------------------------------------------------
        package_pat = re.compile(r'^\s*package\s+([\w\.]+)\s*;\s*', re.MULTILINE)
        pkg_match = package_pat.search(java_code)
        package_name = pkg_match.group(1) if pkg_match else ""

        # ------------------------------------------------------------------
        # 2️⃣ クラス宣言の取得（クラス名だけ抜き出す）
        # ------------------------------------------------------------------
        #   class / interface / enum のいずれかが対象。アノテーションや修飾子は無視。
        class_pat = re.compile(
            r'''(?x)                                   # Verbose
                (?:@\w+(?:\s*\([^)]*\))?\s*)*           # 前置アノテーション（任意）
                (public|protected|private)?\s*         # アクセス修飾子（任意）
                (final|abstract)?\s*                   # class 修飾子（任意）
                (class|interface|enum)\s+              # キーワード
                (?P<name>\w+)                          # クラス名（取得対象）
                (?:\s*<[^>]*>)?                        # ジェネリクス（任意）
                (?:\s+extends\s+[^{]+)?                # extends 句（任意）
                (?:\s+implements\s+[^{]+)?             # implements 句（任意）
                \s*{                                   # 開始波括弧
            ''')
        class_match = class_pat.search(java_code)
        if not class_match:
            raise ValueError("クラス宣言が見つかりませんでした。")
        class_name = class_match.group('name')

        # ------------------------------------------------------------------
        # 3️⃣ メソッド（＝コンストラクタも含む）全体を抽出
        # ------------------------------------------------------------------
        #   正規表現で「コメント・アノテーション + 修飾子 + 戻り値(またはコンストラクタ) + 名前 + パラメータ + 本体」までを取得。
        #   コメントは //, /** */ , /* */ のいずれか。アノテーションは @ で始まる。
        #   本体は波括弧の対称性を数えて取得（re.DOTALL で改行も含める）。
        method_pat = re.compile(
            r'''(?x)                                                       # Verbose
                (?:                                                         
                    (?:/\*\*.*?\*/\s*)?      # Javadoc コメント（任意）
                    (?:/\*.*?\*/\s*)?        # ブロックコメント（任意）
                    (?:\/\/[^\n]*\s*)?       # 行コメント（任意）
                )*
                (?:@\w+(?:\s*\([^)]*\))?\s*)*   # アノテーション（0 個以上）
                (?:public|protected|private|\s)* # アクセス修飾子（任意）
                (?:static\s+)?                 # static 修飾子（任意）
                (?:final\s+|synchronized\s+|abstract\s+|native\s+)* # 余分な修飾子（任意）
                (?:<[^>]+>\s+)?                # メソッドレベルのジェネリクス（任意）
                (?:[\w\<\>\[\]]+\s+)?          # 戻り値型（コンストラクタなら無い）
                (?P<name>\w+)                  # メソッド名（コンストラクタはクラス名）
                \s*\(                          # パラメータ開始
                    [^\)]*                     # 中身は簡易的に「) まで」スキップ
                \)\s*
                (?:throws\s+[^{]+)?           # throws 句（任意）
                \{                             # 本体開始
            ''')

        # メソッド本体の波括弧対称性を数えるためのヘルパー
        def extract_body(start_idx: int) -> Tuple[int, str]:
            """start_idx は '{' の位置。対になる '}' まで走査して全文字列を返す。"""
            depth = 0
            i = start_idx
            while i < len(java_code):
                ch = java_code[i]
                if ch == '{':
                    depth += 1
                elif ch == '}':
                    depth -= 1
                    if depth == 0:
                        # i を含めて抜き出す
                        return i + 1, java_code[start_idx:i + 1]
                i += 1
            raise ValueError("メソッド本体の終端 '}' が見つかりません。")

        # すべてのメソッド情報を格納するリスト
        methods: List[Dict] = []

        # 走査インデックス
        pos = 0
        while True:
            m = method_pat.search(java_code, pos)
            if not m:
                break

            # メソッド名取得
            method_name = m.group('name')
            # コンストラクタかどうか判定（名前がクラス名と同じならコンストラクタ）
            is_constructor = method_name == class_name

            # メソッド宣言全体の開始位置（コメント・アノテーションを含むので、直前に遡る）
            decl_start = m.start()
            # ただし上記正規表現はコメント・アノテーションを「0 回以上」含めているので
            # ここで取得した start はすでにそれらを含んだ位置になる。

            # 本体開始波括弧のインデックス
            brace_idx = java_code.find('{', m.end() - 1)
            if brace_idx == -1:
                raise ValueError("メソッド本体開始 '{' が見つかりません。")

            # 本体全体を取得
            body_end, body_str = extract_body(brace_idx)

            # 完全なメソッド文字列（宣言 + 本体）
            method_full = java_code[decl_start:body_end]

            # 位置情報を保持して後で「残りコード」から除去できるようにする
            methods.append({
                "methodName": method_name,
                "isConstructor": is_constructor,
                "code": method_full,
                "start": decl_start,
                "end": body_end
            })

            # 次の検索は本体終了位置から続ける
            pos = body_end

        # ------------------------------------------------------------------
        # 4️⃣ 「残りコード」作成（メソッド領域を空白に置換してからトリム）
        # ------------------------------------------------------------------
        remaining = list(java_code)  # 文字列を可変リストに
        for m in methods:
            # メソッド領域はスペースで埋めておく（行番号・インデントを保つため）
            for i in range(m["start"], m["end"]):
                remaining[i] = ' '
        remaining_code = ''.join(remaining)

        # 余計な空行を削除（ただしクラスの波括弧は残す）
        remaining_code = re.sub(r'\n\s*\n', '\n', remaining_code).strip() + '\n'

        # ------------------------------------------------------------------
        # 5️⃣ JSON オブジェクト生成
        # ------------------------------------------------------------------
        json_files: List[Dict] = []
        for m in methods:
            file_name = f"{class_name}_{m['methodName']}.txt"
            # エスケープ処理（JSON 用に \ と " をエスケープ）
            escaped_code = m["code"].replace('\\', '\\\\').replace('"', '\\"')
            escaped_remaining = remaining_code.replace('\\', '\\\\').replace('"', '\\"')

            json_files.append({
                "fileName": file_name,
                "className": class_name,
                "methodName": m["methodName"],
                "package": package_name,
                "code": escaped_code,
                "remainingClassCode": escaped_remaining
            })

        result = {"files": json_files}
        return json.dumps(result, ensure_ascii=False, indent=2)

    @staticmethod
    def _extract_statement_nodes(root: ET.Element) -> List[ET.Element]:
        """返回所有可执行语句的 Element（保留完整节点）。"""
        stmts = []
        for tag in ("select", "insert", "update", "delete"):
            stmts.extend(root.findall(f".//{tag}"))
        return stmts


    def split_mybatis_xml(self, xml_path, out_dir: Path) -> List:
        """
        把根节点中的每条语句（select/insert/update/delete）按照它们的 id
        写入独立文件。每个子文件只包含单条语句本身（不再包裹 <mapper>）。
        """
        parser = ET.XMLParser(remove_blank_text=False)  # 保留原始缩进、换行
        tree = ET.parse(str(xml_path), parser=parser)
        root = tree.getroot()

        out_dir.mkdir(parents=True, exist_ok=True)

        out_put_list = []
        for stmt in self._extract_statement_nodes(root):
            stmt_id = stmt.get("id")
            if not stmt_id:  # 没有 id 的语句直接跳过
                continue

            # 复制一份，防止修改原始树结构
            stmt_copy = copy.deepcopy(stmt)

            # 生成文件路径（这里仍然使用 .xml，当然你可以改成 .sql、.txt …）
            out_path = out_dir / f"{stmt_id}.xml"

            # 把单条语句写入文件
            #   - xml_declaration=False  → 不输出 <?xml …?> 声明
            #   - pretty_print=True      → 保持原始的缩进格式
            tree = ET.ElementTree(stmt_copy)
            tree.write(
                str(out_path),
                encoding="utf-8",
                xml_declaration=False,
                pretty_print=True
            )
            print(f"✔ 生成 {out_path}")
            out_put_list.append(out_path)

        return out_put_list


    def run(self):
        try:

            lines = read_file_lines(self.file_path)

            str_code = ''.join(lines)

            remove_file_type = self.__getattribute__('file_type')
            output_file_path = self.__getattribute__('target_file_path')
            match remove_file_type:
                case 'Java':
                    _split_result = self.split_java_methods(str_code)
                    write_json_file(json.loads(_split_result), output_file_path)
                case 'mybatis':
                    _split_file_list = self.split_mybatis_xml(self.file_path, output_file_path)
                    setattr(self, 'split_file_list', _split_file_list)
                case _:
                    _split_result =None

        except Exception as e:
            self.logger.error(f"{__name__}異常終了. {e}")
            return

        super().run()