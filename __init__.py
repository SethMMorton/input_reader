from input_reader import InputReader, ReaderError, SUPPRESS, Namespace
from files import *

__all__ = [
           'InputReader',
           'ReaderError',
           'SUPPRESS',
           'Namespace', 
           'abs_file_path',
           'file_safety_check',
           'range_check',
          ]

def range_check(low, high, expand=True):
    '''\
    :py:func:`range_check` will verify that that given range has a
    *low* lower than the *high*.  If both numbers are integers, it
    will return a list of the expanded range unless *expand* is
    :py:const:`False`, in which it will just return the high and low.
    If *low* or *high* is not an integers, it will return the *low*
    and *high* values as floats.

    :argument low:
       The low value if the range to check.
    :type low: float, int
    :argument high:
       The high value if the range to check.
    :type high: float, int
    :keyword expand:
        If :py:const:`True` and both *low* or *high* are integers, then
        :py:func:`range_check` will return the range of integers between
        *low* and *high*, inclusive. Otherwise, :py:func:`range_check`
        just returns *low* and *high*.
    :type expand: bool, optional
    :rtype:
        See the explanation of *expand*.
    :exception:
        * :py:exc:`ValueError`: *low* > *high*.
        * :py:exc:`ValueError`: *low* or *high* cannot be converted to a
          :py:func:`float`.
    '''
    if isinstance(low, int) and isinstance(high, int):
        if low >= high:
            raise ValueError('low >= high')
        return range(low, high+1) if expand else (low, high)
    try:
        if low.isdigit() and high.isdigit():
            low = int(low)
            high = int(high)
            if low >= high:
                raise ValueError('low >= high')
            return range(low, high+1) if expand else (low, high)
    except AttributeError:
        low = float(low)
        high = float(high)
        if low >= high:
            raise ValueError('low >= high')
        return low, high
