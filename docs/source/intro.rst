.. default-domain:: py

The :mod:`input_reader` module
=================================

.. module:: input_reader

:mod:`input_reader` is a python module that provides tools to help read the
contents of a block-type input file. If you have ever written a custom
parser for an input file, you will know that there are many non-obvious
challenges that must be overcome, mostly in the realm of error handling.
The challenges include dealing with unknown or missing keys, incorrect
input (:obj:`str` vs :obj:`float`), data storage, and parse ordering.
Handling these issues can make a seemingly easy task become a complicated 
mess that obscures the intent of your program.  

The :mod:`input_reader` module was designed with a balance of conciseness
and clarity in mind, as well as a strong resemblance to the :mod:`argparse`
module in the python standard library.  With :mod:`input_reader`, you can
define how to read your input files in a relatively small number of lines
(~1-2 per keyword) that are (for the most part) easy to read.  

This documentation is written in a combination API/tutorial style.  You will
be guided through creating a generic :mod:`input_reader` definition for a 
generic input file while being introduced to the functionality of the 
:class:`InputReader` one piece at a time.  

Exported objects
----------------

:mod:`input_reader` exports the following objects by default
(i.e. with ``from input_reader import *``):

1. The class :class:`InputReader`
    This is the workhorse of the :mod:`input_reader` module.  It is used to
    define what is to be read in and also read the input file.

2. The exception :exc:`ReaderError`
    This exception is raised when an error occurs reading in the file.

3. The class :class:`SUPPRESS`
    This is an empty class that is used to specify that a key not included in
    the input file should not be included in the :class:`Namespace`.

4. The function :func:`abs_file_path`
    This function returns the absolute path of a file, substituting any
    environment variables or the ``~`` character correctly.

5. The function :func:`file_safety_check`
    Checks that a file is "safe", i.e. it exists and can be opened.

6. The function :func:`range_check`
    Checks that a given range is valied, i.e. the low value is lower than the
    high value.

Optionally, the class :class:`Namespace` may be imported by name.  This
class contains all the data read into the input file.
