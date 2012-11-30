from unittest import TestSuite, TextTestRunner
import test_constructor
import test_keywords
import test_read_file
import test_boolean
import test_line

def loadAllTests():
    suite = TestSuite()
    suite.addTest(test_constructor.suite())
    suite.addTest(test_keywords.suite())
    suite.addTest(test_read_file.suite())
    suite.addTest(test_boolean.suite())
    suite.addTest(test_line.suite())
    return suite

def run_tests():
    TextTestRunner(verbosity=2).run(loadAllTests())

if __name__ == "__main__":
    run_tests()
