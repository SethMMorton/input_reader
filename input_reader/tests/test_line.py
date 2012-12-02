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
        with self.assertRaisesRegexp(TypeError, regex):
            self.reader.add_line_key('blue', glob={'len':'*'},
                                             keywords={'bird':{}})

    def test_name(self):
        with self.assertRaisesRegexp(ValueError, 'Keyname must be str'):
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
        regex = 'type, glob and keywords cannot all be empty'
        with self.assertRaisesRegexp(ValueError, regex):
            u = self.reader.add_line_key('gray', type=None)
        v = self.reader.add_line_key('cyan', type=[(int, float), str])
        self.assertEqual(v._type, [(int, float), str])
        import re
        regex = re.compile(r'(\s+|\w*)')
        w = self.reader.add_line_key('pink', type=regex)
        self.assertEqual(w._type, [regex])
        # Make sure incorrect types are not OK
        regex = r'type must be one of'
        with self.assertRaisesRegexp(ValueError, regex):
            self.reader.add_line_key('black', type=set([str, int]))
        with self.assertRaisesRegexp(ValueError, regex):
            self.reader.add_line_key('black', type=complex)
        regex = r'Embedded lists not allowed in type'
        with self.assertRaisesRegexp(ValueError, regex):
            self.reader.add_line_key('black', type=[str, [str, int]])
        regex = r'Empty tuple in type'
        with self.assertRaisesRegexp(ValueError, regex):
            self.reader.add_line_key('black', type=[str, ()])

    def test_glob(self):
        # Test that glob checking is OK
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
        # Test that glob checking is OK for bad input
        with self.assertRaisesRegexp(ValueError, 'glob must be a dict'):
            self.reader.add_line_key('black', glob='wrong')
        regex = r'"len" must be one of "\*", "\+", or "\?" in glob'
        with self.assertRaisesRegexp(ValueError, regex):
            self.reader.add_line_key('black', glob={'len':'1'})
        with self.assertRaisesRegexp(ValueError, r'"len" required for glob'):
            self.reader.add_line_key('black', glob={'join':True})
        regex = r'"join" must be a bool in glob'
        with self.assertRaisesRegexp(ValueError, regex):
            self.reader.add_line_key('black', glob={'len':'*', 'join':'True'})
        regex = r'type must be one of'
        with self.assertRaisesRegexp(ValueError, regex):
            self.reader.add_line_key('black', glob={'len':'*', 'type':complex})
        regex = r'list not allowed in type for glob or keywords'
        with self.assertRaisesRegexp(ValueError, regex):
            self.reader.add_line_key('black', glob={'len':'*', 'type':[str]})
        with self.assertRaisesRegexp(TypeError, 'Unknown key in glob'):
            self.reader.add_line_key('black', glob={'len':'*', 'dumb':True})

    def test_keyword(self):
        # Test that keyword checking is OK
        a = self.reader.add_line_key('red', keywords={'rose':{}})
        self.assertEqual(a._keywords, {'rose':{'default':SUPPRESS,'type':str}})
        b = self.reader.add_line_key('blue', keywords={'rose':None})
        self.assertEqual(b._keywords, {'rose':{'default':SUPPRESS,'type':str}})
        c = self.reader.add_line_key('pink', keywords={
                                        'elephant':{'default':'drunk'},
                                        'cadillac':{'default':'bruce'}})
        self.assertEqual(c._keywords, 
                         {'elephant':{'default':'drunk','type':str},
                          'cadillac':{'default':'bruce','type':str}})
        # Test that keyword checking is OK for bad input
        with self.assertRaisesRegexp(ValueError, 'keywords must be a dict'):
            self.reader.add_line_key('cyan', keywords='wrong')
        with self.assertRaisesRegexp(TypeError, 'Unknown key in keyword'):
            self.reader.add_line_key('cyan', keywords={'p':{'wrong':None}})
        with self.assertRaisesRegexp(ValueError, 'must be of type str'):
            self.reader.add_line_key('cyan', keywords={23:None})
        regex = 'Options for keyword "\w+" must be a dict'
        with self.assertRaisesRegexp(ValueError, regex):
            self.reader.add_line_key('cyan', keywords={'p':['things']})
        with self.assertRaisesRegexp(ValueError, 'list not allowed in type'):
            self.reader.add_line_key('cyan', keywords={'p':{'type':[str]}})
        with self.assertRaisesRegexp(ValueError, 'type must be one of'):
            self.reader.add_line_key('cyan', keywords={'p':{'type':complex}})

class TestReadLine(TestCase):

    def setUp(self):
        self.r = InputReader()

    def test_line_defaults(self):
        self.r.add_line_key('blue')
        inp = self.r.read_input(['blue bird'])[0]
        self.assertEquals(inp.blue, 'bird')
        regex = 'expected .*\d+ arguments, got \d+'
        with self.assertRaisesRegexp(ReaderError, regex):
            inp = self.r.read_input(['blue'])[0]
        with self.assertRaisesRegexp(ReaderError, regex):
            inp = self.r.read_input(['blue bird egg'])[0]

    def test_line_types(self):
        self.r.add_line_key('blue', type=int)
        inp = self.r.read_input(['blue 23'])[0]
        self.assertEqual(inp.blue, 23)
        with self.assertRaisesRegexp(ReaderError, 'expected \w+, got \w+'):
            inp = self.r.read_input(['blue bird'])[0]

        self.r.add_line_key('red', type=(0, 1, 2, 3))
        inp = self.r.read_input(['red 3'])[0]
        self.assertEqual(inp.red, 3)
        with self.assertRaisesRegexp(ReaderError, 'expected .+, got \w+'):
            inp = self.r.read_input(['red 4'])[0]

        self.r.add_line_key('green', type=(float, None))
        inp = self.r.read_input(['green 3'])[0]
        self.assertEqual(inp.green, 3)
        inp = self.r.read_input(['green 3.5'])[0]
        self.assertEqual(inp.green, 3.5)
        inp = self.r.read_input(['green none'])[0]
        self.assertIsNone(inp.green)
        with self.assertRaisesRegexp(ReaderError, 'expected .+, got \w+'):
            inp = self.r.read_input(['green bird'])[0]

        self.r.add_line_key('cyan', type=[str, (None, str), float])
        inp = self.r.read_input(['cyan cat dog 6'])[0]
        self.assertEqual(inp.cyan, ('cat', 'dog', 6))
        with self.assertRaisesRegexp(ReaderError, 'expected .+, got \w+'):
            inp = self.r.read_input(['cyan cat dog 7 8'])[0]
        with self.assertRaisesRegexp(ReaderError, 'expected \w+, got \w+'):
            inp = self.r.read_input(['cyan cat none bird'])[0]
        inp = self.r.read_input(['cyan cat none 7.8'])[0]
        self.assertEqual(inp.cyan, ('cat', None, 7.8))

        import re
        self.r.add_line_key('pink', type=re.compile(r'neat\d+'))
        inp = self.r.read_input(['pink neat68'])[0]
        self.assertEqual(inp.pink, 'neat68')
        with self.assertRaisesRegexp(ReaderError, 'expected regex\(.*\)'):
            inp = self.r.read_input(['pink near68'])[0]

    def test_line_case(self):
        self.r.add_line_key('blue', type=str)
        inp = self.r.read_input(['blue HeLLo'])[0]
        self.assertEqual(inp.blue, 'hello')
        self.r.add_line_key('red', type=str, case=True)
        inp = self.r.read_input(['red HeLLo'])[0]
        self.assertEqual(inp.red, 'HeLLo')
        
    def test_line_glob(self):
        pass

    def test_keyword_glob(self):
        pass

# Function to export the tests in a controlled manner
def suite():
    suite = TestSuite()
    suite.addTest(TestLoader().loadTestsFromTestCase(TestAddLine))
    suite.addTest(TestLoader().loadTestsFromTestCase(TestReadLine))
    return suite

if __name__ == '__main__':
    from unittest import main
    main()
