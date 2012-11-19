from input_reader import InputReader, ReaderError, Namespace
from unittest import TestCase, TestSuite, TestLoader

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

class TestReadBoolean(TestCase):
    pass

# Function to export the tests in a controlled manner
def suite():
    suite = TestSuite()
    suite.addTest(TestLoader().loadTestsFromTestCase(TestAddBoolean))
    suite.addTest(TestLoader().loadTestsFromTestCase(TestReadBoolean))
    return suite

if __name__ == '__main__':
    from unittest import main
    main()
