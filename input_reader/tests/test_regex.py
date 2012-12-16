from input_reader import InputReader, ReaderError, SUPPRESS
from pytest import raises, fixture
from re import search
import re

def test_regex_missing_handle():
    r = InputReader()
    with raises(TypeError):
        r.add_regex_line()
    with raises(TypeError):
        r.add_regex_line('red')

def test_regex_correct_call():
    r = InputReader()
    a = r.add_regex_line('red', r'funny\d+dog')
    assert a.name == 'red'
    assert a._regex.pattern == r'funny\d+dog'
    assert not a._case
    regex = re.compile(r'funny\d+dog')
    b = r.add_regex_line('blue', regex)
    assert b.name == 'blue'
    assert b._regex == regex
    assert not b._case

def test_regex_case_definition():
    r = InputReader()
    a = r.add_regex_line('red', r'funny\d+DOG')
    assert a.name == 'red'
    assert a._regex.pattern == r'funny\d+DOG'
    assert a._regex.flags == re.IGNORECASE
    regex = re.compile(r'funny\d+dog', re.IGNORECASE)
    b = r.add_regex_line('blue', regex)
    assert b.name == 'blue'
    assert b._regex == regex
    c = r.add_regex_line('green', r'funny\d+DOG', case=True)
    assert c.name == 'green'
    assert c._regex.pattern == r'funny\d+DOG'
    assert c._regex.flags != re.IGNORECASE
    regex = re.compile(r'funny\d+dog', re.IGNORECASE)
    # Case is ignored if a regex flag is given
    d = r.add_regex_line('gray', regex, case=True)
    assert d.name == 'gray'
    assert d._regex == regex

def test_regex_handle_definition():
    r = InputReader()
    with raises(ValueError) as e:
        r.add_regex_line(23, r'test')
    assert 'handle must be str' in str(e.value)
    with raises(ValueError) as e:
        r.add_regex_line('hello goodbye', r'test')
    assert 'String cannot contain spaces' in str(e.value)
    with raises(ValueError) as e:
        r.add_regex_line('', r'test')
    assert 'String cannot be of zero length' in str(e.value)

def test_regex_repeat_in_definition():
    # You cannot repeat keys
    r = InputReader()
    r.add_regex_line('red', r'test')
    with raises(ReaderError) as e:
        r.add_regex_line('red', r'tax')
    regex = r'The key "\w+" has been defined twice'
    assert search(regex, str(e.value))

def test_regex_read():
    r = InputReader()
    # Remember it's case-insensitive
    r.add_regex_line('red', r'funny(\d+)DOG\s*(kitty)?')
    inp = r.read_input(['funny14dog'])
    assert inp.red.group(0) == 'funny14dog'
    assert inp.red.group(1) == '14'
    inp = r.read_input(['funny12DOG kitty'])
    # Regex won't lowercase for you
    assert inp.red.group(0) == 'funny12DOG kitty'
    assert inp.red.group(1) == '12'
    assert inp.red.group(2) == 'kitty'
    r.add_regex_line('blue', r'(SILLY|ODD)\s*(goose|duck)', case=True)
    inp = r.read_input(['SILLY goose'])
    assert inp.blue.group(0) == 'SILLY goose'
    inp = r.read_input(['ODD duck'])
    assert inp.blue.group(0) == 'ODD duck'
