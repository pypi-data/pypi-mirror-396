"""Module containing the logic for predicate."""

import logging
from dictlistlib.validation import RegexValidation
from dictlistlib.validation import OpValidation
from dictlistlib.validation import CustomValidation
from dictlistlib.validation import VersionValidation
from dictlistlib.validation import DatetimeValidation

from dictlistlib.exceptions import PredicateParameterDataTypeError

logger = logging.getLogger(__file__)


def get_value(data, key):
    """Get value from dict or dict-like instance.

    Parameters
    ----------
    data (dict): a dict or dict-like instance.
    key (str): a key of dict or dict-like instance.

    Returns
    -------
    Any: any data.
    """
    if not isinstance(data, dict):
        msg = 'data must be instance of dict (?? {} ??).'.format(type(data))
        raise PredicateParameterDataTypeError(msg)
    try:
        value = data.get(key)
        return value
    except Exception as ex:
        msg = 'Warning *** {}: {}'.format(type(ex).__name__, ex)
        logger.warning(msg)
        return '__EXCEPTION__'


class Predicate:
    """Contains Predicate classmethod for validation.

    Methods
    -------
    Predicate.is_(data, key='', custom='', on_exception=True) -> bool
    Predicate.isnot(data, key='', custom='', on_exception=True) -> bool
    Predicate.match(data, key='', pattern='', on_exception=True) -> bool
    Predicate.notmatch(data, key='', pattern='', on_exception=True) -> bool
    Predicate.compare_number(data, key='', op='', other='', on_exception=True) -> bool
    Predicate.compare(data, key='', op='', other='', on_exception=True) -> bool
    Predicate.contain(data, key='', other='', on_exception=True) -> bool
    Predicate.notcontain(data, key='', other='', on_exception=True) -> bool
    Predicate.belong(data, key='', other='', on_exception=True) -> bool
    Predicate.notbelong(data, key='', other='', on_exception=True) -> bool
    Predicate.true(data) -> bool
    Predicate.false(data) -> bool
    """
    @classmethod
    def is_(cls, data, key='', custom='', on_exception=True):
        """is keyword for expression validation.

        Parameters
        ----------
        data (dict): a dict or dict-like instance.
        key (str): a key of dict or dict-like instance.
        custom (str): a custom keyword.
        on_exception (bool): raise `Exception` if set True, otherwise, return False.

        Returns
        -------
        bool: True if meet custom keyword condition, otherwise, False.
        """
        value = get_value(data, key)
        result = CustomValidation.validate(
            custom, value, on_exception=on_exception
        )
        return result

    @classmethod
    def isnot(cls, data, key='', custom='', on_exception=True):
        """is_not or isnot keyword for expression validation.

        Parameters
        ----------
        data (dict): a dict or dict-like instance.
        key (str): a key of dict or dict-like instance.
        custom (str): a custom keyword.
        on_exception (bool): raise `Exception` if set True, otherwise, return False.

        Returns
        -------
        bool: True or False.
        """

        value = get_value(data, key)
        result = CustomValidation.validate(
            custom, value, valid=False, on_exception=on_exception
        )
        return result

    @classmethod
    def match(cls, data, key='', pattern='', on_exception=True):
        """match keyword for expression validation.

        Parameters
        ----------
        data (dict): a dict or dict-like instance.
        key (str): a key of dict or dict-like instance.
        pattern (str): a regular expression.
        on_exception (bool): raise `Exception` if set True, otherwise, return False.

        Returns
        -------
        bool: True if regular expression is matched, otherwise, False.
        """
        value = get_value(data, key)
        result = RegexValidation.match(
            pattern, value, on_exception=on_exception
        )
        return result

    @classmethod
    def notmatch(cls, data, key='', pattern='', on_exception=True):
        """not_match or notmatch keyword for expression validation.

        Parameters
        ----------
        data (dict): a dict or dict-like instance.
        key (str): a key of dict or dict-like instance.
        pattern (str): a regular expression.
        on_exception (bool): raise `Exception` if set True, otherwise, return False.

        Returns
        -------
        bool: True if regular expression is not matched, otherwise, False.
        """
        value = get_value(data, key)
        result = RegexValidation.match(
            pattern, value, valid=False, on_exception=on_exception
        )
        return result

    @classmethod
    def compare_number(cls, data, key='', op='', other='', on_exception=True):
        """compare_number keyword for expression validation.

        Parameters
        ----------
        data (dict): a dict or dict-like instance.
        key (str): a key of dict or dict-like instance.
        op (str): an operator such as lt, le, gt, ge, eq, or ne.
        other (str, int, float): other number.
        on_exception (bool): raise `Exception` if set True, otherwise, return False.

        Returns
        -------
        bool: True if meet operator comparison, otherwise, False.
        """
        value = get_value(data, key)
        result = OpValidation.compare_number(
            value, op, other, on_exception=on_exception
        )
        return result

    @classmethod
    def compare(cls, data, key='', op='', other='', on_exception=True):
        """compare keyword for expression validation.

        Parameters
        ----------
        data (dict): a dict or dict-like instance.
        key (str): a key of dict or dict-like instance.
        op (str): an operator such eq or ne.
        other (str): other data.
        on_exception (bool): raise `Exception` if set True, otherwise, return False.

        Returns
        -------
        bool: True if meet operator comparison, otherwise, False.
        """
        value = get_value(data, key)
        result = OpValidation.compare(
            value, op, other, on_exception=on_exception
        )
        return result

    @classmethod
    def compare_version(cls, data, key='', op='', other='', on_exception=True):
        """compare_version keyword for expression validation.

        Parameters
        ----------
        data (dict): a dict or dict-like instance.
        key (str): a key of dict or dict-like instance.
        op (str): an operator such lt, le, gt, ge, eq or ne.
        other (str): other data.
        on_exception (bool): raise `Exception` if set True, otherwise, return False.

        Returns
        -------
        bool: True if meet operator comparison, otherwise, False.
        """
        value = get_value(data, key)
        result = VersionValidation.compare_version(
            value, op, other, on_exception=on_exception
        )
        return result

    @classmethod
    def compare_semantic_version(cls, data, key='', op='', other='', on_exception=True):
        """compare_semantic_version keyword for expression validation.

        Parameters
        ----------
        data (dict): a dict or dict-like instance.
        key (str): a key of dict or dict-like instance.
        op (str): an operator such lt, le, gt, ge, eq or ne.
        other (str): other data.
        on_exception (bool): raise `Exception` if set True, otherwise, return False.

        Returns
        -------
        bool: True if meet operator comparison, otherwise, False.
        """
        value = get_value(data, key)
        result = VersionValidation.compare_semantic_version(
            value, op, other, on_exception=on_exception
        )
        return result

    @classmethod
    def compare_datetime(cls, data, key='', op='', other='', on_exception=True):
        """compare_datetime keyword for expression validation.

        Parameters
        ----------
        data (dict): a dict or dict-like instance.
        key (str): a key of dict or dict-like instance.
        op (str): an operator such lt, le, gt, ge, eq or ne.
        other (str): other data.
        on_exception (bool): raise `Exception` if set True, otherwise, return False.

        Returns
        -------
        bool: True if meet operator comparison, otherwise, False.
        """
        value = get_value(data, key)
        result = DatetimeValidation.compare_datetime(
            value, op, other, on_exception=on_exception
        )
        return result

    @classmethod
    def contain(cls, data, key='', other='', on_exception=True):
        """contain keyword for expression validation.

        Parameters
        ----------
        data (dict): a dict or dict-like instance.
        key (str): a key of dict or dict-like instance.
        other (str): other data.
        on_exception (bool): raise `Exception` if set True, otherwise, return False.

        Returns
        -------
        bool: True if value of data contains other, otherwise, False.
        """
        value = get_value(data, key)
        result = OpValidation.contain(
            value, other, on_exception=on_exception
        )
        return result

    @classmethod
    def notcontain(cls, data, key='', other='', on_exception=True):
        """not_contain or notcontain keyword for expression validation.

        Parameters
        ----------
        data (dict): a dict or dict-like instance.
        key (str): a key of dict or dict-like instance.
        other (str): other data.
        on_exception (bool): raise `Exception` if set True, otherwise, return False.

        Returns
        -------
        bool: True if value of data doesn't contain other, otherwise, False.
        """
        value = get_value(data, key)
        result = OpValidation.contain(
            value, other, valid=False, on_exception=on_exception
        )
        return result

    @classmethod
    def belong(cls, data, key='', other='', on_exception=True):
        """belong keyword for expression validation.

        Parameters
        ----------
        data (dict): a dict or dict-like instance.
        key (str): a key of dict or dict-like instance.
        other (str): other data.
        on_exception (bool): raise `Exception` if set True, otherwise, return False.

        Returns
        -------
        bool: True if value of data belong other, otherwise, False.
        """
        value = get_value(data, key)
        result = OpValidation.belong(
            value, other, on_exception=on_exception
        )
        return result

    @classmethod
    def notbelong(cls, data, key='', other='', on_exception=True):
        """not_belong or notbelong keyword for expression validation.

        Parameters
        ----------
        data (dict): a dict or dict-like instance.
        key (str): a key of dict or dict-like instance.
        other (str): other data.
        on_exception (bool): raise `Exception` if set True, otherwise, return False.

        Returns
        -------
        bool: True if value of data doesn't belong other, otherwise, False.
        """
        value = get_value(data, key)
        result = OpValidation.belong(
            value, other, valid=False, on_exception=on_exception
        )
        return result

    @classmethod
    def true(cls, data, on_exception=True):     # noqa
        """Regardless a user provided data, it always returns True.

        Parameters
        ----------
        data (dict): a dict or dict-like instance.
        on_exception (bool): raise `Exception` if set True, otherwise, return False.

        Returns
        -------
        bool: True

        Notes
        -----
        Both data and on_exception will skip because this method always return True.
        """
        return True

    @classmethod
    def false(cls, data, on_exception=True):    # noqa
        """Regardless a user provided data, it always returns False.

        Parameters
        ----------
        data (dict): a dict or dict-like instance.
        on_exception (bool): raise `Exception` if set True, otherwise, return False.

        Returns
        -------
        bool: False

        Notes
        -----
        Both data and on_exception will skip because this method always return False.
        """
        return False
