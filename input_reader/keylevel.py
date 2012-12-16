from __future__ import division, print_function
import re
from helpers import Namespace, SUPPRESS, ReaderError

class _KeyLevel(object):
    '''An abstract base class that knows how to add keys to itself'''

    def __init__(self, case=False):
        '''Initiallizes the key holders in this class'''
        # Are the keys case-sensitive by default?
        self._case = case
        if not isinstance(case, bool):
            raise ValueError ('case must be bool, '
                              'given '+repr(self._case))

        # Default the key dictionary
        self._keys  = {}

        # The mutually exclusive groups
        self._meg = []

    def add_boolean_key(self, keyname, action=True, **kwargs):
        '''Add a boolean key to the input searcher.

        :argument keyname:
            The name of the boolean-type key to search for.
        :type keyname: str
        :argument action:
            What value to store if this key is found.  The default is
            :py:obj:`True`.
        :argument required:
            Indicates that not inlcuding *keyname* is an error.
            It makes no sense to include this for a boolean key.
            The default is :py:obj:`False`.

            If *keyname* is part of a mutually exclusive group, it is best
            to set *required* for the group as a whole and not set it for 
            the individual members of the group because you may get unforseen
            errors.
        :type required: bool
        :argument default:
            The value stored for this key if it does not appear in
            the input block.  A value of :py:obj:`None` is equivalent
            to no default. It makes no sense to give a default and mark
            it *required* as well.  
            If the class :py:class:`SUPPRESS` is given instead of 
            :py:obj:`None`, then this key will be removed from the 
            namespace if it is not given.
            The default is :py:obj:`None`.

            If *keyname* is part of a mutually exclusive group and the
            group has been given a *dest* value, it is best
            to set *default* for the group as a whole and not set it for
            the individual members of the group because you may get 
            unforseen errors.
        :argument dest:
            If *dest* is given, *keyname* will be stored in the returned
            :py:class:`Namespace` as *dest*, not *keyname*.  
            A  value of :py:obj:`None` is equivalent to no dest.
            The default is :py:obj:`None`.

            If *keyname* is part of a mutually exclusive group and the
            group has been given a *dest* value, do not set *dest*
            for individual members of the group.
        :type dest: str
        :argument depends:
            Use *depends* to specify another key in the input file
            at the same input level (i.e. inside the same block or not
            in any block at all) that must also appear or a
            :py:exc:`ReaderError` will be raised.
            A  value of :py:obj:`None` is equivalent to no depends.
            The default is :py:obj:`None`.
        :type depends: str
        :argument repeat:
            Determines if *keyname* can appear only once in the input
            file or several times.  The default is :py:obj:`False`,
            which means this the *keyname* can only appear once or an
            error will be raised.  If *repeat* is :py:obj:`True`, the
            collected data will be returned in a list in the order in
            which it was read in.
            The default is :py:obj:`False`.
        :type repeat: bool
        '''
        # : keyname must be str
        if not isinstance(keyname, str):
            raise ValueError (repr(keyname)+': : keyname must be str')
        # Cannot repeat keys
        if keyname in self._keys:
            raise ReaderError ('The key "'+keyname+'" has been defined twice')
        # Lower keyname if not case sensitive
        if not self._case:
            keyname = keyname.lower()
        # Use global default if none was given
        if 'default' not in kwargs:
            kwargs['default'] = self._default
        # Store this key
        self._keys[keyname] = BooleanKey(keyname, action, **kwargs)
        return self._keys[keyname]

    def add_line_key(self, keyname, type=str, glob={}, keywords={},
                     case=None, **kwargs):
        '''Add a line key to the input searcher.

        :argument keyname:
            The name of the key to search for.
        :type keyname: str
        :argument type:
            The data type that to be read in for each positional
            argument, given as a :py:obj:`list`. The length of the list 
            dictates how many arguments to look for. If this is an empty 
            :py:obj:`list` or :py:obj:`None` no positional arguments will 
            be read in.

            *type* may be one or more of:

                - :py:obj:`int`
                - :py:obj:`float`
                - :py:obj:`str`
                - :py:obj:`None`
                - an explicit :py:obj:`int` (i.e. :py:const:`4`),
                  :py:obj:`float` (i.e. :py:const:`5.4`) or :py:obj:`str` (i.e.
                  :py:const:`"hello"`)
                - a compiled regular expression object

            If you give an explicit :py:obj:`int`, :py:obj:`float` or
            :py:obj:`str`, it is assumed that the 
            value must equal what you gave.  :py:obj:`None` means that the 
            word :py:const:`"none"` is
            what is expected.  NOTE: If the entirety of *type* is
            :py:obj:`None`, (i.e. ``type=None``), then no types are expected,
            and one of *glob* or *keywords* is required.

            If you only wish to read in one argument, you may give the type(s)
            for that one argument directly (meaning not in a :py:obj:`list`).  
            This will cause the returned value to be the value itself, not a 
            1-length :py:obj:`list`.

            For each value, you may give a :py:obj:`tuple` of types to indicate
            more than one type is valid for that argument position.
            NOTE: Is is very important that type choices for each argument are
            given as :py:obj:`tuple` s, and that the :py:obj:`list` passed to 
            *type* is an actual :py:obj:`list` (as opposed to :py:obj:`tuple`)
            because these are treated differently.

            The default value is :py:obj:`str`.
        :argument glob:
            *glob* is a :py:obj:`dict` giving information on how to read in a
            glob of arguments.  Globs are read in after the positional 
            arguments.  If there are no positional arguments, the whole 
            line is globbed.  *glob* is not valid with *keywords*.
            The glob :py:obj:`dict` accepts only four keys:

            *len*
                Must be one of :py:const:`'*'`, :py:const:`'+'`, or
                :py:const:`'?'`.  :py:const:`'*'` is a zero or more
                glob, :py:const:`'+'` is an at least one or more glob, and
                :py:const:`'?'` is a zero or one glob.
            *type*
                Indicates the data type the glob must be.  This may be
                any one of the types presented for positional arguments. 
                If this is omitted, then :py:obj:`str` is assumed.
            *join*
                *join* will join the globbed values as a space-separated
                :py:obj:`str` and thus return a single :py:obj:`str` 
                instead of a :py:obj:`list`.
                This is useful for reading in sentences or titles.  
                The default is :py:obj:`False` if *len* is :py:const:`'*'`
                or :py:const:`'+'`
                and :py:obj:`True` if *len* is :py:const:`'?'`.
            *default*
                In the case that no glob is given this is what will
                be put into the *glob*. If there is no default,
                nothing is put into the *glob*.

            By default this is an empty :py:obj:`dict`.
        :type glob: dict
        :argument keywords:
            *keywords* is a nested dictionary indicating key-value
            pairs that can be read in. Each key in the dictionary is a
            keyword to look for, and the value for that key is another
            dictionary with the keys *type* and *default*.  If an empty
            dictionary or :py:obj:`None` is given, the defaults of 
            :py:class:`str` and :py:class:`SUPPRESS` will be chosen,
            respectively.  Like positional arguments, you may give as 
            many types as you wish per keyword.

            By default this is an empty :py:obj:`dict`.
        :type keywords: nested dict
        :argument case:
            States if this particular key is case-sensitive. Note that
            this applies only to the arguments of *keyname*; *keyname*
            itself uses the case-sensitivity default of the current
            level.
            By default, case is determined by the global value set when
            initiallizing the class.
        :type case: bool
        :argument required:
            Indicates that not inlcuding *keyname* is an error.
            It makes no sense to give a *default* and mark it *required*
            as well.
            The default is :py:obj:`False`

            If *keyname* is part of a mutually exclusive group, it is best
            to set *required* for the group as a whole and not set it for 
            the individual members of the group because you may get unforseen
            errors.
        :type required: bool
        :argument default:
            The value stored for this key if it does not appear in
            the input block.  A value of :py:obj:`None` is equivalent
            to no default. It makes no sense to give a default and mark
            it *required* as well.  
            If the class :py:class:`SUPPRESS` is given instead of 
            :py:obj:`None`, then this key will be removed from the 
            namespace if it is not given.
            The default is :py:obj:`None`.

            If *keyname* is part of a mutually exclusive group and the
            group has been given a *dest* value, it is best
            to set *default* for the group as a whole and not set it for
            the individual members of the group because you may get 
            unforseen errors.
        :argument dest:
            If *dest* is given, *keyname* will be stored in the returned
            :py:class:`Namespace` as *dest*, not *keyname*.  
            A  value of :py:obj:`None` is equivalent to no dest.
            The default is :py:obj:`None`.

            If *keyname* is part of a mutually exclusive group and the
            group has been given a *dest* value, do not set *dest*
            for individual members of the group.
        :type dest: str
        :argument depends:
            Use *depends* to specify another key in the input file
            at the same input level (i.e. inside the same block or not
            in any block at all) that must also appear or a
            :py:exc:`ReaderError` will be raised.
            A  value of :py:obj:`None` is equivalent to no depends.
            The default is :py:obj:`None`.
        :type depends: str
        :argument repeat:
            Determines if *keyname* can appear only once in the input
            file or several times.  The default is :py:obj:`False`,
            which means this the *keyname* can only appear once or an
            error will be raised.  If *repeat* is :py:obj:`True`, the
            collected data will be returned in a list in the order in
            which it was read in.
            The default is :py:obj:`False`.
        :type repeat: bool
        '''
        # : keyname must be str
        if not isinstance(keyname, str):
            raise ValueError (repr(keyname)+': keyname must be str')
        # Cannot repeat keys
        if keyname in self._keys:
            raise ReaderError ('The key "'+keyname+'" has been defined twice')
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
        return self._keys[keyname]

    def add_block_key(self, keyname, end='end', case=None,
                      ignoreunknown=None, **kwargs):
        '''Add a block key to the input searcher.

        :argument keyname:
            The name of the key to search for.
        :type keyname: str
        :argument end:
            The :py:obj:`str` used to signify the end of this block.
            The default is :py:const:`'end'`.
        :type end: str
        :argument case:
            States if this particular key is case-sensitive. Note that
            this applies only to the subkeys of *keyname*; *keyname*
            itself uses the case-sensitivity default of the current
            level.
            By default, case is determined by the global value set when
            initiallizing the class.
        :type case: bool
        :argument ignoreunknown:
            Suppresses raising the :py:exc:`ReaderError` when an unknown
            key is found.
            By default, ignoreunknown is determined by the global value set when
            initiallizing the class.
        :type ignoreunknown: bool
        :argument required:
            Indicates that not inlcuding *keyname* is an error.
            It makes no sense to give a *default* and mark it *required*
            as well.
            The default is :py:obj:`False`.

            If *keyname* is part of a mutually exclusive group, it is best
            to set *required* for the group as a whole and not set it for 
            the individual members of the group because you may get unforseen
            errors.
        :type required: bool
        :argument default:
            The value stored for this key if it does not appear in
            the input block.  A value of :py:obj:`None` is equivalent
            to no default. It makes no sense to give a default and mark
            it *required* as well.  
            If the class :py:class:`SUPPRESS` is given instead of 
            :py:obj:`None`, then this key will be removed from the 
            namespace if it is not given.
            The default is :py:obj:`None`.

            If *keyname* is part of a mutually exclusive group and the
            group has been given a *dest* value, it is best
            to set *default* for the group as a whole and not set it for
            the individual members of the group because you may get 
            unforseen errors.
        :argument dest:
            If *dest* is given, *keyname* will be stored in the returned
            :py:class:`Namespace` as *dest*, not *keyname*.  
            A  value of :py:obj:`None` is equivalent to no dest.
            The default is :py:obj:`None`.

            If *keyname* is part of a mutually exclusive group and the
            group has been given a *dest* value, do not set *dest*
            for individual members of the group.
        :type dest: str
        :argument depends:
            Use *depends* to specify another key in the input file
            at the same input level (i.e. inside the same block or not
            in any block at all) that must also appear or a
            :py:exc:`ReaderError` will be raised.
            A  value of :py:obj:`None` is equivalent to no depends.
            The default is :py:obj:`None`.
        :type depends: str
        :argument repeat:
            Determines if *keyname* can appear only once in the input
            file or several times.  The default is :py:obj:`False`,
            which means this the *keyname* can only appear once or an
            error will be raised.  If *repeat* is :py:obj:`True`, the
            collected data will be returned in a list in the order in
            which it was read in.
            The default is :py:obj:`False`.
        :type repeat: bool
        '''
        # keyname must be str
        if not isinstance(keyname, str):
            raise ValueError (repr(keyname)+': keyname must be str')
        # end must be str
        if not isinstance(end, str):
            raise ValueError (keyname+': end must be str, given '+repr(end))
        # Cannot repeat keys
        if keyname in self._keys:
            raise ReaderError ('The key "'+keyname+'" has been defined twice')
        # Use default case if no case is given here
        if case is None:
            case = self._case
        # Use global default if none was given
        if 'default' not in kwargs:
            kwargs['default'] = self._default
        # Use parents's ignoreunknown if not given
        if ignoreunknown is None:
            ignoreunknown = self._ignoreunknown
        # ignoreunknown must be bool
        if not isinstance(ignoreunknown, bool):
            raise ValueError (keyname+': ignoreunknown must be bool, '
                                        'given '+repr(ignoreunknown))
        # Lower keyname if not case sensitive
        if not case:
            keyname = keyname.lower()
        # Store this key
        self._keys[keyname] = BlockKey(keyname, end, case, ignoreunknown,
                                       **kwargs)
        # Save the upper default
        self._keys[keyname]._upper_case = self._case
        return self._keys[keyname]

    def add_regex_line(self, handle, regex, case=None, **kwargs):
        '''Add a regular expression line to the input searcher.
        This searches the entire line based on the given regex.

        NOTE: You may either pass a string that will be converted to
        a regular expression object, or a compiled regular expression
        object.

        :argument handle:
            The name to store the resultant regex match object in
            the namespace.  This is required since there is technically
            no keyword.
        :type handle: str
        :argument regex:
            The regular expression that is used to search each line.
        :type regex: str, compiled re object
        :argument case:
            Determines if the if the search of this line is case-sensitive.
            This only applies if a string is given as *regex*; you determine
            if the regex is case-sensitive or not if you compile it yourself.
            By default, case is determined by the global value set when
            initiallizing the class.
        :type case: bool
        :argument required:
            Indicates that not inlcuding *regex* is an error.
            It makes no sense to give a *default* and mark it *required*
            as well.
            The default is :py:obj:`False`.

            If *regex* is part of a mutually exclusive group, it is best
            to set *required* for the group as a whole and not set it for 
            the individual members of the group because you may get unforseen
            errors.
        :type required: bool
        :argument default:
            The value stored for this key if it does not appear in
            the input block.  A value of :py:obj:`None` is equivalent
            to no default. It makes no sense to give a default and mark
            it *required* as well.  
            If the class :py:class:`SUPPRESS` is given instead of 
            :py:obj:`None`, then this key will be removed from the 
            namespace if it is not given.
            The default is :py:obj:`None`.

            If *regex* is part of a mutually exclusive group and the
            group has been given a *dest* value, it is best
            to set *default* for the group as a whole and not set it for
            the individual members of the group because you may get 
            unforseen errors.
        :argument dest:
            If *dest* is given, *regex* will be stored in the returned
            :py:class:`Namespace` as *dest*, not *handle*.  
            A  value of :py:obj:`None` is equivalent to no dest.
            The default is :py:obj:`None`.

            If *regex* is part of a mutually exclusive group and the
            group has been given a *dest* value, do not set *dest*
            for individual members of the group.
        :type dest: str
        :argument depends:
            Use *depends* to specify another key in the input file
            at the same input level (i.e. inside the same block or not
            in any block at all) that must also appear or a
            :py:exc:`ReaderError` will be raised.
            A  value of :py:obj:`None` is equivalent to no depends.
            The default is :py:obj:`None`.
        :type depends: str
        :argument repeat:
            Determines if *regex* can appear only once in the input
            file or several times.  The default is :py:obj:`False`,
            which means this the *regex* can only appear once or an
            error will be raised.  If *repeat* is :py:obj:`True`, the
            collected data will be returned in a list in the order in
            which it was read in.
            The default is :py:obj:`False`.
        :type repeat: bool
        '''
        # handle must be str
        if not isinstance(handle, str):
            raise ValueError (repr(handle)+': handle must be str')
        # Cannot repeat keys
        if handle in self._keys:
            raise ReaderError ('The key "'+handle+'" has been defined twice')
        # Use default case if no case is given here
        if case is None:
            case = self._case
        if not isinstance(case, bool):
            raise ValueError (handle+': case must be bool, given '+repr(case))
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
        return self._keys[handle]

    def add_mutually_exclusive_group(self, dest=None, default=None,
                                     required=False):
        '''Defines a mutually exclusive group.

        :argument dest:
            Defines an alternate name for the key to be stored in rather
            than the keyname.  Useful if you you wish to access the data
            from the mutually exclusive group without having to search
            the names of all the keys in the group.  It also removes the
            names of the keys in this group from the :py:class:`Namespace`.  
            NOTE: It is best not to set the *dest* value for members of 
            the group (just the group itself), as it may result in undetected
            errors.
        :type dest: str
        :argument default:
            The default to use for the mutually exclusive group.
            This is only valid if *dest* is defined.  This overwrites the
            defaults of the keys in this group.  
            NOTE: It is best not to set the default
            value for members of the group (just the group itself)
            as it as it may result in undetected errors.  
            If :py:class:`SUPPRESS` is given then this group
            will not apprear in the namespace if not found in input.
        :argument required: 
            At one of the members of this group is required to be in the
            input file
            NOTE: It is best not to set the required status for
            members of the group (just the group itself), as it may result
            in the program flagging errors for keys in this group when there
            in fact is no error.
        :type required: bool
        '''
        if default is None:
            default = self._default
        if dest is not None and not isinstance(dest, str):
            raise ValueError ('dest must be a str, given '+repr(dest))
        if not isinstance(required, bool):
            raise ValueError ('required value must be a bool, '
                              'given '+repr(required))

        # Add this group to the list, then return it
        self._meg.append(MutExGroup(self._case, dest, default, required,
                                    self._ignoreunknown))
        return self._meg[-1]

    def _add_kwargs(self, **kwargs):
        '''Generic keyword arguments common to many methods'''

        # If this class defines a default default attribute, use that instead
        self._default = getattr(self, 'default', None)
        if self._default is None:
            self._default = kwargs.pop('default', None)

        # Repeat
        self._repeat = kwargs.pop('repeat', False)
        if not isinstance(self._repeat, bool):
            raise ValueError ('repeat value must be a bool, '
                              'given '+repr(self._repeat))

        # Required
        self._required = kwargs.pop('required', False)
        if not isinstance(self._required, bool):
            raise ValueError ('required value must be a bool, '
                              'given '+repr(self._required))

        # If this class defines a default dest attribute, use that instead
        self._dest = getattr(self, 'dest', None)
        if self._dest is None:
            self._dest = kwargs.pop('dest', None)
        if self._dest is not None and not isinstance(self._dest, str):
            raise ValueError ('dest value '+repr(self._dest)+' must be a str')

        # Depends
        self._depends = kwargs.pop('depends', None)

        # Make sure nothing extra was given
        if kwargs:
            msg = ': Unknown arguments given: '+','.join(kwargs.keys())
            raise TypeError (self.name+msg)

    def _validate_string(self, string):
        '''Make sure a string has no spaces'''
        if hasattr(string, 'pattern'):
            for s in (r'\s', r'.'):
                if s in string.pattern:
                    msg = ': Regex should not allow the possibility of spaces'
                    msg += ', given "'+string.pattern+'"'
                    raise ValueError (self.name+msg)
        else:
            if len(string.split()) == 0:
                msg = ': String cannot be of zero length'
                raise ValueError (self.name+msg)
            elif len(string.split()) > 1:
                msg = ': String cannot contain spaces, given "'+string+'"'
                raise ValueError (self.name+msg)

    def _return_val(self, i, val, namespace):
        '''Returns the result properly, depending on the key type
        and how the user wants it.'''

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
                raise ReaderError (self.name+': The key "'+name+'" appears twice')
            # If the key has not been found, simply return
            else:
                return i, name, val

    def _defaults_and_unfind(self):
        '''
        Return the defaults for the keys as a dictionary.
        Also unfind all keys in case this is the second time
        we are reading a file with this class.
        '''
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
        namespace = Namespace(**self._defaults_and_unfind())

        # Populate the namespace with what was found in the input
        i, namespace = self._find_keys_in_input(f, i, namespace)

        # Post process to make sure that the keys fit the requirements
        self._post(namespace)

        return i, namespace

    def _find_keys_in_input(self, f, i, namespace):
        '''Find all the keys in the input block.'''

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
                elif not self._case and f[i].lower() == self._end.lower():
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
        Raises a ReaderError if the key in this line is unrecognized.
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

        # If this is a block key, check if this is the end of the block
        try:
            e = f[i] if self._upper_case else f[i].lower()
        except AttributeError:
            pass
        else:
            if e == self._end:
                return i+1

        # If nothing was found, raise an error
        raise ReaderError (self.name+': Unrecognized key: "'+f[i]+'"')

    def _post(self, namespace):
        '''Post-process the keys.'''

        # Process the mutually exclusive groups separately
        for meg in self._meg:
            nkeys = 0
            # Loop over each key in this group and count the
            # number in the namespace
            for key, val in meg._keys.items():
                name = val._dest if val._dest is not None else val.name
                if name in namespace:
                    nkeys += 1
                    thekey = [name, getattr(namespace, name)]
            # If none of the keys in the group were found
            if nkeys == 0:
                # Alert the user if a required key group was not found
                if meg._required:
                    keys = sorted(meg._keys.keys())
                    msg = ': One and only one of '
                    msg += ', '.join([repr(x) for x in keys[:-1]])
                    msg += ', or '+repr(keys[-1])+' must be included.'
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
                keys = sorted(meg._keys.keys())
                msg = ': Only one of '
                msg += ', '.join([repr(x) for x in keys[:-1]])
                msg += ', or '+repr(keys[-1])+' may be included.'
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
                    # Delete the keys in the group from the namespace defaults
                    for val in meg._keys.values():
                        name = val._dest if val._dest is not None else val.name
                        namespace.remove(name)
                        try:
                            del namespace._defaults[name]
                        except KeyError:
                            pass

        # Loop over the non-grouped keys and check key requirements
        for key, val in self._keys.items():
            name = val._dest if val._dest is not None else val.name
            # Identify missing required keys and raise error if not found
            if val._required and name not in namespace:
                msg = ': The key "'+key+'" is required but not found'
                raise ReaderError (self.name+msg)

        # Loop over the keys that were found and see if there are any
        # dependencies that were not filled.
        for key in namespace.keys():
            # Check if this key has any dependencies,
            # and if so, they are given as well.
            for val in self._keys.values():
                name = val._dest if val._dest is not None else val.name
                if key == name:
                    depends = getattr(val, '_depends', None)
                    break
            else:
                depends = None
            # Raise an error if the depending key is not found
            if depends and depends not in namespace:
            #if depends and depends not in namespace._order:
                msg = ': The key "'+key+'" requires that "'+depends
                msg += '" is also present, but it is not'
                raise ReaderError (self.name+msg)
            
        # Finalize the namespace
        namespace.finalize()

class LineKey(_KeyLevel):
    '''A class to store data on a line key'''

    def __init__(self, keyname, type, glob, keywords, case, **kwargs):
        '''Defines a line key.'''
        _KeyLevel.__init__(self, case=case)
        # Fill in the values
        self.name = keyname
        # Add the generic keyword arguments
        self._add_kwargs(**kwargs)
        # Check strings
        self._validate_string(self.name)
        if self._dest is not None:
            self._validate_string(self._dest)
        # Cannot have both glob and keywords defined
        if glob and keywords:
            msg = ': Cannot define both glob and keywords'
            raise TypeError (self.name+msg)
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

        # Make sure type is legal.  Use a recursive function.
        def check_type(typ):
            for t in typ:
                if isinstance(t, list):
                    msg = ': Embedded lists not allowed in type'
                    raise ValueError (self.name+msg)
                elif isinstance(t, tuple):
                    if len(t) == 0:
                        msg = ': Empty tuple in type'
                        raise ValueError (self.name+msg)
                    else:
                        check_type(t)
                elif not (isinstance(t, str) or isinstance(t, int) or
                          isinstance(t, float) or t is None or
                          hasattr(t, 'pattern') or t is str or t is int or
                          t is float):
                    msg = (': type must be one of None, str, float '
                           'int, or an instance of str, float, '
                           'int or regex')
                    raise ValueError (self.name+msg)
                if isinstance(t, str) or hasattr(t, 'pattern'):
                    self._validate_string(t)
        check_type(self._type)

        # Validate glob
        if glob:
            if not isinstance(glob, dict):
                raise ValueError (self.name+': glob must be a dict')
            if 'len' not in glob:
                raise ValueError (self.name+': "len" required for glob')
            elif glob['len'] not in ('*', '+', '?'):
                msg = ': "len" must be one of "*", "+", or "?" in glob'
                raise ValueError (self.name+msg)
            if 'type' not in glob:
                glob['type'] = str
            if isinstance(glob['type'], list):
                msg = ': list not allowed in type for glob or keywords'
                raise ValueError (self.name+msg)
            check_type([glob['type']])
            if 'join' not in glob:
                glob['join'] = False
            if glob['join'] and glob['len'] == '?':
                msg = ': "join=True" makes no sense for "len=?"'
                raise ValueError (self.name+msg)
            if set(glob.keys()) != set(['len', 'type', 'join']):
                if set(glob.keys()) != set(['len', 'type', 'join', 'default']):
                    raise TypeError (self.name+': Unknown key in glob')
            if not isinstance(glob['join'], bool):
                raise ValueError (self.name+': "join" must be a bool in glob')
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
                raise ValueError (self.name+': keywords must be a dict')
            for key in keywords:
                if not isinstance(key, str):
                    msg = ': keys in keywords must be of type str'
                    raise ValueError (self.name+msg)
                else:
                    self._validate_string(key)
                if keywords[key] is None:
                    keywords[key] = {}
                elif not isinstance(keywords[key], dict):
                    msg = ': Options for keyword "'+key+'" must be a dict'
                    raise ValueError (self.name+msg)
                if 'default' not in keywords[key]:
                    keywords[key]['default'] = SUPPRESS
                if 'type' not in keywords[key]:
                    keywords[key]['type'] = str
                if set(keywords[key].keys()) != set(['default', 'type']):
                    msg = ': Unknown key in keyword: "'+key+'"'
                    raise TypeError (self.name+msg)
                # Check the type of the keyword
                if isinstance(keywords[key]['type'], list):
                    msg = ': list not allowed in type for glob or keywords'
                    raise ValueError (self.name+msg)
                else:
                    check_type([keywords[key]['type']])
            self._keywords = keywords
                
            # Since we append this dict to the end, we must keep as a list
            # unless only the keywords are being kept
            self._nolist = True if not self._type else False
        else:
            self._keywords = {} # In case keywords = None

        # Type, glob and keywords can't be empty
        if not (self._type or self._glob or self._keywords):
            msg = ': type, glob and keywords cannot all be empty'
            raise ValueError (self.name+msg)

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
            if self._glob.get('len') == '+':
                msg = ': expected at least '+str(len(self._type)+1)
            else:
                msg = ': expected '+str(len(self._type))
            msg += ' arguments, got '+str(len(args))
            raise ReaderError (self.name+msg)

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
            if isinstance(val, int) or  isinstance(val, float):
                return str(val)
            elif isinstance(val, str):
                return '"'+str(val)+'"'
            elif val is None:
                return '"None"'
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
                    msg = self.name+': expected one of {0}, got "{1}"'
                    t = []
                    for x in sorted(typ):
                        t.append(make_readable(x))
                    t = ', '.join(t[:-1])+' or '+t[-1]
                    raise ReaderError (msg.format(t, val))
            else:
                try:
                    return validate(val, typ, case)
                except ValueError:
                    msg = self.name+': expected {0}, got "{1}"'
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
                if self._nolist:
                    if isinstance(glob, str):
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
                    raise ReaderError (self.name+msg)
                # Make sure the keyword is good
                if not self._case:
                    key = key.lower()
                if key not in self._keywords:
                    raise ReaderError (self.name+': Unknown keyword: "'+key+'"')
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

class BooleanKey(_KeyLevel):
    '''A class to store data on a boolean key'''

    def __init__(self, keyname, action, **kwargs):
        '''Defines a boolean key.'''
        _KeyLevel.__init__(self)
        # Fill in the non-generic values
        self.name     = keyname
        self._action  = action
        # Add the generic keyword arguments
        self._add_kwargs(**kwargs)
        # Check strings
        self._validate_string(self.name)
        if self._dest is not None:
            self._validate_string(self._dest)

    def _parse(self, f, i, namespace):
        '''Parses the current line for the key.  Returns the line that
        we read from and the value'''
        n = len(f[i].split())
        if n == 1:
            return self._return_val(i, self._action, namespace)
        else:
            raise ReaderError ('The boolean "'+self.name+'" was given '
                               'arguments, this is illegal')

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
        # Check strings
        self._validate_string(self.name)
        if self._dest is not None:
            self._validate_string(self._dest)

    def _parse(self, f, i, namespace):
        '''Parses the current line for the regex.  Returns the match objext
        for the line.'''

        # Grab the match object for this line
        val = self._regex.match(f[i])
        return self._return_val(i, val, namespace)

class BlockKey(_KeyLevel):
    '''A class to store data in a block key'''

    def __init__(self, keyname, end, case, ignoreunknown, **kwargs):
        _KeyLevel.__init__(self, case=case)
        '''Defines a block key.'''
        # Fill in the values
        self.name = keyname
        if self._case:
            self._end = end.lower()
        else:
            self._end = end
        self._ignoreunknown = ignoreunknown
        # Add the generic keyword arguments
        self._add_kwargs(**kwargs)
        # Check strings
        self._validate_string(self.name)
        if self._dest is not None:
            self._validate_string(self._dest)
        self._validate_string(self._end)

    def _parse(self, f, i, namespace):
        '''Parses the current line for the key.  Returns the line that
        we read from and the value'''

        # Parse this block
        n = len(f[i].split())
        if n == 1:
            i, val = self._parse_key_level(f, i+1)
            return self._return_val(i, val, namespace)
        else:
            raise ReaderError ('The block "'+self.name+'" was given '
                               'arguments, this is illegal')

class MutExGroup(_KeyLevel):
    '''A class to hold a mutually exclusive group'''

    def __init__(self, case, dest, default, required, _ignoreunknown):
        '''Initiallizes the mutually exclusive group.'''
        _KeyLevel.__init__(self, case=case)
        self._default  = default
        self._dest = dest
        # Check strings
        if self._dest is not None:
            self._validate_string(self._dest)
        self._required = required
        self._ignoreunknown = _ignoreunknown
