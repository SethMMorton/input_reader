from __future__ import print_function, unicode_literals
from input_reader import abs_file_path, file_safety_check, range_check
from pytest import raises
from os.path import join, abspath
from os import environ, curdir, remove
from sys import platform

def test_abs_file_path():
    assert abs_file_path('sample') == join(abspath(curdir), 'sample')
    if platform == 'win32':
        assert abs_file_path(join('~', 'sample')) == \
                    join(environ['HOMEDRIVE'], environ['HOMEPATH'], 'sample')
    else:
        assert abs_file_path(join('~', 'sample')) == \
                    join(environ['HOME'], 'sample')
    environ['__TESTING__'] = 'SILLY'
    assert abs_file_path(join(environ['__TESTING__'], 'sample')) == \
                    join(abspath(curdir), 'SILLY', 'sample')
    assert abs_file_path(join(environ['HOME'], 'sample'), env=True) == \
                    join('$HOME', 'sample')

def test_file_safety_check():
    with open('TEMP', 'w') as fl:
        print('test', file=fl)
    file_safety_check('TEMP')
    remove('TEMP')
    with raises(IOError):
        file_safety_check('TEMP')

def test_range_check():
    assert range_check(1, 10) == (1, 10)
    assert range_check(1.0, 10.0) == (1.0, 10.0)
    assert range_check(1.0, 10.0, asint=True) == (1, 10)
    assert range_check(1, 10, expand=True) == (1, 2, 3, 4, 5, 6, 7, 8, 9, 10)
    assert range_check(1.5, 10) == (1.5, 10.0)
    with raises(ValueError):
        range_check(10, 1)
    with raises(ValueError):
        range_check(10, 10)
