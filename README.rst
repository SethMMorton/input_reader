input_reader
============

A python module to facilitate reading input files
-------------------------------------------------

``input_reader`` is used to define and read a general input file for a program.
This ``README`` only contains a *brief* synopsis of what ``input_reader`` can
do.  For a more detailed description of the API, please see the documentation
at http://packages.python.org/input_reader.  The API is inspired by that of the
``argparse`` module from the python standard library, so hopefully it will be
easy to learn.

The Problem
-----------

Let's say you have to write a program that cooks a meal.  You have the
following requirements:

    1) The user must specify one and only one of breakfast, lunch, or dinner.

        a) For breakfast, the user must specify scrambled or poached eggs and
           how many eggs.  Also, the user specifies waffles or pancakes, and
           specifies if they want butter and/or syrup.  The user may
           optionally request bacon.

        b) For lunch, the user must specify if they want a sandwich (BLT,
           ham, or turkey) or soup (vegetable or chili). The user also
           specifies if they want bread.

        c) For dinner, the user specifies steak (rare, medium or well),
           salmon, or pasta (red or white sauce).  There is a choice of
           soup or salad.  The user may also choose to have dessert.

    2) The user must specify a drink, and that drink can be water, milk,
       OJ, beer, soda, or wine.

    3) The user can request an organic meal and/or gluten-free.

How We Want the Input Files
---------------------------

Let's say that someone wants a scrambled egg breakfast with syrupy pancakes
and bacon, and OJ for a drink.  Here is how we might define the input::

    drink oj

    breakfast
        eggs 2 scrambled
        pancakes syrup
        bacon
    end

Or, what if someone with a gluten allergy wants dinner with wine. They want
a medium steak with salad, and they want the dessert.  Here is the input::

    nogluten

    drink wine

    dinner
        steak medium
        salad
        dessert
    end

The ``input_reader`` Code
-------------------------

To define the above requirements, we would use the following code:

.. code:: python

    import sys
    from input_reader import InputReader, ReaderError

    reader = InputReader()

    # Gluten free or organic meal?  These are simple booleans
    reader.add_boolean_key('nogluten')
    reader.add_boolean_key('organic')

    # The drink has an argument, and accepts a specific list of values
    reader.add_line_key('drink', type=('water', 'milk', 'oj', 'beer', 'soda', 'wine'))

    # We are allowed to specify breakfast, lunch or dinner, so we use
    # a mutually exclusive group.  We need one of these, so we call this
    # required.
    meal = reader.add_mutually_exclusive_group(required=True)

    # We define the breakfast block
    bfast = meal.add_block_key('breakfast')
    # Eggs, number of eggs then the style
    bfast.add_line_key('eggs', type=[int, ('scrambled', 'poached')], required=True)
    # Pancakes OR waffles.  Syrup and/or butter is optional
    wp = bfast.add_mutually_exclusive_group(required=True)
    wp.add_line_key('waffles', type=None, glob={'len':'*', 'type':('syrup', 'butter')})
    wp.add_line_key('pancakes', type=None, glob={'len':'*', 'type':('syrup', 'butter')})
    # BACON!
    bfast.add_boolean_key('bacon')

    # The lunch block
    lunch = meal.add_block_key('lunch')
    # Bread?
    lunch.add_boolean_key('bread')
    # Sandwitch or soup
    ss = lunch.add_mutually_exclusive_group(required=True)
    ss.add_line_key('sandwich', type=('blt', 'ham', 'turkey'))
    ss.add_line_key('soup', type=('vegetable', 'chili'))

    # The dinner block
    dinner = meal.add_block_key('dinner')
    # Dessert?
    dinner.add_boolean_key('dessert')
    # Soup or salad?
    ss = dinner.add_mutually_exclusive_group()
    ss.add_boolean_key('soup')
    ss.add_boolean_key('salad')
    # Main course
    mcourse = dinner.add_mutually_exclusive_group(required=True)
    mcourse.add_line_key('steak', type=('rare', 'medium', 'well'))
    mcourse.add_boolean_key('salmon')
    mcourse.add_line_key('pasta', type=('red', 'white'))

You can read in and analyze the file in a manner given below:

.. code:: python

    # Assuming the input file is in argv[1], read in the input file
    try:
        inp = reader.read_input(sys.argv[1])
    except ReaderError as e:
        sys.exit(str(e))

    # Is the meal gluten free?
    if inp.nogluten:
        ...

    # Is lunch served?
    if inp.lunch:
        # If so, what type of soup?
        if inp.lunch.soup == 'chili':
            ...

    # Etc...

Author
------

Seth M. Morton

History
-------

01-14-2013 v. 1.0.2
'''''''''''''''''''

    - Added input_file attribute to InputReader class
    - Fixed typo in documentation
    - Updated version updating code

12-22-2012 v. 1.0.1
'''''''''''''''''''

    - Fixed error in MANIFEST.in

12-16-2012 v. 1.0.0
'''''''''''''''''''

    - Fixed bugs in unit tests
    - Finished documentation with doctests
    - Added a post_process method to InputReader that can be subclassed
    - Made improvements to the setup process

12-3-2012 v. 0.9.1
''''''''''''''''''

    - Added unit tests
    - Added extra checks for bad input

