from __future__ import division, print_function
import re
from helpers import Namespace, SUPPRESS, ReaderError

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

        :argument keyname:
            The name of the boolean-type key to search for.
        :type keyname: str
        :argument action:
            What value to store if this key is found.  The default is
            :py:const:`True`.
        :argument required:
            Indicates that not inlcuding `keyname` is an error.
            It makes no sense to give a `default` and mark it `required`
            as well.

            If `keyname` is part of a mutually exclusive group, it is best
            to set `required` for the group as a whole and not set it for 
            the individual members of the group because you may get unforseen
            errors.
        :type required: bool
        :argument default:
            The value stored for this key if it does not appear in
            the input block.  A value of :py:const:`None` is equivalent
            to no default. It makes no sense to give a default and mark
            it `required` as well.  
            If the class :py:class:`SUPPRESS` is given instead of 
            :py:const:`None`, then this key will be removed from the 
            namespace if it is not given.

            If `keyname` is part of a mutually exclusive group and the
            group has been given a `dest` value, it is best
            to set `default` for the group as a whole and not set it for
            the individual members of the group because you may get 
            unforseen errors.
        :argument dest:
            If `dest` is given, `keyname` will be stored in the returned
            :py:class:`Namespace` as `dest`, not `keyname`.  

            If `keyname` is part of a mutually exclusive group and the
            group has been given a `dest` value, do not set `dest`
            for individual members of the group.
        :type dest: str
        :argument depends:
            Use `depends` to specify another key in the input file
            at the same input level (i.e. inside the same block or not
            in any block at all) that must also appear or a
            :py:exc:`ReaderError` will be raised.
        :type depends: str
        :argument repeat:
            Determines if `keyname` can appear only once in the input
            file or several times.  The default is :py:const:`False`,
            which means this the `keyname` can only appear once or an
            error will be raised.  If `repeat` is :py:const:`True`, the
            collected data will be returned in a list in the order in
            which it was read in.
        :type repeat: bool
        :argument overwritedefault:
            `overwritedefault` can only be used if `repeat` is also given.
            If :py:const:`False`, on the first appearance of `keyname`
            the new value will be appended to what was given as default
            (if default is not :py:const:`None`).  If :py:const:`True`,
            then the default value will be discarded before those found in
            the input file are added.
        :type overwritedefault: bool
        '''
        from otherkeys import BooleanKey

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

        :argument keyname:
            The name of the key to search for.
        :type keyname: str
        :argument type:
            The data type that to be read in for each positional
            argument, given as a list. The length of the list dictates how
            many arguments to look for. If this is an empty list or 
            :py:const:`None` no positional arguments will be read in.

            `type` may be one or more of:

                - :py:class:`int`
                - :py:class:`float`
                - :py:class:`str`
                - :py:const:`None`
                - an explicit int (i.e. 4), float (i.e. 5.4) or str (i.e
                  "hello")
                - a compiled regular expression object

            If you give an explicit int, float or str, it is assumed that the 
            value must equal what you gave.  None means that the word "none" is
            what is expected.

            If you only wish to read in one argument, you may give the type(s)
            for that one argument directly (meaning not in a list).  This will
            cause the returned value to be the value itself, not a 1-length
            list.

            For each value, you may give a tuple of types to indicate more than
            one type is valid for that argument position.
            NOTE: Is is very important that type choices for each argument are
            given as tuples, and that the list passed to type is an actual list
            (as opposed to tuple) because these are treated differently.
        :argument glob:
            `glob` is a dictionary giving information on how to read in a
            glob of arguments.  Globs are read in after the positional 
            arguments.  If there are no positional arguments, the whole 
            line is globbed.  `glob` is not valid with `keywords`.
            The glob dictionary accepts only four keys:

            `len`
                Must be one of '*', '+', or '?'.  '*' is a zero or more
                glob, '+' is an at least one or more glob, and '?' is a 
                zero or one glob.
            `type`
                Indicates the data type the glob must be.  This may be
                any one of the types presented for positional arguments. 
                If this is omitted, then :py:class:`str` is assumed.
            `join`
                `join` will join the globbed values as a space-separated
                string and thus return a single string instead of a list.
                This is useful for reading in sentences or titles.  
                The default is :py:const:`False` if `len` is '*' or '+'
                and :py:const:`True` if `len` is '?'.
            `default`
                In the case that no glob is given this is what will
                be put into the `glob`. If there is no default,
                nothing is put into the `glob`.

        :type glob: dict
        :argument keywords:
            `keywords` is a nested dictionary indicating key-value
            pairs that can be read in. Each key in the dictionary is a
            keyword to look for, and the value for that key is another
            dictionary with the keys 'type' and 'default'.  If an empty
            dictionary or :py:const:`None` is given, the defaults of 
            :py:class:`str` and :py:class:`SUPPRESS` will be chosen,
            respectively.  Like positional arguments, you may give as 
            many types as you wish per keyword.
        :type keywords: nested dict
        :argument case:
            States if this particular key is case-sensitive. Note that
            this applies only to the arguments of `keyname`; `keyname`
            itself uses the case-sensitivity default of the current
            level.
        :type case: bool
        :argument required:
            Indicates that not inlcuding `keyname` is an error.
            It makes no sense to give a `default` and mark it `required`
            as well.

            If `keyname` is part of a mutually exclusive group, it is best
            to set `required` for the group as a whole and not set it for 
            the individual members of the group because you may get unforseen
            errors.
        :type required: bool
        :argument default:
            The value stored for this key if it does not appear in
            the input block.  A value of :py:const:`None` is equivalent
            to no default. It makes no sense to give a default and mark
            it `required` as well.  
            If the class :py:class:`SUPPRESS` is given instead of 
            :py:const:`None`, then this key will be removed from the 
            namespace if it is not given.

            If `keyname` is part of a mutually exclusive group and the
            group has been given a `dest` value, it is best
            to set `default` for the group as a whole and not set it for
            the individual members of the group because you may get 
            unforseen errors.
        :argument dest:
            If `dest` is given, `keyname` will be stored in the returned
            :py:class:`Namespace` as `dest`, not `keyname`.  

            If `keyname` is part of a mutually exclusive group and the
            group has been given a `dest` value, do not set `dest`
            for individual members of the group.
        :type dest: str
        :argument depends:
            Use `depends` to specify another key in the input file
            at the same input level (i.e. inside the same block or not
            in any block at all) that must also appear or a
            :py:exc:`ReaderError` will be raised.
        :type depends: str
        :argument repeat:
            Determines if `keyname` can appear only once in the input
            file or several times.  The default is :py:const:`False`,
            which means this the `keyname` can only appear once or an
            error will be raised.  If `repeat` is :py:const:`True`, the
            collected data will be returned in a list in the order in
            which it was read in.
        :type repeat: bool
        :argument overwritedefault:
            `overwritedefault` can only be used if `repeat` is also given.
            If :py:const:`False`, on the first appearance of `keyname`
            the new value will be appended to what was given as default
            (if default is not :py:const:`None`).  If :py:const:`True`,
            then the default value will be discarded before those found in
            the input file are added.
        :type overwritedefault: bool
        '''
        from linekey import LineKey
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

        :argument keyname:
            The name of the key to search for.
        :type keyname: str
        :argument end:
            The string used to signify the end of this block.
        :type end: str
        :argument case:
            States if this particular key is case-sensitive. Note that
            this applies only to the subkeys of `keyname`; `keyname`
            itself uses the case-sensitivity default of the current
            level.
        :type case: bool
        :argument ignoreunknown:
            Suppresses raising the :py:exc:`ReaderError` when an unknown
            key is found.
        :type ignoreunknown: bool
        :argument required:
            Indicates that not inlcuding `keyname` is an error.
            It makes no sense to give a `default` and mark it `required`
            as well.

            If `keyname` is part of a mutually exclusive group, it is best
            to set `required` for the group as a whole and not set it for 
            the individual members of the group because you may get unforseen
            errors.
        :type required: bool
        :argument default:
            The value stored for this key if it does not appear in
            the input block.  A value of :py:const:`None` is equivalent
            to no default. It makes no sense to give a default and mark
            it `required` as well.  
            If the class :py:class:`SUPPRESS` is given instead of 
            :py:const:`None`, then this key will be removed from the 
            namespace if it is not given.

            If `keyname` is part of a mutually exclusive group and the
            group has been given a `dest` value, it is best
            to set `default` for the group as a whole and not set it for
            the individual members of the group because you may get 
            unforseen errors.
        :argument dest:
            If `dest` is given, `keyname` will be stored in the returned
            :py:class:`Namespace` as `dest`, not `keyname`.  

            If `keyname` is part of a mutually exclusive group and the
            group has been given a `dest` value, do not set `dest`
            for individual members of the group.
        :type dest: str
        :argument depends:
            Use `depends` to specify another key in the input file
            at the same input level (i.e. inside the same block or not
            in any block at all) that must also appear or a
            :py:exc:`ReaderError` will be raised.
        :type depends: str
        :argument repeat:
            Determines if `keyname` can appear only once in the input
            file or several times.  The default is :py:const:`False`,
            which means this the `keyname` can only appear once or an
            error will be raised.  If `repeat` is :py:const:`True`, the
            collected data will be returned in a list in the order in
            which it was read in.
        :type repeat: bool
        :argument overwritedefault:
            `overwritedefault` can only be used if `repeat` is also given.
            If :py:const:`False`, on the first appearance of `keyname`
            the new value will be appended to what was given as default
            (if default is not :py:const:`None`).  If :py:const:`True`,
            then the default value will be discarded before those found in
            the input file are added.
        :type overwritedefault: bool
        '''
        from otherkeys import BlockKey

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
            This only applies if a string is given as `regex`.
        :type case: bool
        :argument required:
            Indicates that not inlcuding `keyname` is an error.
            It makes no sense to give a `default` and mark it `required`
            as well.

            If `keyname` is part of a mutually exclusive group, it is best
            to set `required` for the group as a whole and not set it for 
            the individual members of the group because you may get unforseen
            errors.
        :type required: bool
        :argument default:
            The value stored for this key if it does not appear in
            the input block.  A value of :py:const:`None` is equivalent
            to no default. It makes no sense to give a default and mark
            it `required` as well.  
            If the class :py:class:`SUPPRESS` is given instead of 
            :py:const:`None`, then this key will be removed from the 
            namespace if it is not given.

            If `keyname` is part of a mutually exclusive group and the
            group has been given a `dest` value, it is best
            to set `default` for the group as a whole and not set it for
            the individual members of the group because you may get 
            unforseen errors.
        :argument dest:
            If `dest` is given, `keyname` will be stored in the returned
            :py:class:`Namespace` as `dest`, not `keyname`.  

            If `keyname` is part of a mutually exclusive group and the
            group has been given a `dest` value, do not set `dest`
            for individual members of the group.
        :type dest: str
        :argument depends:
            Use `depends` to specify another key in the input file
            at the same input level (i.e. inside the same block or not
            in any block at all) that must also appear or a
            :py:exc:`ReaderError` will be raised.
        :type depends: str
        :argument repeat:
            Determines if `keyname` can appear only once in the input
            file or several times.  The default is :py:const:`False`,
            which means this the `keyname` can only appear once or an
            error will be raised.  If `repeat` is :py:const:`True`, the
            collected data will be returned in a list in the order in
            which it was read in.
        :type repeat: bool
        :argument overwritedefault:
            `overwritedefault` can only be used if `repeat` is also given.
            If :py:const:`False`, on the first appearance of `keyname`
            the new value will be appended to what was given as default
            (if default is not :py:const:`None`).  If :py:const:`True`,
            then the default value will be discarded before those found in
            the input file are added.
        :type overwritedefault: bool
        '''
        from otherkeys import Regex

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

        :argument dest:
            Defines an alternate name for the key to be stored in rather
            than the keyname.  Useful if you you wish to access the data
            from the mutually exclusive group without having to search
            the names of all the keys in the group.  It also removes the
            names of the keys in this group from the namespace.  
            NOTE: It is best not to set the `dest` value for members of 
            the group (just the group itself), as it may result in undetected
            errors.
        :type dest: str
        :argument default:
            The default to use for the mutually exclusive group.
            This is only valid if `dest` is defined.  This overwrites the
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
        from otherkeys import MutExGroup
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
        '''Generic keyword arguments common to many methods'''

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
        '''Returns the result properly, depending on the key type
        and how the user wants it.'''

        # Substitute the keyname for dest if required
        name = self._dest if self._dest is not None else self.name

        # If multiple occurences of the keyname may appear, store
        # each of these in the namespace
        if self._repeat:
            # If the name exists, check if we need to append the value
            # to an already generated list, or replace the default value.
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
            # If the keyname does not exist, simply return (as a tuple)
            else:
                return i, name, (val,)
        # In this case, only one instance of the keyname may appear
        # or it is an error.
        else:
            # If the keyname has already been found it is an error,
            # however it is first checked it appears only because
            # it is the default.
            if name in namespace:
                if getattr(namespace, name) != self._default:
                    raise ReaderError (self.name+': This key appears twice')
                else:
                    return i, name, val
            # If the keyname does not exist, simply return
            else:
                return i, name, val

    def _defaults(self):
        '''Return the defaults for the keys as a dictionary.'''
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
