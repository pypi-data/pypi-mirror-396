import os
import re
import shutil
import json
from copy import deepcopy
from pathlib import Path
from typing import List, Tuple

class BuilderUpd:
    TEMPLATE_PATH   = Path(os.path.abspath(__file__)).parent / Path('assets') / Path('template')
    EXAMPLE_PATH    = Path(os.path.abspath(__file__)).parent / Path('assets') / Path('example')
    GITIGNORE_PATH  = Path('.gitignore')
    LAUNCH_PATH     = Path('.vscode/launch.json')
    SETTINGS_PATH   = Path('.vscode/settings.json')
    TASKS_PATH      = Path('.vscode/tasks.json')
    VERSION_TAG     = 'builderUpd.version'


    def __init__(self, prj_path : Path):
        prj_path = Path(prj_path)
        if prj_path == os.path.abspath(__file__):
            raise ValueError('Invalid output path')
        self.__prj_path = prj_path


    @staticmethod
    def __text_2_list(text_path : Path) -> list:
        try:
            with open(text_path, 'r', encoding='utf-8') as f:
                return f.readlines()
        except FileNotFoundError:
            return None


    @staticmethod
    def __list_2_text(text_path : Path, in_list : list):
        if not text_path.parent.exists():
            Path.mkdir(text_path.parent, parents=True)
        with open(text_path, 'w', encoding='utf-8') as f:
            f.write(in_list)


    @staticmethod
    def __json_2_dict(json_path : Path) -> dict:
        if json_path.exists():
            with open(json_path, 'r') as f:
                buf = f.read()
                buf = re.sub(r'//.*', '', buf)
                buf = re.sub(r'/\*[\s\S]*?\*/', '', buf)
                return json.loads(buf)


    @staticmethod
    def __dict_2_json(in_dict : dict, json_path : Path):
        if not json_path.parent.exists():
            Path.mkdir(json_path.parent, parents=True)
        with open(json_path, 'w') as f:
            json.dump(in_dict, f, indent=4)
            f.write('\n')


    @staticmethod
    def __get_files_list(root_path : Path = '.') -> List[Path]:
        files_list = []
        for root, dirs, files in os.walk(root_path):
            for file in files:
                file_path = Path(os.path.join(root, file))
                files_list.append(file_path)
        return files_list


    @staticmethod
    def __copy(src_path : Path, dst_path : Path):
        with open(src_path, 'r', encoding='utf-8') as sf:
            if not dst_path.parent.exists():
                Path.mkdir(dst_path.parent, parents=True)
            with open(dst_path, 'w', encoding='utf-8') as df:
                print(f'  copy to "{dst_path}"')
                for _, line in enumerate(sf):
                    df.write(line)


    @staticmethod
    def __copy_files_from_template(files_list : List[Path], dst_path : Path):
        for file in files_list:
            BuilderUpd.__copy(BuilderUpd.TEMPLATE_PATH / file, dst_path / file)


    def clean_old_files(self):
        print('Clean old dirs:')
        dir_list = [self.__prj_path / Path(f) for f in ['build_scripts']]
        for d in dir_list:
            if d.exists():
                print(f'  delete "{d}"')
                shutil.rmtree(d)
        print('Clean old files:')
        file_list = [self.__prj_path / Path(f) for f in [   'builder.mk',
                                                            'env_example.mk',
                                                            'global.mk',
                                                            'project_configs/cicd_variables.yml',
                                                            '.vscode/compile_commands.json']]
        for f in file_list:
            if f.exists():
                print(f'  delete {f}')
                os.remove(f)


    def copy_static_files(self):
        static_files = [p.relative_to(BuilderUpd.TEMPLATE_PATH) for p in BuilderUpd.__get_files_list(BuilderUpd.TEMPLATE_PATH / 'build_scripts')]
        static_files += [Path(f) for f in ['makefile', '.gitlab-ci.yml', '.vscode/c_cpp_properties.json']]
        static_files = [p for p in static_files if '__pycache__' not in str(p)]
        print('Copy static files:')
        BuilderUpd.__copy_files_from_template(static_files, self.__prj_path)


    def copy_project_configs(self):
        common_configs = [Path(f) for f in ['project_configs/gitlab-ci-project.yml', 'project_configs/common.mk']]
        print('Copy common configs:')
        BuilderUpd.__copy_files_from_template(common_configs, self.__prj_path)
        bc_release_path = Path('project_configs/build_configs/bc_release.mk')
        bc_old_list : list = [p.relative_to(self.__prj_path) for p in BuilderUpd.__get_files_list(self.__prj_path / bc_release_path.parent)]
        if len(bc_old_list) == 0:
            bc_old_list.append(bc_release_path)
            print('Copy template config:')
        else:
            print('Overwrite exist configs:')
        for path in bc_old_list:
            BuilderUpd.__copy(BuilderUpd.TEMPLATE_PATH / bc_release_path, self.__prj_path / path)


    def copy_example_sources(self):
        shutil.rmtree(self.__prj_path / Path('project_configs'))
        print('Copy example sources:')
        for root, dirs, files in os.walk(BuilderUpd.EXAMPLE_PATH, ):
            for file in files:
                relative_path = (Path(root) / Path(file)).relative_to(BuilderUpd.EXAMPLE_PATH)
                BuilderUpd.__copy(BuilderUpd.EXAMPLE_PATH / relative_path, self.__prj_path / relative_path)


    def update_gitignore(self):
        ignore_old = BuilderUpd.__text_2_list(self.__prj_path / BuilderUpd.GITIGNORE_PATH)
        ignore_new = BuilderUpd.__text_2_list(BuilderUpd.TEMPLATE_PATH / BuilderUpd.GITIGNORE_PATH)
        ignore_res = deepcopy(ignore_new)
        if ignore_old:
            print(f'Use gitignore from "{self.__prj_path / BuilderUpd.GITIGNORE_PATH}"')
            for i in ignore_old:
                if i not in ignore_res:
                    pri = i.replace('\n', '').replace('\r', '')
                    print(f'  user ignore "{pri}"')
                    ignore_res.append(i)
        else:
            print(f'Create clean gitignore from "{BuilderUpd.TEMPLATE_PATH / BuilderUpd.GITIGNORE_PATH}"')
        BuilderUpd.__list_2_text(self.__prj_path / BuilderUpd.GITIGNORE_PATH, ''.join(ignore_res))


    def update_launch(self):
        launch_old : dict = BuilderUpd.__json_2_dict(self.__prj_path / BuilderUpd.LAUNCH_PATH)
        launch_new : dict = BuilderUpd.__json_2_dict(BuilderUpd.TEMPLATE_PATH / BuilderUpd.LAUNCH_PATH)
        launch_res : dict = deepcopy(launch_new)
        if launch_old:
            print(f'Use launch from "{self.__prj_path / BuilderUpd.LAUNCH_PATH}"')
            base_cfg_list : list = []
            for cfg in launch_new['configurations']:
                base_cfg_list.append(cfg['name'])
            for cfg in launch_old['configurations']:
                if cfg['name'] not in base_cfg_list:
                    print(f'  user launch "{cfg["name"]}"')
                    launch_res['configurations'].append(cfg)

            base_ipt_list : list = []
            for ipt in launch_new['inputs']:
                base_ipt_list.append(ipt['id'])
            for ipt in launch_old['inputs']:
                if ipt['id'] not in base_ipt_list:
                    print(f'  user input "{ipt["id"]}"')
                    launch_res['inputs'].append(ipt)
                else:
                    for o in ipt['options']:
                        print(f'  user option "{o}"')
                    launch_res['inputs'][0]['options'] = ipt['options']
        else:
            print(f'Create clean launch from "{BuilderUpd.TEMPLATE_PATH / BuilderUpd.LAUNCH_PATH}"')
            launch_res['inputs'][0]['options'] = ['bc_release/project_name_bc_release.elf']
        BuilderUpd.__dict_2_json(launch_res, self.__prj_path / BuilderUpd.LAUNCH_PATH)


    def update_settings(self):
        settings_old : dict = BuilderUpd.__json_2_dict(self.__prj_path / BuilderUpd.SETTINGS_PATH)
        settings_new : dict = BuilderUpd.__json_2_dict(BuilderUpd.TEMPLATE_PATH / BuilderUpd.SETTINGS_PATH)
        settings_res : dict = deepcopy(settings_new)
        if settings_old:
            print(f'Use settings from "{self.__prj_path / BuilderUpd.SETTINGS_PATH}"')
            for key in settings_old.keys():
                if (settings_res.get(key) != settings_old[key]) and (key != BuilderUpd.VERSION_TAG):
                    print(f'  user setting "{key}": "{settings_old[key]}"')
                    settings_res[key] = settings_old[key]
        else:
            print(f'Create clean settings from "{BuilderUpd.TEMPLATE_PATH / BuilderUpd.SETTINGS_PATH}"')
        BuilderUpd.__dict_2_json(settings_res, self.__prj_path / BuilderUpd.SETTINGS_PATH)


    def update_tasks(self):
        tasks_old : dict = BuilderUpd.__json_2_dict(self.__prj_path / BuilderUpd.TASKS_PATH)
        tasks_new : dict = BuilderUpd.__json_2_dict(BuilderUpd.TEMPLATE_PATH / BuilderUpd.TASKS_PATH)
        tasks_res = deepcopy(tasks_new)
        if tasks_old:
            print(f'Use tasks from "{self.__prj_path / BuilderUpd.TASKS_PATH}"')
            base_task_list : list = []
            for task in tasks_new['tasks']:
                base_task_list.append(task['label'])
            for task in tasks_old['tasks']:
                if task['label'] not in base_task_list:
                    print(f'  user task "{task["label"]}"')
                    tasks_res['tasks'].append(task)

            base_ipt_list : list = []
            for ipt in tasks_new['inputs']:
                base_ipt_list.append(ipt['id'])
            for ipt in tasks_old['inputs']:
                if ipt['id'] not in base_ipt_list:
                    print(f'  user input "{ipt["id"]}"')
                    tasks_res['inputs'].append(ipt)
                else:
                    for o in ipt['options']:
                        print(f'  user option "{o}"')
                    tasks_res['inputs'][0]['options'] = ipt['options']
        else:
            print(f'Create clean tasks from "{BuilderUpd.TEMPLATE_PATH / BuilderUpd.TASKS_PATH}"')
            tasks_res['inputs'][0]['options'] = ['all', 'clean', 'bc_release']
        BuilderUpd.__dict_2_json(tasks_res, self.__prj_path / BuilderUpd.TASKS_PATH)


    def is_old_builder_exist(self) -> bool:
        settings_old : dict = BuilderUpd.__json_2_dict(self.__prj_path / BuilderUpd.SETTINGS_PATH)
        return settings_old != None


    def __get_versions(self) -> Tuple[str, str]:
        settings_old : dict = BuilderUpd.__json_2_dict(self.__prj_path / BuilderUpd.SETTINGS_PATH)
        settings_new : dict = BuilderUpd.__json_2_dict(BuilderUpd.TEMPLATE_PATH / BuilderUpd.SETTINGS_PATH)
        version_old : str = None if settings_old == None else settings_old.get(BuilderUpd.VERSION_TAG)
        version_new : str = settings_new[BuilderUpd.VERSION_TAG]
        return (version_old, version_new)


    def is_force_update_need(self) -> bool:
        version_old, version_new = self.__get_versions()
        if version_old:
            pattern = r'^(\d+)\.(\d+)\.(\d+)$'
            if re.match(pattern, version_old) and re.match(pattern, version_new):
                major_old = int(version_old.split('.')[0])
                major_new = int(version_new.split('.')[0])
                return major_old != major_new
            else:
                raise ValueError('Invalid version format')
        else:
            return True


    def get_builder_version(self) -> str:
        settings: dict = BuilderUpd.__json_2_dict(BuilderUpd.TEMPLATE_PATH / BuilderUpd.SETTINGS_PATH)
        return settings[BuilderUpd.VERSION_TAG]


    def is_versions_match(self) -> bool:
        version_old, version_new = self.__get_versions()
        print(f'Compare project versions "{version_old}" with new "{version_new}"')
        return version_old == version_new
