# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
import sys

class Namespace(object):
    """A simple class to hold the keys and aruments found from the
    input file.  This is a copy-and-paste job from the argparse module
    with some minor additions.

    You can populate the :py:class:`Namespace` at initiallization with
    a series of key-value pairs.  These are considered the defaults.
    """

    def __init__(self, **defaults):
        self._order = []
        self._defaults = defaults.copy()

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

    def __iter__(self):
        for key in self.keys():
            yield key

    def __contains__(self, key):
        return key in self._order

    def __len__(self):
        return len(self._order)

    def add(self, key, val):
        """\
        Add a key-value pair to the :py:class:`Namespace`.

        :argument key:
            The key to add
        :type key: str
        :argument val:
            The value of the key
        :type val: anything
        """
        setattr(self, key, val)
        # Add this to the list of things found in the order found.
        # First check that it doesn't exist because duplicates can be
        # allowed
        if key not in self._order:
            self._order.append(key)
        # Remove this from the default dict
        try:
            del self._defaults[key]
        except KeyError:
            pass

    def remove(self, key):
        """\
        Remove a key from the :py:class:`Namespace`.

        :argument key:
            The key to remove.  If it does not exist, it is ignored.
        :type key: str
        """
        try:
            delattr(self, key)
        except AttributeError:
            pass
        try:
            self._order.remove(key)
        except ValueError:
            pass

    def get(self, key, default=None):
        """\
        Get the value of a key.  If the key does not exist, 
        `default` is returned. This is alternative to the
        namespace.key syntax that does not raise an error
        when `key` does not exist.

        :argument key: The key whose value you wish to retrieve.
        :type key: str
        :argument default:
        :type default: anything (default is :py:obj:`None`)
        :returns: The value associated with `key`
        """
        return getattr(self, key, default)

    def keys(self):
        """\
        Just like the :py:meth:`dict.keys` function for the python 
        :py:class:`dict`.

        :returns: :py:class:`tuple` of all keys in the :py:class:`Namespace`.
        """
        return tuple(self._order)

    def values(self):
        """\
        Just like the :py:meth:`dict.values` function for the python 
        :py:class:`dict`.

        :returns: :py:class:`tuple` of all values in the 
                  :py:class:`Namespace`.
        """
        return tuple([getattr(self, x) for x in self._order])

    def items(self):
        """\
        Just like the :py:meth:`dict.items` function for the python 
        :py:class:`dict`.

        :returns: :py:class:`tuple` of :py:class:`tuple` s of 
                  all key, value pairs in the :py:class:`Namespace`.
        """
        return tuple([(x, getattr(self, x)) for x in self._order])

    def finalize(self):
        """\
        Any defaults not yet added with the :py:meth:`add` are added
        to the :py:class:`Namespace`.
        """
        while True:
            try:
                key, val = self._defaults.popitem()
            except KeyError:
                break
            else:
                self.add(key, val)

class ReaderError(Exception):
    """\
    An exception for the :py:class:`InputReader` class.
    """
    def __init__(self, msg):
        self.msg = msg
    def __str__(self):
        return self.msg

class SUPPRESS(object):
    """
    Use this class to indicate that a key should be suppressed
    if not present (i.e. it does not appear in the input file).

    To use this, put :py:class:`SUPPRESS` for the default of a key.
    """
    pass
