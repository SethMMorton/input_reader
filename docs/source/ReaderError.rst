.. default-domain:: py
.. currentmodule:: input_reader

The :exc:`ReaderError` exception
===================================

.. autoexception:: ReaderError

Whenever there is an error parsing the input file, a :exc:`ReaderError`
exception will be raised.  This will also be raised if there an
:class:`InputReader`-specific error in the key definitions, such as defining
the same key twice.  A common use case might be:

.. code::

    from input_reader import InputReader, ReaderError
    reader = InputReader()
    # key definitions go here #
    try:
        inp = reader.read_file('user_inputs.txt')
    except ReaderError as e:
        from sys import exit
        exit(str(e))
