Changelog
---------

03-01-2014 v. 1.2.2
'''''''''''''''''''

    - Cleaned up import blocks
    - Added spaces between defs/classes (cosmetic)

01-29-2014 v. 1.2.1a
''''''''''''''''''''

    - Fixed bug where strings were compared to unicode instead of basestring in python2.x

01-26-2014 v. 1.2.1
'''''''''''''''''''

    - All calls are completely python2/3 compatible
    - Python2 uses unicode literals
    - Files use unicode encoding

01-16-2014 v. 1.2.0
'''''''''''''''''''

    - Added input_reader.h to provide easy C interface to this python module
    - Added include_path attribute to input_reader module for C compilations
    - Removed distribute_setup.py (cause install problems for some)
    - Unit tests pass for both Python 2.7 and Python 3.x
    - Updated documentation

04-13-2013 v. 1.1.1
'''''''''''''''''''

    - Added the filename attribute to the InputReader class

01-25-2013 v. 1.1.0
'''''''''''''''''''

    - Increased code coverage of tests to ~98%
    - Refactored code to reduce copy/paste and be open for future improvements

01-14-2013 v. 1.0.2
'''''''''''''''''''

    - Added input_file attribute to InputReader class
    - Fixed typo in documentation
    - Updated version updating code

12-22-2012 v. 1.0.1
'''''''''''''''''''

    - Fixed error in MANIFEST.in

12-16-2012 v. 1.0.0
'''''''''''''''''''

    - Fixed bugs in unit tests
    - Finished documentation with doctests
    - Added a post_process method to InputReader that can be subclassed
    - Made improvements to the setup process

12-3-2012 v. 0.9.1
''''''''''''''''''

    - Added unit tests
    - Added extra checks for bad input
