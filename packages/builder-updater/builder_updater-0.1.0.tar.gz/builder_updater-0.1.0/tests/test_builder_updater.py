import pytest
import os
import subprocess
from pathlib import Path
from unittest.mock import patch
from builder_updater.cli import main


def test_cli_help():
    print()
    with patch('sys.argv', ['builder_updater', '-h']):
        with pytest.raises(SystemExit):
            main()


def test_cli_version():
    print()
    with patch('sys.argv', ['builder_updater', '--version']):
        main()


def test_cli_builder_version():
    print()
    with patch('sys.argv', ['builder_updater', '--builder-version']):
        main()


def test_cli_info():
    print()
    with patch('sys.argv', ['builder_updater', '-p', '.', '-i']):
        main()


def test_template_abort(tmp_path):
    print()
    with patch('sys.argv', ['builder_updater', '-p', str(tmp_path)]):
        with pytest.raises(SystemExit):
            main()


def test_template_create(tmp_path):
    print()
    with patch('sys.argv', ['builder_updater', '-p', str(tmp_path), '-f']):
        main()


def test_example_build(tmp_path):
    print()
    with patch('sys.argv', ['builder_updater', '-p', str(tmp_path), '-f', '-e']):
        main()
    assert subprocess.run(['make', '-C', str(tmp_path)]).returncode == 0


def test_example_run(tmp_path):
    print()
    with patch('sys.argv', ['builder_updater', '-p', str(tmp_path), '-f', '-e']):
        main()
    assert subprocess.run(['make', '-C', str(tmp_path)]).returncode == 0

    is_execute_any = False

    for root, dirs, files in os.walk(tmp_path / Path('output'), ):
        for file in files:
            suffix = Path(file).suffix.lower()
            if (suffix == '.exe' or suffix == '') and 'example_project_' in file:
                print(Path(root) / Path(file))
                assert subprocess.run([str(Path(root) / Path(file))]).returncode == 0
                is_execute_any = True

    assert is_execute_any
