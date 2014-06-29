from __future__ import unicode_literals
from input_reader import InputReader, ReaderError, SUPPRESS
from pytest import raises, fixture
from re import search

def test_line_missing_keyname():
    r = InputReader()
    with raises(TypeError):
        r.add_line_key()
    with raises(TypeError):
        r.add_line_key(type=str)
    with raises(TypeError):
        r.add_line_key(glob={})
    with raises(TypeError):
        r.add_line_key(keywords={})
    with raises(TypeError):
        r.add_line_key(case=False)

def test_line_correct_call():
    r = InputReader()
    a = r.add_line_key('red')
    assert a.name == 'red'
    assert a._type == [str]
    assert a._glob == {}
    assert a._keywords == {}
    assert not a._case
    with raises(TypeError) as e:
        r.add_line_key('blue', glob={'len':'*'},
                               keywords={'bird':{}})
    assert 'Cannot define both glob and keywords' in str(e.value)
    with raises(ValueError) as e:
        r.add_line_key('pink', type=None, 
                               glob=None, keywords=None)
    assert 'type, glob and keywords cannot all be empty' in str(e.value)

def test_line_name_definition():
    r = InputReader()
    with raises(ValueError) as e:
        r.add_line_key(23)
    assert 'keyname must be str' in str(e.value)
    with raises(ValueError) as e:
        r.add_line_key('hello goodbye')
    assert 'String cannot contain spaces' in str(e.value)
    with raises(ValueError) as e:
        r.add_line_key('')
    assert 'String cannot be of zero length' in str(e.value)

def test_line_repeat_in_definition():
    # You cannot repeat keys
    r = InputReader()
    r.add_line_key(str('red'))
    with raises(ReaderError) as e:
        r.add_line_key('red')
    assert search(r'The keyname "\w+" has been defined twice', str(e.value))

def test_line_case_definition():
    r = InputReader()
    a = r.add_line_key('red', case=True)
    assert a._case
    with raises(ValueError) as e:
        r.add_line_key('blue', case='True')
    assert 'case must be bool' in str(e.value)

def test_line_type_definitions():
    # Make sure that correct types are OK
    r = InputReader()
    a = r.add_line_key('red', type=str)
    assert a._type == [str]
    s = r.add_line_key('blue', type=[int])
    assert s._type == [int]
    t = r.add_line_key('green', type=(14, 2.8, None, 'hey', str('hello'), str))
    assert t._type == [(14, 2.8, None, 'hey', 'hello', str)]
    with raises(ValueError) as e:
        u = r.add_line_key('gray', type=None)
    assert 'type, glob and keywords cannot all be empty' in str(e.value)
    v = r.add_line_key('cyan', type=[(int, float), str])
    assert v._type == [(int, float), str]
    import re
    regex = re.compile(r'(\d+|\w*)')
    w = r.add_line_key('pink', type=regex)
    assert w._type == [regex]
    # Make sure incorrect types are not OK
    regex = re.compile(str(r'hi\s+bye'))
    with raises(ValueError) as e:
        r.add_line_key('black', type=regex)
    assert 'Regex should not allow the possibility of spaces' in str(e.value)
    regex = re.compile(r'hi.*bye')
    with raises(ValueError) as e:
        r.add_line_key('black', type=regex)
    assert 'Regex should not allow the possibility of spaces' in str(e.value)
    with raises(ValueError) as e:
        r.add_line_key('black', type="")
    assert 'String cannot be of zero length' in str(e.value)
    with raises(ValueError) as e:
        r.add_line_key('black', type='hey there')
    assert 'String cannot contain spaces' in str(e.value)
    with raises(ValueError) as e:
        r.add_line_key('black', type=str('hey there'))
    assert 'String cannot contain spaces' in str(e.value)
    with raises(ValueError) as e:
        r.add_line_key('black', type=set([str, int]))
    assert 'type must be one of' in str(e.value)
    with raises(ValueError) as e:
        r.add_line_key('black', type=complex)
    assert 'type must be one of' in str(e.value)
    with raises(ValueError) as e:
        r.add_line_key('black', type=[str, [str, int]])
    assert r'Embedded lists not allowed in type' in str(e.value)
    with raises(ValueError) as e:
        r.add_line_key('black', type=[str, ()])
    assert r'Empty tuple in type' in str(e.value)

def test_line_glob_definitions():
    # Test that glob checking is OK
    r = InputReader()
    a = r.add_line_key('red', glob={'len':'*'})
    assert a._glob == {'len':'*', 'type':str, 'join':False}
    b = r.add_line_key('blue', glob={str('len'):str('?')})
    assert b._glob == {'len':'?', 'type':str, 'join':False}
    c = r.add_line_key('green', glob={'len':'+', 'join':True})
    assert c._glob == {'len':'+', 'type':str, 'join':True}
    e = r.add_line_key('pink', glob={'len':'?', 'type':int})
    assert e._glob == {'len':'?', 'type':int, 'join':False}
    f = r.add_line_key('gray', glob={'len':'*', 'type':(int,"hey",str("hi"),str)})
    assert f._glob == {'len':'*', 'type':(int,"hey","hi",str), 'join':False}
    # Test that glob checking is OK for bad input
    with raises(ValueError) as e:
        r.add_line_key('black', glob='wrong')
    assert 'glob must be a dict' in str(e.value)
    with raises(ValueError) as e:
        r.add_line_key('black', glob={'len':'1'})
    assert search(r'"len" must be one of "\*", "\+", or "\?" in glob', str(e.value))
    with raises(ValueError) as e:
        r.add_line_key('black', glob={'join':True})
    assert '"len" required for glob' in str(e.value)
    with raises(ValueError) as e:
        r.add_line_key('black', glob={'len':'*', 'join':'True'})
    assert '"join" must be a bool in glob' in str(e.value)
    with raises(ValueError) as e:
        r.add_line_key('black', glob={'len':'*', 'type':complex})
    assert 'type must be one of' in str(e.value)
    with raises(ValueError) as e:
        r.add_line_key('black', glob={'len':'*', 'type':[str]})
    assert 'list not allowed in type for glob or keywords' in str(e.value)
    with raises(TypeError) as e:
        r.add_line_key('black', glob={'len':'*', 'dumb':True})
    assert 'Unknown key in glob' in str(e.value)
    with raises(ValueError) as e:
        r.add_line_key('black', glob={'len':'?', 'join':True})
    assert r'"join=True" makes no sense for "len=?"' in str(e.value)

def test_line_keyword_definitions():
    # Test that keyword checking is OK
    r = InputReader()
    a = r.add_line_key('red', keywords={'rose':{}})
    assert a._keywords == {'rose':{'default':SUPPRESS,'type':str}}
    # Make sure str works, not just unicode (python2.x)
    b = r.add_line_key('blue', keywords={str('rose'):None})
    assert b._keywords == {'rose':{'default':SUPPRESS,'type':str}}
    c = r.add_line_key('pink', keywords={
                                    'elephant':{str('default'):'drunk'},
                                    'cadillac':{'default':str('bruce')}})
    assert c._keywords == \
                     {'elephant':{'default':'drunk','type':str},
                      'cadillac':{'default':'bruce','type':str}}
    # Test that keyword checking is OK for bad input
    with raises(ValueError) as e:
        r.add_line_key('cyan', keywords='wrong')
    assert 'keywords must be a dict' in str(e.value)
    with raises(TypeError) as e:
        r.add_line_key('cyan', keywords={'p':{'wrong':None}})
    assert 'Unknown key in keyword' in str(e.value)
    with raises(ValueError) as e:
        r.add_line_key('cyan', keywords={23:None})
    assert 'must be of type str' in str(e.value)
    with raises(ValueError) as e:
        r.add_line_key('cyan', keywords={'p':['things']})
    assert search(r'Options for keyword "\w+" must be a dict', str(e.value))
    with raises(ValueError) as e:
        r.add_line_key('cyan', keywords={'p':{'type':[str]}})
    assert 'list not allowed in type' in str(e.value)
    with raises(ValueError) as e:
        r.add_line_key('cyan', keywords={'p':{'type':complex}})
    assert 'type must be one of' in str(e.value)

def test_line_read_using_defaults():
    r = InputReader()
    r.add_line_key('blue')
    inp = r.read_input(['blue bird'])
    assert inp.blue == 'bird'
    with raises(ReaderError) as e:
        inp = r.read_input(['blue'])
    assert search(r'expected .*\d+ arguments, got \d+', str(e.value))
    with raises(ReaderError) as e:
        inp = r.read_input(['blue bird egg'])
    assert search(r'expected .*\d+ arguments, got \d+', str(e.value))

def test_line_reading_types():
    r = InputReader()
    r.add_line_key('blue', type=int)
    inp = r.read_input(['blue 23'])
    assert inp.blue == 23
    with raises(ReaderError) as e:
        inp = r.read_input(['blue bird'])
    assert search(r'expected \w+, got "\w+"', str(e.value))

    r.add_line_key('red', type=(0, 1, 2, 3))
    inp = r.read_input(['red 3'])
    assert inp.red == 3
    with raises(ReaderError) as e:
        inp = r.read_input(['red 4'])
    assert search(r'expected one of .+, got "\w+"', str(e.value))

    r.add_line_key('green', type=(float, None))
    inp = r.read_input(['green 3'])
    assert inp.green == 3
    inp = r.read_input(['green 3.5'])
    assert inp.green == 3.5
    inp = r.read_input(['green none'])
    assert inp.green is None
    with raises(ReaderError) as e:
        inp = r.read_input(['green bird'])
    assert search(r'expected one of .+, got "\w+"', str(e.value))

    r.add_line_key('cyan', type=[str, (None, str), float])
    inp = r.read_input(['cyan cat dog 6'])
    assert inp.cyan == ('cat', 'dog', 6)
    with raises(ReaderError) as e:
        inp = r.read_input(['cyan cat dog 7 8'])
    assert search('expected .+, got \w+', str(e.value))
    with raises(ReaderError) as e:
        inp = r.read_input(['cyan cat none bird'])
    assert search('expected \w+, got "\w+"', str(e.value))
    inp = r.read_input(['cyan cat none 7.8'])
    assert inp.cyan == ('cat', None, 7.8)

    r.add_line_key('black', type=('hey', str('hi'), 4, 2.8))
    inp = r.read_input(['black 4'])
    assert inp.black == 4
    inp = r.read_input(['black 2.8'])
    assert inp.black == 2.8
    inp = r.read_input(['black hey'])
    assert inp.black == 'hey'
    inp = r.read_input(['black hi'])
    assert inp.black == 'hi'
    with raises(ReaderError) as e:
        inp = r.read_input(['black whoops'])
    assert search('expected one of [a-zA-Z0-9, ".]+, got "\w+"', str(e.value))
    with raises(ReaderError) as e:
        inp = r.read_input(['black 2'])
    assert search('expected one of [a-zA-Z0-9, ".]+, got "\d+"', str(e.value))

    import re
    r.add_line_key('pink', type=re.compile(r'neat\d+'))
    inp = r.read_input(['pink neat68'])
    assert inp.pink == 'neat68'
    with raises(ReaderError) as e:
        inp = r.read_input(['pink near68'])
    assert search('expected regex\(.*\)', str(e.value))

def test_line_read_case_sensitive():
    r = InputReader()
    r.add_line_key('blue', type=str)
    inp = r.read_input(['blue HeLLo'])
    assert inp.blue == 'hello'
    r.add_line_key('red', type=str, case=True)
    inp = r.read_input(['red HeLLo'])
    assert inp.red == 'HeLLo'
    
def test_line_read_using_globs():
    r = InputReader()
    r.add_line_key('blue', type=[int, int],
                        glob={'len':'*', 'type':int})
    inp = r.read_input(['blue 1 2 3 4 5 6 7'])
    assert inp.blue == (1, 2, 3, 4, 5, 6, 7)
    inp = r.read_input(['blue 1 2'])
    assert inp.blue == (1, 2)

    r.add_line_key('red', type=[int, int],
                        glob={'len':'*', 'type':int, 'join':True})
    inp = r.read_input(['red 1 2 3 4 5 6 7'])
    assert inp.red == (1, 2, '3 4 5 6 7')
    inp = r.read_input(['red 1 2'])
    assert inp.red == (1, 2)

    r.add_line_key('pink', type=[int, int],
                        glob={'len':'+', 'type':float, 'join':True})
    inp = r.read_input(['pink 1 2 3 4 5 6 7'])
    assert inp.pink == (1, 2, '3.0 4.0 5.0 6.0 7.0')
    inp = r.read_input(['pink 1 2 3'])
    assert inp.pink == (1, 2, '3.0')

    r.add_line_key('cyan', type=[int, int],
                        glob={'len':'?', 'type':int})
    inp = r.read_input(['cyan 1 2 3'])
    assert inp.cyan == (1, 2, 3)
    inp = r.read_input(['cyan 1 2'])
    assert inp.cyan == (1, 2)

    r.add_line_key('yellow', type=int, glob={'len':'?', 'type':int})
    inp = r.read_input(['yellow 1 2'])
    assert inp.yellow == (1, 2)
    inp = r.read_input(['yellow 1'])
    assert inp.yellow == (1,)

    r.add_line_key('teal', type=int, glob={'len':'?', 'type':int, 'default':3})
    inp = r.read_input(['teal 1 2'])
    assert inp.teal == (1, 2)
    inp = r.read_input(['teal 1'])
    assert inp.teal == (1, 3)

    r.add_line_key('gray', type=None, glob={'len':'?'})
    inp = r.read_input(['gray bye'])
    assert inp.gray == 'bye'
    inp = r.read_input(['gray'])
    assert inp.gray == ''

    r.add_line_key('white', type=None, glob={'len':'*'})
    inp = r.read_input(['white hi lo'])
    assert inp.white == ('hi', 'lo')
    inp = r.read_input(['white'])
    assert inp.white == ()

    r.add_line_key('green', type=None, glob={'len':'+', 'join':True})
    inp = r.read_input(['green hi lo'])
    assert inp.green == 'hi lo'

    r.add_line_key('orange', type=None, glob={'len':'*', 'join':True})
    inp = r.read_input(['orange'])
    assert inp.orange == ''

    r.add_line_key('black', type=int, glob={'len':'?', 'type':int})
    with raises(ReaderError) as e:
        r.read_input(['black 1 2 3'])
    assert search(r'expected at most \d+ arguments, got \d+', str(e.value))
    r.add_line_key('maroon', type=int, glob={'len':'+', 'type':int})
    with raises(ReaderError) as e:
        r.read_input(['maroon 1'])
    assert search(r'expected at least \d+ arguments, got \d+', str(e.value))

def test_line_read_using_keywords():
    r = InputReader()
    r.add_line_key('red', type=int, 
                          keywords={'robin':{}})
    inp = r.read_input(['red 5 robin=early'])
    assert inp.red == (5, {'robin':'early'})
    inp = r.read_input(['red 5'])
    assert inp.red == (5, {})
    with raises(ReaderError) as e:
        r.read_input(['red 5 robin=early light=special'])
    assert 'Unknown keyword' in str(e.value)
    
    r.add_line_key('blue', type=[int, int],
                           keywords={'egg':{'type':int, 'default':1},
                                     'ice':{'type':(4, 5)}})
    inp = r.read_input(['blue 5 7 egg=6 ice=4'])
    assert inp.blue == (5, 7, {'egg':6, 'ice':4})
    inp = r.read_input(['blue 5 7 ice=5'])
    assert inp.blue == (5, 7, {'egg':1, 'ice':5})
    inp = r.read_input(['blue 5 7'])
    assert inp.blue == (5, 7, {'egg':1})

    r.add_line_key('cyan', type=None, keywords={'by':{'type':int},
                                                'to':{'type':int}})
    inp = r.read_input(['cyan by=14 to=11'])
    assert inp.cyan == {'by':14, 'to':11}
    inp = r.read_input(['cyan by=14'])
    assert inp.cyan == {'by':14}
    inp = r.read_input(['cyan'])
    assert inp.cyan == {}
    with raises(ReaderError) as e:
        inp = r.read_input(['cyan by = 3'])
    assert 'Error reading keyword argument' in str(e.value)
