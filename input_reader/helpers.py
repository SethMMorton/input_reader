from __future__ import division, print_function

class Namespace(object):
    '''A simple class to hold the keys and aruments found from the
    input file.  This is a copy-and-paste job from the argparse module.
    '''

    def __init__(self, **kwargs):
        for name in kwargs:
            setattr(self, name, kwargs[name])
        self._order = []

    def __repr__(self):
        type_name = type(self).__name__
        arg_strings = []
        for name, value in self._get_kwargs():
            arg_strings.append('%s=%r' % (name, value))
        return '%s(%s)' % (type_name, ', '.join(arg_strings))

    def _get_kwargs(self):
        try:
            return [(k, self.__dict__[k]) for k in self._order]
        except AttributeError:
            return sorted(self.__dict__.items())

    def __eq__(self, other):
        try:
            return vars(self) == vars(other)
        except TypeError:
            return vars(self) == other

    def __ne__(self, other):
        return not (self == other)

    def __contains__(self, key):
        return key in self.__dict__

    def __iter__(self):
        self._ix = 0
        return self

    def add(self, key, val):
        setattr(self, key, val)
        # Add this to the list of things found in the order found.
        # First check that it doesn't exist because duplicates can be
        # allowed
        if key not in self._order:
            self._order.append(key)

    def remove(self, key):
        try:
            delattr(self, key)
        except AttributeError:
            pass
        try:
            self._order.remove(key)
        except ValueError:
            pass

    def next(self):
        if self._ix == len(self._order):
            raise StopIteration
        item = self.__dict__[self._order[self._ix]]
        self._ix += 1
        return item

    def make_set(self):
        return set(self.__dict__.keys()) - set(['_order'])

class ReaderError(Exception):
    '''\
    An exception for the :py:class:`InputReader` class.
    '''
    def __init__(self, msg):
        self.msg = msg
    def __str__(self):
        return self.msg

class SUPPRESS(object):
    '''
    Use this class to indicate that a key should be suppressed
    if not present (i.e. it does not appear in the namespace).

    To use this, put :py:class:`SUPRESS` for the default of a key.
    '''
    pass
