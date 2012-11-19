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
        self.reader.add_boolean_key('RED')
        self.reader.add_boolean_key('BLUE', action=False)

# Function to export the tests in a controlled manner
def suite():
    suite = TestSuite()
    suite.addTest(TestLoader().loadTestsFromTestCase(TestAddBoolean))
    return suite

if __name__ == '__main__':
    from unittest import main
    main()
