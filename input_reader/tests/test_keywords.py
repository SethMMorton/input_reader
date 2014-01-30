from __future__ import unicode_literals
from input_reader import InputReader, ReaderError, SUPPRESS
from pytest import raises, fixture
from re import search
from textwrap import dedent

@fixture
def setup():
    r = InputReader()
    s1 = dedent("""\
                blue
                red
                """).split('\n')
    s2 = dedent("""\
                blue
                red
                blue
                """).split('\n')
    return r, s1, s2

def test_suppress_at_class_level():
    ir = InputReader(default=SUPPRESS)
    assert ir._default is SUPPRESS
    b = ir.add_boolean_key('RED')
    assert b._default is SUPPRESS

def test_string_default_at_class_level():
    ir = InputReader(default='roses')
    assert ir._default == 'roses'
    b = ir.add_boolean_key('RED')
    assert b._default == 'roses'

def test_case_sensitivity_at_class_level():
    ir = InputReader(case=True)
    assert ir._case
    l = ir.add_line_key('RED')
    assert l._case
    with raises(ValueError):
        ir2 = InputReader(case='True')

def test_use_default_values(setup):
    r, s1, s2 = setup
    b = r.add_boolean_key('red')
    assert not b._required
    assert b._default is None
    assert b._dest is None
    assert b._depends is None
    assert not b._repeat

def test_dont_use_default_values(setup):
    r, s1, s2 = setup
    b = r.add_boolean_key('red', True,
                                    required=False,
                                    default=None,
                                    dest=None,
                                    depends=None,
                                    repeat=False)
    assert not b._required
    assert b._default is None
    assert b._dest is None
    assert b._depends is None
    assert not b._repeat

def test_custom_values(setup):
    r, s1, s2 = setup
    b = r.add_boolean_key('red', True,
                                    required=True,
                                    default='BANANA',
                                    dest='fruit',
                                    depends='something',
                                    repeat=True)
    assert b._required
    assert b._default == 'BANANA'
    assert b._dest == 'fruit'
    assert b._depends == 'something'
    assert b._repeat

def test_custom_values_str(setup):
    r, s1, s2 = setup
    b = r.add_boolean_key('red', True,
                                 required=True,
                                 default=str('BANANA'),
                                 dest=str('fruit'),
                                 depends=str('something'),
                                 repeat=True)
    assert b._required
    assert b._default == 'BANANA'
    assert b._dest == 'fruit'
    assert b._depends == 'something'
    assert b._repeat

def test_incorrect_options(setup):
    # The keyword 'wrong' doesn't exist
    r, s1, s2 = setup
    with raises(TypeError):
        r.add_boolean_key('RED', wrong=True)
    # Dest requires a string
    with raises(ValueError):
        r.add_boolean_key('RED', dest=14)
    # Required requires a boolean
    with raises(ValueError):
        r.add_boolean_key('RED', required=None)
    # Repeat requires a boolean
    with raises(ValueError):
        r.add_boolean_key('RED', repeat=None)

def test_read_custom_default_values(setup):
    # Test when individual keys define their own default
    r, s1, s2 = setup
    r.add_boolean_key('blue')
    r.add_boolean_key('red')
    r.add_boolean_key('green')
    r.add_boolean_key('yellow', default=False)
    r.add_boolean_key('white', default=SUPPRESS)
    inp = r.read_input(s1)
    assert inp.blue
    assert inp.red
    assert inp.green is None
    assert not inp.yellow
    assert 'white' not in inp

def test_read_required_works_correctly(setup):
    # A keyword that is not required does not appear... OK
    r, s1, s2 = setup
    r.add_boolean_key('blue', required=False)
    r.add_boolean_key('red', required=True)
    r.add_boolean_key('green', required=False)
    inp = r.read_input(s1)
    assert inp.blue
    assert inp.red
    assert inp.green is None

def test_read_required_fails_when_incorrect(setup):
    # A keyword that is required does not appear... NOT OK
    r, s1, s2 = setup
    r.add_boolean_key('blue', required=True)
    r.add_boolean_key('red', required=False)
    r.add_boolean_key('green', required=True)
    with raises(ReaderError):
        inp = r.read_input(s1)

def test_read_keywords_cannot_repeat(setup):
    # A keyword appears twice that shouldn't repeat... NOT OK
    r, s1, s2 = setup
    r.add_boolean_key('blue', repeat=False)
    r.add_boolean_key('red', repeat=False)
    with raises(ReaderError) as e:
        inp = r.read_input(s2)
    assert 'appears twice' in str(e.value)

def test_read_keywords_can_repeat(setup):
    # A keyword appears twice that can repeat... OK
    r, s1, s2 = setup
    r.add_boolean_key('blue', repeat=True)
    r.add_boolean_key('red', repeat=True)
    inp = r.read_input(s2)
    assert inp.red == (True,)
    assert inp.blue == (True,  True)

def test_read_destination_different_from_given_name(setup):
    # Keys are sent into an alternate destination
    r, s1, s2 = setup
    r.add_boolean_key('blue', dest='berries')
    r.add_boolean_key('red', dest='apples')
    inp = r.read_input(s1)
    assert inp.berries
    assert inp.apples

def test_read_destination_is_same_and_done_incorrectly(setup):
    # Keys are sent into the same alternate destination
    r, s1, s2 = setup
    r.add_boolean_key('blue', action='blue', dest='colors')
    r.add_boolean_key('red', action='red', dest='colors')
    # They are both sent to other dest, repeat is needed
    with raises(ReaderError) as e:
        inp = r.read_input(s1)
    assert 'appears twice' in str(e.value)

def test_read_destination_is_same_and_done_correctly(setup):
    # Try the above with repeat=True
    r, s1, s2 = setup
    r.add_boolean_key('blue', action='blue', dest='colors',
                      repeat=True)
    r.add_boolean_key('red', action='red', dest='colors',
                      repeat=True)
    inp = r.read_input(s1)
    # Set is used below so that order doesn't matter
    assert set(inp.colors) == set(('blue', 'red'))

def test_read_destination_required(setup):
    r, s1, s2 = setup
    r.add_boolean_key('blue', action='blue', dest='rcolor', required=True)
    r.add_boolean_key('red', action='red', dest='bcolor', required=True)
    r.add_boolean_key('green', action='green', dest='gcolor', required=True)
    with raises(ReaderError) as e:
        inp = r.read_input(s1)
    assert search('The key "\w+" is required but not found', str(e.value))

def test_read_depends_dependee_present(setup):
    # Red depends on blue
    r, s1, s2 = setup
    r.add_boolean_key('blue')
    r.add_boolean_key('red', depends='blue')
    inp = r.read_input(s1)
    assert inp.blue
    assert inp.red

def test_read_depends_dependee_missing(setup):
    # Red depends on green, but green isn't present
    r, s1, s2 = setup
    r.add_boolean_key('blue')
    r.add_boolean_key('red', depends='green')
    with raises(ReaderError) as e:
        inp = r.read_input(s1)
    regex = r'The key "\w+" requires that "\w+" is also present'
    assert search(regex, str(e.value))
