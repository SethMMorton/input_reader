from __future__ import unicode_literals
from input_reader import InputReader, ReaderError
from pytest import raises

# Subclass InputReader to implement the post_process method
class MyInputReader(InputReader):
    def __init__(self):
        super(MyInputReader, self).__init__()
    def post_process(self, namespace):
        """ Process the regular expression in a way that is easier to use"""

        allowedcolors = ('red', 'green', 'blue', 'yellow', 'violet')
        numbers = []
        colors = []
        for r in namespace.sample:
            # Check validity of numbers
            num = float(r.group(1))
            if not (1000 > num > -1000):
                raise ReaderError ('sample: given number range must be '
                                   '-1000 < num < 1000, given '+str(num))
            numbers.append(num)

            # Check validity of colors
            col = r.group(2)
            if col not in allowedcolors:
                c = ', '.join([repr(x) for x in allowedcolors[:-2]])
                raise ReaderError ('sample: allowed colors are '+c+
                              ' '+repr(allowedcolors[-1])+', given '+repr(col))
            else:
                colors.append(col)

        # Add the results to the namespace
        namespace.add('numbers', tuple(numbers))
        namespace.add('colors', tuple(colors))

def test_custom_reader_works():
    # Use the custom input reader
    reader = MyInputReader()
    reader.add_regex_line('sample', r'(-?\d+\.?\d*) (\w+)', repeat=True)

    inp = reader.read_input(['40.432 red',
                             '-593 blue'])

    assert inp.sample[0].group(0) == '40.432 red'
    assert inp.sample[1].group(0) == '-593 blue'
    assert inp.numbers == (40.432, -593.0)
    assert inp.colors == ('red', 'blue')

def test_custom_reader_error():
    # Errors
    reader = MyInputReader()
    reader.add_regex_line('sample', r'(-?\d+\.?\d*) (\w+)', repeat=True)

    with raises(ReaderError) as e:
        inp = reader.read_input(['40.432 black'])
    assert 'allowed colors are' in str(e.value)

    with raises(ReaderError) as e:
        inp = reader.read_input(['-2000 blue'])
    assert ' given number range must be -1000 < num < 1000' in str(e.value)
