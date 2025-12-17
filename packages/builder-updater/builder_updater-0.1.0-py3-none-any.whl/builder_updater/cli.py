import os
import argparse
from pathlib import Path

from .builder_info import show_projects_info
from .builder_updater import BuilderUpd
from builder_updater import __version__


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--path', help='Project path', action='store', default=Path(os.getcwd()))
    parser.add_argument('-f', '--force', help='Force update', action='store_true', default=False)
    parser.add_argument('-c', '--clean', help='Clean old files', action='store_true', default=False)
    parser.add_argument('-e', '--example', help='Copy example sources', action='store_true', default=False)
    parser.add_argument('-i', '--info', help='Show projects info', action='store_true', default=False)
    parser.add_argument('--version', help='Show package version', action='store_true', default=False)
    parser.add_argument('--builder-version', help='Show builder version', action='store_true', default=False)
    args = parser.parse_args()

    try:
        if args.version:
            print(f'C/C++ project builder updater {__version__}')
            return

        if args.info:
            show_projects_info(args.path)
            return

        bu = BuilderUpd(args.path)

        if args.builder_version:
            print(f'builder version: {bu.get_builder_version()}')
            return

        if not args.force:
            if bu.is_versions_match():
                print('Update aborted - versions match, add "--force" flag.')
                exit(1)
            if bu.is_force_update_need():
                print('Update aborted - force is required, add "--force" flag.')
                exit(1)

        if args.clean:
            bu.clean_old_files()

        bu.copy_static_files()
        bu.update_gitignore()
        bu.update_launch()
        bu.update_settings()
        bu.update_tasks()

        if args.force:
            bu.copy_project_configs()

        if args.example:
            bu.copy_example_sources()

    except KeyboardInterrupt:
        print(f'Exit by user')

    except ValueError as e:
        print(f'Value error: {e}')

    except RuntimeError as e:
        print(f'Runtime error: {e}')

    finally:
        pass
