from __future__ import division, print_function
from keylevel import _KeyLevel
from helpers import ReaderError

class BooleanKey(_KeyLevel):
    '''A class to store data on a boolean key'''

    def __init__(self, keyname, action=True, **kwargs):
        '''Defines a boolean key.'''
        _KeyLevel.__init__(self)
        # Fill in the non-generic values
        self.name     = keyname
        self._action  = action
        # Add the generic keyword arguments
        self._add_kwargs(**kwargs)

    def _parse(self, f, i, namespace):
        '''Parses the current line for the key.  Returns the line that
        we read from and the value'''
        return self._return_val(i, self._action, namespace)

class Regex(_KeyLevel):
    '''A class to store data from a regex'''

    def __init__(self, handle, regex, **kwargs):
        '''Defines a regex searcher.'''
        _KeyLevel.__init__(self)
        # Fill in the non-generic values
        self.name    = handle
        self._regex  = regex
        # Add the generic keyword arguments
        self._add_kwargs(**kwargs)

    def _parse(self, f, i, namespace):
        '''Parses the current line for the regex.  Returns the match objext
        for the line.'''

        # Grab the match object for this line
        val = self._regex.match(f[i])
        return self._return_val(i, val, namespace)

class BlockKey(_KeyLevel):
    '''A class to store data in a block key'''

    def __init__(self, keyname, end='end', case=False, ignoreunknown=False,
                 **kwargs):
        _KeyLevel.__init__(self, case=case)
        '''Defines a block key.'''
        # Fill in the values
        self.name     = keyname
        if self._case:
            self._end  = end.lower()
        else:
            self._end  = end
        self._ignoreunknown = ignoreunknown
        # Add the generic keyword arguments
        self._add_kwargs(**kwargs)

    def _parse(self, f, i, namespace):
        '''Parses the current line for the key.  Returns the line that
        we read from and the value'''

        # Parse this block
        i, val = self._parse_key_level(f, i+1)
        return self._return_val(i, val, namespace)

class MutExGroup(_KeyLevel):
    '''A class to hold a mutually exclusive group'''

    def __init__(self, case=False, dest=None, default=None,
                 required=False, _ignoreunknown=False):
        '''Initiallizes the mutually exclusive group.'''
        _KeyLevel.__init__(self, case=case)
        self._default  = default
        if dest is not None and not isinstance(dest, str):
            raise ReaderError ('dest value '+str(dest)+' must be a string')
        else:
            self._dest = dest
        self._required = required
        self._ignoreunknown = _ignoreunknown
