from pathlib import Path

from db.sql_executor import exec_ddl


this_path = Path(__file__).resolve()

this_dir = this_path.parent





ddl_file_path_list = [
    # this_dir / 'ddl' / 'METHOD_CLASS_INFO.sql',
    # this_dir / 'ddl' / 'METHOD_FILE_INFO.sql',
    this_dir / 'ddl' / 'METHOD_INFO.sql',
    # this_dir / 'ddl' / 'METHOD_PARAMETER_INFO.sql',
    # this_dir / 'ddl' / 'METHOD_PARSING_INFO.sql',
    # this_dir / 'ddl' / 'METHOD_SUB_METHOD_INFO.sql',
    # this_dir / 'ddl' / 'SQL_CONDITION_INFO.sql',
    # this_dir / 'ddl' / 'SQL_CONTENT_INFO.sql',
    # this_dir / 'ddl' / 'SQL_FILE_INFO.sql',
    # this_dir / 'ddl' / 'SQL_TABLE_INFO.sql',
    # this_dir / 'ddl' / 'SQL_PARAMETER_INFO.sql',
    # this_dir / 'ddl' / 'SQL_PARSING_INFO.sql',
    # this_dir / 'ddl' / 'SQL_COLUMN_INFO.sql',
    # this_dir / 'ddl' / 'TABLE_INFO.sql',
    # this_dir / 'ddl' / 'TABLE_COLUMN_INFO.sql'
]


for ddl_file_path in ddl_file_path_list:
    exec_ddl(str(ddl_file_path))