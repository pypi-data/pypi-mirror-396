import fnmatch
import os
from pathlib import Path
from typing import Dict, Any

from pilot.job.impl.base_job import BaseJob

from base.file_operation import write_json_file
from db.sql_service import select_sql_info

class MakeParsingJavaOrderBase(BaseJob):

    def get_no_sub_method_java_list(self):

        search_result = select_sql_info('sql_no_sub_method_info', {})
        parsing_no_sub_method_list = []
        if search_result:
            for result_info in search_result:
                str_class_name = result_info.get('CLASS_NAME')
                str_method_name = result_info.get('METHOD_NAME')
                str_package_name = result_info.get('PACKAGE_NAME')

                if '.dao' not in str_package_name:
                    params_get_count_sub_method_info= {
                        "sub_method_name": str_method_name,
                        "called_method_class": str_package_name + '.' + str_class_name
                    }

                    search_count_result = self.get_count_sub_method_info(params_get_count_sub_method_info)
                    if search_count_result > 0:
                        no_sub_method_java_info = str_class_name + ',' + str_method_name + ',' + str_package_name
                        parsing_no_sub_method_list.append(no_sub_method_java_info)

        return parsing_no_sub_method_list

    def get_dao_method_list(self):
        search_result = select_sql_info('sql_get_dao_method_info', {'package_name': '%.dao%'})
        parsing_dao_list = []
        if search_result:
            for result_info in search_result:

                _str_class_name = result_info.get('CLASS_NAME')
                str_method_name = result_info.get('METHOD_NAME')
                str_package_name = result_info.get('PACKAGE_NAME')

                str_class_name = _str_class_name.replace('_' + str_method_name, '')

                params_get_count_sub_method_info = {
                    "sub_method_name": str_method_name,
                    "called_method_class": str_package_name + '.' + str_class_name
                }

                search_count_result = self.get_count_sub_method_info(params_get_count_sub_method_info)

                if search_count_result > 0:
                    doa_info = str_class_name + ',' + str_method_name + ',' + str_package_name
                    parsing_dao_list.append(doa_info)

        return parsing_dao_list

    def other_parsing_method(self, json_list, round_num):

        while json_list:
            values_str_list = []
            for json_info in json_list:
                json_info_arr = json_info.split(',')
                class_name = json_info_arr[0]
                method_name = json_info_arr[1]
                package_name = json_info_arr[2]

                values_str_list.append((class_name, method_name))
            values_str = ",\n".join(
                f"('{cls}', '{method}')" for cls, method in values_str_list
            )
            search_result = select_sql_info('sql_get_sub_method_info_all_list', {'values_str': values_str_list})

            if not search_result:
                break

            parsing_java = []

            for result_info in search_result:
                _str_class_name = result_info.get('CLASS_NAME')
                str_method_name = result_info.get('METHOD_NAME')
                str_package_name = result_info.get('PACKAGE_NAME')

                str_class_name = _str_class_name.replace('_' + str_method_name, '')

                params_get_count_sub_method_info = {
                    "sub_method_name": str_method_name,
                    "called_method_class": str_package_name + '.' + str_class_name
                }

                search_count_result = self.get_count_sub_method_info(params_get_count_sub_method_info)
                if search_count_result > 0:
                    parsing_java_info_1 = str_class_name + ',' + str_method_name + ',' + str_package_name
                    parsing_java.append(parsing_java_info_1)

            json_file_name = os.path.basename(self.file_path).split('.')[0] + '_' + str(round_num) + '.json'
            json_file_path = str(os.path.join(os.path.dirname(self.file_path), json_file_name))

            write_json_file(parsing_java, json_file_path)

            round_num += 1
            json_list = parsing_java


    @staticmethod
    def get_count_sub_method_info(params: Dict[str, Any]) -> int:

        search_count_result = select_sql_info('get_count_sub_method_info', params)
        if search_count_result:
            for count_info in search_count_result:
                count = count_info.get('COUNT')
                return count

    def run(self):
        try:

            file_name = os.path.splitext(os.path.basename(self.file_path))[0]

            no_sub_method_java_list = self.get_no_sub_method_java_list()
            dao_list = self.get_dao_method_list()
            search_list = no_sub_method_java_list + dao_list

            count_index = 0

            if no_sub_method_java_list:
                count_index = count_index + 1
                out_file_name = file_name + '_' + str(count_index) + '.json'
                no_sub_method_json_path = os.path.join(os.path.dirname(self.file_path), out_file_name)
                write_json_file(no_sub_method_java_list, no_sub_method_json_path)

            if dao_list:
                count_index = count_index + 1
                out_file_name = file_name + '_' + str(count_index) + '.json'
                dao_json_path = os.path.join(os.path.dirname(self.file_path), out_file_name)
                write_json_file(dao_list, dao_json_path)

            if search_list:
                self.other_parsing_method(search_list, count_index + 1)

            matches = []
            for root, dirs, files in os.walk(Path(self.file_path).parent):
                for filename in fnmatch.filter(files, "*.json"):
                    matches.append(os.path.join(root, filename))

            setattr(self, '_list', matches)

        except Exception as e:
            self.logger.error(f"{__name__}異常終了. {e}")
            return

        super().run()