.. default-domain:: py
.. currentmodule:: input_reader

.. _capi:

C-API
=====

A C/C++ api has been provided for developers who are embedding Python into
their program and wish to use the :mod:`input_reader` module to parse
an input file.  The API provides functions that make it easy to set up
the Python environment within your C program, and to extract information
from the :class:`Namespace` object returned from 
:meth:`InputReader.read_input` without having to worry about reference
counting (when possible).

:attr:`InputReader.include_path`
--------------------------------

This is a "header-only" library, meaning that you only need to include the
header file supplied with this package to use it.  You can determine the path
to this header programatically using :attr:`InputReader.include_path`.  In
`bash` this might look like

.. code::

    $ cc -I$(python -c "import input_reader; print input_reader.include_path") -c a.c -o a.o

Or, to reduce the number of calls to the Python interpreter for large projects,

.. code::

    $ INPUT_READER=$(python -c "import input_reader; print input_reader.include_path")
    $ cc -I$INPUT_READER -c a.c -o a.o
    $ cc -I$INPUT_READER -c b.c -o b.o


The C Functions
---------------

.. doxygenfile:: input_reader.h
   :project: input_reader
   :no-link: