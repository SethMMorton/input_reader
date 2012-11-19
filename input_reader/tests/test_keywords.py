from input_reader import InputReader, ReaderError, Namespace
from unittest import TestCase, TestSuite, TestLoader

class TestKeywords(TestCase):

    def setUp(self):
        self.reader = InputReader()

    def test_use_defaults(self):
        self.reader.add_boolean_key('RED', action=True)

    def test_dont_use_defaults(self):
        self.reader.add_boolean_key('RED', 
                                    action=True,
                                    required=False,
                                    default=None,
                                    dest=None,
                                    depends=None,
                                    repeat=False,
                                    overwritedefault=False)

    def test_incorrect_option(self):
        with self.assertRaises(TypeError):
            self.reader.add_boolean_key('RED', wrong=True)

    def test_dest(self):
        # Dest requires a string
        with self.assertRaises(ValueError):
            self.reader.add_boolean_key('RED', dest=14)
        self.reader.add_boolean_key('RED', dest='color')

# Function to export the tests in a controlled manner
def suite():
    suite = TestSuite()
    suite.addTest(TestLoader().loadTestsFromTestCase(TestKeywords))
    return suite

if __name__ == '__main__':
    from unittest import main
    main()
