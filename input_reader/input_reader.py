from __future__ import division, print_function
from keylevel import _KeyLevel
from helpers import ReaderError, SUPPRESS, Namespace

__all__ = ['InputReader', 'ReaderError', 'SUPPRESS']

class InputReader(_KeyLevel):
    '''\
    :py:class:`InputReader` is a class that is designed to read in
    an input file and return the information contained based on rules
    supplied to the class using a syntax similar to what is used in 
    the :py:mod:`argparse` module in the Python standard library.


    :py:class:`InputReader` accepts blocks-type, line-type and
    boolean-type keys, mutually exclusive groups, required keys,
    defaults, and more.

    :keyword comment:
        Defines what is a comment in the input block.
        This can be a single string or a list of strings.
        The default is *['#']*.
    :type comment: str or list, optional
    :keyword case:
        Tells if the keys are case-sensitive or not.
        The default is :py:const:`False`.
    :type case: bool, optional
    :keyword ignoreunknown:
        Ignore keys that are not defined.  The default is
        :py:const:`False`.
    :type ignoreunknown: bool, optional
    :keyword default:
        The default default that will be given when a
        key is created without a default.
    :type default: optional
    '''

    def __init__(self, comment=['#'], case=False, ignoreunknown=False,
                 default=None):
        '''Initiallize the :py:class:`InputReader` class.'''
        _KeyLevel.__init__(self, case=case)

        # Name (main is default)
        self.name = 'main'

        # What constitutes a comment?
        if not isinstance(comment, list):
            comment = [comment]
        self._comment = comment

        # Ignore unknown keys?
        self._ignoreunknown = ignoreunknown

        # The default default
        self._default = default

    def read_input(self, filename):
        '''\
        Reads in the input from a given file using the supplied rules.

        :argument filename:
            The name of the file to read in.
        :type filename: str
        :rtype: :py:class:`Namespace`: This class contains the read-in data
            each key is stored as members of the class.
        :exception:
            :py:exc:`ReaderError`: Any known errors will be raised with
            this custom exception.
        '''

        # Read in the file, removeing comments and extra whitespace/newlines
        f = self._read_in_file(filename)

        # Parse this key level, recursively reading lower levels
        i, namespace = self._parse_key_level(f, 0)
        namespace.filename = filename
        namespace._order.append('filename')
        return namespace, f

    def _read_in_file(self, filename):
        '''Store the filename as a list'''

        # Read in the file into a list
        f = []
        try:
            with open(filename) as fl:
                for line in fl:
                    # Remove comments
                    for com in self._comment:
                        if com in line:
                            line = line.partition(com)[0]
                    # Add this to the list
                    f.append(line.strip())

        except (IOError, OSError) as e:
            raise ReaderError ('Cannot read in file '+filename+':'+str(e))

        return f

