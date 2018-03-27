from expects import expect, equal

import pep8
import os

# TODO fix import

# Just add here the local path of the excluded file (example: 'test/unit/test_to_ignore.py')
EXCLUDED_FILES = []

# Add the local directories you wish to lint (example: 'src', 'config, 'test', etc)
CHECKED_DIRS = ['twoboards', 'test']


def root_path():
    this_path = os.path.normpath(os.path.dirname(__file__))
    return os.path.abspath(os.path.join(this_path, os.pardir, os.pardir))


def get_excluded_files():
    result = []
    for path in EXCLUDED_FILES:
        result.append(os.path.join(root_path(), path))
    return result


def get_config_file():
    return os.path.join(root_path(), 'linter.cfg')


with description('Test Code Conformation'):
    with it('conforms PEP8'):
        pep8style = pep8.StyleGuide(config_file=get_config_file(), exclude=get_excluded_files())
        result = pep8style.check_files(CHECKED_DIRS)
        expect(result.total_errors).to(equal(0))
