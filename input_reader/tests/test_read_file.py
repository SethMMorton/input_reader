from input_reader import InputReader, ReaderError, Namespace
from unittest import TestCase, TestSuite, TestLoader
from cStringIO import StringIO
from textwrap import dedent
from os import remove

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
        with self.assertRaises(ReaderError):
            self.reader._read_in_file(self.s)

    def test_strinio(self):
        inp = self.reader._read_in_file(self.io)
        self.assertEqual(inp, self.r)

    def test_list(self):
        inp = self.reader._read_in_file(self.l)
        self.assertEqual(inp, self.r)

    def tearDown(self):
        remove(TEMPNAME)

# Function to export the tests in a controlled manner
def suite():
    suite = TestSuite()
    suite.addTest(TestLoader().loadTestsFromTestCase(TestReadFile))
    return suite

if __name__ == '__main__':
    from unittest import main
    main()
