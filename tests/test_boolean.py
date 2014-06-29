from __future__ import unicode_literals
from input_reader import InputReader, ReaderError, SUPPRESS
from pytest import raises, fixture
from re import search
from textwrap import dedent

@fixture
def setup():
    s1 = dedent("""\
              blue
              red # Comment
              """).split('\n')
    s2 = dedent(str("""\
                    blue
                    red color # This is illegal
                    """)).split('\n')
    return s1, s2, InputReader()

def test_boolean_missing_keyname(setup):
    s1, s2, r = setup
    with raises(TypeError):
        r.add_boolean_key()
    with raises(TypeError):
        r.add_boolean_key(action=True)

def test_boolean_correct_call(setup):
    s1, s2, r = setup
    a = r.add_boolean_key('red')
    assert a.name == 'red'
    assert a._action
    b = r.add_boolean_key('blue', action=False)
    assert b.name == 'blue'
    assert not b._action
    def fun(x):
        return x*x
    c = r.add_boolean_key(str('green'), action=fun)
    assert c._action is fun

def test_boolean_name_definition(setup):
    s1, s2, r = setup
    with raises(ValueError) as e:
        r.add_boolean_key(23)
    assert 'keyname must be str' in str(e.value)
    with raises(ValueError) as e:
        r.add_boolean_key('hello goodbye')
    assert 'String cannot contain spaces' in str(e.value)
    with raises(ValueError) as e:
        r.add_boolean_key('')
    assert 'String cannot be of zero length' in str(e.value)
    with raises(ValueError) as e:
        r.add_boolean_key(str('hello goodbye'))
    assert 'String cannot contain spaces' in str(e.value)

def test_boolean_repeat_in_definition(setup):
    # You cannot repeat keys
    s1, s2, r = setup
    r.add_boolean_key('red')
    with raises(ReaderError) as e:
        r.add_boolean_key('red')
    regex = r'The keyname "\w+" has been defined twice'
    assert search(regex, str(e.value))

def test_boolean_read_arguments(setup):
    # Booleans cannot have arguments
    s1, s2, r = setup
    r.add_boolean_key('blue')
    r.add_boolean_key('red')
    with raises(ReaderError) as e:
        inp = r.read_input(s2)
    regex = 'The boolean "\w+" was given arguments, this is illegal'
    assert search(regex, str(e.value))

def test_boolean_read_actions(setup):
    s1, s2, r = setup
    r.add_boolean_key('blue', action=['something', 'odd'])
    # An action can be a function, too!
    r.add_boolean_key('red', 
                      action=lambda x: "hello" if x else "goodbye")
    inp = r.read_input(s1)
    assert inp.blue == ['something', 'odd']
    assert inp.red(True) == "hello"
    assert inp.red(0) == "goodbye"
