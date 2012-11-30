from input_reader import InputReader, ReaderError, SUPPRESS
from unittest import TestCase, TestSuite, TestLoader
from textwrap import dedent

class TestAddBoolean(TestCase):

    def setUp(self):
        self.reader = InputReader()

    def test_missing_keyname(self):
        with self.assertRaises(TypeError):
            self.reader.add_boolean_key()
        with self.assertRaises(TypeError):
            self.reader.add_boolean_key(action=True)

    def test_correct_call(self):
        r = self.reader.add_boolean_key('red')
        self.assertEqual(r.name, 'red')
        self.assertTrue(r._action)
        b = self.reader.add_boolean_key('blue', action=False)
        self.assertEqual(b.name, 'blue')
        self.assertFalse(b._action)
        def fun(x):
            return x*x
        c = self.reader.add_boolean_key('green', action=fun)
        self.assertIs(c._action, fun)

    def test_name(self):
        with self.assertRaisesRegexp(ReaderError, 'Keyname must be str'):
            self.reader.add_boolean_key(23)

    def test_repeat(self):
        # You cannot repeat keys
        self.reader.add_boolean_key('red')
        regex = r'The key \w+ has been defined twice'
        with self.assertRaisesRegexp(ReaderError, regex):
            self.reader.add_boolean_key('red')

class TestReadBoolean(TestCase):

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
    suite.addTest(TestLoader().loadTestsFromTestCase(TestAddBoolean))
    suite.addTest(TestLoader().loadTestsFromTestCase(TestReadBoolean))
    return suite

if __name__ == '__main__':
    from unittest import main
    main()
