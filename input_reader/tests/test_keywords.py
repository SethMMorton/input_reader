from input_reader import InputReader, ReaderError, SUPPRESS
from unittest import TestCase, TestSuite, TestLoader
from textwrap import dedent

class TestClassKeywords(TestCase):

    def test_suppress(self):
        ir = InputReader(default=SUPPRESS)
        self.assertIs(ir._default, SUPPRESS)
        b = ir.add_boolean_key('RED')
        self.assertIs(b._default, SUPPRESS)

    def test_str_default(self):
        ir = InputReader(default='roses')
        self.assertEqual(ir._default, 'roses')
        b = ir.add_boolean_key('RED')
        self.assertEqual(b._default, 'roses')

    def test_case(self):
        ir = InputReader(case=True)
        self.assertTrue(ir._case)
        l = ir.add_line_key('RED')
        self.assertTrue(l._case)
        with self.assertRaises(ValueError):
            ir2 = InputReader(case='True')

class TestCommonKeywords(TestCase):

    def setUp(self):
        self.reader = InputReader()

    def test_use_defaults(self):
        b = self.reader.add_boolean_key('red')
        self.assertFalse(b._required)
        self.assertIsNone(b._default)
        self.assertIsNone(b._dest)
        self.assertIsNone(b._depends)
        self.assertFalse(b._repeat)

    def test_dont_use_defaults(self):
        b = self.reader.add_boolean_key('red', True,
                                        required=False,
                                        default=None,
                                        dest=None,
                                        depends=None,
                                        repeat=False)
        self.assertFalse(b._required)
        self.assertIsNone(b._default)
        self.assertIsNone(b._dest)
        self.assertIsNone(b._depends)
        self.assertFalse(b._repeat)

    def test_custom_values(self):
        b = self.reader.add_boolean_key('red', True,
                                        required=True,
                                        default='BANANA',
                                        dest='fruit',
                                        depends='something',
                                        repeat=True)
        self.assertTrue(b._required)
        self.assertEqual(b._default, 'BANANA')
        self.assertEqual(b._dest, 'fruit')
        self.assertEqual(b._depends, 'something')
        self.assertTrue(b._repeat)

    def test_incorrect_options(self):
        # The keyword 'wrong' doesn't exist
        with self.assertRaises(TypeError):
            self.reader.add_boolean_key('RED', wrong=True)
        # Dest requires a string
        with self.assertRaises(ValueError):
            self.reader.add_boolean_key('RED', dest=14)
        # Required requires a boolean
        with self.assertRaises(ValueError):
            self.reader.add_boolean_key('RED', required=None)
        # Repeat requires a boolean
        with self.assertRaises(ValueError):
            self.reader.add_boolean_key('RED', repeat=None)

class TestReadKeywords(TestCase):

    def setUp(self):
        self.r = InputReader()
        self.s1 = dedent('''\
                  blue
                  red
                  ''').split('\n')
        self.s2 = dedent('''\
                  blue
                  red
                  blue
                  ''').split('\n')

    def test_custom_default(self):
        # Test when individual keys define their own default
        self.r.add_boolean_key('blue')
        self.r.add_boolean_key('red')
        self.r.add_boolean_key('green')
        self.r.add_boolean_key('yellow', default=False)
        self.r.add_boolean_key('white', default=SUPPRESS)
        inp = self.r.read_input(self.s1)[0]
        self.assertTrue(inp.blue)
        self.assertTrue(inp.red)
        self.assertIsNone(inp.green)
        self.assertFalse(inp.yellow)
        with self.assertRaises(AttributeError):
            inp.white

    def test_required_correct(self):
        # A keyword that is not required does not appear... OK
        self.r.add_boolean_key('blue', required=False)
        self.r.add_boolean_key('red', required=True)
        self.r.add_boolean_key('green', required=False)
        inp = self.r.read_input(self.s1)[0]
        self.assertTrue(inp.blue)
        self.assertTrue(inp.red)
        self.assertIsNone(inp.green)

    def test_required_incorrect(self):
        # A keyword that is required does not appear... NOT OK
        self.r.add_boolean_key('blue', required=True)
        self.r.add_boolean_key('red', required=False)
        self.r.add_boolean_key('green', required=True)
        with self.assertRaises(ReaderError):
            inp = self.r.read_input(self.s1)[0]

    def test_cannot_repeat(self):
        # A keyword appears twice that shouldn't repeat... NOT OK
        self.r.add_boolean_key('blue', repeat=False)
        self.r.add_boolean_key('red', repeat=False)
        with self.assertRaisesRegexp(ReaderError, 'This key appears twice'):
            inp = self.r.read_input(self.s2)[0]

    def test_can_repeat(self):
        # A keyword appears twice that can repeat... OK
        self.r.add_boolean_key('blue', repeat=True)
        self.r.add_boolean_key('red', repeat=True)
        inp = self.r.read_input(self.s2)[0]
        self.assertEqual(inp.red, (True,))
        self.assertEqual(inp.blue, (True, True))

    def test_dest_different(self):
        # Keys are sent into an alternate destination
        self.r.add_boolean_key('blue', dest='berries')
        self.r.add_boolean_key('red', dest='apples')
        inp = self.r.read_input(self.s1)[0]
        self.assertTrue(inp.berries)
        self.assertTrue(inp.apples)

    def test_dest_same_incorrect(self):
        # Keys are sent into the same alternate destination
        self.r.add_boolean_key('blue', action='blue', dest='colors')
        self.r.add_boolean_key('red', action='red', dest='colors')
        # They are both sent to other dest, repeat is needed
        with self.assertRaisesRegexp(ReaderError, 'This key appears twice'):
            inp = self.r.read_input(self.s1)[0]

    def test_dest_same_correct(self):
        # Try the above with repeat=True
        self.r.add_boolean_key('blue', action='blue', dest='colors',
                               repeat=True)
        self.r.add_boolean_key('red', action='red', dest='colors',
                               repeat=True)
        inp = self.r.read_input(self.s1)[0]
        # Set is used below so that order doesn't matter
        self.assertEqual(set(inp.colors), set(('blue', 'red')))

    def test_depends_present(self):
        # Red depends on blue
        self.r.add_boolean_key('blue')
        self.r.add_boolean_key('red', depends='blue')
        inp = self.r.read_input(self.s1)[0]
        self.assertTrue(inp.blue)
        self.assertTrue(inp.red)

    def test_depends_missing(self):
        # Red depends on green, but green isn't present
        self.r.add_boolean_key('blue')
        self.r.add_boolean_key('red', depends='green')
        regex = 'The key "\w+" requires that "\w+" is also present'
        with self.assertRaisesRegexp(ReaderError, regex):
            inp = self.r.read_input(self.s1)[0]

# Function to export the tests in a controlled manner
def suite():
    suite = TestSuite()
    suite.addTest(TestLoader().loadTestsFromTestCase(TestClassKeywords))
    suite.addTest(TestLoader().loadTestsFromTestCase(TestCommonKeywords))
    suite.addTest(TestLoader().loadTestsFromTestCase(TestReadKeywords))
    return suite

if __name__ == '__main__':
    from unittest import main
    main()
