
import subprocess
import re

from typing import List
from os import walk as os_walk
from pathlib import Path


def get_git_projects(path) -> List[Path]:
    res = []
    for root, dirs, files in os_walk(path):
        for df in dirs + files:
            if '.git' == df:
                abs_path = Path(root)#.resolve()
                res.append(abs_path)
    res.sort()
    return res


def show_info(info, first_max_indent):
    for i, el in enumerate(info):
        sep_size = first_max_indent if i == 0 else (8 if i < 4 else 20)
        print(f'{el:<{sep_size}}', end=' ')
    print('')


def show_projects_info(path):
    projects = get_git_projects(path)
    if projects:
        max_indent = max(16, max(len(p.as_posix()) for p in projects))
    else:
        raise RuntimeError('Can\'t find any projects')

    show_info(['Project path', 'Status', 'Remote', 'Version', 'Branch', 'Origin'], max_indent)

    for prj in projects:
        status_res = subprocess.run(['git', '-C', str(prj), 'status'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        remote_res = subprocess.run(['git', '-C', str(prj), 'remote', '-v'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)

        if status_res.returncode != 0:
            raise RuntimeError('failed to get status')

        info = []
        info.append(prj.as_posix())
        info.append('clean' if ('working tree clean' in status_res.stdout) else 'dirty')
        info.append('sync' if ('is up to date with' in status_res.stdout) else 'diff')

        builder_version = 'none'
        is_builder = 'builder_updater' in str(prj)
        settings_json = prj / Path('builder_updater/assets/template/.vscode/settings.json' if is_builder else '.vscode/settings.json')

        if settings_json.exists():
            builder_version = 'none'
            with open(settings_json, 'r', encoding='utf-8') as f:
                ver_match = re.search(r'"builderUpd.version": (\S*)', f.read())
                if ver_match:
                    builder_version = ver_match.group(1).replace('"', '')
        info.append(builder_version)

        branch_match = re.search(r'On branch (\S*)', status_res.stdout)
        if branch_match and branch_match.group(1):
            info.append(branch_match.group(1))
        else:
            info.append('none')

        remote_match = re.search(r'.*?(\S*)\s*\(fetch\)', remote_res.stdout)
        if remote_match and remote_match.group(1):
            info.append(remote_match.group(1))
        else:
            info.append('none')

        show_info(info, max_indent)
