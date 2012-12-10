input_reader API
================

.. py:currentmodule:: input_reader

The ``input_reader``  Module
----------------------------

The :py:mod:`input_reader` module imports the classes :py:class:`InputReader`
and :py:class:`SUPPRESS`,
the :py:exc:`ReaderError` exception, and the functions :py:func:`abs_file_path`,
:py:func:`file_safety_check`, and :py:func:`range_check`.

The ``InputReader`` Class
-------------------------

.. autoclass:: InputReader

    .. automethod:: add_boolean_key

    .. automethod:: add_line_key

    .. automethod:: add_block_key

    .. automethod:: add_regex_line

    .. automethod:: add_mutually_exclusive_group

    .. automethod:: read_input

The ``Namespace`` Class
-----------------------

.. autoclass:: Namespace
    :members:

The ``ReaderError`` Exception
-----------------------------

.. autoexception:: ReaderError

The ``SUPPRESS`` Class
----------------------

.. autoclass:: SUPPRESS
