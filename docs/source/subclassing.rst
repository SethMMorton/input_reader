.. default-domain:: py
.. currentmodule:: input_reader

.. testsetup::

    from os import utime
    with file('DATA.txt', 'a'):
        utime('DATA.txt', None)
    
.. testcleanup::

    from os import remove
    remove('DATA.txt')

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

.. _subclassing:

Sublcassing |InputReader|
=========================

Quite often it is necessary to do some further processing of the data that is
read in before it can be used.  This can range from actual further editing of
the data to simply rearranging the data to be more easily accessed.
|InputReader| has a :meth:`~InputReader.post_process` method that is called
immediately before the |Namespace| is returned from
:meth:`~InputReader.read_input`.  In the base |InputReader| class it is
implemented as a no-op (it does nothing), but you can subclass |InputReader|
and use this function to further edit the data in the |Namespace|.  

Here is the boilerplate to use to subclass |InputReader|:

.. code::

    from input_reader import InputReader, ReaderError

    class CustomReader(InputReader):

        # Run the InputReader initializations
        def __init__(self):
            super(CustomReader, self).__init__()

        # The post-processing code
        def post_process(self, namespace):
            pass

As an example of how we might use the :meth:`~InputReader.post_process` method,
let's use some examples from the plotting program used to discuss
|InputReader|.

Below is a full example of code that defines the custom reader, sets up the
reading rules, then takes a look at what is in the namespace. 

.. testcode:: 

    from input_reader import InputReader, ReaderError, abs_file_path
    from input_reader import abs_file_path, file_safety_check, range_check

    ############################
    # Define the custom reader #
    ############################

    class CustomReader(InputReader):

        # Run the InputReader initializations
        def __init__(self):
            super(CustomReader, self).__init__()

        # The post-processing code
        def post_process(self, namespace):

            # If a polygon is given, extract the data and store in a tuple of
            # the container class XYPoint 
            if 'polygon' in namespace:
                points = []
                class XYPoint(object):
                    pass
                for xy in namespace.polygon.xypoint:
                    xyp = XYPoint()
                    # We don't have to protect against ValueErrors here because
                    # the regex only accepted floating point numbers
                    xyp.x = float(xy.group(1))
                    xyp.y = float(xy.group(2))
                    points.append(xyp)
                # Access vertex points as namespace.polygon.vertices[0].x
                namespace.polygon.add('vertices', points)

            # Convert all filenames to absolute paths.  Make sure they exist
            namespace.rawdata = list(namespace.rawdata)
            for n in xrange(len(namespace.rawdata)):
                namespace.rawdata[n] = abs_file_path(namespace.rawdata[n])
                file_safety_check(namespace.rawdata[n]) # Raises IOError if unsafe
            namespace.rawdata = tuple(namespace.rawdata)

            # Also construct the output file name correctly
            out = abs_file_path(namespace.output[0])
            out = '.'.join([out, namespace.output[-1]['format']])
            # To be accessed as namespace.output['name'] (or 'compression')
            namespace.output = {'name': out, 
                                'compression': namespace.output[-1]['compression']}

    ###########################
    # Define the reader rules #
    ###########################

    # Remember to use your custom reader!
    reader = CustomReader()

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
    polygon = reader.add_block_key('polygon')
    polygon.add_regex_line('xypoint', r'(-?\d+\.?\d*) (-?\d+\.?\d*)', repeat=True)

    ##################
    # The input file #
    ##################

    from StringIO import StringIO
    from textwrap import dedent
    user_input = StringIO()
    user_input.write(dedent('''\
            # Plot in centimeters
            centimeters
            # ... and in hours
            hours

            # Read from two data files
            rawdata DATA.txt

            # Output filename and format
            output myplot format=png compression=zip

            # Line and point styles
            linestyle dashed
            # Point style... make them big, and green!
            pointstyle circles color=green size=8

            # Place a polygon
            polygon
                0 0
                4.5 0
                5 5.5
                0 5
            end
            '''))

    #########################
    # Namespace exploration #
    #########################

    inp = reader.read_input(user_input)

    print inp.rawdata
    print inp.output
    for vert in inp.polygon.vertices:
        print vert.x, vert.y

We would see this for output

.. testoutput::

    ('.../DATA.txt',)
    {'name': '.../myplot.png', 'compression': 'zip'}
    0.0 0.0
    4.5 0.0
    5.0 5.5
    0.0 5.0
