from __future__ import unicode_literals
from input_reader import InputReader, ReaderError
from pytest import raises

def test_empty_costructor():
    ir = InputReader()
    assert ir.name == 'main'
    assert ir._comment == ['#']
    assert not ir._case
    assert not ir._ignoreunknown
    assert ir._default is None

def test_set_constructor_using_defaults():
    ir = InputReader(comment=['#'], 
                     case=False, 
                     ignoreunknown=False,
                     default=None)
    assert ir.name == 'main'
    assert ir._comment == ['#']
    assert not ir._case
    assert not ir._ignoreunknown
    assert ir._default is None

def test_set_constructor():
    ir = InputReader(comment='//', 
                     case=True, 
                     ignoreunknown=True,
                     default=False)
    assert ir.name == 'main'
    assert ir._comment == ['//']
    assert ir._case
    assert ir._ignoreunknown
    assert not ir._default

def test_incorrect_constructor_options():
    # 'wrong' keyword does not exist
    with raises(TypeError):
        InputReader(wrong=True)
    # Case requires a bool
    with raises(ValueError):
        InputReader(case='spam')
    # Ignoreunknown requires a bool
    with raises(ValueError):
        InputReader(ignoreunknown=15.8)
    # Comment requires a strings or list of strings
    with raises(ValueError):
        InputReader(comment=14.5)
    with raises(ValueError):
        InputReader(comment=[14.5])
    with raises(ValueError):
        InputReader(comment=['#', 14.5])
