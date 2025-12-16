import os
import re
from pathlib import Path

from pilot.job.impl.base_job import BaseJob

from base.file_operation import write_file_line, write_java_files, read_json_file_lines, read_file_lines
from db.sql_service import delete_sql_info, insert_sql_info, select_sql_info, update_sql_info


class DBOperationBase(BaseJob):

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

    @staticmethod
    def _insert_sql_content_info(sql_mapper_name, sql_id, sql_content):

        params_delete_sql_content_info = {
            "sql_mapper_name": sql_mapper_name,
            "sql_id": sql_id
        }

        delete_sql_info('delete_sql_content_info', params_delete_sql_content_info)

        params_file_info = {
            "sql_mapper_name": sql_mapper_name,
            "sql_id": sql_id,
            "sql_content": sql_content
        }

        insert_sql_info('sql_content_info', params_file_info)

    @staticmethod
    def _update_sql_table_content_info(sql_mapper_name, sql_id, result_info):
        sql_style = result_info.get('SQL_STYLE')
        # SQL CONTENTテーブル情報の更新処理
        params_info = {
            'sql_style': sql_style,
            'sql_mapper_name': sql_mapper_name,
            'sql_id': sql_id
        }

        update_sql_info('update_sql_table_content_info', params_info)

    @staticmethod
    def _insert_sql_table_info(sql_mapper_name, sql_id, result_info):
        sql_content = result_info.get('CONTENT')

        sql_style = result_info.get('SQL_STYLE')

        if sql_content:

            params_delete_sql_table_info = {
                "sql_mapper_name": sql_mapper_name,
                "sql_id": sql_id
            }

            delete_sql_info('delete_sql_table_info', params_delete_sql_table_info)

            if sql_style.upper() == 'DDL':
                table_name = sql_content.get('OBJECT_NAME')
                params_file_info = {
                    "sql_mapper_name": sql_mapper_name,
                    "sql_id": sql_id,
                    "sql_style": sql_style,
                    "mapper_file_name": sql_mapper_name + '.xml',
                    "table_name": table_name,
                    "table_alias": ''
                }

                insert_sql_info('sql_table_info', params_file_info)

            tables_list = sql_content.get('TARGET_TABLES')

            # SQLのテーブル情報の登録処理
            if tables_list:
                for table_info in tables_list:
                    table_name = table_info.get('TABLE_NAME')
                    table_alias = table_info.get('ALIAS')
                    params_file_info = {
                        "sql_mapper_name": sql_mapper_name,
                        "sql_id": sql_id,
                        "sql_style": sql_style,
                        "mapper_file_name": sql_mapper_name + '.xml',
                        "table_name": table_name,
                        "table_alias": table_alias
                    }

                    insert_sql_info('sql_table_info', params_file_info)

    @staticmethod
    def _insert_sql_condition_info(sql_mapper_name, sql_id, result_info):

        params_delete_sql_condition_info = {
            "sql_mapper_name": sql_mapper_name,
            "sql_id": sql_id
        }

        delete_sql_info('delete_sql_condition_info', params_delete_sql_condition_info)

        sql_content = result_info.get('CONTENT')

        sql_style = result_info.get('SQL_STYLE')

        condition_info = sql_content.get('WHERE_CLAUSE')
        if condition_info:
            params_condition_info = {
                "sql_mapper_name": sql_mapper_name,
                "sql_id": sql_id,
                "sql_style": sql_style,
                "mapper_file_name": sql_mapper_name + '.xml',
                "condition_content": condition_info
            }
            insert_sql_info('sql_condition_info', params_condition_info)

    @staticmethod
    def _insert_sql_column_info(sql_mapper_name, sql_id, result_info):

        params_delete_sql_column_info_info = {
            "sql_mapper_name": sql_mapper_name,
            "sql_id": sql_id
        }

        delete_sql_info('delete_sql_column_info_info', params_delete_sql_column_info_info)

        sql_style = result_info.get('SQL_STYLE')
        sql_content = result_info.get('CONTENT')
        operation_type = sql_content.get('OPERATION_TYPE')
        # SQLのカラム情報の登録処理
        table_name_ddl = ''
        if sql_style.upper() == 'DDL':
            table_name = sql_content.get('OBJECT_NAME')
            table_name_ddl = table_name

            definition_details_info = sql_content.get('DEFINITION_DETAILS')
            columns_info_list = definition_details_info.get('COLUMNS')
        else:
            columns_info_list = sql_content.get('COLUMNS')

        if columns_info_list:
            for column_info in columns_info_list:
                if sql_style.upper() == 'DDL':
                    table_name = table_name_ddl
                    table_alias = ''
                    column_name = column_info.get('COLUMN_NAME')
                    column_alias = ''
                else:
                    table_name = column_info.get('TABLE_NAME')
                    table_alias = column_info.get('TABLE_ALIAS')
                    column_name = column_info.get('COLUMN_NAME')
                    column_alias = column_info.get('COLUMN_ALIAS')

                params_column_info = {
                    "sql_mapper_name": sql_mapper_name,
                    "sql_id": sql_id,
                    "sql_style": sql_style,
                    "mapper_file_name": sql_mapper_name + '.xml',
                    "table_name": table_name,
                    "table_alias": table_alias,
                    "sql_type": operation_type,
                    "column_name": column_name,
                    "column_alias": column_alias
                }
                insert_sql_info('sql_column_info', params_column_info)

    @staticmethod
    def _insert_sql_parameter_info(sql_mapper_name, sql_id, result_info):

        params_delete_sql_parameter_info = {
            "sql_mapper_name": sql_mapper_name,
            "sql_id": sql_id
        }

        delete_sql_info('delete_sql_parameter_info', params_delete_sql_parameter_info)

        sql_style = result_info.get('SQL_STYLE')
        sql_content = result_info.get('CONTENT')

        # SQLのパラメーター条件情報の登録処理
        params_info_list = sql_content.get('PARAMETERS')
        if params_info_list:
            for params_info in params_info_list:
                parameter_name = params_info.get('PARAMETER_NAME')
                parameter_column_name = params_info.get('LINKED_ITEM')
                parameter_table_name = params_info.get('LINKED_TABLE_NAME')
                params_parameter_info = {
                    "sql_mapper_name": sql_mapper_name,
                    "sql_id": sql_id,
                    "sql_style": sql_style,
                    "mapper_file_name": sql_mapper_name + '.xml',
                    "parameter_name": parameter_name,
                    "parameter_column_name": parameter_column_name,
                    "parameter_table_name": parameter_table_name
                }
                insert_sql_info('sql_parameter_info', params_parameter_info)

    @staticmethod
    def _insert_sql_parsing_info(sql_mapper_name, sql_id, result_info, parsing_sql_file_path):

        params_delete_sql_parameter_info = {
            "sql_mapper_name": sql_mapper_name,
            "sql_id": sql_id
        }

        delete_sql_info('delete_sql_parsing_info', params_delete_sql_parameter_info)

        in_parameter_info = result_info.get('IN_DTO')
        output_info = result_info.get('OUT_DTO')
        sql_description = result_info.get('SQL_PURPOSE')
        sql_content = result_info.get('SQL')

        insert_value = {
            'sql_mapper_name': sql_mapper_name,
            'sql_id': sql_id,
            'in_parameter_info': str(in_parameter_info),
            'output_info': str(output_info),
            'sql_description': sql_description,
            'sql_content': sql_content,
            'parsing_file_path': parsing_sql_file_path
        }

        insert_sql_info('sql_parsing_info', insert_value)

    @staticmethod
    def _update_method_info(method_all_info, class_name):
        # パッケージ名
        package_name = method_all_info.get('package')
        # メソッド情報
        methods_info = method_all_info.get('methods')

        if methods_info:
            for method_info in methods_info:
                method_name = method_info.get('method_name')
                return_type = method_info.get('return_type')

                params_method_info = {
                    "package_name": package_name,
                    "class_name": class_name,
                    "method_name": method_name,
                    "return_type": return_type
                }
                update_sql_info('update_method_info', params_method_info)

    @staticmethod
    def _insert_method_parameter_info(method_all_info, class_name):
        # パッケージ名
        package_name = method_all_info.get('package')
        # メソッド情報
        methods_info = method_all_info.get('methods')
        if methods_info:
            for method_info in methods_info:
                parameters_info = method_info.get('parameters')
                method_name = method_info.get('method_name')
                if parameters_info:

                    params_delete_parameter_info = {
                        "package_name": package_name,
                        "class_name": class_name,
                        "method_name": method_name
                    }
                    delete_sql_info('delete_method_parameter_info', params_delete_parameter_info)
                    for parameter_info in parameters_info:
                        parameter_type = parameter_info.get('parameter_type')
                        parameter_name = parameter_info.get('parameter_name')

                        params_parameter_info = {
                            "package_name": package_name,
                            "class_name": class_name,
                            "method_name": method_name,
                            "parameter_type": parameter_type,
                            "parameter_name": parameter_name
                        }
                        insert_sql_info('method_parameter_info', params_parameter_info)

    @staticmethod
    def _insert_method_sub_method_info(method_all_info, class_name):
        # パッケージ名
        package_name = method_all_info.get('package')
        # メソッド情報
        methods_info = method_all_info.get('methods')

        if methods_info:
            for method_info in methods_info:
                method_name = method_info.get('method_name')
                sub_method_calls = method_info.get('sub_method_calls')

                if sub_method_calls:
                    params_delete_sub_method_calls_info = {
                        "package_name": package_name,
                        "class_name": class_name,
                        "method_name": method_name
                    }
                    delete_sql_info('delete_method_sub_method_info', params_delete_sub_method_calls_info)

                    for sub_method_call in sub_method_calls:
                        sub_method_name = sub_method_call.get('sub_method_name')
                        called_method_full_signature = sub_method_call.get('called_method_full_signature')
                        called_method_class = sub_method_call.get('called_method_class')
                        called_method_class_package = sub_method_call.get('called_method_class_package')

                        params_sub_method_calls_info = {
                            "package_name": package_name,
                            "class_name": class_name,
                            "method_name": method_name,
                            "sub_method_name": sub_method_name,
                            "called_method_full_signature": called_method_full_signature,
                            "called_method_class": called_method_class,
                            "called_method_class_package": called_method_class_package
                        }
                        insert_sql_info('sub_method_info', params_sub_method_calls_info)



    @staticmethod
    def _insert_method_info(file_info_list):

        if file_info_list:
            for file_info in file_info_list:
                file_name = file_info.get('fileName')
                class_name = file_info.get('className')
                method_name = file_info.get('methodName')
                package_name = file_info.get('package')
                method_code = file_info.get('code')
                remaining_class_code = file_info.get('remainingClassCode')

                params_delete_method_info = {
                    "package_name": package_name,
                    "class_name": class_name,
                    "method_name": method_name
                }
                delete_sql_info('delete_method_info', params_delete_method_info)

                params_method_info = {
                    "package_name": package_name,
                    "class_name": class_name,
                    "file_name": file_name,
                    "method_name": method_name,
                    "full_method_signature": method_code,
                    "return_type": '',
                    "remaining_class_code": remaining_class_code
                }

                insert_sql_info('method_info', params_method_info)

    @staticmethod
    def _insert_method_file_info(package_info, class_name, file_name, file_path):

        full_class_name = package_info + '.' + class_name

        params_delete_method_file_info = {
            "package_name": package_info,
            "class_name": class_name
        }
        delete_sql_info('delete_method_file_info', params_delete_method_file_info)

        # クラス情報
        params_method_file_info = {
            "package_name": package_info,
            "class_name": class_name,
            "file_name": file_name,
            "original_file_path": full_class_name,
            "no_comment_file_path": file_path
        }

        insert_sql_info('method_file_info', params_method_file_info)

    @staticmethod
    def _insert_method_class_info(imports_info, package_info, class_name, file_name):
        full_class_name = package_info + '.' + class_name

        # クラスのimport情報
        if imports_info:
            params_delete_method_class_info = {
                "package_name": package_info,
                "class_name": class_name
            }
            delete_sql_info('delete_method_class_info', params_delete_method_class_info)

            for import_info in imports_info:
                params_method_class_info = {
                    "package_name": package_info,
                    "class_name": class_name,
                    "file_name": file_name,
                    "class_type": '',
                    'full_class_name': full_class_name,
                    "import_object_name": import_info
                }
                insert_sql_info('method_class_info', params_method_class_info)

    def create_sub_file(self, file_info_list):

        output_folder = self.__getattribute__('output_folder')

        sub_file_path =[]
        if file_info_list:
            for file_info in file_info_list:
                file_name = file_info.get('fileName')
                class_name = file_info.get('className')
                package_name = file_info.get('package')
                method_code = file_info.get('code')

                # クラス別のimport情報ファイルを作成する
                import_file_path = os.path.join(str(output_folder), class_name + '.json')
                package_info_path = os.path.join(str(output_folder), class_name + '_package.json')

                write_file_line(package_info_path, package_name)
                self.copy_input_file_to_next_step(package_info_path)

                if not os.path.exists(import_file_path):
                    params_method_class_info = {
                        "package_name": package_name,
                        "class_name": class_name
                    }
                    method_class_info_result = select_sql_info('method_class_info', params_method_class_info)
                    method_class_info_list = []
                    if method_class_info_result:
                        for method_class_info in method_class_info_result:
                            import_info = method_class_info.get('IMPORT_OBJECT_NAME')
                            method_class_info_list.append(import_info)

                    str_method_class_info = '\n'.join(method_class_info_list)

                    write_file_line(import_file_path, str_method_class_info)
                    self.copy_input_file_to_next_step(import_file_path)

                file_path = os.path.join(str(output_folder), file_name)
                write_java_files(Path(file_path), method_code)
                sub_file_path.append(file_path)
        return sub_file_path

    def run(self):
        try:

            file_name = Path(self.file_path).name

            class_name = file_name.split('.')[0]

            db_operation_type = self.__getattribute__('db_operation_type')

            match db_operation_type:
                case 'method_base':
                    package_info, imports_info = self.extract()
                    self._insert_method_file_info(package_info, class_name, file_name, self.file_path)
                    self._insert_method_class_info(imports_info, package_info, class_name, file_name)
                case 'method_info':
                    _file_info = read_json_file_lines(self.file_path)
                    file_info_list = _file_info.get('files')
                    self._insert_method_info(file_info_list)
                    sub_file_path = self.create_sub_file(file_info_list)
                    setattr(self, 'sub_file_path', sub_file_path)
                case 'sub_method_info':
                    method_all_info = self.__getattribute__('method_all_info')
                    # メソッド情報の取得する
                    # クラス名
                    class_name = str(Path(Path(self.file_path).parent).name)

                    self._update_method_info(method_all_info, class_name)

                    self._insert_method_parameter_info(method_all_info, class_name)

                    self._insert_method_sub_method_info(method_all_info, class_name)

                case 'sql_base':

                    sql_content_list = read_file_lines(self.file_path)
                    sql_content = ''.join(sql_content_list)
                    sql_mapper_name = Path(Path(self.file_path).parent).name
                    sql_id = file_name.split('.')[0]
                    # SQLの基本情報の登録する
                    self._insert_sql_content_info(sql_mapper_name, sql_id, sql_content)

                case 'sub_sql_info':

                    sql_mapper_name = Path(Path(self.file_path).parent).name
                    sql_id = file_name.split('.')[0]
                    all_sql_info = self.__getattribute__('all_sql_info')
                    # SQL基本情報の更新処理
                    self._update_sql_table_content_info(sql_mapper_name, sql_id, all_sql_info)
                    # SQL用テーブル情報の登録する
                    self._insert_sql_table_info(sql_mapper_name, sql_id, all_sql_info)
                    # SQLの条件情報の登録する
                    self._insert_sql_condition_info(sql_mapper_name, sql_id, all_sql_info)
                    # SQLの条件項目情報の登録する
                    self._insert_sql_column_info(sql_mapper_name, sql_id, all_sql_info)

                case 'parsing_sql':
                    # DB登録する
                    sql_mapper_name = Path(Path(self.file_path).parent).name
                    sql_id = file_name.split('.')[0]
                    parsing_result_info = self.__getattribute__('parsing_result_info')

                    # SQLの条件項目情報の登録する
                    self._insert_sql_parsing_info(sql_mapper_name, sql_id, parsing_result_info, self.file_path)

                case _:
                    del_comment_code =''


        except Exception as e:
            self.logger.error(f"{__name__}異常終了. {e}")
            return

        super().run()

    def extract(self):

        package_re = re.compile(r'^\s*package\s+([\w.]+)\s*;', re.MULTILINE)
        import_re = re.compile(r'^\s*import\s+([^\s;]+)\s*;(.*)', re.MULTILINE)

        file_path = Path(self.file_path)
        src = file_path.read_text(encoding='utf-8')

        pkg_match = package_re.search(src)
        package_name = pkg_match.group(1) if pkg_match else '(default)'

        imports = [m.group(1).strip() for m in import_re.finditer(src)]

        return package_name, imports


