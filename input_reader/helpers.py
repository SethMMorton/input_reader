from __future__ import division, print_function

class Namespace(object):
    '''A simple class to hold the keys and aruments found from the
    input file.  This is a copy-and-paste job from the argparse module
    with some minor additions.

    You can populate the Namespace when initiallization with a series
    of key-value pairs.
    '''

    def __init__(self, **kwargs):
        self._order = []
        for name in kwargs:
            setattr(self, name, kwargs[name])
            if name not in self._order:
                self._order.append(name)

    def __repr__(self):
        type_name = type(self).__name__
        arg_strings = []
        for name, value in self._get_kwargs():
            arg_strings.append('%s=%r' % (name, value))
        return '%s(%s)' % (type_name, ', '.join(arg_strings))

    def _get_kwargs(self):
        try:
            return [(k, getattr(self, k)) for k in self._order]
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

    def __len__(self):
        return len(self._order)

    def add(self, key, val):
        '''\
        Add a key-value pair to the :py:class:`Namespace`.

        :argument key:
            The key to add
        :type key: :py:class:`str`
        :argument val:
            The value of the key
        :type val: :py:class:`any`
        '''
        setattr(self, key, val)
        # Add this to the list of things found in the order found.
        # First check that it doesn't exist because duplicates can be
        # allowed
        if key not in self._order:
            self._order.append(key)

    def remove(self, key):
        '''\
        Remove a key from the :py:class:`Namespace`.

        :argument key:
            The key to remove.  If it does not exist, it is ignored.
        :type key: :py:class:`str`
        '''
        try:
            delattr(self, key)
        except AttributeError:
            pass
        try:
            self._order.remove(key)
        except ValueError:
            pass

    def get(self, key, default=None):
        '''\
        Get the value of a key.  If the key does not exist, 
        `default` is returned. This is alternative to the
        namespace.key syntax that does not raise an error
        when `key` does not exist.

        :argument key: The key whose value you wish to retrieve.
        :type key: :py:const:`str`
        :argument default:
        :type default: :py:class:`any` (default is :py:const:`None`)
        :returns: The value associated with `key`
        '''
        return getattr(self, key, default)

    def keys(self):
        '''\
        Just like the :py:meth:`keys` function for the python 
        :py:class:`dict`.

        :returns: :py:class:`tuple` of all keys in the :py:class:`Namespace`.
        '''
        return tuple(self._order)

    def values(self):
        '''\
        Just like the :py:meth:`values` function for the python 
        :py:class:`dict`.

        :returns: :py:class:`tuple` of all values in the 
                  :py:class:`Namespace`.
        '''
        return tuple([getattr(self, x) for x in self._order])

    def items(self):
        '''\
        Just like the :py:meth:`items` function for the python 
        :py:class:`dict`.

        :returns: :py:class:`tuple` of :py:class:`tuple`s of 
                  all key, value pairs in the :py:class:`Namespace`.
        '''
        return tuple([(x, getattr(self, x)) for x in self._order])

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
