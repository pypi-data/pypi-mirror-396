from pathlib import Path

from db.sql_executor import exec_ddl, exec_dml, exec_multiple_dml
from db.sql_service import select_sql_info


# メソッド別のファイル情報を登録する
def insert_file_info(params):
    # パッケージ名
    package_name = params.get('package_name')
    # ファイルパス
    file_path = params.get('file_path')
    # ファイル名
    file_name = params.get('file_name')
    # コメントなしのファイルパス
    no_comment_file_path = params.get('no_comment_file_path')
    # パラメーター情報をマッピング情報に設定する
    dml_params = {
        "package_name": package_name,
        "file_name": file_name,
        "original_file_path": file_path,
        "no_comment_file_path": no_comment_file_path,
        "comment_file_path": "XXXX"
    }
    #
    dml_file_path = r'ddl\INSERT_METHOD_FILE_INFO.sql'

    exec_dml(dml_file_path, dml_params)


def insert_class_info(params):

    package_name = params.get('package_name')

    file_name = params.get('file_name')

    class_name = params.get('class_name')

    class_type = params.get('class_type')

    full_class_name = params.get('full_class_name')

    import_object_name = params.get('import_object_name')

    dml_params = {
        "package_name": package_name,
        "file_name": file_name,
        "class_name": class_name,
        "class_type": class_type,
        "full_class_name": full_class_name,
        "import_object_name": import_object_name

    }

    dml_file_path = r'ddl\INSERT_METHOD_CLASS_INFO.sql'

    exec_dml(dml_file_path, dml_params)


def insert_method_info(params):

    package_name = params.get('package_name')

    file_name = params.get('file_name')

    class_name = params.get('class_name')

    class_type = params.get('class_type')

    full_class_name = params.get('full_class_name')

    import_object_name = params.get('import_object_name')

    dml_params = {
        "package_name": package_name,
        "file_name": file_name,
        "class_name": class_name,
        "class_type": class_type,
        "full_class_name": full_class_name,
        "import_object_name": import_object_name

    }

    dml_file_path = r'ddl\INSERT_METHOD_INFO.sql'

    exec_dml(dml_file_path, dml_params)


def insert_method_parameter_info(params):

    package_name = params.get('package_name')

    file_name = params.get('file_name')

    class_name = params.get('class_name')

    class_type = params.get('class_type')

    full_class_name = params.get('full_class_name')

    import_object_name = params.get('import_object_name')

    dml_params = {
        "package_name": package_name,
        "file_name": file_name,
        "class_name": class_name,
        "class_type": class_type,
        "full_class_name": full_class_name,
        "import_object_name": import_object_name

    }

    dml_file_path = r'ddl\INSERT_METHOD_PARAMETER_INFO.sql'

    exec_dml(dml_file_path, dml_params)


def insert_sub_method_info(params):

    package_name = params.get('package_name')

    file_name = params.get('file_name')

    class_name = params.get('class_name')

    class_type = params.get('class_type')

    full_class_name = params.get('full_class_name')

    import_object_name = params.get('import_object_name')

    dml_params = {
        "package_name": package_name,
        "file_name": file_name,
        "class_name": class_name,
        "class_type": class_type,
        "full_class_name": full_class_name,
        "import_object_name": import_object_name

    }

    dml_file_path = r'ddl\INSERT_SUB_METHOD_INFO.sql'

    exec_dml(dml_file_path, dml_params)


def insert_sql_file_info(params):

    mapper_file_name = params.get('mapper_file_name')

    original_file_path = params.get('original_file_path')

    no_comment_file_path = params.get('no_comment_file_path')

    dml_params = {
        "mapper_file_name": mapper_file_name,
        "original_file_path": original_file_path,
        "no_comment_file_path": no_comment_file_path
    }

    dml_file_path = r'ddl\INSERT_SQL_FILE_INFO.sql'

    exec_dml(dml_file_path, dml_params)


def insert_sql_info(params):

    sql_id = params.get('sql_id')

    sql_style = params.get('sql_style')

    mapper_file_name = params.get('mapper_file_name')

    table_name = params.get('table_name')

    table_alias = params.get('table_alias')

    dml_params = {
        "sql_id": sql_id,
        "sql_style": sql_style,
        "mapper_file_name": mapper_file_name,
        "table_name" : table_name,
        "table_alias" : table_alias
    }

    dml_file_path = r'ddl\INSERT_SQL_INFO.sql'

    exec_dml(dml_file_path, dml_params)


def insert_condition_info(params):
    sql_id = params.get('sql_id')

    sql_style = params.get('sql_style')

    mapper_file_name = params.get('mapper_file_name')

    condition_content = params.get('condition_content')

    dml_params = {
        "sql_id": sql_id,
        "sql_style": sql_style,
        "mapper_file_name": mapper_file_name,
        "condition_content" : condition_content
    }

    dml_file_path = r'ddl\INSERT_CONDITION_INFO.sql'

    exec_dml(dml_file_path, dml_params)

def insert_parameter_info(params):
    sql_id = params.get('sql_id')

    sql_style = params.get('sql_style')

    mapper_file_name = params.get('mapper_file_name')

    condition_content = params.get('condition_content')

    dml_params = {
        "sql_id": sql_id,
        "sql_style": sql_style,
        "mapper_file_name": mapper_file_name,
        "condition_content" : condition_content
    }

    dml_file_path = r'ddl\INSERT_CONDITION_INFO.sql'

    exec_dml(dml_file_path, dml_params)


def insert_column_info(params):
    sql_id = params.get('sql_id')

    sql_style = params.get('sql_style')

    mapper_file_name = params.get('mapper_file_name')

    condition_content = params.get('condition_content')

    dml_params = {
        "sql_id": sql_id,
        "sql_style": sql_style,
        "mapper_file_name": mapper_file_name,
        "condition_content" : condition_content
    }

    dml_file_path = r'ddl\INSERT_CONDITION_INFO.sql'

    exec_dml(dml_file_path, dml_params)



#
#
#

if __name__ == "__main__":
    # ddl_file_path = r'E:\METHOD_FILE_INFO.sql'
    # exec_ddl(ddl_file_path)
    #
    # params = {
    #     "package_name": "com.example.service",
    #     "file_name": "OrderService.py",
    #     "original_file_path": "/src/com/example/service/OrderService.py",
    #     "no_comment_file_path": "/tmp/no_comment/OrderService.py",
    #     "comment_file_path": "/tmp/commented/OrderService.py"
    # }

    # search_sql_info = select_sql_info('sql_info', {'sql_id': 'batchInsertAddress'})


    # dml_file_path = r'E:\SELECT_SQL_PARAMETER_INFO.sql'
    #
    # dml_file_path = r'E:\SELECT_SQL_TABLE_INFO.sql'
    #
    # dml_file_path = r'E:\SELECT_METHOD_SUB_METHOD_INFO.sql'
    #
    dml_file_path = r'E:\SELECT_METHOD_INFO.sql'
    result = exec_dml(dml_file_path)

    for row_info in result:

        print(dict(row_info))

    # #
    # dml_file_path = r'E:\DROP_TABLE_METHOD.sql'
    # dml_file_path = r'E:\DELETE_METHOD_INFO.sql'
    # # dml_file_path = r'E:\UPDATE_METHOD_SUB_METHOD_INFO.sql'
    # result = exec_multiple_dml(dml_file_path)



