"""Module containing the logic for the argument helper."""

from dictlistlib.exceptions import ArgumentError
from dictlistlib.exceptions import ArgumentValidationError


def validate_argument_type(*args, **kwargs):
    """Validate function/method argument type.

    Parameters
    ----------
    args (tuple): list of data type
    kwargs (dict): list of argument that needs to valid their types

    Returns
    -------
    bool: True if arguments match their types.

    Raises
    ______
    ArgumentError: if `args` is empty or element of `args` is not class
    ArgumentValidationError: if value's type of (key, value) pair doesn't match
        with a type of element in `args`

    Example
    -------
        >>> from dictlistlib.argumenthelper import validate_argument_type
        >>> def test(dict_obj):
        ...     validate_argument_type(dict, dict_obj=dict_obj)
        ...
        >>> dict_obj = dict()
        >>> test(dict_obj)
        >>> list_obj = list()
        >>> test(list_obj)
        Traceback (most recent call last):
          File "<stdin>", line 1, in <module>
          ...
        dlquery.argumenthelper.ArgumentValidationError: dict_obj argument must be a data type of dict.
        >>>
    """
    if len(args) == 0:
        msg = 'Cannot validate argument with no reference data type.'
        raise ArgumentError(msg)
    else:
        for arg in args:
            if not issubclass(arg, object):
                msg = 'args must contain all classes.'
                raise ArgumentError(msg)

    fmt = '{} argument must be a data type of {}.'
    type_name = ', '.join(arg.__name__ for arg in args)
    type_name = '({})'.format(type_name) if len(args) > 1 else type_name

    for name, obj in kwargs.items():
        if not isinstance(obj, args):
            raise ArgumentValidationError(fmt.format(name, type_name))
    return True


def validate_argument_choice(**kwargs):
    """Validate function/method argument choice.

    Parameters
    ----------
    kwargs (dict): list of argument that needs to valid their types
        a value of (key, value) pair must consist
        argument value and a list of choices.

    Returns
    -------
    bool: True if argument matches its argument choice.

    Raises
    ------
    ArgumentError: if invalid number of arguments of (key, value) pair
    ArgumentValidationError: if argument is not belong to choices.

    Example
    -------

        >>>
        >>> from dictlistlib.argumenthelper import validate_argument_choice
        >>> def test(kind='car'):
        ...     '''argument `kind` must be either ``car`` or ``bicycle```'''
        ...     validate_argument_choice(kind=(kind, ('car', 'bicycle')))
        ...
        >>> test(kind='car')
        >>> test(kind='bicycle')
        >>> test(kind='house')
        Traceback (most recent call last):
          File "<stdin>", line 1, in <module>
          ...
        dlquery.argumenthelper.ArgumentValidationError: kind argument must be a choice of ('car', 'bicycle').
        >>>
        >>>
    """
    for name, value in kwargs.items():
        try:
            argument, choices = value
        except Exception as ex:     # noqa
            msg = 'Invalid argument for verifying validate_argument_choice'
            raise ArgumentError(msg)

        is_not_a_list = not isinstance(choices, (list, tuple))
        is_empty = not bool(choices)

        if is_not_a_list or is_empty:
            raise ArgumentError('choices CAN NOT be empty.')

        if argument not in choices:
            fmt = '{} argument must be a choice of {}.'
            raise ArgumentValidationError(fmt.format(name, choices))
    return True


def validate_argument_is_not_empty(**kwargs):
    """Validate function/method argument is/are not empty.

    Parameters
    ----------
    kwargs (dict): list of argument and its value

    Returns
    -------
    bool: True if argument(s) is/are not empty.

    Raise
    -----
    ArgumentValidationError: if argument is empty.

    Example
    -------
        >>> from dictlistlib.argumenthelper import validate_argument_is_not_empty
        >>> def test(node):
        ...     validate_argument_is_not_empty(node=node)
        ...
        >>> test('abc')
        >>> test('')
        Traceback (most recent call last):
          File "<stdin>", line 1, in <module>
          ...
        dlquery.argumenthelper.ArgumentValidationError: a node argument CANNOT be empty.
        >>>
    """
    empty_args = []
    for name, value in kwargs.items():
        if not value:
            empty_args.append(name)

    if empty_args:
        if len(empty_args) == 1:
            msg = 'a {} argument CANNOT be empty.'.format(empty_args[0])
        else:
            msg = '({}) arguments CANNOT be empty.'.format(', '.join(empty_args))
        raise ArgumentValidationError(msg)
    return True
