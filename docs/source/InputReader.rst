.. default-domain:: py
.. currentmodule:: input_reader

.. testsetup:: *

    from input_reader import InputReader, ReaderError

.. testsetup:: prebool

    from input_reader import InputReader, ReaderError
    reader = InputReader()
    reader.add_boolean_key('red')
    reader.add_boolean_key('blue')
    reader.add_boolean_key('green')

The :class:`InputReader` Class
==============================

.. autoclass:: InputReader

The :class:`InputReader` class allows the user to define the keys to be read in
from the input file, and also reads the input file to parse the data.  

In the simplest use case, you may simply instantiate :class:`InputReader`
with no aruments, as in

.. code::

    from input_reader import InputReader
    reader = InputReader()

The above instantiation assumes that the ``#`` character will be a comment in
the input file, the input file is case-insensitive, unknown keys in the input
file will cause the parsing to fail, and any key not found in the input file
will be defaulted to :obj:`None`.  

If an unknown parameter is passed to :class:`InputReader`, a
:exc:`TypeError` will be raised.  If an inappropriate value is passed to a
parameter a :exc:`ValueError` will be raised. 

:class:`InputReader` options
----------------------------

There are four optional parameters to :class:`InputReader`: *case*,
*comment*, *ignoreunknown*, and *default*.  The defaults for these are
illustrated below:

.. testcode:: 

    # The following are equivalent
    reader = InputReader(comment=['#'], case=False, ignoreunknown=False, default=None)
    reader = InputReader()

Of course, the user may choose to change these default values.

.. _comment:

comment
'''''''

The comment option specifies the characters that will be interpreted as a
comment by :class:`InputReader`.  As mentioned above, the default is ``#``.
You are free to choose as many characters as you wish.  If you choose one
character, it may be given as a string or as a single element list of strings
as shown below:

.. testcode:: 

    # The following are equivalent 
    reader = InputReader(comment='%')
    reader = InputReader(comment=['%'])

If you wish to allow multiple comment characters, you *must* place them in a
list of strings:

.. testcode:: 

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

.. testcode:: 

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
:obj:`False`.  Any key that is not known to :class:`InputReader` causes
a :exc:`ReaderError` to be raised.  If this is not desireable for your use-case,
you can disable this with:

.. testcode:: 

    reader = InputReader(ignoreunknown=True)

.. _default_input:

default
'''''''

If a key is defined, but does not appear in the input file,
:class:`InputReader` will assign a default value to it.  By default this is
:obj:`None`.  This is useful because one can check that the key appeared
in the input file with ``if inp.key is not None``.  However, it may be
desireable to have a different default value, such as :obj:`False`,
:obj:`0`, or :obj:`''`. To change the default value, use:

.. testcode:: 

    reader = InputReader(default=False)

Alternatively, you can request that keys not appearring in the input file be
ommited from the :class:`Namespace`.  This would raise a
:exc:`AttributeError` when trying to access a non-existant key, or you can
check that the key exists with ``if key in inp``.   To do this, use:

.. testcode:: 

    from input_reader import SUPPRESS
    reader = InputReader(default=SUPPRESS)

.. _read_input:

:meth:`~InputReader.read_input`
----------------------------------

.. automethod:: InputReader.read_input

:meth:`~InputReader.read_input` does only one thing: parse an input file
based on the key rules given to it.  In the coming sections, we will discuss
how to define these rules, but it will be helpful first to know how we can
parse input files.  

:meth:`~InputReader.read_input` accepts one of three input types: a filename,
a :mod:`StringIO` object, or a list of strings.  Let's say we want to parse
the following input::

    red
    blue
    green

This can be sent to the input reader in one of three ways.  First, we can
create a text file containing this data and parse the file itself:

.. testcode:: prebool

    from os import remove
    from tempfile import mkstemp

    user_input = mkstemp()[1]
    with open(user_input, 'w') as ui:
        ui.write('red\n')
        ui.write('blue\n')
        ui.write('green\n')

    # Code defining how to read input goes here #
    inp = reader.read_input(user_input)
    remove(user_input)
    print inp

.. testoutput:: prebool
    :hide:

    Namespace(red=True, blue=True, green=True)

Alternatively, we could use the :mod:`StringIO` object:

.. testcode:: prebool

    from StringIO import StringIO

    io = StringIO()
    io.write('red\n')
    io.write('blue\n')
    io.write('green\n')
    
    # Code defining how to read input goes here #
    inp = reader.read_input(io)
    print inp
    
.. testoutput:: prebool
    :hide:

    Namespace(red=True, blue=True, green=True)

Last, you can simply define a list of strings.

.. testcode:: prebool

    lst = ['red', 'blue', 'green']
    
    # Code defining how to read input goes here #
    inp = reader.read_input(lst)
    print inp
    
The above three sets of code would all print:

.. testoutput:: prebool

    Namespace(red=True, blue=True, green=True)

Of course, the most common use case is to parse a file, as it is unlikely your
users will write python code as their input file; however, these alternate
modes of parsing are provided for easy testing of your key definitions.

.. _boolean_key:

:meth:`~InputReader.add_boolean_key`
---------------------------------------

.. automethod:: InputReader.add_boolean_key

A boolean key is a key in which the presence of the key triggers an action; 
there are no arguments to a boolean key in the input file.  Typically, the 
presence of a boolean key makes that key :obj:`True`, and the absence will 
make it false.  

Let's say that you are defining an input file for a plotting
program where distance is plotted versus time.
Let's say the unit choices for distance are meters, centimeters, kilometers, or
milimeters, and the unit choices for time are seconds, minutes, and hours.
We also want to know if we the distance scale (y-axis) should start at zero
or at the smallest distance value to plot.  
We might specify this set of boolean keys in  this way:

.. testcode::

    reader = InputReader()
    # The distance units
    reader.add_boolean_key('milimeters')
    reader.add_boolean_key('centimeters')
    reader.add_boolean_key('meters')
    reader.add_boolean_key('kilometers')
    # The time units
    reader.add_boolean_key('seconds')
    reader.add_boolean_key('minutes')
    reader.add_boolean_key('hours')
    # Start at 0 on y-axis?
    reader.add_boolean_key('zero_y_axis')

    # Print some results
    def print_result(inp):
        # Distance unit?
        if inp.meters:
            print "distance in meters"
        elif inp.centimeters:
            print "distance in centimeters"
        elif inp.kilometers:
            print "distance in kilometers"
        elif inp.milimeters:
            print "distance in milimeters"
        else:
            print "defaulting to distance in meters"
        # Time unit?
        if inp.seconds:
            print "time in seconds"
        elif inp.minutes:
            print "time in minutes"
        elif inp.hours:
            print "time in hours"
        else:
            print "defaulting to time in seconds"
        # Zero the y-axis
        if inp.zero_y_axis:
            print "y-axis starts at zero"
        else:
            print "y-axis starts at minimum distance point"
        print '-----'

    # Sample inputs
    print_result(reader.read_input(['meters', 'minutes', 'zero_y_axis']))
    print_result(reader.read_input(['kilometers', 'hours']))
    print_result(reader.read_input(['zero_y_axis']))

The above code would output

.. testoutput::

    distance in meters
    time in minutes
    y-axis starts at zero
    -----
    distance in kilometers
    time in hours
    y-axis starts at minimum distance point
    -----
    defaulting to distance in meters
    defaulting to time in seconds
    y-axis starts at zero
    -----

Of course, the above code does not forbid both ``meters`` and
``centimeters`` (for example) to
be defined simultaneously; the solution to this problem will be discussed 
in the :ref:`mutex_group` section. 

.. note::

    The options *default*, *depends*, *dest*, *required* and *repeat* are 
    common beween :meth:`~InputReader.add_boolean_key`, 
    :meth:`~InputReader.add_line_key`,
    :meth:`~InputReader.add_block_key`, and :meth:`~InputReader.add_regex_line`
    and therefore will be discussed together in the :ref:`common_options` 
    section.

.. _action:

action
''''''

.. hint::

    *action* defaults to :obj:`True`, so the following two lines are 
    equvalent:

        .. code::
    
            reader.add_boolean_key('key')
            reader.add_boolean_key('key', action=True)

The *action* option is what the key will be set to in the
:class:`Namespace`.  By default it is :obj:`True`.  However, in some
scenarios it may be advantagous to set this to something other than a 
:obj:`bool`.  You can even set it to a function.  For example, lets say that 
the input to our plotting program is given in seconds and meters.  It would be
advantagous then to use our boolean keys to define a function to convert 
from the input unit to the plotted unit.

.. testcode::

    reader = InputReader()
    # The distance units
    reader.add_boolean_key('meters', action=lambda x: 1.0 * x)
    reader.add_boolean_key('centimeters', action=lambda x: 100.0 * x)
    reader.add_boolean_key('kilometers', action=lambda x: 0.001 * x)
    reader.add_boolean_key('milimeters', action=lambda x: 1000.0 * x)
    # The time units
    reader.add_boolean_key('seconds', action=lambda x: x / 1.0)
    reader.add_boolean_key('minutes', action=lambda x: x / 60.0)
    reader.add_boolean_key('hours', action=lambda x: x / 3600.0)

    def print_results(inp, distance, time):
        # Distance unit?
        if inp.meters:
            print inp.meters(distance), 'meters'
        elif inp.centimeters:
            print inp.centimeters(distance), 'centimeters'
        elif inp.kilometers:
            print inp.kilometers(distance), 'kilometers'
        elif inp.milimeters:
            print inp.milimeters(distance), 'milimeters'
        else:
            print float(x), 'meters'
        # Time unit?
        if inp.seconds:
            print inp.seconds(time), 'seconds'
        elif inp.minutes:
            print inp.minutes(time), 'minutes'
        elif inp.hours:
            print inp.hours(time), 'hours'
        else:
            print float(time), 'seconds'
        print '----'

    # Supply 50 meters and 1800 seconds
    print_results(reader.read_input(['centimeters', 'minutes']), 50, 1800)
    print_results(reader.read_input(['kilometers', 'hours']), 50, 1800)
    print_results(reader.read_input(['milimeters']), 50, 1800)

The above code would output

.. testoutput::

    5000.0 centimeters
    30.0 minutes
    ----
    0.05 kilometers
    0.5 hours
    ----
    50000.0 milimeters
    1800.0 seconds
    ----

Of course, the above example is still not quite satisfactory, because our
conversion function is still in one of several variables. As a result
there is a lot of needless code just to perform this conversion.  It would be
more convenient to have a single variable to place each group of boolean keys
into. We will discuss how to do this in the :ref:`dest_common` subsection
of the :ref:`common_options` section.

.. _line_key:

:meth:`~InputReader.add_line_key`
------------------------------------

.. automethod:: InputReader.add_line_key

The line key is likely do be the work horse of your input file.  It allows
you to consisely specify a key and its parameters in a flexible way.  There are
a lot of things to think about when it comes to line keys,  so we'll take it
slowly.  

.. note::

    The options *default*, *depends*, *dest*, *required* and *repeat* are 
    common beween :meth:`~InputReader.add_boolean_key`, 
    :meth:`~InputReader.add_line_key`,
    :meth:`~InputReader.add_block_key`, and :meth:`~InputReader.add_regex_line`
    and therefore will be discussed together in the :ref:`common_options` 
    section.

.. _type_line:

type
''''

.. hint::

    *type* defaults to :obj:`str`, so the following two lines are 
    equvalent:

        .. code::
        
            reader.add_line_key('key')
            reader.add_line_key('key', type=str)

.. _single_type:

Specifying one type
"""""""""""""""""""

The *type* key specifies the python types that are to be read in on the line
key.  The allowed types are :obj:`int`, :obj:`float`, :obj:`str`
:obj:`None`, an explicit :obj:`int` (i.e. :const:`4`), explicit 
:obj:`float` (i.e. :const:`5.4`) explicit :obj:`str` 
(i.e. :const:`"hello"`), or a compiled regular expression object.  The
default for *type* is :obj:`str`.

Continuing with our plotting program, we need to specify
the style of the lines on the plot (i.e.
solid, dashed, dotted, etc.). 
The user may optionally specify an offset for the time data, as well
as the total number of data points to plot.  We could 
specify the above requirements as

.. testcode::

    reader = InputReader()
    reader.add_line_key('linestyle', type=str)
    reader.add_line_key('offset', type=float)
    reader.add_line_key('numpoints', type=int)

    user_input = ['numpoints 10',
                  'linestyle dashed',
                  'offset 100']

    inp = reader.read_input(user_input)
    print isinstance(inp.linestyle, str) ,isinstance(inp.offset, float), isinstance(inp.numpoints, int)
    print inp

The above code would output

.. testoutput::

    True True True
    Namespace(numpoints=10, linestyle='dashed', offset=100.0)

This is great, but you may notice a huge flaw: nothing is preventing the user
from giving something silly like ``lobster`` as the linestyle.  It would be
better to limit what the user may give for the linestyle.  Also, we should
provide a way to specify plotting of all given points. We can do this by
providing a :obj:`tuple` of choices:

.. testcode::

    reader = InputReader()
    reader.add_line_key('linestyle', type=('solid', 'dashed', 'dotted'))
    reader.add_line_key('offset', type=float)
    reader.add_line_key('numpoints', type=(int, 'all'))

    # Some examples of what won't work
    try:
        inp = reader.read_input(['numpoints 10.5'])
    except ReaderError as e:
        print str(e)
    try:
        inp = reader.read_input(['linestyle lobster'])
    except ReaderError as e:
        print str(e)
    try:
        inp = reader.read_input(['offset "100"'])
    except ReaderError as e:
        print str(e)

    # Now things that do work
    user_input = ['numpoints all',
                  'linestyle dashed',
                  'offset 150.3']

    inp = reader.read_input(user_input)
    print isinstance(inp.numpoints, int), isinstance(inp.numpoints, str)
    print inp

The above code would output

.. testoutput::

    ...expected one of int, all, got 10.5
    ...expected one of solid, dashed, dotted, got lobster
    ...expected float, got "100"
    False True
    Namespace(numpoints='all', linestyle='dashed', offset=150.3)

.. attention::

    It is important that you provide a :obj:`tuple` of choices, not a
    :obj:`list`, as these two object types are interpreted differently by the
    *type* option. This will be illustrated in the :ref:`multiple_types` 
    subsection.

.. warning::

    When giving a :obj:`tuple` of *type* choices and one of those choices is a
    :obj:`str`, it is important that you give the :obj:`str` last.  This is
    because :obj:`str` acts as a catch-all (i.e. :obj:`str` matches
    everything). Given the line :const:`"key 4.5"`, 
    ``type=(float, str)`` will return the :obj:`float` :const:`4.5`,
    but ``type=(str, float)`` will return the :obj:`str` :const:`"4.5"`.

It is valid for a user to specify :const:`"none"`.  It makes sense that the
user may not want an offset, and can give :const:`"none"` as a value (of 
course one could just specify :const:`0` but that wouldn't teach us anything).
The variable will be set to :obj:`None`:

.. testcode::

    reader = InputReader()
    reader.add_line_key('offset', type=(float, None))

    inp = reader.read_input(['offset 50.0'])
    print inp.offset # 50.0
    inp = reader.read_input(['offset none'])
    print inp.offset is None # True

.. testoutput::
    :hide:

    50.0
    True

There are always times when you may want more specificity than the native
python types provide, but it is impractical to specify all possibilities.  For
this purpose, you may also give a compiled regular expression object as a type.
(This doesn't really apply to our plotting program, so here is an arbitrary
example):

.. testcode::

    import re
    reader = InputReader()
    reader.add_line_key('red', type=re.compile(r'silly\d+\w*thing'))

    # OK
    inp = reader.read_input(['red silly5314whatisthisthing'])
    print inp.red
    
    # Error
    try:
        inp = reader.read_input(['red silly542.0notsogood'])
    except ReaderError as e:
        print str(e)

The above code would output

.. testoutput::

    silly5314whatisthisthing
    ...expected regex(silly\d+\w*thing), got silly542.0notsogood

.. _multiple_types:

Specifying multiple types
"""""""""""""""""""""""""

Continuing with our plotting program, we need to specify the color and shape
of the data point markers on our plot, as well as the size of the marker
(an integer).  We should also be able to specify the color and size of the
connecting lines.  To give multiple data entries for a single line key, you
must provide a :obj:`list` to *type*.  Our definitions would be changed as
follows:

.. testcode::

    reader = InputReader()
    colors = ('green', 'red', 'blue', 'orange', 'black', 'violet')
    reader.add_line_key('linestyle', type=[('solid', 'dashed', 'dotted'), colors, int])
    reader.add_line_key('pointstyle', type=[('circles', 'squares', 'triangles'), colors, int])

    user_input = ['linestyle solid black 2',
                  'pointstyle squares blue 3']

    inp = reader.read_input(user_input)
    print inp
    print inp.pointstyle[1]

    # Some examples of what won't work
    try:
        inp = reader.read_input(['linestyle dashed green'])
    except ReaderError as e:
        print str(e)
    try:
        inp = reader.read_input(['pointstyle squares red 5 extra'])
    except ReaderError as e:
        print str(e)

The above code would output

.. testoutput::

    Namespace(linestyle=('solid', 'black', 2), pointstyle=('squares', 'blue', 3))
    blue
    ...expected at least 3 arguments, got 2
    ...expected 3 arguments, got 4

The parameters are read in the order in which they were defined.  For this
reason, parameters defined using the *type* option will be refered to as
*positional parameters*.

.. attention::

    The :obj:`tuple` vs. :obj:`list` disctintion is very important for the
    *type* option; a :obj:`tuple` is used to define parameter *choices*, and a
    :obj:`list` is used to define *multiple parameters*.  It is not legal to 
    have a :obj:`list` inside of a :obj:`list` for the *type* object. 

.. warning::

    If you are specifying only one parameter, it is important to realize that
    the following are **not** equivalent:

        .. code::

            reader.add_line_key('key1', type=str)
            reader.add_line_key('key2', type=[str])

    The former will store a :obj:`str` in the *key* attribute of the
    :class:`Namespace`, whereas the latter will store a single-element
    :obj:`list` of a :obj:`str`.  Let's say that our input was ``['key1 fish',
    'key2 fish']``.  Our result would be:

        .. code::

            print inp.key1    # fish
            print inp.key2    # ["fish"]
            print inp.key2[0] # fish

    Obviously, this distinction will affect how you access the input data.

.. note::

    Each of the parameters in the :obj:`list` follows
    the rules discussed for a single type as descussed in subsection
    :ref:`single_type`.  

.. hint::

    If you do not wish to define **any** *type* parameters, you can give
    :obj:`None`.  This may be useful when using the :ref:`glob_type` or 
    :ref:`keyword_type` options.


.. _case_type:

case
''''

.. hint::

    *case* defaults to :obj:`False`, so the following two lines are 
    equvalent:

        .. code::
        
            reader.add_line_key('key')
            reader.add_line_key('key', case=False)

The *case* option allows makes the parameters to the given line key
case-sensitive.  This does not make the keyword itself case-sensitive, just the
parameters.  The most obvious use-case would be for file names or labels.
In our plotting program, we need to specify the file name that contains the raw
data:

.. testcode::

    reader = InputReader()
    reader.add_line_key('rawdata', case=True)
    
    inp = reader.read_input(['rawdata /path/to/RAW/Data.txt'])

    print inp.rawdata # /path/to/RAW/Data.txt
    # If case=False, this would return /path/to/raw/data.txt

.. testoutput::
    :hide:

    /path/to/RAW/Data.txt

Obviously, this only affects :obj:`str` types.  This has no affect on compiled
regular expressions because case-sensitivity is determined at compile-time for
regular expressions.

.. _glob_type:

glob
''''

.. hint::

    *glob* defaults to :const:`{}`, so the following two lines are 
    equvalent:

        .. code::
        
            reader.add_line_key('key')
            reader.add_line_key('key', glob={})

.. note::

    The options *glob* and *keywords* are mutually exclusive.

There are often times when you may not know the number of parameters the user
will give.  For this purpose, the option *glob* has been provided.  With
*glob*, it is possible to specify that a variable number of parameters will be
given, with the options being:

:const:`*` - Zero or more parameters

:const:`+` - One or more parameters

:const:`?` - Zero or one parameters

*glob* must be given as a :obj:`dict`; the key *len* specifies one of the above
three variable length specifiers.  Two other important keys are *type*, which
follows the same rules as discussed in subsection :ref:`single_type`, and
*default*, which is the default value assigned if the glob is not included. 
Like the *type* option, if the *type* key for *glob* is omitted, the default
is :obj:`str`. The
*glob* values are appended to the end of the :obj:`tuple` for the given key.

Thinking about our plotting program, we might prefer to not force the user to
specify the size of the lines and points and default them to
:const:`1` if not included.  This could be coded as:

.. testcode::

    reader = InputReader()
    colors = ('green', 'red', 'blue', 'orange', 'black', 'violet')
    reader.add_line_key('linestyle', type=[('solid', 'dashed', 'dotted'), colors],
                        glob={'len':'?', 'type':int, 'default':1})
    reader.add_line_key('pointstyle', type=[('circles', 'squares', 'triangles'), colors],
                        glob={'len':'?', 'type':int, 'default':1})

    # We choose the default size for linestyle
    inp = reader.read_input(['linestyle dotted red', 
                             'pointstyle circles violet 3'])

    # The glob values are appended to the end of the tuple
    print inp

    try:
        inp = reader.read_input(['linestyle solid black 4 extra'])
    except ReaderError as e:
        print str(e)

The above code would output

.. testoutput::

    Namespace(linestyle=('dotted', 'red', 1), pointstyle=('circles', 'violet', 3))
    ...expected at most 3 arguments, got 4

There is a fourth key to the *glob* option, and it is *join*.  Join causes all
the globbed parameters to be joined together into a single space-seperated
string.  The default value is :obj:`False`.  *join* is useful when reading 
things like titles.  For example, to allow
the user to specify a title for the plot, we would use the following code:

.. testcode::

    reader = InputReader()
    reader.add_line_key('title', type=None, case=True, glob={'len':'*', 'join':True, 'default':''})

    inp = reader.read_input(['title The Best Plot EVER!!!'])

    print inp.title # The Best Plot EVER!!!
    # If join=False, this would be ('The', 'Best', 'Plot', 'EVER!!!')

.. testoutput::
    :hide:

    The Best Plot EVER!!!

Please note that in the above code, we used ``type=None``.  This means there
are no required positional parameters, and only *glob* parameters will be
read.  

.. note::

    When the *glob* option is used, the parameters will always be stored as a
    :obj:`tuple` with the *glob* parameters appended to the end of the
    positional parameters. There is one exception to this rule.  
    If *type* equals :obj:`None` and *join* equals :obj:`True`, then the
    parameters will be returned as the joined string, similar to if *type*
    equals :obj:`str` and *glob* is omitted.

What if it was possible to read in raw data from multiple files? There are two
ways we might choose to code this:

.. testcode::

    # Method 1
    reader = InputReader()
    reader.add_line_key('rawdata', case=True, type=str, glob={'len':'*'}) # Remember that str is the default type
    inp = reader.read_input(['rawdata file1.txt file2.txt file3.txt'])
    print inp.rawdata
    
    # Method 2
    reader = InputReader()
    reader.add_line_key('rawdata', case=True, type=None, glob={'len':'+'})
    inp = reader.read_input(['rawdata file1.txt file2.txt file3.txt'])
    print inp.rawdata

The above code would output

.. testoutput::

    ('file1.txt', 'file2.txt', 'file3.txt')
    ('file1.txt', 'file2.txt', 'file3.txt')

OK, so what's the difference between ``type=str, glob={'len':'*'}`` and
``type=None, glob={'len':'+'}``?  In the above example, nothing.  However, if
*join* were :obj:`True`, then method 1 above would return 
:const:`'file1.txt file2.txt file3.txt'`, whereas method 2 would return
:const:`('file1.txt', 'file2.txt file3.txt')`.  This is an obscure use-case,
but it may be important for you in the future.

.. _keyword_type:

keywords
''''''''

.. hint::

    *keywords* defaults to :const:`{}`, so the following two lines are 
    equvalent:

        .. code::
        
            reader.add_line_key('key')
            reader.add_line_key('key', keywords={})

.. note::

    The options *glob* and *keywords* are mutually exclusive.



.. _block_key:

:meth:`~InputReader.add_block_key`
-------------------------------------

.. automethod:: InputReader.add_block_key

.. note::

    The options *default*, *depends*, *dest*, *required* and *repeat* are 
    common beween :meth:`~InputReader.add_boolean_key`, 
    :meth:`~InputReader.add_line_key`,
    :meth:`~InputReader.add_block_key`, and :meth:`~InputReader.add_regex_line`
    and therefore will be discussed together in the :ref:`common_options` 
    section.

.. _regex_line:

:meth:`~InputReader.add_regex_line`
--------------------------------------

.. automethod:: InputReader.add_regex_line

.. note::

    The options *default*, *depends*, *dest*, *required* and *repeat* are 
    common beween :meth:`~InputReader.add_boolean_key`, 
    :meth:`~InputReader.add_line_key`,
    :meth:`~InputReader.add_block_key`, and :meth:`~InputReader.add_regex_line`
    and therefore will be discussed together in the :ref:`common_options` 
    section.

.. _common_options:

Common Options
--------------

The methods :meth:`~InputReader.add_boolean_key`, 
:meth:`~InputReader.add_line_key`, :meth:`~InputReader.add_block_key`,
and :meth:`~InputReader.add_regex_line` all share a set of options:
*dest*, *default*, *depends*, *required*, and *repeat*.  They will be discussed
together here.

.. _dest_common:

dest
''''

Of course, the above example is still not quite satisfactory, because our
conversion function is still on one of four different variables.  It would be
more convenient to have a single variable to place this group of boolean keys
into. For this, we use the *dest* option.

.. code::

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

A :exc:`ReaderError` would be raised if both ``meters`` and ``centimeters``
had been defined in the input file.  As you will see later, it is often more
advantageous to use *dest* in conjunction with 
:meth:`~InputReader.add_mutually_exclusive_group` because it provides more
protection against bad user input for keys that are grouped together.

.. _default_common:

default
'''''''

This is the default value of the boolean key.  It defaults to :obj:`None`.

.. _depends_common:

depends
'''''''

The *depends* option specifies that in order for this key to be valid, another
key must also appear in the input.  For example, let's say that we add the
boolean key ``miles`` to the above list.  In addition, we add ``nautical``, but
this only makes sense in the context of miles.  Therefore, the key ``nautical``
*depends* on the ``miles`` key.  This part of the code would be given as
follows:

.. code::

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
to prevent you from doing so if you need it!  A :exc:`ReaderError` is raised
if the key is missing from the input file.

.. _repeat_common:

repeat
''''''

By default, a key is only allowed to appear once; if it appears twice a
:exc:`ReaderError` is raised.  However, there are certain use cases when it
makes sense to have a key repeat.  If this is is the case, you can specify the
*repeat* option to be true.  The values will be returned in a
:class:`tuple`, so you will have to be wary of this when extracting the data
from the :class:`Namespace`.

.. code::

    reader.add_boolean_key('red')
    reader.add_boolean_key('blue')
    inp = read.read_input(['blue', 'red', 'blue'])
    print inp.blue == (True, True) # True
    print inp.red == True # True

The order of the :obj:`tuple` returned when *repeat* is :obj:`True` is
the same as the order the keys appear in the input file.

.. _mutex_group:

:meth:`~InputReader.add_mutually_exclusive_group`
----------------------------------------------------

.. automethod:: InputReader.add_mutually_exclusive_group

.. _gotchas:

Gotchas
-------

case-sensitivity
''''''''''''''''

If you have set *case* to :obj:`True` in either the :class:`InputReader`
constructor or in a block key, the variables in the :class:`Namespace` must
be accessed with the same case that was given in the definition.  Conversely,
if *case* is :obj:`False`, the variables will be accessed with a lower-cased
version.  In the  *case* = :obj:`True` version:

.. code::

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

In the  *case* = :obj:`False` version (default):

.. code::

    from input_reader import InputReader
    reader = InputReader()
    reader.add_boolean_key('RED')
    inp = reader.read_input(['red'])
    print 'red' in inp # True
    print 'RED' in inp # False
    inp = reader.read_input(['RED'])
    print 'red' in inp # True
    print 'RED' in inp # False

Strings with spaces
'''''''''''''''''''

:class:`InputReader` does not let you use strings with spaces in them.  This
is because it is impossible (read: very difficult to implement) to parse each
line without splitting them on whitespace first.  If a key name or other given
:obj:`str` had a space, it would be split and be difficult to detect,
resulting in unforseen parsing errors.  For this reasonm,
:class:`InputReader` will raise an error if it is attempted to give a
:obj:`str` with spaces.

.. code::

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
spaces will raise a :exc:`ValueError`.  Not only does this include regular
expressions with an expicit space, but also with whitespace character
(:const:`"\s"`) and the anything character (:const:`"."`) as these may
potentially match spaces.  
