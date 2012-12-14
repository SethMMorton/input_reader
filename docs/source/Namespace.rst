.. default-domain:: py
.. currentmodule:: input_reader

The :class:`Namespace` class
===============================

.. autoclass:: Namespace
   :members:

In general, it is unlikely you need to use many of these methods unless you
have to manually modify the :class:`Namespace`.  In general you will likely
be using the namespace as given below:

.. code::

    # Typically, you won't populate the Namespace yourself.  It will be done
    # for you with the read_input method.  Don't worry about the next three
    # lines
    from input_reader import Namespace
    inp = Namespace(red=True, blue=False, green=True)
    inp.finalize()

    # Here is where the typical use case
    if inp.red: # True
        print 'red'
    if inp.blue: # False
        print 'blue'
    if 'green' in inp: # True
        print 'Maybe green'
    if 'yellow' in inp: # False
        print 'Maybe yellow'
    
    # You may need to add a key, since the Namespace can act as a safe way to
    # pass around global variables
    inp.add('yellow', True)
    if 'yellow' in inp: # True
        print 'Maybe yellow'

    # Of course you can iterate over the keys if you want
    for key in inp.keys():
        print key, key in inp
