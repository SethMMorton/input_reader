from input_reader import InputReader, ReaderError, SUPPRESS
from unittest import TestCase, TestSuite, TestLoader
from cStringIO import StringIO
from textwrap import dedent
from os import remove

def case_keys(reader, s):
    reader.add_boolean_key('RED')
    reader.add_boolean_key('BLUE')
    reader.add_line_key('PATH')
    return reader.read_input(s)[0]
def default_keys(reader, s):
    reader.add_boolean_key('RED')
    reader.add_boolean_key('BLUE')
    reader.add_boolean_key('GREEN')
    reader.add_line_key('PATH')
    reader.add_line_key('LINE')
    return reader.read_input(s)[0]
def default_checks(self, inp):
    self.assertTrue(inp.red)
    self.assertTrue(inp.blue)
    self.assertEqual(inp.path, 'this/is/a/pathname.txt')

TEMPNAME = 'tempinput'

class TestReadFile(TestCase):

    def setUp(self):
        self.reader = InputReader()
        # Make a string of the input
        self.s = dedent('''\
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
                 end''')
        # Make a StringIO version of the same input
        self.io = StringIO()
        self.io.write(self.s)
        # Write the input to file
        self.f = open(TEMPNAME, 'w')
        self.f.write(self.s)
        self.f.close()
        # Make a list of strings for the input
        self.l = self.s.split('\n')

        # Here is what the read in input should look like
        self.r = ['', '', '', '', 'spam', '', '', 'eggs 5', '', '',
                  'cheese', 'brie', 'cheddar', 'end']

    def test_file(self):
        inp = self.reader._read_in_file(TEMPNAME)
        self.assertEqual(inp, self.r)

    def test_string(self):
        # If a string is given directly, it is assumed to be the file name
        with self.assertRaisesRegexp(ReaderError, 'Cannot read in file'):
            self.reader._read_in_file(self.s)

    def test_stringio(self):
        inp = self.reader._read_in_file(self.io)
        self.assertEqual(inp, self.r)

    def test_list(self):
        inp = self.reader._read_in_file(self.l)
        self.assertEqual(inp, self.r)

    def tearDown(self):
        remove(TEMPNAME)

class TestParseFile(TestCase):

    def setUp(self):
        self.s = dedent('''\
                 PATH this/is/a/pathName.txt // A comment

                 BLUE
                 RED''')
        self.s = self.s.split('\n')

    def test_comment(self):
        reader = InputReader(comment='#')
        reader.add_boolean_key('red')
        reader.add_boolean_key('blue')
        reader.add_line_key('path')
        regex = 'expected \d+ arguments, got \d+'
        with self.assertRaisesRegexp(ReaderError, regex):
            reader.read_input(self.s)

    def test_ignoreunknown_false(self):
        # Don't ignore unknown keys
        reader = InputReader(comment='//', ignoreunknown=False)
        reader.add_boolean_key('red')
        reader.add_line_key('path')
        with self.assertRaisesRegexp(ReaderError, 'Unrecognized key: \w+'):
            reader.read_input(self.s)

    def test_ignoreunknown_true(self):
        # Ignore unknown keys
        reader = InputReader(comment='//', ignoreunknown=True)
        reader.add_boolean_key('red')
        reader.add_line_key('path')
        inp = reader.read_input(self.s)[0]
        with self.assertRaises(AttributeError):
            inp.blue

    def test_case_sensitive(self):
        # Case-sensitive
        reader = InputReader(comment='//', case=True)
        inp = case_keys(reader, self.s)
        self.assertTrue(inp.RED)
        self.assertTrue(inp.BLUE)
        self.assertEqual(inp.PATH, 'this/is/a/pathName.txt')
        del reader, inp

    def test_case_insensitive(self):
        # Case-insensitive
        reader = InputReader(comment='//', case=False)
        inp = case_keys(reader, self.s)
        self.assertTrue(inp.red)
        self.assertTrue(inp.blue)
        self.assertEqual(inp.path, 'this/is/a/pathname.txt')

    def test_default_none(self):
        # Default not found keys to None
        reader = InputReader(comment='//')
        inp = default_keys(reader, self.s)
        default_checks(self, inp)
        self.assertIsNone(inp.green)
        self.assertIsNone(inp.line)

    def test_default_false(self):
        # Default not found keys to False
        reader = InputReader(comment='//', default=False)
        inp = default_keys(reader, self.s)
        default_checks(self, inp)
        self.assertFalse(inp.green)
        self.assertFalse(inp.line)

    def test_default_suppress(self):
        # Default not found keys to SUPPRESS
        reader = InputReader(comment='//', default=SUPPRESS)
        inp = default_keys(reader, self.s)
        default_checks(self, inp)
        with self.assertRaises(AttributeError):
            inp.green
        with self.assertRaises(AttributeError):
            inp.line

# Function to export the tests in a controlled manner
def suite():
    suite = TestSuite()
    suite.addTest(TestLoader().loadTestsFromTestCase(TestReadFile))
    suite.addTest(TestLoader().loadTestsFromTestCase(TestParseFile))
    return suite

if __name__ == '__main__':
    from unittest import main
    main()
