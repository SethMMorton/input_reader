# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from .keylevel import _KeyLevel, LineKey, Regex, BooleanKey
from .helpers import ReaderError, SUPPRESS, Namespace
from .py23compat import py23_str, py23_items, py23_values
import re

class _KeyAdder(_KeyLevel):
    """An abstract base class that knows how to add keys to itself
    and check the keys read within it."""

    def __init__(self, case=False):
        """Initiallizes the key holders in this class"""
        super(_KeyAdder, self).__init__(case=case)

        # Default the key dictionary
        self._keys  = {}

        # The mutually exclusive groups
        self._meg = []

    def _ensure_default_has_a_value(self, kwargs):
        if 'default' not in kwargs:
            kwargs['default'] = self._default

    def _check_keyname(self, keyname, strid):
        """Run the given keyname through a few checks"""
        # Check that the keyname is valid
        if not isinstance(keyname, py23_str):
            raise ValueError('{0}: {1} must be str'.format(repr(keyname), strid))
        # Check that the keyname is not defined twice
        if keyname in self._keys:
            raise ReaderError('The {0} "{1}" has been defined twice'.format(strid, keyname))
        # Adjust keyname if this is case sensitive
        if not self._case:
            keyname = keyname.lower()
        return keyname

    def _check_case(self, case, keyname):
        # Use default case if no case is given here
        if case is None:
            case = self._case
        if not isinstance(case, bool):
            raise ValueError(keyname + ': case must be bool, given ' + repr(case))
        return case

    def add_boolean_key(self, keyname, action=True, **kwargs):
        """Add a boolean key to the input searcher.

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
        """
        keyname = self._check_keyname(keyname, 'keyname')
        self._ensure_default_has_a_value(kwargs)
        # Store this key
        self._keys[keyname] = BooleanKey(keyname, action, **kwargs)
        return self._keys[keyname]

    def add_line_key(self, keyname, type=str, glob={}, keywords={},
                     case=None, **kwargs):
        """Add a line key to the input searcher.

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
        """
        keyname = self._check_keyname(keyname, 'keyname')
        self._ensure_default_has_a_value(kwargs)
        case = self._check_case(case, keyname)
        # Store this key
        self._keys[keyname] = LineKey(keyname, type, glob, keywords, case, **kwargs)
        return self._keys[keyname]

    def add_block_key(self, keyname, end='end', case=None,
                      ignoreunknown=None, **kwargs):
        """Add a block key to the input searcher.

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
        """
        keyname = self._check_keyname(keyname, 'keyname')
        self._ensure_default_has_a_value(kwargs)
        case = self._check_case(case, keyname)

        # end must be str
        if not isinstance(end, py23_str):
            raise ValueError (keyname+': end must be str, given '+repr(end))

        # Use parents's ignoreunknown if not given
        if ignoreunknown is None:
            ignoreunknown = self._ignoreunknown

        # ignoreunknown must be bool
        if not isinstance(ignoreunknown, bool):
            raise ValueError (keyname+': ignoreunknown must be bool, '
                                        'given '+repr(ignoreunknown))
        # Store this key
        self._keys[keyname] = BlockKey(keyname, end, case, ignoreunknown, **kwargs)
        # Save the upper default
        self._keys[keyname]._upper_case = self._case
        return self._keys[keyname]

    def add_regex_line(self, handle, regex, case=None, **kwargs):
        """Add a regular expression line to the input searcher.
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
        """
        handle = self._check_keyname(handle, 'handle')
        self._ensure_default_has_a_value(kwargs)
        case = self._check_case(case, handle)

        # Compile the regex if a string.
        if isinstance(regex , py23_str):
            if case:
                regex = re.compile(regex)
            else:
                regex = re.compile(regex, re.IGNORECASE)

        # Store this key
        self._keys[handle] = Regex(handle, regex, **kwargs)
        return self._keys[handle]

    def add_mutually_exclusive_group(self, dest=None, default=None, required=False):
        """Defines a mutually exclusive group.

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
        """
        if default is None:
            default = self._default
        if dest is not None and not isinstance(dest, py23_str):
            raise ValueError ('dest must be a str, given '+repr(dest))
        if not isinstance(required, bool):
            raise ValueError ('required value must be a bool, '
                              'given '+repr(required))

        # Add this group to the list, then return it
        self._meg.append(MutExGroup(self._case, dest, default, required,
                                    self._ignoreunknown))
        return self._meg[-1]



    def _defaults_and_unfind(self):
        """
        Return the defaults for the keys as a dictionary.
        Also unfind all keys in case this is the second time
        we are reading a file with this class.
        """
        defaults = {}
        for key, val in py23_items(self._keys)():
            if val._default is not SUPPRESS:
                name = val._dest if val._dest is not None else val.name
                defaults[name] = val._default
        for meg in self._meg:
            for key, val in py23_items(meg._keys)():
                if val._default is not SUPPRESS:
                    name = val._dest if val._dest is not None else val.name
                    defaults[name] = val._default
        return defaults

    def _parse_key_level(self, f, i):
        """Parse the current key level, recursively
         parsing sublevels if necessary
        """

        # Populate the namespace with the defaults
        namespace = Namespace(**self._defaults_and_unfind())

        # Populate the namespace with what was found in the input
        i, namespace = self._find_keys_in_input(f, i, namespace)

        # Post process to make sure that the keys fit the requirements
        self._post(namespace)

        return i, namespace

    def _find_keys_in_input(self, f, i, namespace):
        """Find all the keys in the input block."""

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
        """Attempt to find a key in this line.
        Returns the new current line number.
        Raises a ReaderError if the key in this line is unrecognized.
        """

        first = f[i].split()[0]
        if not self._case:
            first = first.lower()
        # Find in the usual places
        for key, val in py23_items(self._keys)():
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
            for key, val in py23_items(meg._keys)():
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
        """Post-process the keys."""

        # Process the mutually exclusive groups separately
        for meg in self._meg:
            nkeys = 0
            # Loop over each key in this group and count the
            # number in the namespace
            for key, val in py23_items(meg._keys)():
                name = val._dest if val._dest is not None else val.name
                if name in namespace:
                    nkeys += 1
                    thekey = [name, getattr(namespace, name)]
            # If none of the keys in the group were found
            if nkeys == 0:
                # Alert the user if a required key group was not found
                if meg._required:
                    keys = sorted(meg._keys)
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
                keys = sorted(meg._keys)
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
                    for val in py23_values(meg._keys)():
                        name = val._dest if val._dest is not None else val.name
                        namespace.remove(name)
                        try:
                            del namespace._defaults[name]
                        except KeyError:
                            pass

        # Loop over the non-grouped keys and check key requirements
        for key, val in py23_items(self._keys)():
            name = val._dest if val._dest is not None else val.name
            # Identify missing required keys and raise error if not found
            if val._required and name not in namespace:
                msg = ': The key "'+key+'" is required but not found'
                raise ReaderError (self.name+msg)

        # Loop over the keys that were found and see if there are any
        # dependencies that were not filled.
        for key in namespace:
            # Check if this key has any dependencies,
            # and if so, they are given as well.
            for val in py23_values(self._keys)():
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


class MutExGroup(_KeyAdder):
    """A class to hold a mutually exclusive group"""

    def __init__(self, case, dest, default, required, _ignoreunknown):
        """Initiallizes the mutually exclusive group."""
        super(MutExGroup, self).__init__(case=case)
        self._default  = default
        self._dest = dest
        # Check strings
        self._validate_string(self._dest)
        self._required = required
        self._ignoreunknown = _ignoreunknown


class BlockKey(_KeyAdder):
    """A class to store data in a block key"""

    def __init__(self, keyname, end, case, ignoreunknown, **kwargs):
        """Defines a block key."""
        super(BlockKey, self).__init__(case=case)
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
        self._validate_string(self._dest)
        self._validate_string(self._end)

    def _parse(self, f, i, namespace):
        """Parses the current line for the key.  Returns the line that
        we read from and the value"""

        # Parse this block
        n = len(f[i].split())
        if n == 1:
            i, val = self._parse_key_level(f, i+1)
            return self._return_val(i, val, namespace)
        else:
            raise ReaderError ('The block "'+self.name+'" was given '
                               'arguments, this is illegal')