# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
from .helpers import  ReaderError, SUPPRESS
from .py23compat import py23_str, py23_basestring

class _KeyLevel(object):
    """An abstract base class that provides functionality essential
    for a key"""

    def __init__(self, case=False):
        """Init the KeyLevel class"""

        # Are the keys case-sensitive by default?
        self._case = case
        if not isinstance(case, bool):
            raise ValueError('case must be bool, '
                              'given '+repr(self._case))

    def _validate_string(self, string):
        """Make sure a string has no spaces"""
        if string is None:
            return
        elif hasattr(string, 'pattern'):
            for s in (r'\s', r'.'):
                if s in string.pattern:
                    msg = ': Regex should not allow the possibility of spaces'
                    msg += ', given "'+string.pattern+'"'
                    raise ValueError(self.name+msg)
        else:
            if len(string.split()) == 0:
                msg = ': String cannot be of zero length'
                raise ValueError(self.name+msg)
            elif len(string.split()) > 1:
                msg = ': String cannot contain spaces, given "'+string+'"'
                raise ValueError(self.name+msg)

    def _return_val(self, i, val, namespace):
        """Returns the result properly, depending on the key type
        and how the user wants it."""

        # Substitute the keyname for dest if required
        name = self._dest if self._dest is not None else self.name

        # If multiple occurences of the keyname may appear, store
        # each of these in the namespace
        if self._repeat:
            # If this key has been found, check if we need to append to
            # the previous values or create the new value
            if name in namespace:
                return i, name, getattr(namespace, name)+(val,)
            # If the key jas not been found, simply return (as a tuple)
            else:
                return i, name, (val,)
        # In this case, only one instance of the keyname may appear
        # or it is an error.
        else:
            # If the keyname has already been found it is an error,
            if name in namespace:
                raise ReaderError(self.name+': The key "'+name+'" appears twice')
            # If the key has not been found, simply return
            else:
                return i, name, val

    def _add_kwargs(self, **kwargs):
        """Generic keyword arguments common to many methods"""

        # If this class defines a default default attribute, use that instead
        self._default = getattr(self, 'default', None)
        if self._default is None:
            self._default = kwargs.pop('default', None)

        # Repeat
        self._repeat = kwargs.pop('repeat', False)
        if not isinstance(self._repeat, bool):
            raise ValueError('repeat value must be a bool, '
                              'given '+repr(self._repeat))

        # Required
        self._required = kwargs.pop('required', False)
        if not isinstance(self._required, bool):
            raise ValueError('required value must be a bool, '
                              'given '+repr(self._required))

        # If this class defines a default dest attribute, use that instead
        self._dest = getattr(self, 'dest', None)
        if self._dest is None:
            self._dest = kwargs.pop('dest', None)
        if self._dest is not None and not isinstance(self._dest, py23_basestring):
            raise ValueError('dest value '+repr(self._dest)+' must be a str')

        # Depends
        self._depends = kwargs.pop('depends', None)

        # Make sure nothing extra was given
        if kwargs:
            msg = ': Unknown arguments given: '+','.join(kwargs)
            raise TypeError(self.name+msg)


class BooleanKey(_KeyLevel):
    """A class to store data in a boolean key"""

    def __init__(self, keyname, action, **kwargs):
        """Defines a boolean key."""
        super(BooleanKey, self).__init__()
        # Fill in the non-generic values
        self.name     = keyname
        self._action  = action
        # Add the generic keyword arguments
        self._add_kwargs(**kwargs)
        # Check strings
        self._validate_string(self.name)
        self._validate_string(self._dest)

    def _parse(self, f, i, namespace):
        """Parses the current line for the key.  Returns the line that
        we read from and the value"""
        n = len(f[i].split())
        if n == 1:
            return self._return_val(i, self._action, namespace)
        else:
            raise ReaderError('The boolean "'+self.name+'" was given '
                               'arguments, this is illegal')


class Regex(_KeyLevel):
    """A class to store data from a regex"""

    def __init__(self, handle, regex, **kwargs):
        """Defines a regex searcher."""
        super(Regex, self).__init__()
        # Fill in the non-generic values
        self.name    = handle
        self._regex  = regex
        # Add the generic keyword arguments
        self._add_kwargs(**kwargs)
        # Check strings
        self._validate_string(self.name)
        self._validate_string(self._dest)

    def _parse(self, f, i, namespace):
        """Parses the current line for the regex.  Returns the match objext
        for the line."""

        # Grab the match object for this line
        val = self._regex.match(f[i])
        return self._return_val(i, val, namespace)


class LineKey(_KeyLevel):
    """A class to store data on a line key"""

    def __init__(self, keyname, type, glob, keywords, case, **kwargs):
        """Defines a line key."""
        super(LineKey, self).__init__(case=case)
        # Fill in the values
        self.name = keyname
        # Add the generic keyword arguments
        self._add_kwargs(**kwargs)
        # Check strings
        self._validate_string(self.name)
        self._validate_string(self._dest)
        # Cannot have both glob and keywords defined
        if glob and keywords:
            msg = ': Cannot define both glob and keywords'
            raise TypeError(self.name+msg)
        # Validate type
        # type given as a list
        if isinstance(type, list):
            self._type = type
            self._nolist = False
        # type given as a single value
        elif type is None:
            self._type = []
            self._nolist = False
        else:
            self._type = [type]
            self._nolist = True

        self._check_types_in_list(self._type)

        # Validate glob
        if glob:
            if not isinstance(glob, dict):
                raise ValueError(self.name+': glob must be a dict')
            if 'len' not in glob:
                raise ValueError(self.name+': "len" required for glob')
            elif glob['len'] not in ('*', '+', '?'):
                msg = ': "len" must be one of "*", "+", or "?" in glob'
                raise ValueError(self.name+msg)
            if 'type' not in glob:
                glob['type'] = str
            if isinstance(glob['type'], list):
                msg = ': list not allowed in type for glob or keywords'
                raise ValueError(self.name+msg)
            self._check_types_in_list([glob['type']])
            if 'join' not in glob:
                glob['join'] = False
            if glob['join'] and glob['len'] == '?':
                msg = ': "join=True" makes no sense for "len=?"'
                raise ValueError(self.name+msg)
            if set(glob.keys()) != set(['len', 'type', 'join']):
                if set(glob.keys()) != set(['len', 'type', 'join', 'default']):
                    raise TypeError(self.name+': Unknown key in glob')
            if not isinstance(glob['join'], bool):
                raise ValueError(self.name+': "join" must be a bool in glob')
            # Make the result is only a string when there is no positionals
            if not self._type and (glob['join'] or glob['len'] == '?'):
                self._nolist = True
            else:
                self._nolist = False
            self._glob = glob
        else:
            self._glob = {} # In case glob = None

        # Validate keywords
        if keywords:
            if not isinstance(keywords, dict):
                raise ValueError(self.name+': keywords must be a dict')
            for key in keywords:
                if not isinstance(key, py23_basestring):
                    msg = ': keys in keywords must be of type str'
                    raise ValueError(self.name+msg)
                else:
                    self._validate_string(key)
                if keywords[key] is None:
                    keywords[key] = {}
                elif not isinstance(keywords[key], dict):
                    msg = ': Options for keyword "'+key+'" must be a dict'
                    raise ValueError(self.name+msg)
                if 'default' not in keywords[key]:
                    keywords[key]['default'] = SUPPRESS
                if 'type' not in keywords[key]:
                    keywords[key]['type'] = str
                if set(keywords[key].keys()) != set(['default', 'type']):
                    msg = ': Unknown key in keyword: "'+key+'"'
                    raise TypeError(self.name+msg)
                # Check the type of the keyword
                if isinstance(keywords[key]['type'], list):
                    msg = ': list not allowed in type for glob or keywords'
                    raise ValueError(self.name+msg)
                else:
                    self._check_types_in_list([keywords[key]['type']])
            self._keywords = keywords

            # Since we append this dict to the end, we must keep as a list
            # unless only the keywords are being kept
            self._nolist = True if not self._type else False
        else:
            self._keywords = {} # In case keywords = None

        # Type, glob and keywords can't be empty
        if not (self._type or self._glob or self._keywords):
            msg = ': type, glob and keywords cannot all be empty'
            raise ValueError(self.name+msg)

    def _parse(self, f, i, namespace):
        """Parses the current line for the key.  Returns the line that
        we read from and the value"""

        # Separate the arguments from the key
        if self._case:
            args = f[i].split()[1:]
        else:
            args = f[i].lower().split()[1:]

        # Check that the length of args matches the type length
        if len(args) == len(self._type):
            if not self._glob and not self._keywords:
                pass # Not expecting anything else, we're good to go
            elif self._glob.get('len') == '+':
                msg = ': expected at least '+str(len(self._type)+1)
                msg += ' arguments, got '+str(len(args))
                raise ReaderError(self.name+msg)
            # Checking keywords will be done later

        # If the # args is less than the positional
        elif len(args) < len(self._type):
            if self._glob.get('len') == '+':
                msg = ': expected at least '+str(len(self._type)+1)
            else:
                msg = ': expected '+str(len(self._type))
            msg += ' arguments, got '+str(len(args))
            raise ReaderError(self.name+msg)

        # If there are too many arguments
        elif len(args) > len(self._type):
            if self._keywords:
                pass
            elif self._glob and self._glob['len'] in ('*', '+'):
                pass
            else:
                n = len(self._type)
                if self._glob.get('len') == '?':
                    n += 1
                    msg =': expected at most '+str(n)
                else:
                    msg =': expected '+str(n)
                if len(args) != n:
                    msg += ' arguments, got '+str(len(args))
                    raise ReaderError(self.name+msg)

        # Read in the arguments, making sure they match the types and choices
        val = []
        for a, t in zip(args[:len(self._type)], self._type):
            val.append(self._check_type_of_value(a, t, self._case))

        # Remove the arguments that were just read in
        try:
            args = args[len(self._type):]
        except IndexError:
            args = []

        # Read in the glob or the keywords
        glob = []
        kw = {}
        if self._glob:
            t = self._glob['type']
            for a in args:
                glob.append(self._check_type_of_value(a, t, self._case))
            # Assign the default if there was nothing
            if self._glob['join']:
                if not glob:
                    try:
                        glob = self._glob['default']
                    except KeyError:
                        pass
                else:
                    # Change all the globbed values to strings
                    for j, v in enumerate(glob):
                        glob[j] = py23_str(v)
                    glob = ' '.join(glob)
            elif not glob:
                try:
                    glob.append(self._glob['default'])
                except KeyError:
                    pass
            # Tag onto the end of val and prep val
            if not val:
                if self._nolist:
                    if isinstance(glob, py23_basestring):
                        val = glob
                    else:
                        try:
                            val = glob[0]
                        except IndexError:
                            val = ''
                else:
                    val = tuple(glob)
            elif not glob:
                if self._nolist:
                    val = val[0]
                else:
                    val = tuple(val)
            elif self._glob['join']:
                val.append(glob)
                val = tuple(val)
            else:
                val.extend(glob)
                val = tuple(val)
        elif self._keywords:
            # Each keyword is assumed to be key=value with no spaces
            for kvpair in args:
                try:
                    key, value = kvpair.split('=')
                except ValueError:
                    msg = ': Error reading keyword argument "'+kvpair+'"'
                    raise ReaderError(self.name+msg)
                # Make sure the keyword is good
                if not self._case:
                    key = key.lower()
                if key not in self._keywords:
                    raise ReaderError(self.name+': Unknown keyword: "'+key+'"')
                # Assign this keyword
                try:
                    t = self._keywords[key]['type']
                except KeyError:
                    t = str # Default to string if not given
                kw[key] = self._check_type_of_value(value, t, self._case)
            # Assign the defaults
            for key in self._keywords:
                try:
                    default = self._keywords[key]['default']
                except KeyError:
                    continue
                if key not in kw and default is not SUPPRESS:
                    kw[key] = default
            # Tag onto the end of val and prep val
            if not val:
                val = kw
            elif not kw:
                if self._nolist:
                    val = val[0]
                else:
                    val.append({})
                    val = tuple(val)
            else:
                val.append(kw)
                val = tuple(val)
        else:
            if self._nolist:
                try:
                    val = val[0]
                except IndexError:
                    val = ''
            else:
                val = tuple(val)

        return self._return_val(i, val, namespace)

    def _check_types_in_list(self, typ):
        """Make sure each type in a list is legal.  The function is recursive"""
        for t in typ:
            if isinstance(t, list):
                msg = ': Embedded lists not allowed in type'
                raise ValueError(self.name+msg)
            elif isinstance(t, tuple):
                if len(t) == 0:
                    msg = ': Empty tuple in type'
                    raise ValueError(self.name+msg)
                else:
                    self._check_types_in_list(t)
            elif not (isinstance(t, py23_basestring) or isinstance(t, int) or
                      isinstance(t, float) or t is None or
                      hasattr(t, 'pattern') or t is str or t is int or
                      t is float):
                msg = (': type must be one of None, str, float '
                       'int, or an instance of str, float, '
                       'int or regex')
                raise ValueError(self.name+msg)
            if isinstance(t, py23_basestring) or hasattr(t, 'pattern'):
                self._validate_string(t)

    def _validate_given_value(self, val, typ, case):
        """Checks that the given value is valid by checking
        its type. Raises ValueError if unsuccessful.
        """
        # Check case if necessary
        if not case:
            try:
                typ = type.lower()
            except AttributeError:
                pass
        # One of the core datatypes
        if typ is float or typ is int or typ is str:
            return typ(val)
        # Explicit None
        elif typ is None:
            if val.lower() == 'none':
                return None
            else:
                raise ValueError
        # Explicit choices
        elif (isinstance(typ, py23_basestring) or isinstance(typ, int) or
              isinstance(typ, float)):
            if type(typ)(val) == typ:
                return type(typ)(val)
            else:
                raise ValueError
        # Regular expression
        else:
            if typ.match(val):
                return val
            else:
                raise ValueError

    def _check_type_of_value(self, val, typ, case):
        """Checks the type of a value, accounting for
        various forms of type"""
        if isinstance(typ, tuple):
            for tp in typ:
                try:
                    return self._validate_given_value(val, tp, case)
                except ValueError:
                    continue
            else:
                msg = self.name+': expected one of {0}, got "{1}"'
                t = sorted([self._make_value_readable(x) for x in typ])
                t = ', '.join(t[:-1])+' or '+t[-1]
                raise ReaderError(msg.format(t, val))
        else:
            try:
                return self._validate_given_value(val, typ, case)
            except ValueError:
                msg = self.name+': expected {0}, got "{1}"'
                raise ReaderError(msg.format(self._make_value_readable(typ), val))

    def _make_value_readable(self, val):
        """Returns a a string version of the input value."""
        if isinstance(val, int) or  isinstance(val, float):
            return str(val)
        elif isinstance(val, py23_basestring):
            return '"'+str(val)+'"'
        elif val is None:
            return '"None"'
        else:
            try:
                return 'regex({0})'.format(val.pattern)
            except AttributeError:
                return str(val).split()[1].strip("'><")

