import configparser
import os
from dataclasses import dataclass
from pathlib import Path

def generate_code():
    # マインコンバート
    cwd = Path(os.getcwd())

    config_file_path = os.path.join(cwd, 'config', 'create_file.properties')
    config_dto = read_config_file(config_file_path)

    target_project_root_path = cwd.parent
    # サンプルファイル作成
    print('CONFIGファイルを作成する')
    sample_config_file_path = os.path.join(cwd, 'sample', 'config', 'properties.txt')
    replacements = {
        "WORK_SPACE": config_dto.work_space,
        "PROJECT_NAME": os.path.basename(target_project_root_path),
        "STEP_NAME": "step_000,step_001,step_002"
    }
    target_project_config_path = os.path.join(target_project_root_path, 'config', config_dto.sub_project_name + '_' + config_dto.sub_source_folder + '_' + config_dto.sub_sub_source_folder_1+'.properties')
    read_replace_create_file(sample_config_file_path, replacements, Path(target_project_config_path))

    print('Main Jobファイルを作成する')
    # サブファイルコントロール、ジョブ、ユニットファイルの作成
    target_project_sub_project_path = os.path.join(target_project_root_path, 'src', config_dto.sub_project_name, config_dto.sub_source_folder, config_dto.sub_sub_source_folder_1)
    # サンプルサブコントロールファイルの作成
    sample_job_file_path = os.path.join(cwd, 'sample', 'child_sample', 'job.txt')
    replacements_job = {}
    target_project_sub_job_path = os.path.join(target_project_sub_project_path, config_dto.sub_source_folder + '_' + config_dto.sub_sub_source_folder_1 + '_job.py')
    read_replace_create_file(sample_job_file_path, replacements_job, Path(target_project_sub_job_path))

    print('Main Unitファイルを作成する')
    sample_unit_file_path = os.path.join(cwd, 'sample', 'child_sample', 'unit.txt')
    replacements_unit = {
        "JOB_PACKAGE": 'src.'+ config_dto.sub_project_name + '.'+ config_dto.sub_source_folder + '.' + config_dto.sub_sub_source_folder_1 + '.' + os.path.basename(target_project_sub_job_path).split('.')[0],
        "GYOMU_JOB_PACKAGE_000": 'src.'+ config_dto.sub_project_name + '.' + config_dto.sub_source_folder + '.' + config_dto.sub_sub_source_folder_1 + '.jobs.job_000',
        "GYOMU_JOB_PACKAGE_001": 'src.' + config_dto.sub_project_name + '.' + config_dto.sub_source_folder + '.' + config_dto.sub_sub_source_folder_1 + '.jobs.job_001',
        "GYOMU_JOB_PACKAGE_002": 'src.' + config_dto.sub_project_name + '.' + config_dto.sub_source_folder + '.' + config_dto.sub_sub_source_folder_1 + '.jobs.job_002'
    }
    target_project_unit_path = os.path.join(target_project_sub_project_path, config_dto.sub_source_folder + '_' + config_dto.sub_sub_source_folder_1 + '_unit.py' )
    read_replace_create_file(sample_unit_file_path, replacements_unit, Path(target_project_unit_path))

    print('Main Controllerファイルを作成する')
    sample_controller_file_path = os.path.join(cwd, 'sample', 'child_sample', 'controller.txt')
    replacements_control = {
        "UNIT_PACKAGE": 'src.'+ config_dto.sub_project_name + '.'+ config_dto.sub_source_folder + '.'+ config_dto.sub_sub_source_folder_1 + '.' + os.path.basename(target_project_unit_path).split('.')[0]
    }
    target_project_sub_controller_path = os.path.join(target_project_sub_project_path, config_dto.sub_source_folder + '_' + config_dto.sub_sub_source_folder_1 + '_control.py')
    read_replace_create_file(sample_controller_file_path, replacements_control, Path(target_project_sub_controller_path))

    init_file_path = Path(os.path.join(target_project_sub_project_path, '__init__.py'))
    create_file(init_file_path,'')

    print('業務Job用フォルダを作成する')
    job_file_path = Path(os.path.join(target_project_sub_project_path,'jobs'))
    job_file_path.mkdir(parents=True, exist_ok=True)
    sample_job000_file_path = os.path.join(cwd, 'sample', 'child_sample', 'job' ,'job_000.txt')
    sample_job_sample_file_path = os.path.join(cwd, 'sample', 'child_sample', 'job', 'job_sample.txt')
    replacements_job000 = {
        'JOB_PACKAGE': 'src.'+ config_dto.sub_project_name + '.'+ config_dto.sub_source_folder + '.' + config_dto.sub_sub_source_folder_1 + '.'  + os.path.basename(target_project_sub_job_path).split('.')[0]
    }
    target_project_job000_path = os.path.join(target_project_sub_project_path, 'jobs','job_000.py')
    target_project_job001_path = os.path.join(target_project_sub_project_path, 'jobs','job_001.py')
    target_project_job002_path = os.path.join(target_project_sub_project_path, 'jobs', 'job_002.py')
    read_replace_create_file(sample_job000_file_path, replacements_job000, Path(target_project_job000_path))
    replacements_job001 = {
        'JOB_NAME':'Job_001',
        'JOB_PACKAGE': 'src.'+ config_dto.sub_project_name + '.'+ config_dto.sub_source_folder + '.' + config_dto.sub_sub_source_folder_1 + '.'  + os.path.basename(target_project_sub_job_path).split('.')[0]
    }
    read_replace_create_file(sample_job_sample_file_path, replacements_job001, Path(target_project_job001_path))
    replacements_job002 = {
        'JOB_NAME': 'Job_002',
        'JOB_PACKAGE': 'src.'+ config_dto.sub_project_name + '.'+ config_dto.sub_source_folder + '.' + config_dto.sub_sub_source_folder_1 + '.'  + os.path.basename(target_project_sub_job_path).split('.')[0]
    }
    read_replace_create_file(sample_job_sample_file_path, replacements_job002, Path(target_project_job002_path))

    init_job_file_path = Path(os.path.join(target_project_sub_project_path, 'jobs', '__init__.py'))
    create_file(init_job_file_path,'')

    print('Main controllerファイルを作成する')
    # サンプルパス
    sample_main_controller_file_path = os.path.join(cwd, 'sample', 'main_convert.txt')
    # パラメーター
    replacements = {
        "CONTROLLER_PACKAGE": 'src.'+ config_dto.sub_project_name + '.' + config_dto.sub_source_folder + '.' + config_dto.sub_sub_source_folder_1 +'.' + os.path.basename(target_project_sub_controller_path).split('.')[0],
        "PYTHON_CONFIG_PROPERTIES": config_dto.sub_project_name + '_' + config_dto.sub_source_folder + '_' + config_dto.sub_sub_source_folder_1 + '.properties'
    }
    # 目標ファイルパス
    target_project_main_controller_path = Path(os.path.join(target_project_root_path, config_dto.sub_project_name + '_'
                                                            + config_dto.sub_source_folder + '_' + config_dto.sub_sub_source_folder_1 +'_controller.py'))
    read_replace_create_file(sample_main_controller_file_path, replacements, target_project_main_controller_path)


def read_replace_create_file(sample_file_path:str, replacements, target_file_path):
    file_content = read_file(sample_file_path)
    after_replace_content = replace_template_vars(file_content, replacements)

    create_file(target_file_path, after_replace_content)

def read_file(template_file_path) -> str:
    with open(template_file_path, 'r', encoding='utf-8') as f:
        template_file = f.read()
    return template_file

def replace_template_vars(template: str, replacements: dict) -> str:
    result = template
    if replacements:
        for key, value in replacements.items():
            placeholder = f"{{{{{key}}}}}"
            result = result.replace(placeholder, str(value))
    return result


def create_file(target_path, target_file_content):
    target_path.parent.mkdir(parents=True, exist_ok=True)
    with open(target_path, 'w', encoding='utf-8') as f:
        f.write(target_file_content)

def read_config_file(find_config_path):
    config = configparser.ConfigParser()
    config.optionxform = str

    with open(find_config_path, 'r', encoding='utf-8') as f:
        content = f.read()
    if not content.lstrip().startswith('['):
        content = '[DEFAULT]\n' + content
    config.read_string(content)

    work_space = config.get('DEFAULT', 'work_space', fallback='.')
    str_sub_project_name = config.get('DEFAULT', 'sub_project_name', fallback='.')
    str_sub_source_folder = config.get('DEFAULT', 'sub_source_folder', fallback='.')
    str_source_folder_1 = config.get('DEFAULT', 'sub_sub_source_folder_1', fallback='.')
    return ConfigDTO(
        work_space=work_space,
        sub_project_name=str_sub_project_name,
        sub_source_folder=str_sub_source_folder,
        sub_sub_source_folder_1=str_source_folder_1
    )

@dataclass
class ConfigDTO:
    work_space: str
    sub_project_name:str
    sub_source_folder:str
    sub_sub_source_folder_1:str

if __name__ == "__main__":
    generate_code()