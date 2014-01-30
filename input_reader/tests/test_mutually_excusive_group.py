from __future__ import unicode_literals
from input_reader import InputReader, ReaderError, SUPPRESS
from pytest import raises, fixture
from re import search

def test_create_mutex_group():
    r = InputReader()
    meg = r.add_mutually_exclusive_group()
    assert meg._default is None
    assert meg._dest is None
    assert not meg._required

def test_mutex_correct_call():
    r = InputReader()
    meg = r.add_mutually_exclusive_group()
    a = meg.add_boolean_key('red')
    assert a.name == 'red'
    assert a._action
    assert not a._default
    meg.add_boolean_key('blue')
    with raises(ReaderError):
        meg.add_boolean_key('red')

def test_mutex_custom_options():
    r = InputReader()
    meg = r.add_mutually_exclusive_group(dest='rainbow', default='cloudy',
                                         required=True)
    assert meg._dest == 'rainbow'
    assert meg._default == 'cloudy'
    assert meg._required
    with raises(ValueError) as e:
        meg = r.add_mutually_exclusive_group(dest=23)
    assert 'dest must be a str, given' in str(e.value)
    with raises(ValueError) as e:
        meg = r.add_mutually_exclusive_group(required='True')
    assert 'required value must be a bool, given' in str(e.value)

def test_mutex_custom_options_str():
    r = InputReader()
    meg = r.add_mutually_exclusive_group(dest=str('rainbow'),
                                         default=str('cloudy'))
    assert meg._dest == 'rainbow'
    assert meg._default == 'cloudy'

def test_read_mutex():
    r = InputReader()
    meg = r.add_mutually_exclusive_group()
    meg.add_boolean_key('red')
    meg.add_boolean_key('blue')
    meg.add_boolean_key('green')

    inp = r.read_input(['red'])
    assert inp.red
    assert not inp.blue
    assert not inp.green

    with raises(ReaderError) as e:
        inp = r.read_input(['red', 'blue'])
    assert search(r'Only one of .* may be included', str(e.value))

    # Unfortunately we cannot detect duplicate groups in different meg's
    meg2 = r.add_mutually_exclusive_group()
    meg2.add_boolean_key('red')

def test_read_mutex_set_default():
    r = InputReader()
    meg = r.add_mutually_exclusive_group(default='water')
    meg.add_boolean_key('red')
    meg.add_boolean_key('blue')
    meg.add_boolean_key('green')
    inp = r.read_input(['red'])
    assert inp.red
    assert inp.blue == 'water'
    assert inp.green == 'water'
    inp = r.read_input([])
    assert inp.red == 'water'
    assert inp.blue == 'water'
    assert inp.green == 'water'

    # Using default=SUPPRESS was the intended use case of default for meg's
    meg = r.add_mutually_exclusive_group(default=SUPPRESS)
    meg.add_boolean_key('pink')
    meg.add_boolean_key('gray')
    meg.add_boolean_key('cyan')
    inp = r.read_input(['pink'])
    assert inp.pink
    assert 'gray' not in inp
    assert 'cyan' not in inp

def test_read_mutex_set_dest():
    r = InputReader()
    # This is the best way to use meg's
    meg = r.add_mutually_exclusive_group(dest='color')
    meg.add_boolean_key('red', action='red')
    meg.add_boolean_key('blue', action='blue')
    meg.add_boolean_key('green', action='green')
    meg.add_boolean_key('pink', action='pink')
    meg.add_boolean_key('gray', action='pink')
    meg.add_boolean_key('cyan', action='cyan')
    r.add_boolean_key('white')
    inp = r.read_input(['cyan', 'white'])
    assert inp.color == 'cyan'
    assert inp.white
    assert 'red' not in inp
    assert 'blue' not in inp
    assert 'green' not in inp
    assert 'pink' not in inp
    assert 'gray' not in inp
    assert 'cyan' not in inp

def test_read_mutex_set_required():
    r = InputReader()
    meg = r.add_mutually_exclusive_group(required=True)
    meg.add_boolean_key('red')
    meg.add_boolean_key('blue')
    meg.add_boolean_key('green')

    inp = r.read_input(['blue'])
    assert inp.blue
    assert not inp.red
    assert not inp.green

    with raises(ReaderError) as e:
        inp = r.read_input([])
    assert search(r'One and only one of .* must be included', str(e.value))

def test_read_mutex_set_dest_set_required():
    r = InputReader()
    meg = r.add_mutually_exclusive_group(required=True, dest='color')
    meg.add_boolean_key('red')
    meg.add_boolean_key('blue')
    meg.add_boolean_key('green')
    r.add_boolean_key('cyan')

    with raises(ReaderError) as e:
        inp = r.read_input(['cyan'])
    assert search(r'One and only one of .* must be included', str(e.value))
