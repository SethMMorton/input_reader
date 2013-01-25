from input_reader import InputReader, ReaderError, SUPPRESS, Namespace
from pytest import raises, fixture
from re import search

def test_block_missing_keyname():
    r = InputReader()
    with raises(TypeError):
        r.add_block_key()
    with raises(TypeError):
        r.add_block_key(end='subend')
    with raises(TypeError):
        r.add_block_key(ignoreunknown=True)
    with raises(TypeError):
        r.add_block_key(case=False)

def test_unterminated_block():
    r = InputReader(ignoreunknown=True)
    a = r.add_block_key('red')
    a.add_boolean_key('rose')
    with raises(ReaderError) as e:
        r.read_input(['red', 'rose'])
    assert search('Unterminated block', str(e.value))

def test_block_correct_call():
    r = InputReader()
    a = r.add_block_key('red')
    assert a.name == 'red'
    assert a._end == 'end'
    assert not a._case
    assert not a._ignoreunknown

def test_block_name_definition():
    r = InputReader()
    with raises(ValueError) as e:
        r.add_block_key(23)
    assert 'keyname must be str' in str(e.value)
    with raises(ValueError) as e:
        r.add_block_key('hello goodbye')
    assert 'String cannot contain spaces' in str(e.value)
    with raises(ValueError) as e:
        r.add_block_key('')
    assert 'String cannot be of zero length' in str(e.value)

def test_block_repeat_in_definition():
    # You cannot repeat keys
    r = InputReader()
    r.add_block_key('red')
    with raises(ReaderError) as e:
        r.add_block_key('red')
    assert search(r'The keyname "\w+" has been defined twice', str(e.value))

def test_block_end_definition():
    r = InputReader()
    a = r.add_block_key('red', end='subend')
    assert a._end == 'subend'
    with raises(ValueError) as e:
        r.add_block_key('blue', end=23)
    assert 'end must be str' in  str(e.value)
    
def test_block_case_definition():
    r = InputReader()
    a = r.add_block_key('red', case=True)
    assert a._case
    with raises(ValueError) as e:
        r.add_block_key('blue', case='True')
    assert 'case must be bool' in str(e.value)

def test_block_ignoreunknown_definition():
    r = InputReader()
    a = r.add_block_key('red', ignoreunknown=True)
    assert a._ignoreunknown
    with raises(ValueError) as e:
        b = r.add_block_key('blue', ignoreunknown='True')
    assert 'ignoreunknown must be bool' in str(e.value)

def test_block_read_using_defaults():
    r = InputReader()
    a = r.add_block_key('blue')
    inp = r.read_input(['blue', 'end'])
    assert inp.blue == Namespace()
    b = r.add_block_key('red')
    b.add_boolean_key('rose', default=False)
    b.add_boolean_key('rider', default=False)
    inp = r.read_input(['red', 'rose', 'end'])
    assert inp.red.rose
    assert not inp.red.rider
    inp = r.read_input(['red', 'end'])
    assert not inp.red.rose
    assert not inp.red.rider
    c = r.add_block_key('cyan')
    with raises(ReaderError) as e:
        inp = r.read_input(['cyan word', 'end'])
    assert search(r'The block "\w+" was given arguments, this is illegal',
                  str(e.value))

def test_block_read_end():
    r = InputReader()
    a = r.add_block_key('red', end='subend')
    a.add_boolean_key('rose', default=False)
    inp = r.read_input(['red', 'rose', 'subend'])
    assert inp.red.rose
    inp = r.read_input(['red', 'subend'])
    assert not inp.red.rose

def test_block_read_case_sensitive():
    r = InputReader()
    a = r.add_block_key('red', case=True, end='END')
    a.add_boolean_key('ROSE')
    inp = r.read_input(['RED', 'ROSE', 'END'])
    assert 'rose' not in inp.red
    assert inp.red.ROSE
    b = r.add_block_key('pink', case=False)
    b.add_boolean_key('ROSE')
    inp = r.read_input(['PINK', 'ROSE', 'END'])
    assert 'ROSE' not in inp.pink
    assert inp.pink.rose
    
def test_block_read_ignoreunknown():
    r = InputReader()
    a = r.add_block_key('red', ignoreunknown=False)
    a.add_boolean_key('rose')
    with raises(ReaderError) as e:
        inp = r.read_input(['red', 'rose', 'rider', 'end'])
    assert 'Unrecognized key' in str(e.value)
    b = r.add_block_key('blue', ignoreunknown=True)
    b.add_boolean_key('rose')
    inp = r.read_input(['blue', 'rose', 'rider', 'end'])
    assert inp.blue.rose
    assert 'rider' not in inp.blue

def test_block_read_subblocks():
    r = InputReader()
    a = r.add_block_key('red')
    b = a.add_block_key('blue')
    b.add_boolean_key('egg')
    inp = r.read_input(['red', 'blue', 'egg', 'end', 'end'])
    assert inp.red.blue.egg
    c = r.add_block_key('pink')
    d = c.add_block_key('blue', end='subend')
    d.add_boolean_key('egg')
    inp = r.read_input(['pink', 'blue', 'egg', 'subend', 'end'])
    assert inp.pink.blue.egg
