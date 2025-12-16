"""Top-level module for dictlistlib.

This module

- initialize a query instance from DLQuery class
- or create a query instance from create_from_csv_file,
  create_from_csv_data, create_from_json_file, create_from_json_data,
  create_from_yaml_file, or create_from_yaml_data functions.

A query instance has find method to traverse entire dictionary or list
to extract a list of records based on a lookup and select-statement.

a lookup instance has two parts: left expression and right expression.
Both of these expressions supports filtering mechanism _text(...), _itext(...),
_wildcard(...), _iwildcard(...), _regex(...), _iregex(...) where
i standards for ignorecase.  A right expression supports additional
validations such as is_empty(), is_not_empty(), is_ipv4_address(), and so on.

a select-statement works similar to SQL, but it has minimal
criteria to filter record.

For example, assuming there is a list of dictionary

>>> lst_of_dict = [
...     {"a": "Apple", "b": "Banana", "c": "Cherry"},
...     {"a": "Apricot", "b": "Boysenberry", "c": "Cantaloupe"},
...     {"a": "Avocado", "b": "Blueberry", "c": "Clementine"},
... ]
>>>

we want to find any fruit beginning with letters Ap in group "a".  First,
we need to import DLQuery library and instantiate a query_obj

>>> from dictlistlib import DLQuery
>>> query_obj = DLQuery(lst_of_dict)

Snippet 1: using a lookup with a wildcard filtering

>>> result = query_obj.find(lookup='a=_wildcard(Ap*)', select='')
>>> assert result == ['Apple', 'Apricot']

Snippet 2: using a lookup with a regex filtering

>>> result = query_obj.find(lookup='a=_regex(Ap\\w+)', select='')
>>> assert result == ['Apple', 'Apricot']

Snippet 3: using a lookup to get an entry point and select-statement with
    WHERE clause to filter a result

>>> query_obj.find(lookup='a', select='WHERE a match Ap\\w+')
>>> assert result == ["Apple", "Apricot"]

In the previous example, we don't select any group.  As a result, the result
of query is a list of value(s).  If we want to find a filtered record with
its sibling, we need to select in a select-statement to retrieve more data

Snippet 4: using lookup with wildcard filtering and select-statement to select a, b

>>> result = query_obj.find(lookup='a=_wildcard(Ap*)', select='SELECT a, b')
>>> assert result == [{'a': 'Apple', 'b': 'Banana'}, {'a': 'Apricot', 'b': 'Boysenberry'}]

Snippet 5: using lookup with regex filtering and select-statement to select a, c

>>> result = query_obj.find(lookup='a=_regex(Ap\\w+)', select='SELECT a, c')
>>> assert result == [{'a': 'Apple', 'c': 'Cherry'}, {'a': 'Apricot', 'c': 'Cantaloupe'}]

Snippet 6: using lookup and select-statement to select c with WHERE clause

>>> query_obj.find(lookup='a', select='SELECT c WHERE a match Ap\\w+')
>>> assert result == [{'c': 'Cherry'}, {'c': 'Cantaloupe'}]
"""

from dictlistlib.dlquery import DLQuery         # noqa
from dictlistlib.factory import create_from_yaml_file   # noqa
from dictlistlib.factory import create_from_yaml_data   # noqa
from dictlistlib.factory import create_from_json_file   # noqa
from dictlistlib.factory import create_from_json_data   # noqa
from dictlistlib.factory import create_from_csv_file    # noqa
from dictlistlib.factory import create_from_csv_data    # noqa

from dictlistlib.validation import RegexValidation      # noqa
from dictlistlib.validation import OpValidation         # noqa
from dictlistlib.validation import CustomValidation     # noqa

from dictlistlib.config import version
from dictlistlib.config import edition

__version__ = version
__edition__ = edition

__all__ = [
    'CustomValidation',
    'DLQuery',
    'OpValidation',
    'RegexValidation',
    'create_from_csv_file',
    'create_from_csv_data',
    'create_from_json_file',
    'create_from_json_data',
    'create_from_yaml_file',
    'create_from_yaml_data',
    'version',
    'edition'
]
