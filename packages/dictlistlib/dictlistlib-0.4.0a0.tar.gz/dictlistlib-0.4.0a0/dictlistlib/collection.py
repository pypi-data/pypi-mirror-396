"""Module containing the logic for the collection of data structure."""

import yaml
import json
import re
from functools import partial
from dictlistlib.argumenthelper import validate_argument_type
from dictlistlib import utils
from dictlistlib.parser import SelectParser
from dictlistlib.validation import OpValidation
from dictlistlib.validation import CustomValidation

from dictlistlib.exceptions import ListIndexError
from dictlistlib.exceptions import ResultError
from dictlistlib.exceptions import LookupClsError
from dictlistlib.exceptions import ObjectArgumentError


class List(list):
    """This is a class for List Collection.

    Properties
    ----------
    is_empty (boolean): a check point to tell an empty list or not.
    first (Any): return a first element of a list
    last (Any): return a last element of a list
    total (int): total element in list

    Raise
    -----
    ListIndexError: if a list is out of range.
    """
    def __getattribute__(self, attr):
        match = re.match(r'index(?P<index>_?[0-9]+)$', attr)    # noqa
        if match:
            index = match.group('index').replace('_', '-')
            try:
                value = self[int(index)]
                return value
            except Exception as ex:
                raise ListIndexError(str(ex))
        else:
            value = super().__getattribute__(attr)
            return value

    @property
    def is_empty(self):
        """Check an empty list."""
        return self.total == 0

    @property
    def first(self):
        """Get a first element of list if list is not empty"""
        if not self.is_empty:
            return self[0]

        raise ListIndexError('Can not get a first element of an empty list.')

    @property
    def last(self):
        """Get a last element of list if list is not empty"""
        if not self.is_empty:
            return self[-1]
        raise ListIndexError('Can not get last element of an empty list.')

    @property
    def total(self):
        """Get a size of list"""
        return len(self)


class Result:
    """The Result Class to store data.

    Attributes
    ----------
    data (Any): the data.
    parent (Result): keyword arguments.

    Properties
    ----------
    has_parent -> boolean

    Methods
    -------
    update_parent(parent: Result) -> None

    Raise
    -----
    ResultError: if parent is not instance of None or Result.
    """
    def __init__(self, data, parent=None):
        self.parent = None
        self.data = data
        self.update_parent(parent)

    def update_parent(self, parent):
        """Update parent to Result

        Parameters
        ----------
        parent (Result): a Result instance.
        """
        if parent is None or isinstance(parent, self.__class__):
            self.parent = parent
        else:
            msg = 'parent argument must be Result instance or None.'
            raise ResultError(msg)

    @property
    def has_parent(self):
        """Return True if Result has parent."""
        return isinstance(self.parent, Result)


class Element(Result):
    """Element class.

    Attributes
    ----------
    data (any): a data.
    index (str): a index value of data if data is list or dictionary.
    parent (Element): an Element instance.
    on_exception (bool): raise `Exception` if set True, otherwise, return False.
    type (str): datatype name of data.

    """
    def __init__(self, data, index='', parent=None, on_exception=False):
        super().__init__(data, parent=parent)
        self.index = index
        self.type = ''
        self.on_exception = on_exception
        self._build(data)

    def __iter__(self):
        if self.type == 'dict':
            return iter(self.data.keys())
        elif self.type == 'list':
            return iter(range(len(self.data)))
        else:
            fmt = '{!r} object is not iterable.'
            msg = fmt.format(type(self).__name__)
            raise TypeError(msg)

    def __getitem__(self, index):
        if self.type not in ['dict', 'list']:
            fmt = '{!r} object is not subscriptable.'
            msg = fmt.format(type(self).__name__)
            raise TypeError(msg)
        result = self.data[index]
        return result

    def _build(self, data):
        self.children = None
        self.value = None
        if isinstance(data, dict):
            self.type = 'dict'
            lst = List()
            for index, val in data.items():
                elm = Element(val, index=index, parent=self)
                lst.append(elm)
            self.children = lst or None
        elif isinstance(data, (list, tuple, set)):
            self.type = 'list'
            lst = List()
            for i, item in enumerate(data):
                index = '__index__{}'.format(i)
                elm = Element(item, index=index, parent=self)
                lst.append(elm)
            self.children = lst or None
        elif isinstance(data, (int, float, bool, str)) or data is None:
            self.type = type(data).__name__
            self.value = data
        else:
            self.type = 'object'
            self.value = data

    @property
    def has_children(self):
        """Return True if an element has children."""
        return bool(self.children)

    @property
    def is_element(self):
        """Return True if an element has children."""
        return self.has_children

    @property
    def is_leaf(self):
        """Return True if an element doesn't have children."""
        return not self.has_children

    @property
    def is_scalar(self):
        """Return True if an element is a scalar type."""
        return isinstance(self.data, (int, float, bool, str, None))     # noqa

    @property
    def is_list(self):
        """Return True if an element is a list type."""
        return self.type == 'list'

    @property
    def is_dict(self):
        """Return True if an element is a list type."""
        return self.type == 'dict'

    def filter_result(self, records, select_statement):
        """Filter a list of records based on select statement

        Parameters
        ----------
        records (List): a list of record.
        select_statement (str): a select statement.

        Returns
        -------
        List: list of filtered records.
        """
        result = List()
        select_obj = SelectParser(select_statement,
                                  on_exception=self.on_exception)
        select_obj.parse_statement()

        if callable(select_obj.predicate):
            lst = List()
            for record in records:
                is_found = select_obj.predicate(record.parent.data,
                                                on_exception=self.on_exception)
                if is_found:
                    lst.append(record)
        else:
            lst = records[:]

        if select_obj.is_zero_select:
            for item in lst:
                result.append(item.data)
        elif select_obj.is_all_select:
            for item in lst:
                result.append(item.parent.data)
        else:
            for item in lst:
                new_data = item.parent.data.fromkeys(select_obj.columns)
                is_added = True
                for key in new_data:
                    is_added &= key in item.parent.data
                    new_data[key] = item.parent.data.get(key, None)
                is_added and result.append(new_data)
        return result

    def find_(self, node, lookup_obj, result):
        """Recursively search a lookup and store a found record to result

        Parameters
        ----------
        node (Element): a `Element` instance.
        lookup_obj (LookupCls): a LookupCls instance.
        result (List): a found result.
        """
        if node.is_dict or node.is_list:
            for child in node.children:
                if node.is_list:
                    if child.is_element:
                        self.find_(child, lookup_obj, result)
                else:
                    if lookup_obj.is_left_matched(child.index):
                        if lookup_obj.is_right:
                            if lookup_obj.is_right_matched(child.data):
                                result.append(child)
                        else:
                            result.append(child)
                    if child.is_element:
                        self.find_(child, lookup_obj, result)

    def find(self, lookup, select=''):
        """recursively search a lookup.

        Parameters
        ---------
        lookup (str): a search pattern.
        select (str): a select statement.

        Returns
        -------
        List: list of record
        """
        records = List()
        lkup_obj = LookupCls(lookup)
        self.find_(self, lkup_obj, records)
        result = self.filter_result(records, select)
        return result


class ObjectDict(dict):
    """The ObjectDict can retrieve value of key as attribute style."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.update(*args, **kwargs)

    ############################################################################
    # Special methods
    ############################################################################
    def __getattribute__(self, attr):
        try:
            value = super().__getattribute__(attr)
            return value
        except Exception as ex:
            if attr in self:
                return self[attr]
            else:
                raise ex

    def __setitem__(self, key, value):
        new_value = self._build(value)
        super().__setitem__(key, new_value)

    def __setattr__(self, attr, value):
        new_value = self._build(value)
        if attr in self:
            self[attr] = new_value
        else:
            super().__setattr__(attr, new_value)

    ############################################################################
    # Private methods
    ############################################################################
    def _build(self, value, forward=True):
        """The function to recursively build a ObjectDict instance
        when the value is the dict instance.

        Parameters
        ----------
        value (Any): The value to recursively build a ObjectDict
                instance when value is the dict instance.
        forward (boolean): set flag to convert dict instance to ObjectDict
                instance or vice versa.  Default is True.
        Returns
        -------
        Any: the value or a new value.
        """
        if isinstance(value, (dict, list, set, tuple)):
            if isinstance(value, ObjectDict):
                if forward:
                    return value
                else:
                    result = dict([i, self._build(j, forward=forward)] for i, j in value.items())  # noqa
                    return result
            elif isinstance(value, dict):
                lst = [[i, self._build(j, forward=forward)] for i, j in value.items()]
                if forward:
                    result = self.__class__(lst)
                    return result
                else:
                    result = dict(lst)      # noqa
                    return result
            elif isinstance(value, list):
                lst = [self._build(item, forward=forward) for item in value]
                return lst
            elif isinstance(value, set):
                lst = [self._build(item, forward=forward) for item in value]
                return set(lst)
            else:
                tuple_obj = (self._build(item, forward=forward) for item in value)
                return tuple_obj
        else:
            return value

    ############################################################################
    # class methods
    ############################################################################
    @classmethod
    def create_from_json_file(cls, filename, **kwargs):
        """Create a ObjectDict instance from JSON file.

        Parameters
        ----------
        filename (str): YAML file.
        kwargs (dict): the keyword arguments.

        Returns
        -------
        Any: any data
        """
        from io import IOBase
        if isinstance(filename, IOBase):
            obj = json.load(filename, **kwargs)
        else:
            with open(filename) as stream:
                obj = json.load(stream, **kwargs)

        obj_dict = ObjectDict(obj)
        return obj_dict

    @classmethod
    def create_from_json_data(cls, data, **kwargs):
        obj = json.loads(data, **kwargs)
        obj_dict = ObjectDict(obj)
        return obj_dict

    @classmethod
    def create_from_yaml_file(cls, filename, loader=yaml.SafeLoader):
        """Create a ObjectDict instance from YAML file.

        Parameters
        ----------
        filename (str): YAML file.
        loader (yaml.loader.Loader): YAML loader.

        Returns
        -------
        Any: any data
        """
        from io import IOBase
        if isinstance(filename, IOBase):
            obj = yaml.load(filename, Loader=loader)    # noqa
        else:
            with open(filename) as stream:
                obj = yaml.load(stream, Loader=loader)

        obj_dict = ObjectDict(obj)
        return obj_dict

    @classmethod
    def create_from_yaml_data(cls, data, loader=yaml.SafeLoader):
        """Create a ObjectDict instance from YAML data.

        Parameters
        ----------
        data (str): YAML data.
        loader (yaml.loader.Loader): YAML loader.

        Returns
        -------
        Any: Any data
        """
        obj = yaml.load(data, Loader=loader)
        obj_dict = ObjectDict(obj)
        return obj_dict

    ############################################################################
    # public methods
    ############################################################################
    def update(self, *args, **kwargs):
        """Update data to ObjectDict."""
        obj = dict(*args, **kwargs)
        new_obj = dict()
        for key, value in obj.items():
            new_obj[key] = self._build(value)
        super().update(new_obj)

    def deep_apply_attributes(self, node=None, **kwargs):
        """Recursively apply attributes to ObjectDict instance.

        Parameters
        ---------
        node (ObjectDict): a `ObjectDict` instance
        kwargs (dict): keyword arguments
        """

        def assign(node_, **kwargs_):
            for key, val in kwargs_.items():
                setattr(node_, key, val)

        def apply(node_, **kwargs_):
            if isinstance(node_, (dict, list, set, tuple)):
                if isinstance(node_, dict):
                    if isinstance(node_, self.__class__):
                        assign(node_, **kwargs_)
                    for value in node_.values():
                        apply(value, **kwargs_)
                else:
                    for item in node_:
                        apply(item, **kwargs_)

        node = self if node is None else node
        validate_argument_type(self.__class__, node=node)
        apply(node, **kwargs)

    def to_dict(self, data=None):
        """Convert a given data to native dictionary

        Parameters
        ----------
        data (ObjectDict): a dynamic dictionary instance.
            if data is None, it will convert current instance to dict.

        Returns
        -------
        dict: dictionary
        """
        if data is None:
            data = dict(self)

        validate_argument_type(dict, data=data)
        result = self._build(data, forward=False)
        return result

    todict = to_dict


class LookupCls:
    """To build a lookup object.

    Attributes
    ----------
    lookup (str): a search criteria.
    left (str): a left lookup which uses to match a key of dictionary.
            It is a regular expression.
    right (str, callable): a right lookup that uses to match a value of
            dictionary.  It that can be regular expression pattern
            or a callable function, i.e. Predicate function.

    Notes
    -----
    A lookup consists two parts:
        + a left lookup which uses to match a key of dictionary.
        + a right lookup which uses to match value of dictionary.
        The proper syntax of lookup can be:

        case 1: lookup='abc'
            a left lookup search any key which key name is abc.
            while a right lookup is empty.  No action.

        case 2: lookup='abc=xyz'
            a left lookup searches any key which key name is abc.
            a right lookup searches item of dict where key == abc and its value ==xyz.

        case 3: lookup='=xyz'
            a left lookup is empty that means all keys.
            a right lookup search item of dict where any value of keys == xyz.

        case 4: lookup='abc=_wildcard(*xyz*)
            a left lookup searches any key which key name is abc.
            a right lookup searches items of dict where key == abc and its value contains xzy

        Both left and right supports text, wildcard, and regex.
        The following combination lookups are valid:
            abc=_wildcard(*xyz*)
            abc=_iwildcard(*xyz*)
            abc=_regex(.*xyz.*)
            abc=_iregex(.*xyz.*)
            _wildcard([Aa][Bb]c)=_wildcard(*xyz*)
            _wildcard([Aa][Bb]c)=_regex(.*xyz.*)
            =_wildcard(*xyz*)
            =_regex(.*xyz.*)

        Furthermore, right lookup also support custom keyword such as
            empty, not_empty, ip_address, ipv4_address,
            ipv6_address, date, datetime, time, ...

        Example:
            abc=empty(), i.e. searches key name is abc and its value is empty.
            abc=ipv4_address(), i.e. searches key name is abc and its value is IPv4 address.
            abc=date(), i.e. search key name is abc and its value is date such as 2021-06-16.
    """
    def __init__(self, lookup):
        self.lookup = str(lookup)
        self.left = None
        self.right = None
        self.process()

    @property
    def is_right(self):
        return bool(self.right)

    @classmethod
    def parse(cls, text):
        """Parse a lookup statement.

        Parameters
        ----------
            text (str): a lookup.

        Returns
        -------
        str: a regular expression pattern.
        """
        def parse_(text_):
            vpat = '''
                _(?P<options>i?)                    # options
                (?P<method>text|wildcard|regex)     # method is wildcard or regex
                [(]
                (?P<pattern>.+)                     # wildcard or regex pattern
                [)]
            '''
            match_ = re.search(vpat, text_, re.VERBOSE)
            options_ = match_.group('options').lower()
            method_ = match_.group('method').lower()
            pattern_ = match_.group('pattern')

            ignorecase_ = 'i' in options_
            if method_ == 'wildcard':
                pattern_ = utils.convert_wildcard_to_regex(pattern_)
            elif method_ == 'text':
                pattern_ = re.escape(pattern_)
            return pattern_, ignorecase_

        def parse_other_(text_):
            vpat1_ = '''
                (?i)(?P<custom_name>
                is_empty|is_not_empty|
                is_mac_address|is_not_mac_address|
                is_ip_address|is_not_ip_address|
                is_ipv4_address|is_not_ipv4_address|
                is_ipv6_address|is_not_ipv6_address|
                is_date|is_datetime|is_time|
                is_true|is_not_true|
                is_false|is_not_false)
                [(][)]$
            '''
            vpat2_ = '''
                (?i)(?P<op>lt|le|gt|ge|eq|ne)
                [(]
                (?P<other>([0-9]+)?[.]?[0-9]+)
                [)]$
            '''
            vpat3_ = '''
                (?i)(?P<op>eq|ne)
                [(]
                (?P<other>.*[^0-9].*)
                [)]$
            '''
            data_ = text_.lower()
            match1_ = re.match(vpat1_, data_, flags=re.VERBOSE)
            if match1_:
                custom_name = match1_.group('custom_name')
                valid = False if '_not_' in custom_name else True
                custom_name = custom_name.replace('not_', '')
                method = getattr(CustomValidation, custom_name)
                pfunc = partial(method, valid=valid, on_exception=False)
                return pfunc
            else:
                match2_ = re.match(vpat2_, data_, flags=re.VERBOSE)
                if match2_:
                    op = match2_.group('op')
                    other = match2_.group('other')
                    pfunc = partial(
                        OpValidation.compare_number,
                        op=op, other=other, on_exception=False
                    )
                    return pfunc
                else:
                    match3_ = re.match(vpat3_, data_, flags=re.VERBOSE)
                    if match3_:
                        op = match3_.group('op')
                        other = match3_.group('other')
                        pfunc = partial(
                            OpValidation.compare,
                            op=op, other=other, on_exception=False
                        )
                        return pfunc
                    else:
                        pattern_ = '^{}$'.format(re.escape(text_))
                        return pattern_

        pat = r'_i?(text|wildcard|regex)[(].+[)]'

        if not re.search(pat, text):
            result = parse_other_(text)
            return result
        lst = []
        start = 0
        is_ignorecase = False
        for node in re.finditer(pat, text):
            predata = text[start:node.start()]
            lst.append(re.escape(predata))
            data = node.group()
            pattern, ignorecase = parse_(data)
            lst.append(pattern)
            start = node.end()
            is_ignorecase |= ignorecase
        else:
            if lst:
                postdata = text[start:]
                lst.append(re.escape(postdata))

        pattern = ''.join(lst)
        if pattern:
            ss = '' if pattern[0] == '^' else '^'
            es = '' if pattern[-1] == '$' else '$'
            ic = '(?i)' if is_ignorecase else ''
            pattern = '{}{}{}{}'.format(ic, ss, pattern, es)
            return pattern
        else:
            fmt = 'Failed to parse this lookup : {!r}'
            raise LookupClsError(fmt.format(text))

    def process(self):
        """Parse a lookup to two expressions: a left expression and
        a right expression.

        If a lookup has a right expression, it will parse and assign to right,
        else, right expression is None."""

        left, *lst = self.lookup.split('=', maxsplit=1)
        left = left.strip()
        if left:
            self.left = self.parse(left)
        if lst:
            self.right = self.parse(lst[0])

    def is_left_matched(self, data):
        if not isinstance(data, str):
            return False

        if self.left:
            result = re.search(self.left, data)
            return bool(result)
        else:
            return True if self.right else False

    def is_right_matched(self, data):
        if not self.right:
            return True
        else:
            if callable(self.right):
                result = self.right(data)
                return result
            else:
                if not isinstance(data, str):
                    return False
                result = re.search(self.right, data)
                return bool(result)


class Object:
    """To build an object.

    Attributes
    ----------
    args (list): a position arguments.
    kwargs (dict): a keyword arguments.

    Raise
    -----
    ObjectArgumentError: if a position argument is not a dictionary object.
    """
    def __init__(self, *args, **kwargs):
        errors = []
        for index, arg in enumerate(args, 1):
            if not isinstance(arg, dict):
                errors.append(index)
            else:
                self.__dict__.update(arg)
        if errors:
            if len(errors) == 1:
                fmt = 'a position argument #{} is not a dictionary.'
                msg = fmt.format(errors[0])
            else:
                fmt = 'position arguments # {} are not a dictionary'
                msg = fmt.format(tuple(errors))
            raise ObjectArgumentError(msg)
        self.__dict__.update(kwargs)

    def __len__(self):
        return len(self.__dict__)

    def __bool__(self):
        return len(self) > 0
