# Copyright (c) 2020 IBM Corp. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Tests for trestle import command."""
import json
import os
import pathlib
import sys
import tempfile
from unittest.mock import patch

from tests import test_utils

import trestle.core.err as err
from trestle.cli import Trestle

subcommand_list = [
    'catalog',
    'profile',
    'target-definition',
    'component-definition',
    'system-security-plan',
    'assessment-plan',
    'assessment-results',
    'plan-of-action-and-milestones'
]


def test_import_cmd(tmp_dir: pathlib.Path) -> None:
    """Happy path test at the cli level."""
    # Input file, catalog:
    catalog_file_path = pathlib.Path.joinpath(test_utils.JSON_TEST_DATA_PATH.absolute(), 'minimal_catalog.json')
    # Input file, profile:
    profile_file_path = pathlib.Path.joinpath(test_utils.JSON_TEST_DATA_PATH.absolute(), 'good_profile.json')
    # Input file, target:
    target_file_path = pathlib.Path.joinpath(test_utils.JSON_TEST_DATA_PATH.absolute(), 'sample-target-definition.json')
    # Temporary directory for trestle init to trestle import into
    os.chdir(tmp_dir.absolute())
    init_args = ['trestle', 'init']
    with patch.object(sys, 'argv', init_args):
        # Init tmp_dir
        Trestle().run()
        # Test
        test_args = ['trestle', 'import', '-f', str(catalog_file_path), '-o', 'imported']
        with patch.object(sys, 'argv', test_args):
            rc = Trestle().run()
            assert rc == 0
        # Import going to the same output should fail due to output file clash
        test_args = ['trestle', 'import', '-f', str(catalog_file_path), '-o', 'imported']
        with patch.object(sys, 'argv', test_args):
            rc = Trestle().run()
            assert rc == 1
        # Test
        test_args = ['trestle', 'import', '-f', str(profile_file_path), '-o', 'imported']
        with patch.object(sys, 'argv', test_args):
            rc = Trestle().run()
            assert rc == 0
        # Test
        test_args = ['trestle', 'import', '-f', str(target_file_path), '-o', 'imported']
        with patch.object(sys, 'argv', test_args):
            rc = Trestle().run()
            assert rc == 0


def test_import_missing_input(tmp_trestle_dir: pathlib.Path) -> None:
    """Test for missing input argument."""
    # This can't be unit tested here as cli implements checks for required arguments like the input file.
    pass


def test_import_missing_input_file(tmp_trestle_dir: pathlib.Path) -> None:
    """Test for missing input file."""
    # Test
    test_args = ['trestle', 'import', '-f', 'random_named_file.json', '-o', 'catalog']
    with patch.object(sys, 'argv', test_args):
        try:
            Trestle().run()
        except Exception:
            assert True
        else:
            AssertionError()


def test_import_bad_working_directory(tmp_dir: pathlib.Path) -> None:
    """Test for working directory that is not a trestle initialized directory."""
    # DONE
    # Input file, catalog:
    catalog_file_path = pathlib.Path.joinpath(test_utils.JSON_TEST_DATA_PATH.absolute(), 'minimal_catalog.json')
    test_args = f'trestle import -f {str(catalog_file_path)} -o catalog'.split()
    with patch('trestle.utils.fs.get_trestle_project_root') as get_trestle_project_root_mock:
        get_trestle_project_root_mock.return_value = None
        with patch.object(sys, 'argv', test_args):
            try:
                Trestle().run()
            except Exception:
                assert True
            else:
                AssertionError()


def test_import_from_inside_trestle_project_is_bad(tmp_trestle_dir: pathlib.Path) -> None:
    """Test for attempting import from a trestle project directory."""
    # DONE
    sample_file = open('infile.json', 'w+')
    sample_file.write('{}')
    sample_file.close()
    test_args = 'trestle import -f infile.json -o catalog'.split()
    with patch.object(sys, 'argv', test_args):
        try:
            Trestle().run()
        except Exception:
            assert True
        else:
            AssertionError()


def test_import_bad_input_extension(tmp_trestle_dir: pathlib.Path) -> None:
    """Test for bad input extension."""
    # DONE
    # Some input file with bad extension.
    temp_file = tempfile.NamedTemporaryFile(suffix='.txt')
    test_args = f'trestle import -f {temp_file.name} -o catalog'.split()
    with patch.object(sys, 'argv', test_args):
        try:
            Trestle().run()
        except Exception:
            assert True
        else:
            AssertionError()


def test_import_success(tmp_dir):
    """Test for success across multiple models."""
    pass


def test_import_load_file_failure(tmp_dir):
    """Test model failures throw errors and exit badly."""
    # DONE
    # Input file, catalog:
    catalog_file_path = pathlib.Path.joinpath(test_utils.JSON_TEST_DATA_PATH.absolute(), 'bad_simple.json')
    # Temporary directory for trestle init to trestle import into
    os.chdir(tmp_dir.absolute())
    init_args = ['trestle', 'init']
    with patch.object(sys, 'argv', init_args):
        # Init tmp_dir
        Trestle().run()
        # Test
        test_args = ['trestle', 'import', '-f', str(catalog_file_path), '-o', 'imported']
        with patch('trestle.utils.fs.load_file') as load_file_mock:
            load_file_mock.side_effect = err.TrestleError('stuff')
            with patch.object(sys, 'argv', test_args):
                rc = Trestle().run()
                assert rc == 1


def test_import_root_key_failure(tmp_trestle_dir):
    """Test root key is found."""
    # DONE
    sample_file = tempfile.NamedTemporaryFile(suffix='.json')
    # Using dict to json to bytes, to keep flake8 quiet.
    sample_data = {'id': '0000', 'title': 'nothing'}
    sample_file.write(json.dumps(sample_data).encode('utf8'))
    # This seek is necessary to flush to file.
    sample_file.seek(0)
    test_args = f'trestle import -f {sample_file.name} -o catalog'.split()
    with patch.object(sys, 'argv', test_args):
        try:
            Trestle().run()
        except Exception:
            assert True
        else:
            AssertionError()


def test_import_failure_parse_file(tmp_trestle_dir):
    """Test model failures throw errors and exit badly."""
    # DONE
    sample_file = tempfile.NamedTemporaryFile(suffix='.json')
    # Using dict to json to bytes, to keep flake8 quiet.
    sample_data = {'id': '0000'}
    sample_file.write(json.dumps(sample_data).encode('utf8'))
    # This seek is necessary to flush to file.
    sample_file.seek(0)
    test_args = f'trestle import -f {sample_file.name} -o catalog'.split()
    with patch('trestle.core.parser.parse_file') as parse_file_mock:
        parse_file_mock.side_effect = err.TrestleError('stuff')
        with patch.object(sys, 'argv', test_args):
            try:
                Trestle().run()
            except Exception:
                assert True
            else:
                AssertionError()


def test_failure_reference_inside_trestle_project(tmp_dir):
    """Ensure failure if a reference pulls in an object which is inside the current context."""
    pass


def test_failure_duplicate_output_key(tmp_dir):
    """Fail if output name and type is duplicated."""
    pass
