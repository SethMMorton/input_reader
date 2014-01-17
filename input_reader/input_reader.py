from __future__ import division, print_function
from .key_adder import _KeyAdder
from .helpers import ReaderError, SUPPRESS

__all__ = ['InputReader', 'ReaderError', 'SUPPRESS']

class InputReader(_KeyAdder):
    """\
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
        The default is :py:const:`['#']`.  Optional.
    :type comment: str or list
    :keyword case:
        Tells if the keys are case-sensitive or not.
        The default is :py:obj:`False`.  Optional.
    :type case: bool
    :keyword ignoreunknown:
        Ignore keys that are not defined.  The default is
        :py:obj:`False`.  Optional
    :type ignoreunknown: bool
    :keyword default:
        The default default that will be given when a
        key is created without a default.  Optional
    """

    def __init__(self, comment=['#'], case=False, ignoreunknown=False,
                 default=None):
        """Initiallize the :py:class:`InputReader` class."""
        super(InputReader, self).__init__(case=case)

        # Name (main is default)
        self.name = 'main'

        # What constitutes a comment?
        if isinstance(comment, str):
            comment = [comment]
        self._comment = comment
        try:
            for x in self._comment:
                if not isinstance(x, str):
                    raise ValueError ('comment value must be a str, '
                                      'given '+repr(x))
        except TypeError:
            raise ValueError ('comment value must be a str, '
                              'given '+repr(self._comment))

        # Ignore unknown keys?
        self._ignoreunknown = ignoreunknown
        if not isinstance(self._ignoreunknown, bool):
            raise ValueError ('ignoreunknown value must be a bool, '
                              'given '+repr(self._ignoreunknown))

        # The default default
        self._default = default

    def read_input(self, filename):
        """\
        Reads in the input from a given file using the supplied rules.

        :argument filename:
            The name of the file to read in, :py:mod:`StringIO` of input,
            or list of strings containing the input itself.
        :rtype: :py:class:`Namespace`: This class contains the read-in data
            each key is stored as members of the class.
        :exception:
            :py:exc:`ReaderError`: Any known errors will be raised with
            this custom exception.
        """

        # Read in the file, removing comments and extra whitespace/newlines
        f = self._read_in_file(filename)

        # Parse this key level, recursively reading lower levels
        i, namespace = self._parse_key_level(f, 0)

        # If there is any post-processing to do, do it now
        self.input_file = f  # In case the post-processing wants to keep the input
        self.filename = filename
        self.post_process(namespace)

        return namespace

    def post_process(self, namespace):
        """\
        Perform post-processing of the data collected from the input file.

        This is a "virtual" method... does nothing and is intended to be
        re-implemented in a subclass.
        """
        pass

    def _read_in_file(self, filename):
        """Store the filename as a list"""

        f = []
        # Assume a filename was given
        try:
            fl = [x.rstrip() for x in open(filename)]
        except (IOError, OSError) as e:
            raise ReaderError ('Cannot read in file "'+filename+'":'+str(e))
        except TypeError:
            # Assume a StringIO object was given
            try:
                fl = filename.getvalue().split('\n')
            except AttributeError:
                # Assume an iterable of strings was given
                try:
                    fl = [x.rstrip() for x in filename]
                except AttributeError:
                    raise ValueError ('Unknown object passed to '
                                      'read_input: '+repr(filename))

        # Read in the data
        for line in fl:
            # Remove comments
            for com in self._comment:
                if com in line:
                    line = line.partition(com)[0]
            # Add this to the list
            f.append(line.strip())

        return f

