from input_reader import InputReader, ReaderError, SUPPRESS
from unittest import TestCase, TestSuite, TestLoader
from textwrap import dedent

class TestAddLine(TestCase):

    def setUp(self):
        self.reader = InputReader()

    def test_missing_keyname(self):
        with self.assertRaises(TypeError):
            self.reader.add_line_key()
        with self.assertRaises(TypeError):
            self.reader.add_line_key(type=str)
        with self.assertRaises(TypeError):
            self.reader.add_line_key(glob={})
        with self.assertRaises(TypeError):
            self.reader.add_line_key(keywords={})
        with self.assertRaises(TypeError):
            self.reader.add_line_key(case=False)

    def test_correct_call(self):
        r = self.reader.add_line_key('red')
        self.assertEqual(r.name, 'red')
        self.assertEqual(r._type, [str])
        self.assertEqual(r._glob, {})
        self.assertEqual(r._keywords, {})
        self.assertFalse(r._case)
        regex = 'Cannot define both glob and keywords'
        with self.assertRaisesRegexp(ReaderError, regex):
            self.reader.add_line_key('blue', glob={'len':'*'},
                                             keywords={'bird':{}})

    def test_name(self):
        with self.assertRaisesRegexp(ReaderError, 'Keyname must be str'):
            self.reader.add_line_key(23)

    def test_repeat(self):
        # You cannot repeat keys
        self.reader.add_line_key('red')
        regex = r'The key \w+ has been defined twice'
        with self.assertRaisesRegexp(ReaderError, regex):
            self.reader.add_line_key('red')

    def test_type(self):
        # Make sure that correct types are OK
        r = self.reader.add_line_key('red', type=str)
        self.assertEqual(r._type, [str])
        s = self.reader.add_line_key('blue', type=[int])
        self.assertEqual(s._type, [int])
        t = self.reader.add_line_key('green', type=(str, 14, 2.8, None))
        self.assertEqual(t._type, [(str, 14, 2.8, None)])
        u = self.reader.add_line_key('gray', type=None)
        self.assertEqual(u._type, [])
        v = self.reader.add_line_key('cyan', type=[(int, float), str])
        self.assertEqual(v._type, [(int, float), str])
        import re
        regex = re.compile(r'(\s+|\w*)')
        w = self.reader.add_line_key('pink', type=regex)
        self.assertEqual(w._type, [regex])
        # Make sure incorrect types are not OK
        regex = r'type must be one of'
        with self.assertRaisesRegexp(ReaderError, regex):
            self.reader.add_line_key('black', type=set([str, int]))
        with self.assertRaisesRegexp(ReaderError, regex):
            self.reader.add_line_key('black', type=complex)
        regex = r'Embedded lists not allowed in type'
        with self.assertRaisesRegexp(ReaderError, regex):
            self.reader.add_line_key('black', type=[str, [str, int]])
        regex = r'Empty tuple in type'
        with self.assertRaisesRegexp(ReaderError, regex):
            self.reader.add_line_key('black', type=[str, ()])

    def test_glob(self):
        # Test that glob ckecking is OK
        a = self.reader.add_line_key('red', glob={'len':'*'})
        self.assertEqual(a._glob, {'len':'*', 'type':str, 'join':False})
        b = self.reader.add_line_key('blue', glob={'len':'?'})
        self.assertEqual(b._glob, {'len':'?', 'type':str, 'join':True})
        c = self.reader.add_line_key('green', glob={'len':'+', 'join':True})
        self.assertEqual(c._glob, {'len':'+', 'type':str, 'join':True})
        d = self.reader.add_line_key('cyan', glob={'len':'?', 'join':False})
        self.assertEqual(d._glob, {'len':'?', 'type':str, 'join':False})
        e = self.reader.add_line_key('pink', glob={'len':'?', 'type':int})
        self.assertEqual(e._glob, {'len':'?', 'type':int, 'join':True})
        f = self.reader.add_line_key('gray', glob={'len':'*', 'type':(int,str)})
        self.assertEqual(f._glob, {'len':'*', 'type':(int,str), 'join':False})
        # Test that glob ckecking is not OK
        with self.assertRaisesRegexp(ReaderError, 'glob must be a dict'):
            self.reader.add_line_key('black', glob='wrong')
        regex = r'"len" must be one of "\*", "\+", or "\?" in glob'
        with self.assertRaisesRegexp(ReaderError, regex):
            self.reader.add_line_key('black', glob={'len':'1'})
        with self.assertRaisesRegexp(ReaderError, r'"len" required for glob'):
            self.reader.add_line_key('black', glob={'join':True})
        regex = r'"join" must be a bool in glob'
        with self.assertRaisesRegexp(ReaderError, regex):
            self.reader.add_line_key('black', glob={'len':'*', 'join':'True'})
        regex = r'type must be one of'
        with self.assertRaisesRegexp(ReaderError, regex):
            self.reader.add_line_key('black', glob={'len':'*', 'type':complex})
        regex = r'list not allowed in type for glob or keywords'
        with self.assertRaisesRegexp(ReaderError, regex):
            self.reader.add_line_key('black', glob={'len':'*', 'type':[str]})
        with self.assertRaisesRegexp(ReaderError, 'Unknown key in glob'):
            self.reader.add_line_key('black', glob={'len':'*', 'dumb':True})

    def test_keyword(self):
        # Test that keyword checking is OK
        a = self.reader.add_line_key('red', keywords={'rose':{}})
        self.assertEqual(a._keywords, {'rose':{'default':SUPPRESS,'type':str}})
        b = self.reader.add_line_key('blue', keywords={'rose':None})
        self.assertEqual(b._keywords, {'rose':{'default':SUPPRESS,'type':str}})

class TestReadLine(TestCase):

    def setUp(self):
        self.s1 = dedent('''\
                  blue
                  red # Comment
                  ''').split('\n')
        self.s2 = dedent('''\
                  blue
                  red color # This is illegal
                  ''').split('\n')
        self.r = InputReader()

    def test_boolean_arguments(self):
        # Booleans cannot have arguments
        self.r.add_boolean_key('blue')
        self.r.add_boolean_key('red')
        regex = 'The boolean "\w+" was given arguments, this is illegal'
        with self.assertRaisesRegexp(ReaderError, regex):
            inp = self.r.read_input(self.s2)[0]

    def test_actions(self):
        # Actions can be lists, not just bool, str, int or floats
        self.r.add_boolean_key('blue', action=['something', 'odd'])
        # An action can be a function, too!
        self.r.add_boolean_key('red', 
                               action=lambda x: "hello" if x else "goodbye")
        inp = self.r.read_input(self.s1)[0]
        self.assertEqual(inp.blue, ['something', 'odd'])
        self.assertEqual(inp.red(True), "hello")
        self.assertEqual(inp.red(0), "goodbye")

# Function to export the tests in a controlled manner
def suite():
    suite = TestSuite()
    suite.addTest(TestLoader().loadTestsFromTestCase(TestAddLine))
    suite.addTest(TestLoader().loadTestsFromTestCase(TestReadLine))
    return suite

if __name__ == '__main__':
    from unittest import main
    main()
