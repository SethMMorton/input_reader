.. py:currentmodule:: input_reader

The :py:class:`InputReader` Class
=================================

.. autoclass:: InputReader

The :py:class:`InputReader` allows the user to define the keys to be read in
from the input file, and also reads the input file to parse the data.  

In the simplest use case, you may simply instantiate :py:class:`InputReader`
with no aruments, as in

.. code:: python

    from input_reader import InputReader
    reader = InputReader()

The above instantiation assumes that the ``#`` character will be a comment in
the input file, the input file is case-insensitive, unknown keys in the input
file will cause the parsing to fail, and any key not found in the input file
will be defaulted to :py:obj:`None`.  

If an unknown parameter is passed to :py:class:`InputReader`, a
:py:exc:`TypeError` will be raised.  If an inappropriate value is passed to a
parameter (i.e. non :py:obj:`bool` to *case*), a :py:exc:`ValueError` will be
raised. 

:py:class:`InputReader` options
-------------------------------

There are four optional parameters to :py:class:`InputReader`: *case*,
*comment*, *ignoreunknown*, and *default*.  The defaults for these are
described below:

.. code:: python

    # The following are equivalent
    r1 = InputReader(comment=['#'], case=False, ignoreunknown=False,
                     default=None)
    r2 = InputReader()

Of course, the user may choose to change these default values.

.. _comment:

comment
'''''''

The comment option specifies the characters that will be interpreted as a
comment by :py:class:`InputReader`.  As mentioned above, the default is ``#``.
You are free to choose as many characters as you wish.  If you choose one
character, it may be given as a string or as a single element list of strings
as shown below:

.. code:: python

    # The following are equivalent 
    r1 = InputReader(comment='%')
    r2 = InputReader(comment=['%'])

If you wish to allow multiple comment characters, you *must* place them in a
list of strings:

.. code:: python

    # Multiple comment characters.  A comment need not be one characgter long
    reader = InputReader(comment=['#', '//'])

No matter the definition, comments will work just as you might expect from
python: they can appear anywhere in the line, and only characters after the
comment are ignored.

.. _case_input:

case
''''

When case sensitivity is turned off (the default), all lines in the input file
are converted to lower case, and all keys are converted to lower case.
In general, it is best to let input files be case-insensitive, but there may be
a reason this is not desireable.  To turn on case-sensitivity, use

.. code:: python

    reader = InputReader(case=True)

This will cause the input file to be read in as given, and keys to be kept in
the case that is given.

.. _ignoreunknown_input:

ignoreunknown
'''''''''''''

It is best not to assume your end-users will do everything correctly.  For
example, it is common to accidentally misspell a keyword.  You would likey wish
to alert the user of this error instead of continuing with the calculation and
giving bad results.  For this reason, the *ignoreunknown* key is defaulted to
:py:obj:`False`.  Any key that is not known to :py:class:`InputReader` causes
an error to be raised.  If this is not desireable for your use-case, you can
disable this with:

.. code:: python

    reader = InputReader(ignoreunknown=True)

.. _default_input:

default
'''''''

If a key is defined, but does not appear in the input file,
:py:class:`InputReader` will assign a default value to it.  By default, this is
:py:obj:`None`.  This is useful because one can check that the key appeared
in the input file with ``if inp.key is not None``.  However, it may be
desireable to have a different default value, such as :py:obj:`False`,
:py:obj:`0`, or :py:obj:`''`. To change the default value, use:

.. code:: python

    reader = InputReader(default=False)

Alternatively, you can request that keys not appearring in the input file be
ommited from the :py:class:`Namespace`.  This would raise a
:py:exc:`AttributeError` when trying to access a non-existant key, or you can
check that the key exists with ``if key in inp``.   To do this, use:

.. code:: python

    from input_reader import InputReader, SUPPRESS
    reader = InputReader(default=SUPPRESS)

.. _read_input:

:py:meth:`~InputReader.read_input`
----------------------------------

.. automethod:: InputReader.read_input

:py:meth:`~InputReader.read_input` does only one thing: parse an input file
based on the key rules given to it.  In the coming sections, we will discuss
how to define these rules, but it will be helpful first to know how we can
parse input files.  

:py:meth:`~InputReader.read_input` accepts one of three input types: a filename,
a :py:mod:`StringIO` object, or a list of strings.  Let's say we want to parse
the following input::

    red
    blue
    green

This can be sent to the input reader in one of three ways.  First, we can
create a text file containing this data and parse the file itself:

.. code:: python

    from input_reader import InputReader
    
    with open('user_input.txt', 'w') as ui:
        ui.write('red\n')
        ui.write('blue\n')
        ui.write('green\n')

    reader = InputReader()
    # Code that defines the keys goes here #
    inp = reader.read_input('user_input.txt')
    print inp
    # prints Namespace(red=True, blue=True, green=True)

Alternatively, we could use the :py:mod:`StringIO` object:

.. code:: python

    from input_reader import InputReader
    from StringIO import StrinIO

    io = StrinIO()
    io.write('red\n')
    io.write('blue\n')
    io.write('green\n')
    
    reader = InputReader()
    # Code that defines the keys goes here #
    inp = reader.read_input(io)
    print inp
    # prints Namespace(red=True, blue=True, green=True)
    
Last, you can simply define a list of strings.


.. code:: python

    from input_reader import InputReader

    lst = ['red', 'blue', 'green']
    
    reader = InputReader()
    # Code that defines the keys goes here #
    inp = reader.read_input(lst)
    print inp
    # prints Namespace(red=True, blue=True, green=True)
    
Of course, the most common use case is to parse a file as it is unlikely your
users will write python code as their input file; however, these alternate
modes of parsing are provided easy testing of your key definitions.

.. _boolean_key:

:py:meth:`~InputReader.add_boolean_key`
---------------------------------------

.. automethod:: InputReader.add_boolean_key

A boolean key a key in which the presence of the key triggers an action; there
are no arguments to a boolean key in the input file.  Typically, the presence
of a boolean key makes that key :py:obj:`True`, and the absence will make it
false.  

Let's say that you are defining an input file for a physics
program.  You might want the user to specify the units that are assumed in the
input file.  Let's say the unit choices are meters, centimeters, kilometers, or
milimeters. If the key ``centimeters`` is present, then the units are
centimeters.   Maybe we also want the user to specify if degrees will be used
(otherwise we assume radians). We might specify this set of boolean keys in 
this way:

.. code:: python

    from input_reader import InputReader
    reader = InputReader()
    reader.add_boolean_key('meters')
    reader.add_boolean_key('centimeters')
    reader.add_boolean_key('kilometers')
    reader.add_boolean_key('milimeters')
    reader.add_boolean_key('degrees')
    inp = reader.read_input('user_input.txt')

    if inp.meters:
        # calculate as meters
        pass
    elif inp.centimeters:
        # calculate as centimeters
        pass
    elif inp.kilometers:
        # calculate as kilometers
        pass
    elif inp.milimeters:
        # calculate as milimeters
        pass
    else:
        # some default or error
        pass

    if inp.degrees:
        # calculate in degrees
        pass
    else:
        # calculate in radians
        pass

Of course, the above definitions do not forbid both ``meters`` and
``centimeters`` to
be defined simultaneously; this problem will be discussed in the
:py:meth:`~InputReader.add_mutually_exclusive_group` section. 

There are several options available to customize
:py:meth:`~InputReader.add_boolean_key`.  The default values are as follows:

.. code:: python

    # The following are equivalent
    reader.add_boolean_keu('feet')
    reader.add_boolean_key('feet', action=True, default=None, dest=None,
                           required=False, depends=None, repeat=False)

.. _action:

action
''''''

The *action* option is what the key will be set to in the
:py:class:`Namespace`.  By default it is :py:obj:`True`.  However, in some
scenarios it may be advantagous to set this to a string or a number.  You can
even set it to a function.  For example, lets say that our physics program did
all calculations internally in meters.  It would be advantagous then to use our
boolean keys to define a function to convert from the input unit to the
internal unit.

.. code:: python

    from input_reader import InputReader
    reader = InputReader()
    reader.add_boolean_key('meters', action=lambda x: x)
    reader.add_boolean_key('centimeters', action=lambda x: 0.01 * x)
    reader.add_boolean_key('kilometers', action=lambda x: 1000 * x)
    reader.add_boolean_key('milimeters', action=lambda x: 0.001 * x)
    inp = reader.read_input('user_input.txt')

    if inp.meters:
        x = inp.meters(input_data)
    # etc...

.. _line_key:

:py:meth:`~InputReader.add_line_key`
------------------------------------

.. automethod:: InputReader.add_line_key

The line key is likely do be the work horse of your input file.  It allows
you to consisely specify a key and its parameters in a flexible way.  There are
a lot of things to think about when it comes to line keys,  so we'll take it
slowly.  First, the options *dest*, *default*, *depends*, *required*, and 
*repeat* all have the same description that was given for the boolean key.  
It is much more likely that you will use the *required* option for a line key
than for a boolean key.  We will explore this in a bit more detail later.

.. _type_line:

type
''''

.. _single_type:

Specifying one type
"""""""""""""""""""

The *type* key specifies the python types that are to be read in on the line
key.  The allowed types are :py:obj:`int`, :py:obj:`float`, :py:obj:`str`
:py:obj:`None`, an explicit :py:obj:`int` (i.e. :py:const:`4`), explicit 
:py:obj:`float` (i.e. :py:const:`5.4`) explicit :py:obj:`str` 
(i.e. :py:const:`"hello"`), or a compiled regular expression object.  The
default for *type* is :py:obj:`str`, so 

.. code:: python

    # The following are equivalent
    reader.add_line_key('red')
    reader.add_line_key('red', type=str)

Let's say
we want the color red to accept a :py:obj:`str`, the color blue to accept an
:py:obj:`int`, and the color green to accept a :py:obj:`float`.  We would
specify these requirements as

.. code:: python

    from input_reader import InputReader
    from StringIO import StringIO
    reader = InputReader()
    reader.add_line_key('red', type=str)
    reader.add_line_key('blue', type=int)
    reader.add_line_key('green', type=float)

    io = StringIO()
    io.write('red rose\n')
    io.write('blue 52\n')
    io.write('green 3.14\n')

    inp = reader.read_input(io)
    print isinstance(inp.red, str) # True
    print isinstance(inp.blue, int) # True
    print isinstance(inp.green, float) # True
    print inp.red # rose
    print inp.blue # 52
    print inp.green # 3.14

Perhaps you want ``blue`` to accept only the numbers :py:const:`52`,
:py:const:`34`, and :py:const:`63`.  Also, you want ``red`` to only accept the
strings :py:const:`"rose"`, :py:const:`"robin"`, and :py:const:`"nose"`.
Further, if the ``green`` input is not a :py:obj:`float`, then just make it a
:py:obj:`str` (:py:obj:`str` acts as a catch-all).  Our definition would change
to

.. code:: python

    from input_reader import InputReader, ReaderError
    from StringIO import StringIO
    reader = InputReader()
    # NOTE: Notice these choices are given in a tuple, not a list
    # This is actually an important distiction
    reader.add_line_key('red', type=('rose', 'robin', 'nose'))
    reader.add_line_key('blue', type=(52, 34, 63))
    reader.add_line_key('green', type=(float, str))

    # OK
    io = StringIO()
    io.write('red robin\n')
    io.write('blue 34\n')
    io.write('green funky\n')
    inp = reader.read_input(io)

    # Error!
    io = StringIO()
    io.write('red radish\n') # radish is not a choice
    io.write('blue 21\n')    # 21 is not a choice
    io.write('green funky\n')
    try: # ReaderError will be raised because of invalid choices
        inp = reader.read_input(io)
    except ReaderError:
        pass

Note that in the definition of ``green`` :py:obj:`str` was placed *after*
:py:obj:`float`.  You will want to place :py:obj:`str` after all other options
because everything on the input can be a :py:obj:`str` and the types are
checked in the order they are given.  If instead ``type=(str, float)`` was
given, objects would always be returned as a :py:obj:`str`, even if it could be
a :py:obj:`float`.

Perhaps it is valid for a user to specify :py:const:`"none"`.  For
example, maybe sometimes it makes sense to specify that ``red`` has no value.
In this case it is OK to give :py:obj:`None` as a type.  This will set the
variable to :py:obj:`None` if :py:const:`"none"` is given in the input file.

.. code:: python

    from input_reader import InputReader
    reader = InputReader()
    reader.add_line_key('red', type=('rose', 'robin', 'nose', None))

    inp = reader.read_input(['red rose'])
    print inp.red # rose
    inp = reader.read_input(['red none'])
    print inp.red is None # True

There are always times when you may want more specificity than the native
python types provide, but it is impractical to specify all possibilities.  For
this purpose, you may also give a compiled regular expression object as a type.

.. code:: python

    from input_reader import InputReader, ReaderError
    import re
    reader = InputReader()
    reader.add_line_key('red', type=re.compile(r'silly\d+\w*thing'))

    # OK
    inp = reader.read_input(['red silly5314whatisthisthing'])
    print inp.red # silly5314whatisthisthing
    
    # Error
    try: # ReaderError raised because regular expression does not match
        inp = reader.read_input(['red silly542.0notsogood'])
    except ReaderError:
        pass

.. _multiple_types:

Specifying multiple types
"""""""""""""""""""""""""

In many situations, you will want the line key to accept multiple parameters.
You can specify this by supplying a list of types.  For example,

.. code:: python

    from input_reader import InputReader, ReaderError
    reader = InputReader()
    reader.add_line_key('red', type=[str, int, ('car', 'robin'), float])
    inp = reader.read_input(['red candy 51 car 62.4'])
    try: # ReaderError is raised because there aren't enough parameters
        inp = reader.read_input(['red apple 46 rose'])
    except ReaderError:
        pass
    try: # ReaderError is raised because there are too many parameters
        inp = reader.read_input(['red apple 46 rose 74.6 excess'])
    except ReaderError:
        pass

In the above example, red takes 4 parameters; the number of parameters is the
length of the :py:obj:`list`.  (When you define a single parameter such as
``type=str``, it is converted internally to ``type=[str]``).
Each of these parameters follows
the rules discussed for a single type as described above.  It is important to
note that a :py:obj:`list` was used to define multiple type.  The
:py:obj:`tuple` vs. :py:obj:`list` disctintion is very important for the *type*
option; a :py:obj:`tuple` is used to define parameter *choices*, and a
:py:obj:`list` is used to define multiple parameters.  It is not legal to have
a :py:obj:`list` inside of a :py:obj:`list` for the *type* object. 

If you do not wish to define *any* *type* parameters, you can give
:py:obj:`None`.  This may be useful when using the *glob* or *keywords*
options.

.. _glob_type:

glob
''''

.. _keyword_type:

keywords
''''''''

.. _case_type:

case
''''

.. _block_key:

:py:meth:`~InputReader.add_block_key`
-------------------------------------

.. automethod:: InputReader.add_block_key

.. _regex_line:

:py:meth:`~InputReader.add_regex_line`
--------------------------------------

.. automethod:: InputReader.add_regex_line

.. _common_options:

Common Options
--------------

The methods :py:meth:`~InputReader.add_boolean_key`, 
:py:meth:`~InputReader.add_line_key`, :py:meth:`~InputReader.add_block_key`,
and :py:meth:`~InputReader.add_regex_line` all share a set of options:
*dest*, *default*, *depends*, *required*, and *repeat*.  They will be discussed
together here.

.. _dest_common:

dest
''''

Of course, the above example is still not quite satisfactory, because our
conversion function is still on one of four different variables.  It would be
more convenient to have a single variable to place this group of boolean keys
into. For this, we use the *dest* option.

.. code:: python

    from input_reader import InputReader
    reader = InputReader()
    reader.add_boolean_key('meters', action=lambda x: x, dest='conversion')
    reader.add_boolean_key('centimeters', action=lambda x: 0.01*x, dest='conversion')
    reader.add_boolean_key('kilometers', action=lambda x: 1000*x, dest='conversion')
    reader.add_boolean_key('milimeters', action=lambda x: 0.001*x, dest='conversion')
    inp = reader.read_input('user_input.txt')
    
    # No matter what boolean key was used, the conversion function is under
    # "conversion".  The original key names have been removed.
    x = inp.conversion(input_data)
    if 'meters' in inp:
        print "This will never print"

A :py:exc:`ReaderError` would be raised if both ``meters`` and ``centimeters``
had been defined in the input file.  As you will see later, it is often more
advantageous to use *dest* in conjunction with 
:py:meth:`~InputReader.add_mutually_exclusive_group` because it provides more
protection against bad user input for keys that are grouped together.

.. _default_common:

default
'''''''

This is the default value of the boolean key.  It defaults to :py:obj:`None`.

.. _depends_common:

depends
'''''''

The *depends* option specifies that in order for this key to be valid, another
key must also appear in the input.  For example, let's say that we add the
boolean key ``miles`` to the above list.  In addition, we add ``nautical``, but
this only makes sense in the context of miles.  Therefore, the key ``nautical``
*depends* on the ``miles`` key.  This part of the code would be given as
follows:

.. code:: python

    reader.add_boolean_key('miles')
    reader.add_boolean_key('nautical', depends='miles')

    # This would be fine
    inp = reader.read_input(['miles', 'nautical'])
    # This would result in a ReaderError because the dependee is missing!
    inp = reader.read_input(['nautical'])

.. _required_common:

required
''''''''

This specifies that the given key is required to appear in the input file.  I
personally cannot think of a good use case for this in the context of a boolean
key (it makes sense for line and block keys as we will see later), but who am I
to prevent you from doing so if you need it!  A :py:exc:`ReaderError` is raised
if the key is missing from the input file.

.. _repeat_common:

repeat
''''''

By default, a key is only allowed to appear once; if it appears twice a
:py:exc:`ReaderError` is raised.  However, there are certain use cases when it
makes sense to have a key repeat.  If this is is the case, you can specify the
*repeat* option to be true.  The values will be returned in a
:py:class:`tuple`, so you will have to be wary of this when extracting the data
from the :py:class:`Namespace`.

.. code:: python

    reader.add_boolean_key('red')
    reader.add_boolean_key('blue')
    inp = read.read_input(['blue', 'red', 'blue'])
    print inp.blue == (True, True) # True
    print inp.red == True # True

The order of the :py:obj:`tuple` returned when *repeat* is :py:obj:`True` is
the same as the order the keys appear in the input file.

.. _mutex_group:

:py:meth:`~InputReader.add_mutually_exclusive_group`
----------------------------------------------------

.. automethod:: InputReader.add_mutually_exclusive_group

.. _gotchas:

Gotchas
-------

case-sensitivity
''''''''''''''''

If you have set *case* to :py:obj:`True` in either the :py:class:`InputReader`
constructor or in a block key, the variables in the :py:class:`Namespace` must
be accessed with the same case that was given in the definition.  Conversely,
if *case* is :py:obj:`False`, the variables will be accessed with a lower-cased
version.  In the  *case* = :py:obj:`True` version:

.. code:: python

    from input_reader import InputReader
    reader = InputReader(case=True)
    reader.add_boolean_key('RED')
    try:
        inp = reader.read_input(['red']) # Error, 'red' != 'RED'
    except ReaderError:
        pass
    inp = reader.read_input(['RED'])
    print 'red' in inp # False
    print 'RED' in inp # True

In the  *case* = :py:obj:`False` version (default):

.. code:: python

    from input_reader import InputReader
    reader = InputReader()
    reader.add_boolean_key('RED')
    inp = reader.read_input(['red'])
    print 'red' in inp # True
    print 'RED' in inp # False

Strings with spaces
'''''''''''''''''''

:py:class:`InputReader` does not let you use strings with spaces in them.  This
is because it is impossible (read: very difficult to implement) to parse each
line without splitting them on whitespace first.  If a key name or other given
:py:obj:`str` had a space, it would be split and be difficult to detect,
resulting in unforseen parsing errors.  For this reasonm,
:py:class:`InputReader` will raise an error if it is attempted to give a
:py:obj:`str` with spaces.

.. code:: python

    from input_reader import InputReader
    reader = InputReader()
    try: # ValueError is raised because a bad string value is given
        reader.add_boolean_key('hard to parse')
    except ValueError:
        pass
    try: # Same reason
        reader.add_line_key('red', type=('OK', 'NOT OK'))
    except ValueError:
        pass

Regular expressions with spaces
'''''''''''''''''''''''''''''''

For the same reasons as above, regular expression objects that might allow
spaces will raise a :py:exc:`ValueError`.  Not only does this include regular
expressions with an expicit space, but also with whitespace character
(:py:const:`"\s"`) and the anything character (:py:const:`"."`) as these may
potentially match spaces.  
