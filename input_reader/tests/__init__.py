from unittest import TestSuite, TextTestRunner
import test_constructor
import test_keywords
import test_boolean

def loadAllTests():
    suite = TestSuite()
    suite.addTest(test_constructor.suite())
    suite.addTest(test_keywords.suite())
    suite.addTest(test_boolean.suite())
    return suite

def run_tests():
    TextTestRunner().run(loadAllTests())

if __name__ == "__main__":
    run_tests()
