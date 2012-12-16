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

.. testsetup:: fullexample

    from StringIO import StringIO
    from textwrap import dedent

    user_input = StringIO()
    user_input.write(dedent('''\
        # Plot in centimeters
        centimeters
        # ... and in hours
        hours

        # Read from two data files
        rawdata /path/to/DATA.txt # absolute path
        rawdata ../raw.txt        # relative path

        # Output filename and format
        output myplot format=png compression=zip

        # Line and point styles
        linestyle dashed
        # Point style... make them big, and green!
        pointstyle circles color=green size=8

        # Note there is no legend or polygon in this input
        '''))

.. |False| replace:: :obj:`False`
.. |True| replace:: :obj:`True`
.. |None| replace:: :obj:`None`
.. |tuple| replace:: :obj:`tuple`
.. |list| replace:: :obj:`list`
.. |dict| replace:: :obj:`dict`
.. |str| replace:: :obj:`str`
.. |int| replace:: :obj:`int`
.. |float| replace:: :obj:`float`
.. |InputReader| replace:: :class:`InputReader`
.. |Namespace| replace:: :class:`Namespace`
.. |ReaderError| replace:: :exc:`ReaderError`

The |InputReader| Class
=======================

.. autoclass:: InputReader

The |InputReader| class allows the user to define the keys to be read in
from the input file, and also reads the input file to parse the data.  

In the simplest use case, you may simply instantiate |InputReader|
with no arguments, as in

.. code::

    from input_reader import InputReader
    reader = InputReader()

The above instantiation assumes that the ``#`` character will be a comment in
the input file, the input file is case-insensitive, unknown keys in the input
file will cause the parsing to fail, and any key not found in the input file
will be defaulted to |None|.  

If an unknown parameter is passed to |InputReader|, a
:exc:`TypeError` will be raised.  If an inappropriate value is passed to a
parameter a :exc:`ValueError` will be raised. 

|InputReader| options
---------------------

There are four optional parameters to |InputReader|: *case*,
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
comment by |InputReader|.  As mentioned above, the default is ``#``.
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
a reason this is not desirable.  To turn on case-sensitivity, use

.. testcode:: 

    reader = InputReader(case=True)

This will cause the input file to be read in as given, and keys to be kept in
the case that is given.

.. _ignoreunknown_input:

ignoreunknown
'''''''''''''

It is best not to assume your end-users will do everything correctly.  For
example, it is common to accidentally misspell a keyword.  You would likely wish
to alert the user of this error instead of continuing with the calculation and
giving bad results.  For this reason, the *ignoreunknown* key is defaulted to
|False|.  Any key that is not known to |InputReader| causes
a |ReaderError| to be raised.  If this is not desirable for your use-case,
you can disable this with:

.. testcode:: 

    reader = InputReader(ignoreunknown=True)

.. _default_input:

default
'''''''

If a key is defined, but does not appear in the input file,
|InputReader| will assign a default value to it.  By default this is
|None|.  This is useful because one can check that the key appeared
in the input file with ``if inp.key is not None``.  However, it may be
desirable to have a different default value, such as |False|,
:obj:`0`, or :obj:`''`. To change the default value, use:

.. testcode:: 

    reader = InputReader(default=False)

Alternatively, you can request that keys not appearing in the input file be
omitted from the |Namespace|.  This would raise a
:exc:`AttributeError` when trying to access a non-existent key, or you can
check that the key exists with ``if key in inp``.   To do this, use:

.. testcode:: 

    from input_reader import SUPPRESS
    reader = InputReader(default=SUPPRESS)

.. _read_input:

:meth:`~InputReader.read_input`
-------------------------------

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
------------------------------------

.. automethod:: InputReader.add_boolean_key

A boolean key is a key in which the presence of the key triggers an action; 
there are no arguments to a boolean key in the input file.  Typically, the 
presence of a boolean key makes that key |True|, and the absence will 
make it false.  

Let's say that you are defining an input file for a plotting
program where distance is plotted versus time.
Let's say the unit choices for distance are meters, centimeters, kilometers, or
millimeters, and the unit choices for time are seconds, minutes, and hours.
We also want to know if we the distance scale (y-axis) should start at zero
or at the smallest distance value to plot.  
We might specify this set of boolean keys in  this way:

.. testcode::

    reader = InputReader()
    # The distance units
    reader.add_boolean_key('millimeters')
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
        elif inp.millimeters:
            print "distance in millimeters"
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

    *action* defaults to |True|, so the following two lines are 
    equvalent:

        .. code::
    
            reader.add_boolean_key('key')
            reader.add_boolean_key('key', action=True)

The *action* option is what the key will be set to in the
|Namespace|.  By default it is |True|.  However, in some
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
    reader.add_boolean_key('millimeters', action=lambda x: 1000.0 * x)
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
        elif inp.millimeters:
            print inp.millimeters(distance), 'millimeters'
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
    print_results(reader.read_input(['millimeters']), 50, 1800)

The above code would output

.. testoutput::

    5000.0 centimeters
    30.0 minutes
    ----
    0.05 kilometers
    0.5 hours
    ----
    50000.0 millimeters
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
---------------------------------

.. automethod:: InputReader.add_line_key

The line key is likely do be the work horse of your input file.  It allows
you to concisely specify a key and its parameters in a flexible way.  There are
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

    *type* defaults to |str|, so the following two lines are 
    equivalent:

        .. code::
        
            reader.add_line_key('key')
            reader.add_line_key('key', type=str)

.. _single_type:

Specifying one type
"""""""""""""""""""

The *type* key specifies the python types that are to be read in on the line
key.  The allowed types are |int|, |float|, |str|
|None|, an explicit |int| (i.e. :const:`4`), explicit 
|float| (i.e. :const:`5.4`) explicit |str| 
(i.e. :const:`"hello"`), or a compiled regular expression object.  The
default for *type* is |str|.

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
providing a |tuple| of choices:

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
        inp = reader.read_input(["offset '100'"])
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

    ...expected one of "all" or int, got "10.5"
    ...expected one of "dashed", "dotted" or "solid", got "lobster"
    ...expected float, got "'100'"
    False True
    Namespace(numpoints='all', linestyle='dashed', offset=150.3)

.. attention::

    It is important that you provide a |tuple| of choices, not a
    |list|, as these two object types are interpreted differently by the
    *type* option. This will be illustrated in the :ref:`multiple_types` 
    subsection.

.. warning::

    When giving a |tuple| of *type* choices and one of those choices is a
    |str|, it is important that you give the |str| last.  This is
    because |str| acts as a catch-all (i.e. |str| matches
    everything). Given the line :const:`"key 4.5"`, 
    ``type=(float, str)`` will return the |float| :const:`4.5`,
    but ``type=(str, float)`` will return the |str| :const:`"4.5"`.

It is valid for a user to specify :const:`"none"`.  It makes sense that the
user may not want an offset, and can give :const:`"none"` as a value (of 
course one could just specify :const:`0` but that wouldn't teach us anything).
The variable will be set to |None|:

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
For details on how regular expressions see the
documentation for the :mod:`re` module.
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
    ...expected regex(silly\d+\w*thing), got "silly542.0notsogood"

.. _multiple_types:

Specifying multiple types
"""""""""""""""""""""""""

Continuing with our plotting program, we need to specify the color and shape
of the data point markers on our plot, as well as the size of the marker
(an integer).  We should also be able to specify the color and size of the
connecting lines.  To give multiple data entries for a single line key, you
must provide a |list| to *type*.  Our definitions would be changed as
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
    ...expected 3 arguments, got 2
    ...expected 3 arguments, got 4

The parameters are read in the order in which they were defined.  For this
reason, parameters defined using the *type* option will be referred to as
*positional parameters*.

.. attention::

    The |tuple| vs. |list| distinction is very important for the
    *type* option; a |tuple| is used to define parameter *choices*, and a
    |list| is used to define *multiple parameters*.  It is not legal to 
    have a |list| inside of a |list| for the *type* object. 

.. warning::

    If you are specifying only one parameter, it is important to realize that
    the following are **not** equivalent:

        .. code::

            reader.add_line_key('key1', type=str)
            reader.add_line_key('key2', type=[str])

    The former will store a |str| in the *key* attribute of the
    |Namespace|, whereas the latter will store a single-element
    |list| of a |str|.  Let's say that our input was ``['key1 fish',
    'key2 fish']``.  Our result would be:

        .. code::

            print inp.key1    # fish
            print inp.key2    # ["fish"]
            print inp.key2[0] # fish

    Obviously, this distinction will affect how you access the input data.

.. note::

    Each of the parameters in the |list| follows
    the rules discussed for a single type as discussed in subsection
    :ref:`single_type`.  

.. hint::

    If you do not wish to define **any** *type* parameters, you can give
    |None|.  This may be useful when using the :ref:`glob_type` or 
    :ref:`keyword_type` options.


.. _case_type:

case
''''

.. hint::

    *case* defaults to |False|, so the following two lines are 
    equivalent:

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

Obviously, this only affects |str| types.  This has no affect on compiled
regular expressions because case-sensitivity is determined at compile-time for
regular expressions.

.. _glob_type:

glob
''''

.. hint::

    *glob* defaults to :const:`{}`, so the following two lines are 
    equivalent:

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

*glob* must be given as a |dict|; the key *len* specifies one of the above
three variable length specifiers.  Two other important keys are *type*, which
follows the same rules as discussed in subsection :ref:`single_type`, and
*default*, which is the default value assigned if the glob is not included. 
Like the *type* option, if the *type* key for *glob* is omitted, the default
is |str|. The
*glob* values are appended to the end of the |tuple| for the given key.

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
the globbed parameters to be joined together into a single space-separated
string.  The default value is |False|.  *join* is useful when reading 
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
    |tuple| with the *glob* parameters appended to the end of the
    positional parameters. There is one exception to this rule.  
    If *type* equals |None| and *join* equals |True|, then the
    parameters will be returned as the joined string, similar to if *type*
    equals |str| and *glob* is omitted.

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
*join* were |True|, then method 1 above would return 
:const:`'file1.txt file2.txt file3.txt'`, whereas method 2 would return
:const:`('file1.txt', 'file2.txt file3.txt')`.  This is an obscure use-case,
but it may be important for you in the future.

.. warning::

    If you set a default value for *glob*, the default will
    only be set if the keyname actually appears in the input file.  

.. _keyword_type:

keywords
''''''''

.. hint::

    *keywords* defaults to :const:`{}`, so the following two lines are 
    equivalent:

        .. code::
        
            reader.add_line_key('key')
            reader.add_line_key('key', keywords={})

.. note::

    The options *glob* and *keywords* are mutually exclusive.

There are times when a line key should offer optional parameters with more
flexibility than can be offered by the *glob* option.  The *keywords* option
provides this flexibility.  Each parameter specified in the *keywords* option
is accessed through some keyword name; for this reason, we will refer to these
parameters as *named parameters*.  

*keywords* must be given as a |dict| with nested |dict|.  Each named parameter
in the *keywords* |dict| has a |dict| containing two possible keys: *type* and
*default*.  The rules for *type* are the same as described in the
:ref:`single_type` subsection, and *default* can be anything.  If not
specified, the default values of *type* and *default* are |str| and
:class:`SUPPRESS`, respectively.  The named parameters can appear in any order,
as long as they come after the positional parameters.

Going back to our plotting program, we might agree that the way we have set up
the ``linestyle`` and ``pointstyle`` keys is not optimal.  What if the user
wants to accept a default value for the color, but change the size? To get
around this, we will use the *keywords* option:

.. testcode::

    reader = InputReader()
    colors = ('green', 'red', 'blue', 'orange', 'black', 'violet')
    reader.add_line_key('linestyle', type=('solid', 'dashed', 'dotted'),
                        keywords={'color':{'type':colors,'default':'black'},
                                  'size' :{'type':int,   'default':1}})
    reader.add_line_key('pointstyle', type=('circles', 'squares', 'triangles'),
                        keywords={'color':{'type':colors,'default':'black'},
                                  'size' :{'type':int,   'default':1}})

    inp = reader.read_input(['linestyle solid size=3', 
                             'pointstyle circles color=green'])

    print inp.linestyle
    print inp.pointstyle[-1]['color'], inp.pointstyle[-1]['size']

    # Error!
    try:
        inp = reader.read_input(['linestyle solid lobster=red'])
    except ReaderError as e:
        print str(e)
    # Another error!
    try:
        inp = reader.read_input(['linestyle solid color red'])
    except ReaderError as e:
        print str(e)

The above code would output

.. testoutput::

    ('solid', {'color': 'black', 'size': 3})
    green 1
    ...Unknown keyword: "lobster"
    ...Error reading keyword argument "color"

This code illustrates three important points about named parameters.  

1) The parameters are returned as a|tuple|, with the positional parameters
   first and the |dict| containing the named parameters appended to the end.  
   This means that the named parameters will always be the last element of 
   the |tuple|, so you may access them using the ``[-1]`` notation.

    .. note::

        When the *keywords* option is used, the parameters will always be stored
        as a |tuple| with the *keywords* parameter |dict| appended to the end of
        the positional parameters. There is one exception to this rule.  
        If the optiojn *type* equals |None|, the parameters will be returned as
        only the *keywords* parameter |dict|.

2) The value of the parameter **must** be separated from the key by :const:`=`.
   There are no exceptions.  If they are separated by a space or anything else,
   an error will be raised.  **Be sure you make this clear to your users!**

3) Unknown keys will raise a |ReaderError|.

Let's take a look at what happens when no *default* is given.  All along, we
have forgotten to specify a name for the file of our plot!  We will define this
now.  The user will give a filename, then an optional image format and
compression:

.. testcode::

    reader = InputReader()
    formats = ('pdf', 'png', 'jpg', 'svg', 'bmp', 'eps')
    compress = ('zip', 'tgz', 'tbz2')
    reader.add_line_key('output', case=True, type=str, 
                        keywords={'format':{'type':formats},
                                  'compression':{'type':compress}})
    
    print reader.read_input(['output filename format=png compression=zip'])
    print reader.read_input(['output filename format=png'])
    print reader.read_input(['output filename compression=tgz'])
    print reader.read_input(['output filename'])

The above code would output

.. testoutput::

    Namespace(output=('filename', {'compression': 'zip', 'format': 'png'}))
    Namespace(output=('filename', {'format': 'png'}))
    Namespace(output=('filename', {'compression': 'tgz'}))
    Namespace(output=('filename', {}))

Since the default *default* is :class:`SUPPRESS`, named parameters not
appearing in the input are omitted from the |dict|.  This means that if no
named parameters are given, an empty |dict| is returned.

.. warning::

    If you set a default value for *keyword*, the default will
    only be set if the keyname actually appears in the input file.  

.. _block_key:

:meth:`~InputReader.add_block_key`
----------------------------------

.. automethod:: InputReader.add_block_key

.. note::

    The options *default*, *depends*, *dest*, *required* and *repeat* are 
    common beween :meth:`~InputReader.add_boolean_key`, 
    :meth:`~InputReader.add_line_key`,
    :meth:`~InputReader.add_block_key`, and :meth:`~InputReader.add_regex_line`
    and therefore will be discussed together in the :ref:`common_options` 
    section.

A block key is a way to group logically similar keys together.  It is also
useful to separate some keys from the others.  Block keys have the form of::

    block_start
        key
        anotherkey
        etc...
    end

The indentation is optional.  

Let's say that we wanted to add the capability of including a legend in our
plotting program.  We decide to do this as a block key. We need to specify the
location of the legend, the size of the legend, and if the legend should have a
shadow.  We might code this as follows:

.. testcode::

    reader= InputReader()
    # Notice that we return the legend block object
    legend = reader.add_block_key('legend')
    # We add keys to the legend block object just as we have done before
    legend.add_boolean_key('shadow')
    legend.add_line_key('location', type=('upper_left', 'upper_right',
                                          'lower_left', 'lower_right'))
    legend.add_line_key('size', type=int)

    from textwrap import dedent
    from StringIO import StringIO
    user_input = StringIO()
    user_input.write(dedent('''\
                            legend
                                shadow
                                location upper_right
                                size 3
                            end
                            '''))

    inp = reader.read_input(user_input)
    print inp
    print inp.legend.location

The above code would output

.. testoutput::

    Namespace(legend=Namespace(shadow=True, location='upper_right', size=3))
    upper_right

First, we should note that the block creates a |Namespace| held inside the
``legend`` attribute of the main |Namespace|.  This makes it easy to access the
keys within the block with the dot operator (shown for the ``location`` key).

end
'''

By default, a block key is terminated by the word :const:`"end"` (the default
to the *end* option).  However, it may make sense to use a different word.  A
perfect example would be a block inside of another block.  The sub-block might
use the word :const:`subend`.  Perhaps there are more than one thing to specify
for the size parameter of the legend, and we need a sub-block for this:

.. testcode::

    reader = InputReader()
    legend = reader.add_block_key('legend')
    legend.add_boolean_key('shadow')
    legend.add_line_key('location', type=('upper_left', 'upper_right',
                                          'lower_left', 'lower_right'))
    size = legend.add_block_key('size', end='subend')
    size.add_line_key('box', type=int)
    size.add_line_key('font', type=int)

    from textwrap import dedent
    from StringIO import StringIO
    user_input = StringIO()
    user_input.write(dedent('''\
                            legend
                                shadow
                                location upper_right
                                size
                                    box 2
                                    font 5
                                subend
                            end
                            '''))

    inp = reader.read_input(user_input)
    print inp
    print inp.legend.size.font

The above code would output

.. testoutput::

    Namespace(legend=Namespace(shadow=True, location='upper_right', size=Namespace(box=2, font=5)))
    5

We have a |Namespace| nested in a |Namespace| nested in a |Namespace|!  There
is no limit to the amount of nesting you can have, although your users may get
irritated if it is arbitrarily complex.

case
''''

The *case* option for a block key is identical to that of the *case* option for
the |InputReader| class except that it only applies to the keys inside the
block.

ignoreunknown
'''''''''''''

The *ignoreunknown* option for a block key is identical to that of the 
*ignoreunknown* option for
the |InputReader| class except that it only applies to the keys inside the
block.

.. _regex_line:

:meth:`~InputReader.add_regex_line`
-----------------------------------

.. automethod:: InputReader.add_regex_line

.. note::

    The options *default*, *depends*, *dest*, *required* and *repeat* are 
    common beween :meth:`~InputReader.add_boolean_key`, 
    :meth:`~InputReader.add_line_key`,
    :meth:`~InputReader.add_block_key`, and :meth:`~InputReader.add_regex_line`
    and therefore will be discussed together in the :ref:`common_options` 
    section.

Sometimes it is necessary to accept user input that does not fit nicely into
the categories discussed above.  For these situations the regex line is
offered.  The regex line allows you to specify a regular expression that must
match the input line.  For details on how regular expressions see the
documentation for the :mod:`re` module.

Let's say that we want the user to be able to draw polygons on the plot.  The
user can specify a series of x,y points that define the vertices of the
polygon.  We could create a polygon block, and each line in the block is a
vertex:

.. testcode::

    reader = InputReader()
    polygon = reader.add_block_key('polygon')
    polygon.add_regex_line('xypoint', r'(-?\d+\.?\d*) (-?\d+\.?\d*)', repeat=True)
    # Another way to define the above is with the following three lines.  They are completely equivalent.
    # import re
    # reg = re.compile(r'(-?\d+\.?\d*) (-?\d+\.?\d*)')
    # polygon.add_regex_line('xypoint', reg, repeat=True)

    from textwrap import dedent
    from StringIO import StringIO
    user_input = StringIO()
    user_input.write(dedent('''\
                            polygon
                                0 0
                                3.5 0
                                3.3 3.5
                                0 3.3
                            end
                            '''))

    inp = reader.read_input(user_input)
    for regex in inp.polygon.xypoint:
        print regex.group(0), regex.group(1), regex.group(2)

The above code would output

.. testoutput::

    0 0 0 0  
    3.5 0 3.5 0  
    3.3 3.5 3.3 3.5
    0 3.3 0 3.3

The *repeat* option will be discussed in subsection :ref:`repeat_common`; for
now we will say that it allows a key to be repeated multiple times.

Even though the *handle* ``xypoint`` does not appear in the input file, we must
specify it so that we have a name to access in the |Namespace|.  

Note that the regex line cannot do any type checking for you.  You will have to
write your own post-processing to check that the types are correct and to parse
the line so that the data is in a usable format. 

case
''''

The *case* option for the regex line is identical to the *case* option for the
line key, with the exception that *case* only applies to regular expressions
given to :meth:`~InputReader.add_regex_line` as a string and not a compiled
regular expression object.  This is because the regular expression object has
case-sensitivity built in at compile time.

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

The *dest* option specifies that a key will appear under a different name in
the |Namespace| than it does in the input.

Let's think back to our unit conversion example with the boolean keys in the
:ref:`action` section.  The result we came up with was not quite satisfactory
because it required a lot of code to do relatively little work.   It would be
more convenient to have a single variable to place a group of boolean keys
into. We might code this as follows

.. testcode::

    reader = InputReader()
    # The distance units
    reader.add_boolean_key('meters', action=lambda x: 1.0 * x, dest='distconv')
    reader.add_boolean_key('centimeters', action=lambda x: 100.0 * x, dest='distconv')
    reader.add_boolean_key('kilometers', action=lambda x: 0.001 * x, dest='distconv')
    reader.add_boolean_key('milimeters', action=lambda x: 1000.0 * x, dest='distconv')
    # The time units
    reader.add_boolean_key('seconds', action=lambda x: x / 1.0, dest='timeconv')
    reader.add_boolean_key('minutes', action=lambda x: x / 60.0, dest='timeconv')
    reader.add_boolean_key('hours', action=lambda x: x / 3600.0, dest='timeconv')
    
    inp = reader.read_input(['centimeters', 'minutes'])

    # No matter what boolean key was used, the conversion function is under
    # "distconv".  The original key names have been removed.
    if 'centimeters' in inp:
        print "This will never print"

    print inp.distconv(50), inp.timeconv(1800)
    inp = reader.read_input(['kilometers', 'hours'])
    print inp.distconv(50), inp.timeconv(1800)

    # Error:
    try:
        inp = reader.read_input(['meters', 'milimeters', 'hours'])
    except ReaderError as e:
        print str(e)

The above code would output

.. testoutput::

    5000.0 30.0
    0.05 0.5
    ...The key "..." appears twice

As you will see later, it is often more
advantageous to use *dest* in conjunction with 
:meth:`~InputReader.add_mutually_exclusive_group` because it provides more
protection against bad user input for keys that are grouped together.

.. _default_common:

default
'''''''

This is the default value of a key.  It defaults to |None|.

.. _depends_common:

depends
'''''''

The *depends* option specifies that in order for this key to be valid, another
key must also appear in the input.  For example, let's say that we add the
boolean key ``miles`` to the unit conversion list.  In addition, we add 
``nautical``, but
this only makes sense in the context of miles.  Therefore, the key ``nautical``
*depends* on the ``miles`` key.  This part of the code would be given as
follows:

.. testcode::

    reader = InputReader()
    reader.add_boolean_key('miles')
    reader.add_boolean_key('nautical', depends='miles')

    # This is fine
    inp = reader.read_input(['miles', 'nautical'])
    # Error!
    try:
        inp = reader.read_input(['nautical'])
    except ReaderError as e:
        print str(e) #

The above code would output

.. testoutput::

    ...The key "nautical" requires that "miles" is also present, but it is not

.. _required_common:

required
''''''''

This specifies that the given key is required to appear in the input file.
This is not likely to be necessary for a boolean key, but may be necessary for
a line or block key.  For example, our ``rawdata`` line key accepts the file
that contains the raw data to plot.  Our plotting program would not be able to
do anything without this line, so we make it *required*:

.. testcode::

    reader = InputReader()
    reader.add_line_key('rawdata', case=True, required=True)
    reader.add_boolean_key('dummy')

    # This works as expected
    inp = reader.read_input(['dummy', 'rawdata filename.txt'])
    # Error!
    try:
        inp = reader.read_input(['dummy'])
    except ReaderError as e:
        print str(e)

.. testoutput::

    ...The key "rawdata" is required but not found

.. hint::

    Don't bother defining a *default* if *required* equals |True|.

.. _repeat_common:

repeat
''''''

By default, a key is only allowed to appear once; if it appears twice a
|ReaderError| is raised.  However, there are certain use cases when it
makes sense to have a key repeat.  If this is is the case, you can specify the
*repeat* option to be true.  The values will be returned in a
|tuple|, so you will have to be wary of this when extracting the data
from the |Namespace|.

Instead of defining multiple ``rawdata`` files on one line as we did in the
:ref:`glob_type` subsection, perhaps we would want to define multiple files on
different lines:

.. testcode::

    reader = InputReader()
    reader.add_line_key('rawdata', case=True, repeat=True, required=True)
    inp = reader.read_input(['rawdata filename3.txt', 'rawdata filename6.txt', 'rawdata filename1.txt'])
    print inp

    reader = InputReader()
    reader.add_line_key('rawdata', case=True, required=True)
    try:
        inp = reader.read_input(['rawdata filename3.txt', 'rawdata filename6.txt', 'rawdata filename1.txt'])
    except ReaderError as e:
        print str(e)

The above code would output

.. testoutput::

    Namespace(rawdata=('filename3.txt', 'filename6.txt', 'filename1.txt'))
    ...The key "..." appears twice

The order of the |tuple| returned when *repeat* is |True| is
the same as the order the keys appear in the input file.

.. _mutex_group:

:meth:`~InputReader.add_mutually_exclusive_group`
-------------------------------------------------

.. automethod:: InputReader.add_mutually_exclusive_group

There are times when certain keys cannot appear with other keys in an input
file.  This is especially often true of boolean keys.  The 
:meth:`~InputReader.add_mutually_exclusive_group` method allows you to declare
a group of keys that may not appear in the input file together.  Let's look
back to our unit conversion example.  

.. testcode::

    reader = InputReader()
    # The distance units
    dunits = reader.add_mutually_exclusive_group()
    dunits.add_boolean_key('milimeters')
    dunits.add_boolean_key('centimeters')
    dunits.add_boolean_key('meters')
    dunits.add_boolean_key('kilometers')
    # The time units
    tunits = reader.add_mutually_exclusive_group()
    tunits.add_boolean_key('seconds')
    tunits.add_boolean_key('minutes')
    tunits.add_boolean_key('hours')

    # OK!
    inp = reader.read_input(['meters', 'seconds'])
    # Error!!!!
    try:
        reader.read_input(['meters', 'milimeters', 'seconds'])
    except ReaderError as e:
        print str(e)

The above code would output

.. testoutput::

    ...Only one of 'centimeters', 'kilometers', 'meters', or 'milimeters' may be included.


dest
''''

We illustrated that we can use the *dest* option of the
:meth:`~InputReader.add_boolean_key` method to send keys to a different
namespace.  If your keys are part of a mutually exclusive group, you should let
the group handle this for you.  This will be cleaner and give better error
messages:

.. testcode::

    reader = InputReader()
    # The distance units
    dunits = reader.add_mutually_exclusive_group(dest='distconv')
    dunits.add_boolean_key('meters', action=lambda x: 1.0 * x)
    dunits.add_boolean_key('centimeters', action=lambda x: 100.0 * x)
    dunits.add_boolean_key('kilometers', action=lambda x: 0.001 * x)
    dunits.add_boolean_key('millimeters', action=lambda x: 1000.0 * x)
    # The time units
    tunits = reader.add_mutually_exclusive_group(dest='timeconv')
    tunits.add_boolean_key('seconds', action=lambda x: x / 1.0)
    tunits.add_boolean_key('minutes', action=lambda x: x / 60.0)
    tunits.add_boolean_key('hours', action=lambda x: x / 3600.0)
    
    inp = reader.read_input(['centimeters', 'minutes'])

    # No matter what boolean key was used, the conversion function is under
    # "distconv".  The original key names have been removed.
    if 'centimeters' in inp:
        print "This will never print"

    print inp.distconv(50), inp.timeconv(1800)
    inp = reader.read_input(['kilometers', 'hours'])
    print inp.distconv(50), inp.timeconv(1800)

    # Error:
    try:
        inp = reader.read_input(['meters', 'millimeters', 'hours'])
    except ReaderError as e:
        print str(e)

The above code would output

.. testoutput::

    5000.0 30.0
    0.05 0.5
    ...Only one of 'centimeters', 'kilometers', 'meters', or 'millimeters' may be included.

default
'''''''

You may notice that the aboce code cannot handle the situation of a missing
distance coversion or time conversion:

.. testcode::

    inp = reader.read_input(['minutes'])
    try:
        print inp.distconv(50), inp.timeconv(1800)
    except TypeError as e:
        print str(e) # 'NoneType' object is not callable

.. testoutput::
    :hide:

    ...'NoneType' object is not callable

Obvously, we can work around this issue by having a default for the whole
mutually exclusive group:

.. testcode::

    reader = InputReader()
    # The distance units
    dunits = reader.add_mutually_exclusive_group(dest='distconv', default=lambda x: 1.0 * x)
    dunits.add_boolean_key('meters', action=lambda x: 1.0 * x)
    dunits.add_boolean_key('centimeters', action=lambda x: 100.0 * x)
    dunits.add_boolean_key('kilometers', action=lambda x: 0.001 * x)
    dunits.add_boolean_key('millimeters', action=lambda x: 1000.0 * x)
    # The time units
    tunits = reader.add_mutually_exclusive_group(dest='timeconv', default=lambda x: x / 1.0)
    tunits.add_boolean_key('seconds', action=lambda x: x / 1.0)
    tunits.add_boolean_key('minutes', action=lambda x: x / 60.0)
    tunits.add_boolean_key('hours', action=lambda x: x / 3600.0)
    
    inp = reader.read_input(['minutes'])
    print inp.distconv(50), inp.timeconv(1800)

The above code would output

.. testoutput::

    50.0 30.0

required
''''''''

An alternative to supplying a *default* is to simply make one of the keys in
the mutually exclusive group required:

.. testcode::

    reader = InputReader()
    # The distance units
    dunits = reader.add_mutually_exclusive_group(dest='distconv', required=True)
    dunits.add_boolean_key('meters', action=lambda x: 1.0 * x)
    dunits.add_boolean_key('centimeters', action=lambda x: 100.0 * x)
    dunits.add_boolean_key('kilometers', action=lambda x: 0.001 * x)
    dunits.add_boolean_key('millimeters', action=lambda x: 1000.0 * x)
    # The time units
    tunits = reader.add_mutually_exclusive_group(dest='timeconv', required=True)
    tunits.add_boolean_key('seconds', action=lambda x: x / 1.0)
    tunits.add_boolean_key('minutes', action=lambda x: x / 60.0)
    tunits.add_boolean_key('hours', action=lambda x: x / 3600.0)
    
    try:
        inp = reader.read_input(['minutes'])
    except ReaderError as e:
        print str(e)

The above code would output

.. testoutput::

    ...One and only one of 'centimeters', 'kilometers', 'meters', or 'millimeters' must be included.

.. hint::

    Don't bother defining a *default* if *required* equals |True|.

.. _gotchas:

Putting it all together
-----------------------

Let's now take the best of the above examples to make a full working input
reader definition for the plotting program:

.. testcode:: fullexample

    from input_reader import InputReader, ReaderError
    reader = InputReader()

    # Distance conversion booleans.  Default is meters.
    dunits = reader.add_mutually_exclusive_group(dest='distconv', default=lambda x: 1.0 * x)
    dunits.add_boolean_key('meters', action=lambda x: 1.0 * x)
    dunits.add_boolean_key('centimeters', action=lambda x: 100.0 * x)
    dunits.add_boolean_key('kilometers', action=lambda x: 0.001 * x)
    dunits.add_boolean_key('millimeters', action=lambda x: 1000.0 * x)

    # Time conversion booleans. Default is seconds.
    tunits = reader.add_mutually_exclusive_group(dest='timeconv', default=lambda x: x / 1.0)
    tunits.add_boolean_key('seconds', action=lambda x: x / 1.0)
    tunits.add_boolean_key('minutes', action=lambda x: x / 60.0)
    tunits.add_boolean_key('hours', action=lambda x: x / 3600.0)

    # The raw data file(s)
    reader.add_line_key('rawdata', case=True, repeat=True, required=True)

    # Output file
    formats = ('pdf', 'png', 'jpg', 'svg', 'bmp', 'eps')
    compress = ('zip', 'tgz', 'tbz2', None)
    reader.add_line_key('output', case=True, type=str, required=True,
                        keywords={'format':{'type':formats, 'default':'pdf'},
                                  'compression':{'type':compress, 'default':None}})

    # Line and point styles
    colors = ('green', 'red', 'blue', 'orange', 'black', 'violet')
    reader.add_line_key('linestyle', type=('solid', 'dashed', 'dotted'),
                        keywords={'color':{'type':colors,'default':'black'},
                                  'size' :{'type':int,   'default':1}})
    reader.add_line_key('pointstyle', type=('circles', 'squares', 'triangles'),
                        keywords={'color':{'type':colors,'default':'black'},
                                  'size' :{'type':int,   'default':1}})

    # Optional legend on the plot
    legend = reader.add_block_key('legend')
    legend.add_boolean_key('shadow')
    legend.add_line_key('location', type=('upper_left', 'upper_right',
                                          'lower_left', 'lower_right'))
    size = legend.add_block_key('size', end='subend')
    size.add_line_key('box', type=int)
    size.add_line_key('font', type=int)

    # Optional polygon(s) to draw on the plot
    polygon = reader.add_block_key('polygon', repeat=True)
    polygon.add_regex_line('xypoint', r'(-?\d+\.?\d*) (-?\d+\.?\d*)', repeat=True)

Let's say that we give the following input to the input reader::

    # Plot in centimeters
    centimeters
    # ... and in hours
    hours

    # Read from two data files
    rawdata /path/to/DATA.txt # absolute path
    rawdata ../raw.txt        # relative path

    # Output filename and format
    output myplot format=png compression=zip

    # Line and point styles
    linestyle dashed
    # Point style... make them big, and green!
    pointstyle circles color=green size=8

    # Note there is no legend or polygon in this input

This input file is passed to the input reader and the results are as follows:

.. testcode:: fullexample

    # You should always wrap the read_input code in a try block 
    # to catch reader errors
    try:
        inp = reader.read_input(user_input)
    except ReaderError as e:
        import sys
        sys.exit(str(e))

    # Let's take a look at the Namespace
    print inp.rawdata
    print inp.output
    print inp.linestyle
    print inp.pointstyle
    print inp.legend, inp.polygon
    print inp.distconv(400)
    print inp.timeconv(7200)

The above code would output

.. testoutput:: fullexample

    ('/path/to/DATA.txt', '../raw.txt')
    ('myplot', {'compression': 'zip', 'format': 'png'})
    ('dashed', {'color': 'black', 'size': 1})
    ('circles', {'color': 'green', 'size': 8})
    None None
    40000.0
    2.0

:meth:`~InputReader.post_process`
---------------------------------

.. automethod:: InputReader.post_process

Please see :ref:`subclassing` for more details.

Gotchas
-------

case-sensitivity
''''''''''''''''

If you have set *case* to |True| in either the |InputReader|
constructor or in a block key, the variables in the |Namespace| must
be accessed with the same case that was given in the definition.  Conversely,
if *case* is |False|, the variables will be accessed with a lower-cased
version.  In the  *case* = |True| version:

.. code::

    reader = InputReader(case=True)
    reader.add_boolean_key('RED')
    try:
        inp = reader.read_input(['red']) # Error, 'red' != 'RED'
    except ReaderError:
        pass
    inp = reader.read_input(['RED'])
    print 'red' in inp # False
    print 'RED' in inp # True

In the *case* = |False| version (default):

.. code::

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

|InputReader| does not let you use strings with spaces in them.  This
is because it is impossible (read: very difficult to implement) to parse each
line without splitting them on whitespace first.  If a key name or other given
|str| had a space, it would be split and be difficult to detect,
resulting in unforeseen parsing errors.  For this reason,
|InputReader| will raise an error if it is attempted to give a
|str| with spaces.

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
expressions with an explicit space, but also with whitespace character
(:const:`"\s"`) and the anything character (:const:`"."`) as these may
potentially match spaces.  

