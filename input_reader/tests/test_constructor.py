from input_reader import InputReader, ReaderError
from unittest import TestCase, TestSuite, TestLoader

class TestConstructor(TestCase):

    def test_empty_costructor(self):
        ir = InputReader()
        self.assertEqual(ir.name, 'main')
        self.assertEqual(ir._comment, ['#'])
        self.assertFalse(ir._case)
        self.assertFalse(ir._ignoreunknown)
        self.assertIsNone(ir._default)

    def test_set_defaults(self):
        ir = InputReader(comment=['#'], 
                         case=False, 
                         ignoreunknown=False,
                         default=None)
        self.assertEqual(ir.name, 'main')
        self.assertEqual(ir._comment, ['#'])
        self.assertFalse(ir._case)
        self.assertFalse(ir._ignoreunknown)
        self.assertIsNone(ir._default)

    def test_set_not_defaults(self):
        ir = InputReader(comment='//', 
                         case=True, 
                         ignoreunknown=True,
                         default=False)
        self.assertEqual(ir.name, 'main')
        self.assertEqual(ir._comment, ['//'])
        self.assertTrue(ir._case)
        self.assertTrue(ir._ignoreunknown)
        self.assertFalse(ir._default)

    def test_incorrect_option(self):
        # 'wrong' keyword does not exist
        with self.assertRaises(TypeError):
            InputReader(wrong=True)
        # Case requires a bool
        with self.assertRaises(ValueError):
            InputReader(case='spam')
        # Ignoreunknown requires a bool
        with self.assertRaises(ValueError):
            InputReader(ignoreunknown=15.8)
        # Comment requires a strings or list of strings
        with self.assertRaises(ValueError):
            InputReader(comment=14.5)
        with self.assertRaises(ValueError):
            InputReader(comment=[14.5])
        with self.assertRaises(ValueError):
            InputReader(comment=['#', 14.5])

# Function to export the tests in a controlled manner
def suite():
    suite = TestSuite()
    suite.addTest(TestLoader().loadTestsFromTestCase(TestConstructor))
    return suite

if __name__ == '__main__':
    from unittest import main
    main()
