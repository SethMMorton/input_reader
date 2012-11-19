from input_reader import InputReader, ReaderError, Namespace, SUPPRESS
from unittest import TestCase, TestSuite, TestLoader

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
        self.assertFalse(b._overwritedefault)

    def test_dont_use_defaults(self):
        b = self.reader.add_boolean_key('red', True,
                                        required=False,
                                        default=None,
                                        dest=None,
                                        depends=None,
                                        repeat=False,
                                        overwritedefault=False)
        self.assertFalse(b._required)
        self.assertIsNone(b._default)
        self.assertIsNone(b._dest)
        self.assertIsNone(b._depends)
        self.assertFalse(b._repeat)
        self.assertFalse(b._overwritedefault)

    def test_custom_values(self):
        b = self.reader.add_boolean_key('red', True,
                                        required=True,
                                        default='BANANA',
                                        dest='fruit',
                                        depends='something',
                                        repeat=True,
                                        overwritedefault=True)
        self.assertTrue(b._required)
        self.assertEqual(b._default, 'BANANA')
        self.assertEqual(b._dest, 'fruit')
        self.assertEqual(b._depends, 'something')
        self.assertTrue(b._repeat)
        self.assertTrue(b._overwritedefault)

    def test_incorrect_option(self):
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
        # Overwritedefault requires a boolean
        with self.assertRaises(ValueError):
            self.reader.add_boolean_key('RED', overwritedefault=None)

class TestClassKeywords(TestCase):

    def test_suppress(self):
        ir = InputReader(default=SUPPRESS)
        b = ir.add_boolean_key('RED')
        self.assertIs(b._default, SUPPRESS)

    def test_str_default(self):
        ir = InputReader(default='roses')
        b = ir.add_boolean_key('RED')
        self.assertEqual(b._default, 'roses')

    def test_case(self):
        ir = InputReader(case=True)
        l = ir.add_line_key('RED')
        self.assertTrue(l._case)

# Function to export the tests in a controlled manner
def suite():
    suite = TestSuite()
    suite.addTest(TestLoader().loadTestsFromTestCase(TestCommonKeywords))
    suite.addTest(TestLoader().loadTestsFromTestCase(TestClassKeywords))
    return suite

if __name__ == '__main__':
    from unittest import main
    main()
