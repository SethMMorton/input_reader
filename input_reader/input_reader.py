from __future__ import division, print_function
import re

__all__ = ['InputReader', 'ReaderError', 'SUPPRESS', 'Namespace']

#################
# Private Classes
#################

class _KeyLevel(object):
    '''An abstract base class that knows how to add keys to itself'''

    def __init__(self, case=False):
        '''Initiallizes the key holders in this class'''
        # Are the keys case-sensitive by default?
        self._case = case

        # Default the key dictionary
        self._keys  = {}

        # The mutually exclusive groups
        self._meg = []

    def add_boolean_key(self, keyname, action=True, **kwargs):
        '''Add a boolean key to the input searcher.

        keyname is the name of the key to search for.

        action sets the value under the key as either True or False.

        '''
#        __doc__ = __doc__ + self._add_kwargs.__doc__
        # Lower keyname if not case sensitive
        if not self._case:
            keyname = keyname.lower()
        # Use global default if none was given
        if 'default' not in kwargs:
            kwargs['default'] = self._default
        # Store this key
        self._keys[keyname] = BooleanKey(keyname, action, **kwargs)

    def add_line_key(self, keyname, type=str, glob={}, keywords={},
                     case=None, **kwargs):
        '''Add a line key to the input searcher.

        keyname is the name of the key to search for.

        type is the data type that is to be read in for each positional
        argument, given as a list. The length of the list dictates how
        many arguments to look for. If this is an empty list or None,
        no positional arguments will be read in.
        Type may be one or more of:
        int
        float
        str
        None
        an explicit int, float or str
        a compiled regular expression object
        If you give an explicit int, float or str, it is assumed that the 
        value must equal what you gave.  None means that the word "none" is
        what is expected.
        If you only wish to read in one argument, you may give the type(s)
        for that one argument directly (meaning not in a list).  This will
        cause the returned value to be the value itself, an not a 1-length
        list.
        For each value, you may give a tuple of types to indicate more than
        one type is valid for that argument position.
        NOTE: Is is very important that type choices for each argument are
        given as tuples, and that the list passed to type is an actual list
        (as opposed to tuple) because these are treated differently.

        glob is a dictionary giving information on how to read in a glob.
        Globs are read in after the positional arguments.  If there are no
        positional arguments, then the whole line is globbed.  glob is not
        valid with keywords.
        the glob dictionary accepts only four keys:
        len  - type must be one of '*', '+', or '?'.  '*' is a zero or more
               glob, '+' is an at least one or more glob, and '?' is a 
               zero or one glob.
        type - Indicates the data type the glob must be.  This may be any
               one of the types presented for positional arguments. If this
               is omitted, then str is assumed.
        join - join will join the globbed values as a space-separated string
               and thus return a single string instead of a list.  Useful
               for reading in sentances.  The default is False if len is '*'
               or '+' and true if len is '?'.
        default - That is to be in the glob in the case that no glob is given.
                  If there is no default, nothing is put into the glob.

        keywords is a nested dictionary giving indicating keywords that can
        be read in. Each key in the dictionary is a keyword to look for, 
        and the value for that key is an other dictionary with the keys
        type and default.  If an empty dictionary or None is given, the
        defaults of str and SUPPRESS will be chosen.  Like positional
        arguments, you may give as many types as you wish per keyword.

        case states if this particular key is case-sensitive.  Note that
        this applies only to the arguments of the key, the key itself
        uses the global case sensitivity.

        '''
#        __doc__ = __doc__ + self._add_kwargs.__doc__
        # Use default case if no case is given here
        if case is None:
            case = self._case
        # Use global default if none was given
        if 'default' not in kwargs:
            kwargs['default'] = self._default
        # Lower keyname if not case sensitive
        if not case:
            keyname = keyname.lower()
        # Store this key
        self._keys[keyname] = LineKey(keyname, type, glob, keywords, case,
                                      **kwargs)

    def add_block_key(self, keyname, end='end', case=None,
                      ignoreunknown=None, **kwargs):
        '''Add a block key to the input searcher.

        keyname is the name of the key to search for.

        subkeys is a multi-level dictionary defined in _KeyLevel.

        end is the string used to signify the end of this block

        case states if this particular key is case-sensitive. Note that
        this applies only to the subkeys of this block; the key uses the
        global case-sensitivity default.

        ignoreunknown will suppress errors when an unknown key is found.

        '''
#        __doc__ = __doc__ + self._add_kwargs.__doc__
        # Use default case if no case is given here
        if case is None:
            case = self._case
        # Use global default if none was given
        if 'default' not in kwargs:
            kwargs['default'] = self._default
        # Use parents's ignoreunknown if not given
        if ignoreunknown is None:
            ignoreunknown = self._ignoreunknown
        # Lower keyname if not case sensitive
        if not case:
            keyname = keyname.lower()
        # Store this key
        self._keys[keyname] = BlockKey(keyname, end, case, ignoreunknown,
                                       **kwargs)
        return self._keys[keyname]

    def add_regex_line(self, handle, regex, case=None, **kwargs):
        '''Add a regular expression line to the input searcher.
        This searches the entire line based on the given regex.
        NOTE: You may either pass a string that will be converted to
        a regular expression object, or a compiled regular expression
        object.

        handle is the name to store the resultant regex match object,
        since this is not using keyword searching.

        regex is the regular expression to match to the line.

        case states if the search of this line is case-sensitive.
        This only applies if a string is given as the regex.  If a
        compiled regex object is given, it is assumed that case-
        insensitivity is already built in.

        '''
#        __doc__ = __doc__ + self._add_kwargs.__doc__
        # Use default case if no case is given here
        if case is None:
            case = self._case
        # Use global default if none was given
        if 'default' not in kwargs:
            kwargs['default'] = self._default
        # Lower handle name if not case sensitive
        if not case:
            handle = handle.lower()
        # Compile the regex if a string.
        if isinstance(regex , str):
            if case:
                regex = re.compile(regex)
            else:
                regex = re.compile(regex, re.IGNORECASE)

        # Store this key
        self._keys[handle] = Regex(handle, regex, **kwargs)

    def add_mutually_exclusive_group(self, case=None, dest=None, default=None,
                                     required=False):
        '''Defines a mutually exclusive group.

        See MutExGroup class definition for details.
        '''
        # Use default case if no case is given here
        if case is None:
            case = self._case
        if default is None:
            default = self._default
        # Add this group to the list, then return it
        self._meg.append(MutExGroup(case, dest, default, required,
                                    self._ignoreunknown))
        return self._meg[-1]

    def _add_kwargs(self, **kwargs):
        '''Keyword arguments:

        default is the value stored for this key if it does not appear in
        the input block.  A value of None is equivalent to no default.
        It makes no sense to give a default and mark it required also.
        If key is part of a mutually exclusive group, it is best to set
        the default for the group and not set it for the
        individual because otherwise you may get unforseen errors,
        unless you did not set a dest for the group in which case defaults
        for the individual keys will work as expected.
        If the class SUPPRESS is given instead of None, then this key
        will be removed from the namespace if it is not given.

        repeat is a boolean which states if there can be only one or
        several of this key.

        overwritedefault is only to be used with repeat.  If False, on the
        first appearance of the key word the new value will be appended
        to what was given as default (if default is not None).  If True,
        then the default value will be discarded before those found in the
        input are added.

        required indicates if not inlcuding this key is an error.
        It makes no sense to give a default and mark it required also.
        If key is part of a mutually exclusive group, it is best to set
        the required setting for the group and not set it for the
        individual because otherwise you may get unforseen errors.

        dest causes this key to be placed under a different name, which
        is given by dest.  
        If key is part of a mutually exclusive group, it is best to set
        the dest for the group and not set it for the individual because
        otherwise you may get unforseen errors.

        depends is a key that must also appear in the same input level
        for this key to be valid.
        '''
        # If this class defines a default default attribute, use that instead
        self._default = getattr(self, 'default', None)
        if self._default is None:
            self._default = kwargs.pop('default', None)

        # Repeat
        self._repeat = kwargs.pop('repeat', None)
        # Overwrite default only valid when repeat is True
        self._overwritedefault = kwargs.pop('overwritedefault', None)
        if not self._repeat and self._overwritedefault:
            self._overwritedefault = False

        # Required
        self._required = kwargs.pop('required', None)

        # If this class defines a default dest attribute, use that instead
        self._dest = getattr(self, 'dest', None)
        if self._dest is not None and not isinstance(self._dest, str):
            raise ReaderError ('dest value '+str(dest)+' must be a string')
        elif self._dest is None:
            self._dest = kwargs.pop('dest', None)

        # Depends
        self._depends = kwargs.pop('depends', None)

        # Make sure nothing extra was given
        if kwargs:
            msg = ': Unknown arguments given: '+','.join(kwargs.keys())
            raise ReaderError (self.name+msg)

    def _return_val(self, i, val, namespace):
        '''Returns the result properly, depending on stuff.'''
        name = self._dest if self._dest is not None else self.name
        if self._repeat:
            if name in namespace:
                if getattr(namespace, name) is None:
                    return i, name, (val,)
                elif self._overwritedefault:
                    if getattr(namespace, name) == self._default:
                        return i, name, (val,)
                    else:
                        return i, name, getattr(namespace, name)+(val,)
                else:
                    return i, name, getattr(namespace, name)+(val,)
            else:
                return i, name, (val,)
        else:
            if name in namespace:
                if getattr(namespace, name) != self._default:
                    raise ReaderError (self.name+': This key appears twice')
                else:
                    return i, name, val
            else:
                return i, name, val

    def _defaults(self):
        '''Return the defaults in a dictionary.'''
        defaults = {}
        for key, val in self._keys.items():
            if val._default is not SUPPRESS:
                name = val._dest if val._dest is not None else val.name
                defaults[name] = val._default
        for meg in self._meg:
            for key, val in meg._keys.items():
                if val._default is not SUPPRESS:
                    name = val._dest if val._dest is not None else val.name
                    defaults[name] = val._default
        return defaults

    def _parse_key_level(self, f, i):
        '''Parse the current key level, recursively
         parsing sublevels if necessary
        '''

        # Populate the namespace with the defaults
        namespace = Namespace(**self._defaults())

        # Populate the namespace with what was found in the input
        i, namespace = self._find_keys_in_input(f, i, namespace)

        # Post process to make sure that the keys fit the requirements
        self._post(namespace)

        return i, namespace

    def _find_keys_in_input(self, f, i, namespace):
        '''Find the keys in the input block.'''

        notend = True
        while i < len(f) and notend:

            # Only search for something if the line is not blank
            if f[i]:
                # Find if this line belongs to a key
                try:
                    i = self._find_key(f, i, namespace)
                except ReaderError as e:
                    # Error on unknown keys
                    if self._ignoreunknown:
                        if 'Unrecognized' not in str(e):
                            raise ReaderError (self.name+': '+str(e))
                    else:
                        raise ReaderError (self.name+': '+str(e))

            # Increment to the next line
            i += 1

            # If we are in the middle of a block, check if this is the end
            try:
                if self._case and f[i] == self._end:
                    notend = False
                elif not self._case and f[i].lower() == self._end:
                    notend = False
            except AttributeError:
                pass # Not a block, no end attribute
            except IndexError:
                if i == len(f) and self.name != 'main':
                    raise ReaderError (self.name+': Unterminated block.')

        return i, namespace

    def _find_key(self, f, i, namespace):
        '''Attempt to find a key in this line.
        Returns the new current line number.
        Raises a ReaderError if the key is not found
        '''

        first = f[i].split()[0]
        if not self._case:
            first = first.lower()
        # Find in the usual places
        for key, val in self._keys.items():
            try:
                if not val._regex.match(f[i]):
                    continue
            except AttributeError:
                if key != first:
                    continue
            inew, name, parsed = val._parse(f, i, namespace)
            # Add this to the namespace
            namespace.add(name, parsed)
            return inew

        # Look in the mutually exclusive groups if not in usual places
        for meg in self._meg:
            for key, val in meg._keys.items():
                try:
                    if not val._regex.match(f[i]):
                        continue
                except AttributeError:
                    if key != first:
                        continue
                inew, name, parsed = val._parse(f, i, namespace)
                namespace.add(name, parsed)
                return inew

        # If nothing was found, raise an error
        raise ReaderError (self.name+': Unrecognized key: '+f[i])

    def _post(self, namespace):
        '''Post-process the keys.'''

        # Process the mutually exclusive groups separately
        for meg in self._meg:
            nkeys = 0
            # Loop over each key in this group and count the
            # number in the namespace
            for key, val in meg._keys.items():
                name = val._dest if val._dest is not None else val.name
                if getattr(namespace, name, val._default) != val._default:
                    nkeys += 1
                    thekey = [name, getattr(namespace, name)]
            # If none of the keys in the group were found
            if nkeys == 0:
                # Alert the user if a required key group was not found
                if meg._required:
                    keys = meg._keys.keys()
                    msg = ': One and only one of '+', '.join(keys[:-1])
                    msg += ', or '+keys[-1]+' must be included.'
                    raise ReaderError (self.name+msg)
                # Set the dest to the default if not suppressing
                elif meg._dest:
                    if meg._default is not SUPPRESS:
                        # Set the default
                        setattr(namespace, meg._dest, meg._default)
                    # Delete the keys in the group from the namespace
                    for key in meg._keys:
                        namespace.remove(key)
            # If more than one key was given raise an error
            elif nkeys > 1:
                keys = meg._keys.keys()
                msg = ': Only one of '+', '.join(keys[:-1])+', or '
                msg += keys[-1]+' may be included.'
                raise ReaderError (self.name+msg)
            # Otherwise this meg is good to go
            else:
                # If there is a dest the prosses the keys
                if meg._dest:
                    # Add the dest name with the value of the found key
                    setattr(namespace, meg._dest, thekey[1])
                    # Replace this name in the order list
                    indx = namespace._order.index(thekey[0])
                    namespace._order[indx] = meg._dest
                    # Delete the keys in the group from the namespace
                    for key, val in meg._keys.items():
                        name = val._dest if val._dest is not None else val.name
                        namespace.remove(name)
                    # Delete these keys from the found lists
                    klist = list(meg._keys)
                    for key in klist:
                        del meg._keys[key]

        # Loop over the non-grouped keys and check key requirements
        for key, val in self._keys.items():
            # Identify missing required keys and raise error if not found
            name = val._dest if val._dest is not None else val.name
            if val._required and name not in namespace._order:
                msg = ': The key "'+key+'" is required but not found'
                raise ReaderError (self.name+msg)

        # Loop over the keys that were found and see if there are any
        # dependencies that were not filled.
        for key in namespace._order:
            # Check if this key has any dependencies,
            # and if so, they are given as well.
            for k, val in self._keys.items():
                name = val._dest if val._dest is not None else val.name
                if key == name:
                    depends = getattr(val, '_depends', None)
                    break
            else:
                depends = None
            # Raise an error if the depending key is not found
            if depends and depends not in namespace._order:
                msg = ': The key '+key+' requires that '+depends
                msg = ' is also present, but it is not'
                raise ReaderError (self.name+msg)

        # Last, tag on the defaults that were not found
        # in the input file to the end of the order.
        order = set(namespace._order)
        names = namespace.make_set()
        for key in names - order:
            namespace._order.append(key)

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

class LineKey(_KeyLevel):
    '''A class to store data on a line key'''

    def __init__(self, keyname, type=str, glob={}, keywords={}, case=False,
                 **kwargs):
        '''Defines a line key.'''
        _KeyLevel.__init__(self, case=case)
        # Fill in the values
        self.name = keyname
        # Add the generic keyword arguments
        self._add_kwargs(**kwargs)
        # Cannot have both glob and keywords defined
        if glob and keywords:
            msg = ': Cannot define both glob and keywords'
            raise ReaderError (self.name+msg)
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
        # Validate glob
        if glob:
            if 'len' not in glob:
                raise ReaderError (self.name+': "len" required for glob')
            elif glob['len'] not in ('*', '+', '?'):
                msg = ': "len" must be one of "*", "+", or "?" in glob'
                raise ReaderError (self.name+msg)
            if 'type' not in glob:
                glob['type'] = str
            if 'join' not in glob:
                if glob['len'] == '?':
                    glob['join'] = True
                else:
                    glob['join'] = False
            self._glob = glob
            # Make the result only a string when there is no positionals
            if not self._type and self._glob['join']:
                self._nolist = True
            elif self._type and self._glob:
                self._nolist = False
        else:
            self._glob = dict([]) # In case glob = None
        # Validate keywords
        if keywords:
            self._keywords = keywords
            # Since we append this dict to the end, we must keep as a list
            if self._nolist:
                self._nolist = False
        else:
            self._keywords = {} # In case keywords = None

    def _parse(self, f, i, namespace):
        '''Parses the current line for the key.  Returns the line that
        we read from and the value'''

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
                raise ReaderError (self.name+msg)
            # Checking keywords will be done later
        # If the # args is less than the positional
        elif len(args) < len(self._type):
            n = len(self._type)
            if self._glob.get('len') == '+':
                n += 1
            msg = ': expected at least '+str(n)
            msg += ' arguments, got '+str(len(args))
            raise ReaderError (self.name+msg)
        # If there are too many arguments
        elif len(args) > len(self._type):
            if not (self._keywords or self._glob):
                msg =': expected '+str(len(self._type))
                msg += ' arguments, got '+str(len(args))
                raise ReaderError (self.name+msg)

        def validate(val, typ, case):
            '''Checks that the given value is valid by checking
            its type. Raises ValueError if unsuccessful.
            '''
            # Check case if necessary
            if not case:
                try:
                    typ = type.lower()
                except AttributeError:
                    pass
            # One of the core datatypes
            if typ is float or typ is int or typ is str:
                return typ(val)
            # Excplicit None
            elif typ is None:
                if val.lower() == 'none':
                    return None
                else:
                    raise ValueError
            # Explicit choices
            elif (isinstance(typ, str) or isinstance(typ, int) or
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

        def make_readable(val):
            '''Returns a a string version of the input value.'''
            if (isinstance(val, str) or isinstance(val, int) or
                isinstance(val, float)):
                return str(val)
            elif val is None:
                return 'None'
            else:
                try:
                    return 'regex({0})'.format(val.pattern)
                except AttributeError:
                    return str(val).split()[1].strip("'><")

        def check_type(val, typ, case):
            '''Checks the type of a value, accounting for
            various forms of type'''
            if isinstance(typ, tuple):
                for tp in typ:
                    try:
                        return validate(val, tp, case)
                    except ValueError:
                        continue
                else:
                    msg = self.name+': expected one of {0}, got {1}'
                    t = []
                    for x in typ:
                        t.append(make_readable(x))
                    raise ReaderError (msg.format(', '.join(t), val))
            else:
                try:
                    return validate(val, typ, case)
                except ValueError:
                    msg = self.name+': expected {0}, got {1}'
                    raise ReaderError (msg.format(make_readable(typ), val))

        # Read in the arguments, making sure they match the types and choices
        val = []
        for a, t in zip(args[:len(self._type)], self._type):
            val.append(check_type(a, t, self._case))

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
                glob.append(check_type(a, t, self._case))
            if len(glob) < 1 and self._glob['len'] == '+':
                msg = ': at least one argument in glob required'
                raise ReaderError (self.name+msg)
            elif len(glob) > 1 and self._glob['len'] == '?':
                msg = ': no greater than one argument in glob allowed'
                raise ReaderError (self.name+msg)
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
                        glob[j] = str(v)
                    glob = ' '.join(glob)
            elif not glob:
                try:
                    glob.append(self._glob['default'])
                except KeyError:
                    pass
            # Tag onto the end of val and prep val
            if not val:
                val = glob
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
                    msg = ': Error reading keyword argument '+kvpair
                    raise ReaderError (self.name+msg)
                # Make sure the keyword is good
                if not self._case:
                    key = key.lower()
                if key not in self._keywords:
                    raise ReaderError (self.name+': Unknown keyword: '+key)
                # Assign this keyword
                try:
                    t = self._keywords[key]['type']
                except KeyError:
                    t = str # Default to string if not given
                kw[key] = check_type(value, t, self._case)
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
        '''Initiallizes the mutually exclusive group.

        subkeys is a multi-level dictionary defined in _KeyLevel.

        dest defines an alternate name for the key to be placed under
        than the key name.  Useful if you you wish to access the data
        from the mutually exclusive group without having to search
        the names of all the keys.  It also removes the names of the
        keys in this group from the namespace.  NOTE: It is best not
        to set the dest value for members of the group (just the group
        itself), as it may result in undetected errors.

        default is the default to use for the mutually exclusive group.
        only valid if dest is defined.  Overwrites the defaults of
        the keys in this group.  NOTE: It is best not to set the default
        value for members of the group (just the group itself), if
        you are assigning dest for this group, as it as it may result
        in undetected errors.  If SUPPRESS is given then this group
        will not apprear in the namespace if not found in input.

        required is if one of the members of the group is required
        or not. NOTE: It is best not to set the required status for
        members of the group (just the group itself), as it may result
        in the program flagging errors for keys in this group when there
        in fact is no error.
        '''
        _KeyLevel.__init__(self, case=case)
        self._default  = default
        if dest is not None and not isinstance(dest, str):
            raise ReaderError ('dest value '+str(dest)+' must be a string')
        else:
            self._dest = dest
        self._required = required
        self._ignoreunknown = _ignoreunknown

################
# Public Classes
################

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

class ReaderError (ValueError):
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

class InputReader(_KeyLevel):
    '''\
    :py:class:`InputReader` is a class that is designed to read in
    an input file and return the information contained based on rules
    supplied to the class using a syntax similar to what is used in 
    the :py:mod:`argparse` module in the Python standard library.


    :py:class:`InputReader` accepts blocks-type, line-type and
    boolean-type keys, mutually exclusive groups, required keys,
    defaults, and more.
    '''

    def __init__(self, comment=['#'], case=False, ignoreunknown=False,
                 default=None):
        '''Initiallize the :py:class:`InputReader` class.

        :keyword comment:
            Defines what is a comment in the input block.
            This can be a single string or a list of strings.
            The default is *['#']*.
        :type comment: str or list, optional
        :keyword case:
            Tells if the keys are case-sensitive or not.
            The default is :py:const:`False`.
        :type case: bool, optional
        :keyword ignoreunknown:
            Ignore keys that are not defined.  The default is
            :py:const:`False`.
        :type ignoreunknown: bool, optional
        :keyword default:
            The default default that will be given when a
            key is created without a default.
        :type default: optional
        '''
        _KeyLevel.__init__(self, case=case)

        # Name (main is default)
        self.name = 'main'

        # What constitutes a comment?
        if not isinstance(comment, list):
            comment = [comment]
        self._comment = comment

        # Ignore unknown keys?
        self._ignoreunknown = ignoreunknown

        # The default default
        self._default = default

    def read_input(self, filename):
        '''\
        Reads in the input from a given file using the supplied rules.

        :argument filename:
            The name of the file to read in.
        :type filename: str:
        :rtype: :py:class:`Namespace`
        :exception:
            :py:exc:`ReaderError`: Any known errors will be raised with
            this custom exception.
        '''

        # Read in the file, removeing comments and extra whitespace/newlines
        f = self._read_in_file(filename)

        # Parse this key level, recursively reading lower levels
        i, namespace = self._parse_key_level(f, 0)
        namespace.filename = filename
        namespace._order.append('filename')
        return namespace, f

    def _read_in_file(self, filename):
        '''Store the filename as a list'''

        # Read in the file into a list
        f = []
        try:
            with open(filename) as fl:
                for line in fl:
                    # Remove comments
                    for com in self._comment:
                        if com in line:
                            line = line.partition(com)[0]
                    # Add this to the list
                    f.append(line.strip())

        except (IOError, OSError) as e:
            from sys import exit, stderr
            print('Cannot read in file', filename, ':', e, file=stderr)
            exit(1)

        return f

