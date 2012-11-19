from input_reader import InputReader, ReaderError, Namespace
from unittest import TestCase, TestSuite, TestLoader

class TestConstructor(TestCase):

    def test_empty_costructor(self):
        InputReader()

    def test_set_defaults(self):
        InputReader(comment=['#'], 
                    case=False, 
                    ignoreunknown=False,
                    default=None)

    def test_set_not_defaults(self):
        InputReader(comment='//', 
                    case=True, 
                    ignoreunknown=True,
                    default=False)

    def test_incorrect_option(self):
        # This should fail
        with self.assertRaises(TypeError):
            self.cls = InputReader(wrong=True)

# Function to export the tests in a controlled manner
def suite():
    suite = TestSuite()
    suite.addTest(TestLoader().loadTestsFromTestCase(TestConstructor))
    return suite

if __name__ == '__main__':
    from unittest import main
    main()
