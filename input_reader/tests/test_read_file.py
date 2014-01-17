from input_reader import InputReader, ReaderError, SUPPRESS
from pytest import raises, fixture
try:
    from cStringIO import StringIO
except ImportError:
    from io import StringIO
from textwrap import dedent
from os import remove
from re import search
from tempfile import mkstemp

def case_keys(reader, s):
    reader.add_boolean_key('RED')
    reader.add_boolean_key('BLUE')
    reader.add_line_key('PATH')
    return reader.read_input(s)
def default_keys(reader, s):
    reader.add_boolean_key('RED')
    reader.add_boolean_key('BLUE')
    reader.add_boolean_key('GREEN')
    reader.add_line_key('PATH')
    reader.add_line_key('LINE')
    return reader.read_input(s)
def default_checks(inp):
    assert inp.red
    assert inp.blue
    assert inp.path == 'this/is/a/pathname.txt'

TEMPNAME = mkstemp()[1]

@fixture
def setup():
    reader = InputReader()
    # Make a string of the input
    s = dedent("""\
             # Here is an input file
             # It has some comments

             # And a boolean
             spam

             # And a line key
             eggs 5 # I have 5 eggs

             # And a block key
             cheese
                 brie
                 cheddar
             end""")
    # Make a StringIO version of the same input
    io = StringIO()
    io.write(s)
    # Make a list of strings for the input
    l = s.split('\n')

    # Here is what the read in input should look like
    r = ['', '', '', '', 'spam', '', '', 'eggs 5', '', '',
          'cheese', 'brie', 'cheddar', 'end']
    ps = dedent("""\
             PATH This/Is/A/pathName.txt // A comment

             BLUE
             RED""")
    ps = ps.split('\n')
    return reader, s, io, l, r, ps

def test_read_file_properly(setup):
    reader, s, io, l, r, parse_string = setup
    # Write the input to file
    with open(TEMPNAME, 'w') as f:
        f.write(s)
    inp = reader._read_in_file(TEMPNAME)
    assert inp == r
    remove(TEMPNAME)

def test_read_string_fails_properly(setup):
    # If a string is given directly, it is assumed to be the file name
    reader, s, io, l, r, parse_string = setup
    with raises(ReaderError) as e:
        reader._read_in_file(s)
    assert 'Cannot read in file' in str(e.value) 

def test_read_stringio_properly(setup):
    reader, s, io, l, r, parse_string = setup
    inp = reader._read_in_file(io)
    assert inp == r

def test_read_list_properly(setup):
    reader, s, io, l, r, parse_string = setup
    inp = reader._read_in_file(l)
    assert inp == r

def test_read_float_fails_properly(setup):
    reader, s, io, l, r, parse_string = setup
    with raises(ValueError) as e:
        inp = reader._read_in_file([3.4, 4.5])
    assert 'Unknown object passed' in str(e.value)

def test_comments_are_handled_correctly(setup):
    parse_string = setup[-1]
    reader = InputReader(comment='#')
    reader.add_boolean_key('red')
    reader.add_boolean_key('blue')
    reader.add_line_key('path')
    with raises(ReaderError) as e:
        reader.read_input(parse_string)
    regex = r'expected \d+ arguments, got \d+'
    assert search(regex, str(e.value))

def test_unknown_keys_cause_failure(setup):
    # Don't ignore unknown keys
    parse_string = setup[-1]
    reader = InputReader(comment='//', ignoreunknown=False)
    reader.add_boolean_key('red')
    reader.add_line_key('path')
    with raises(ReaderError) as e:
        reader.read_input(parse_string)
    assert 'Unrecognized key' in str(e.value)

def test_ignoreunknown_actually_ignores_unknown(setup):
    # Ignore unknown keys
    parse_string = setup[-1]
    reader = InputReader(comment='//', ignoreunknown=True)
    reader.add_boolean_key('red')
    reader.add_line_key('path')
    inp = reader.read_input(parse_string)
    with raises(AttributeError):
        inp.blue

def test_case_sensitive_reading(setup):
    # Case-sensitive
    parse_string = setup[-1]
    reader = InputReader(comment='//', case=True)
    inp = case_keys(reader, parse_string)
    assert inp.RED
    assert inp.BLUE
    assert inp.PATH == 'This/Is/A/pathName.txt'
    del reader, inp

def test_case_insensitive_reading(setup):
    # Case-insensitive
    parse_string = setup[-1]
    reader = InputReader(comment='//', case=False)
    inp = case_keys(reader, parse_string)
    assert inp.red
    assert inp.blue
    assert inp.path == 'this/is/a/pathname.txt'

def test_missing_key_defaults_to_none(setup):
    # Default not found keys to None
    parse_string = setup[-1]
    reader = InputReader(comment='//')
    inp = default_keys(reader, parse_string)
    default_checks(inp)
    assert inp.green is None
    assert inp.line is None

def test_missing_key_defaults_to_false(setup):
    # Default not found keys to False
    parse_string = setup[-1]
    reader = InputReader(comment='//', default=False)
    inp = default_keys(reader, parse_string)
    default_checks(inp)
    assert not inp.green
    assert not inp.line

def test_missing_key_is_suppressed(setup):
    # Default not found keys to SUPPRESS
    parse_string = setup[-1]
    reader = InputReader(comment='//', default=SUPPRESS)
    inp = default_keys(reader, parse_string)
    default_checks(inp)
    assert 'green' not in inp
    assert 'line' not in inp
