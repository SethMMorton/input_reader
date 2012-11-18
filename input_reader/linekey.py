from __future__ import division, print_function
from keylevel import _KeyLevel
from helpers import SUPPRESS, ReaderError

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
