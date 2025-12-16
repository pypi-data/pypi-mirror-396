"""Module containing the logic for validation."""

import operator
import re
from ipaddress import ip_address
# import functools
import traceback
import logging
from datetime import datetime
from compare_versions.core import verify_list as version_compare
from dateutil.parser import parse
from dateutil.parser import isoparse
from dateutil.tz import gettz
from dateutil.tz import UTC

from dictlistlib.exceptions import ValidationIpv6PrefixError
from dictlistlib.exceptions import ValidationOperatorError
from dictlistlib.exceptions import ParsedTimezoneError


DEBUG = 0
logger = logging.getLogger(__file__)


def get_ip_address(addr, is_prefix=False, on_exception=True):
    """Get an IP address.

    Parameters
    ----------
    addr (str): an IP address
    is_prefix(bool): check to return IP Address and prefix.  Default is False.
    on_exception (bool): raise Exception if it is True, otherwise, return None.

    Returns
    -------
    IPAddress: IP address, otherwise, None.
    """
    try:
        value, *grp = re.split(r'[/%]', str(addr).strip(), maxsplit=1)
        if grp:
            prefix = grp[0].strip()
            chk1 = not prefix.isdigit()
            chk2 = prefix.isdigit() and int(prefix) >= 128
            if chk1 or chk2:
                msg = '{} address containing invalid prefix.'.format(value)
                logger.warning(msg)
                raise ValidationIpv6PrefixError(msg)
        else:
            prefix = None

        if '.' in value:
            octets = value.split('.')
            if len(octets) == 4:
                if value.startswith('0'):
                    value = '.'.join(str(int(i, 8)) for i in octets)
                else:
                    len_chk = list(set(len(i) for i in octets)) == [2]
                    hex_chk = re.search(r'(?i)[a-f]', value)
                    if len_chk and hex_chk:
                        value = '.'.join(str(int(i, 16)) for i in octets)
        ip_addr = ip_address(str(value))
        return (ip_addr, prefix) if is_prefix else ip_addr
    except Exception as ex:  # noqa
        if on_exception:
            raise ex
        return (None, None) if is_prefix else None


def validate_interface(iface_name, pattern='', valid=True, on_exception=True):
    """Verify a provided data is a network interface.

    Parameters
    ----------
    iface_name (str): a network interface
    pattern (str): sub pattern for interface name.  Default is empty.

    Returns
    -------
    bool: True if iface_name is a network interface, otherwise, False.
    """
    iface_name = str(iface_name)

    if iface_name.upper() == '__EXCEPTION__':
        return False

    try:
        pattern = r'\b' + pattern + r' *[0-9]+(/[0-9]+)?([.][0-9]+)?\b'
        result = bool(re.match(pattern, iface_name, re.I))
        return result if valid else not result
    except Exception as ex:
        result = raise_exception_if(ex, on_exception=on_exception)
        return result


# def false_on_exception_for_classmethod(func):
#     """Wrap the classmethod and return False on exception.
#
#     Parameters
#     ----------
#     func (function): a callable function
#
#     Notes
#     -----
#     DO NOT nest this decorator.
#     """
#     @functools.wraps(func)
#     def wrapper_func(*args, **kwargs):
#         """A Wrapper Function"""
#         chk = str(args[1]).upper()
#         if chk == '__EXCEPTION__':
#             return False
#         try:
#             result = func(*args, **kwargs)
#             return result if kwargs.get('valid', True) else not result
#         except Exception as ex:
#             if DEBUG:
#                 traceback.print_exc()
#             else:
#                 msg = 'Warning *** {}: {}'.format(type(ex).__name__, ex)
#                 logger.warning(msg)
#             is_called_exception = kwargs.get('on_exception', False)
#             if is_called_exception:
#                 raise ex
#             else:
#                 return False if kwargs.get('valid', True) else True
#     return wrapper_func


def raise_exception_if(ex, on_exception=True):
    """Raise an exception if condition is required, otherwise return False

    Parameters
    ----------
    ex (Exception): an exception
    on_exception (bool): raise an exception when it set to True

    Returns
    -------
    bool: False if on_exception is False
    """
    if DEBUG:
        traceback.print_exc()
    else:
        msg = 'Warning *** {}: {}'.format(type(ex).__name__, ex)
        logger.warning(msg)
    if on_exception:
        raise ex
    return False


class RegexValidation:
    """A regular expression validation class.

    Methods
    -------
    RegexValidation.match(pattern, value, valid=True, on_exception=True) -> bool
    """
    @classmethod
    def match(cls, pattern, value, valid=True, on_exception=True):
        """Perform regular expression matching.

        Parameters
        ----------
        pattern (str): a regular expression pattern.
        value (str): data
        valid (bool): check for a valid result.  Default is True.
        on_exception (bool): raise Exception if it is True, otherwise, return None.

        Returns
        -------
        bool: True if match pattern, otherwise, False.
        """
        if str(value).upper() == '__EXCEPTION__':
            return False

        try:
            result = bool(re.match(pattern, str(value)))
            return result if valid else not result
        except Exception as ex:
            result = raise_exception_if(ex, on_exception=on_exception)
            return result


class OpValidation:
    """The operator validation class

    Methods
    -------
    OpValidation.compare_number(value, op, other, valid=True, on_exception=True) -> bool
    OpValidation.compare(value, op, other, valid=True, on_exception=True) -> bool
    OpValidation.contain(value, other, valid=True, on_exception=True) -> bool
    OpValidation.belong(value, other, valid=True, on_exception=True) -> bool
    """
    @classmethod
    def compare_number(cls, value, op, other, valid=True, on_exception=True):
        """Perform operator comparison for number.

        Parameters
        ----------
        value (str): data.
        op (str): an operator can be lt, le, gt, ge, eq, ne, <, <=, >, >=, ==, or !=
        other (str): a number.
        valid (bool): check for a valid result.  Default is True.
        on_exception (bool): raise Exception if it is True, otherwise, return None.

        Returns
        -------
        bool: True if a value lt|le|gt|ge|eq|ne other value, otherwise, False.
                or    a value < | <= | > | >= | == | != other value
        """
        if str(value).upper() == '__EXCEPTION__':
            return False

        try:
            op = str(op).lower().strip()
            op = 'lt' if op == '<' else 'le' if op == '<=' else op
            op = 'gt' if op == '>' else 'ge' if op == '>=' else op
            op = 'eq' if op == '==' else 'ne' if op == '!=' else op
            valid_ops = ('lt', 'le', 'gt', 'ge', 'eq', 'ne')
            if op not in valid_ops:
                fmt = 'Invalid {!r} operator for validating number.  It MUST be {}.'
                raise ValidationOperatorError(fmt.format(op, valid_ops))

            v, o = str(value).lower(), str(other).lower()
            value = True if v == 'true' else False if v == 'false' else value
            other = True if o == 'true' else False if o == 'false' else other
            num = float(other)
            value = float(value)
            result = getattr(operator, op)(value, num)
            return result if valid else not result
        except Exception as ex:
            result = raise_exception_if(ex, on_exception=on_exception)
            return result

    @classmethod
    def compare(cls, value, op, other, valid=True, on_exception=True):
        """Perform operator comparison for string.

        Parameters
        ----------
        value (str): data.
        op (str): an operator can be eq, ne, ==, or !=
        other (str): other value
        valid (bool): check for a valid result.  Default is True.
        on_exception (bool): raise Exception if it is True, otherwise, return None.

        Returns
        -------
        bool: True if a value eq|ne other value, otherwise, False.
                or    a value == | != other value
        """
        if str(value).upper() == '__EXCEPTION__':
            return False

        try:
            op = str(op).lower().strip()
            op = 'eq' if op == '==' else 'ne' if op == '!=' else op
            valid_ops = ('eq', 'ne')
            if op not in valid_ops:
                fmt = ('Invalid {!r} operator for checking equal '
                       'or via versa.  It MUST be {}.')
                raise ValidationOperatorError(fmt.format(op, valid_ops))

            result = getattr(operator, op)(value, other)
            return result if valid else not result
        except Exception as ex:
            result = raise_exception_if(ex, on_exception=on_exception)
            return result

    @classmethod
    def contain(cls, value, other, valid=True, on_exception=True):
        """Perform operator checking that value contains other.

        Parameters
        ----------
        value (str): data.
        other (str): other value
        valid (bool): check for a valid result.  Default is True.
        on_exception (bool): raise Exception if it is True, otherwise, return None.

        Returns
        -------
        bool: True if value contains other, otherwise, False.
        """
        if str(value).upper() == '__EXCEPTION__':
            return False

        try:
            result = operator.contains(value, other)
            return result if valid else not result
        except Exception as ex:
            result = raise_exception_if(ex, on_exception=on_exception)
            return result

    @classmethod
    def belong(cls, value, other, valid=True, on_exception=True):
        """Perform operator checking that value belongs other.

        Parameters
        ----------
        value (str): data.
        other (str): other value
        valid (bool): check for a valid result.  Default is True.
        on_exception (bool): raise Exception if it is True, otherwise, return None.

        Returns
        -------
        bool: True if value belongs other, otherwise, False.
        """
        if str(value).upper() == '__EXCEPTION__':
            return False

        try:
            result = operator.contains(other, value)
            return result if valid else not result
        except Exception as ex:
            result = raise_exception_if(ex, on_exception=on_exception)
            return result


class CustomValidation:
    """A custom keyword validation class.

    Methods
    -------
    CustomValidation.validate(case, value, valid=True, on_exception=True) -> bool
    CustomValidation.is_ip_address(addr, valid=True, on_exception=True) -> bool
    CustomValidation.is_ipv4_address(addr, valid=True, on_exception=True) -> bool
    CustomValidation.is_ipv6_address(addr, valid=True, on_exception=True) -> bool
    CustomValidation.is_mac_address(addr, valid=True, on_exception=True) -> bool
    CustomValidation.is_loopback_interface(iface_name, valid=True, on_exception=True) -> bool
    CustomValidation.is_bundle_ether(iface_name, valid=True, on_exception=True) -> bool
    CustomValidation.is_port_channel_interface(iface_name, valid=True, on_exception=True) -> bool
    CustomValidation.is_hundred_gigabit_ethernet(iface_name, valid=True, on_exception=True) -> bool
    CustomValidation.is_ten_gigabit_ethernet(iface_name, valid=True, on_exception=True) -> bool
    CustomValidation.is_gigabit_ethernet(iface_name, valid=True, on_exception=True) -> bool
    CustomValidation.is_fast_ethernet(iface_name, valid=True, on_exception=True) -> bool
    CustomValidation.is_empty(value, valid=True, on_exception=True) -> bool
    CustomValidation.is_optional_empty(value, valid=True, on_exception=True) -> bool
    CustomValidation.is_true(value, valid=True, on_exception=True) -> bool
    CustomValidation.is_false(value, valid=True, on_exception=True) -> bool
    CustomValidation.is_date(value, valid=True, on_exception=True) -> bool
    CustomValidation.is_datetime(value, valid=True, on_exception=True) -> bool
    CustomValidation.is_time(value, valid=True, on_exception=True) -> bool
    CustomValidation.is_isodate(value, valid=True, on_exception=True) -> bool
    """

    @classmethod
    def validate(cls, case, value, valid=True, on_exception=True):
        """Look for a valid custom classmethod and process it.

        Parameters
        ----------
        case (str): custom validation keyword.
        value (str): data for validation.
        valid (bool): check for a valid result.  Default is True.
        on_exception (bool): raise Exception if it is True, otherwise, return None.

        Returns
        -------
        bool: True if match condition, otherwise, False.

        Raise:
        NotImplementedError: if custom method doesn't exist.
        """
        case = str(case).lower()
        name = 'is_{}'.format(case)
        method = getattr(cls, name, None)
        if callable(method):
            return method(value, valid=valid, on_exception=on_exception)
        else:
            msg = 'Need to implement this case {}'.format(case)
            raise NotImplementedError(msg)

    @classmethod
    def is_ip_address(cls, addr, valid=True, on_exception=True):
        """Verify a provided data is an IP address.

        Parameters
        ----------
        addr (str): an IP address
        valid (bool): check for a valid result.  Default is True.
        on_exception (bool): raise Exception if it is True, otherwise, return None.

        Returns
        -------
        bool: True if addr is an IP address, otherwise, False.
        """
        if str(addr).upper() == '__EXCEPTION__':
            return False

        try:
            ip_addr = get_ip_address(addr, on_exception=on_exception)
            chk = True if ip_addr else False
            if not chk:
                logger.info('{!r} is not an IP address.'.format(addr))
            return chk if valid else not chk
        except Exception as ex:
            result = raise_exception_if(ex, on_exception=on_exception)
            return result if valid else not result

    @classmethod
    def is_ipv4_address(cls, addr, valid=True, on_exception=True):
        """Verify a provided data is an IPv4 address.

        Parameters
        ----------
        addr (str): an IPv4 address
        valid (bool): check for a valid result.  Default is True.
        on_exception (bool): raise Exception if it is True, otherwise, return None.

        Returns
        -------
        bool: True if addr is an IPv4 address, otherwise, False.
        """
        if str(addr).upper() == '__EXCEPTION__':
            return False

        try:
            ip_addr = get_ip_address(addr, on_exception=on_exception)
            chk = True if ip_addr and ip_addr.version == 4 else False
            if not chk:
                logger.info('{!r} is not an IPv4 address.'.format(addr))
            return chk if valid else not chk
        except Exception as ex:
            result = raise_exception_if(ex, on_exception=on_exception)
            return result if valid else not result

    @classmethod
    def is_ipv6_address(cls, addr, valid=True, on_exception=True):
        """Verify a provided data is an IPv6 address.

        Parameters
        ----------
        addr (str): an IPv6 address
        valid (bool): check for a valid result.  Default is True.
        on_exception (bool): raise Exception if it is True, otherwise, return None.

        Returns
        -------
        bool: True if addr is an IPv6 address, otherwise, False.
        """
        if str(addr).upper() == '__EXCEPTION__':
            return False

        try:
            ip_addr = get_ip_address(addr, on_exception=on_exception)
            chk = True if ip_addr and ip_addr.version == 6 else False
            if not chk:
                logger.info('{!r} is not an IPv6 address.'.format(addr))
            return chk if valid else not chk
        except Exception as ex:
            result = raise_exception_if(ex, on_exception=on_exception)
            return result if valid else not result

    @classmethod
    def is_mac_address(cls, addr, valid=True, on_exception=True):
        """Verify a provided data is a MAC address.

        Parameters
        ----------
        addr (str): a MAC address
        valid (bool): check for a valid result.  Default is True.
        on_exception (bool): raise Exception if it is True, otherwise, return None.

        Returns
        -------
        bool: True if addr is a MAC address, otherwise, False.
        """
        if str(addr).upper() == '__EXCEPTION__':
            return False

        try:
            addr = str(addr)
            patterns = [
                r'\b[0-9a-f]{2}([-: ])([0-9a-f]{2}\1){4}[0-9a-f]{2}\b',
                r'\b[a-f0-9]{4}[.][a-f0-9]{4}[.][a-f0-9]{4}\b'
            ]
            for pattern in patterns:
                result = re.match(pattern, addr, re.I)
                if result:
                    return True if valid else False
            return False if valid else True
        except Exception as ex:
            result = raise_exception_if(ex, on_exception=on_exception)
            return result

    # @classmethod
    # def is_network_interface(cls, iface_name, valid=True, on_exception=True):
    #     """Verify a provided data is a network interface.
    #
    #     Parameters
    #     ----------
    #     iface_name (str): a network interface
    #     valid (bool): check for a valid result.  Default is True.
    #     on_exception (bool): raise Exception if it is True, otherwise, return None.
    #
    #     Returns
    #     -------
    #     bool: True if iface_name is a network interface, otherwise, False.
    #     """
    #     pattern = r'[a-z]+(-?[a-z0-9]+)?'
    #     result = validate_interface(iface_name, pattern=pattern,
    #                                 valid=valid, on_exception=on_exception)
    #     return result

    @classmethod
    def is_loopback_interface(cls, iface_name, valid=True, on_exception=True):
        """Verify a provided data is a loopback interface.

        Parameters
        ----------
        iface_name (str): a loopback interface
        valid (bool): check for a valid result.  Default is True.
        on_exception (bool): raise Exception if it is True, otherwise, return None.

        Returns
        -------
        bool: True if iface_name is a loopback interface, otherwise, False.
        """
        pattern = r'lo(opback)?'
        result = validate_interface(iface_name, pattern=pattern,
                                    valid=valid, on_exception=on_exception)
        return result

    @classmethod
    def is_bundle_ethernet(cls, iface_name, valid=True, on_exception=True):
        """Verify a provided data is a bundle-ether interface.

        Parameters
        ----------
        iface_name (str): a bundle-ether interface
        valid (bool): check for a valid result.  Default is True.
        on_exception (bool): raise Exception if it is True, otherwise, return None.

        Returns
        -------
        bool: True if iface_name is a bundle-ether interface, otherwise, False.
        """
        pattern = r'bundle-ether|be'
        result = validate_interface(iface_name, pattern=pattern,
                                    valid=valid, on_exception=on_exception)
        return result

    @classmethod
    def is_port_channel(cls, iface_name, valid=True, on_exception=True):
        """Verify a provided data is a port-channel interface.

        Parameters
        ----------
        iface_name (str): a port-channel interface
        valid (bool): check for a valid result.  Default is True.
        on_exception (bool): raise Exception if it is True, otherwise, return None.

        Returns
        -------
        bool: True if iface_name is a bundle-ether interface, otherwise, False.
        """
        pattern = r'po(rt-channel)?'
        result = validate_interface(iface_name, pattern=pattern,
                                    valid=valid, on_exception=on_exception)
        return result

    @classmethod
    def is_hundred_gigabit_ethernet(cls, iface_name, valid=True, on_exception=True):
        """Verify a provided data is a HundredGigaBit interface.

        Parameters
        ----------
        iface_name (str): a HundredGigaBitEthernet interface
        valid (bool): check for a valid result.  Default is True.
        on_exception (bool): raise Exception if it is True, otherwise, return None.

        Returns
        -------
        bool: True if iface_name is a HundredGigaBit interface, otherwise, False.
        """
        pattern = 'Hu(ndredGigE)?'
        result = validate_interface(iface_name, pattern=pattern,
                                    valid=valid, on_exception=on_exception)
        return result

    @classmethod
    def is_ten_gigabit_ethernet(cls, iface_name, valid=True, on_exception=True):
        """Verify a provided data is a TenGigaBitEthernet interface.

        Parameters
        ----------
        iface_name (str): a TenGigaBitEthernet interface
        valid (bool): check for a valid result.  Default is True.
        on_exception (bool): raise Exception if it is True, otherwise, return None.

        Returns
        -------
        bool: True if iface_name is a TenGigaBitEthernet interface, otherwise, False.
        """
        pattern = 'Te(nGigE)?'
        result = validate_interface(iface_name, pattern=pattern,
                                    valid=valid, on_exception=on_exception)
        return result

    @classmethod
    def is_gigabit_ethernet(cls, iface_name, valid=True, on_exception=True):
        """Verify a provided data is a TenGigaBitEthernet interface.

        Parameters
        ----------
        iface_name (str): a TenGigaBitEthernet interface
        valid (bool): check for a valid result.  Default is True.
        on_exception (bool): raise Exception if it is True, otherwise, return None.

        Returns
        -------
        bool: True if iface_name is a TenGigaBitEthernet interface, otherwise, False.
        """
        pattern = 'Gi(gabitEthernet)?'
        result = validate_interface(iface_name, pattern=pattern,
                                    valid=valid, on_exception=on_exception)
        return result

    @classmethod
    def is_fast_ethernet(cls, iface_name, valid=True, on_exception=True):
        """Verify a provided data is a FastEthernet interface.

        Parameters
        ----------
        iface_name (str): a FastEthernet interface
        valid (bool): check for a valid result.  Default is True.
        on_exception (bool): raise Exception if it is True, otherwise, return None.

        Returns
        -------
        bool: True if iface_name is a FastEthernet interface, otherwise, False.
        """
        pattern = r'fa(stethernet)?'
        result = validate_interface(iface_name, pattern=pattern,
                                    valid=valid, on_exception=on_exception)
        return result

    @classmethod
    def is_empty(cls, value, valid=True, on_exception=True):    # noqa
        """Verify a provided data is an empty string.

        Parameters
        ----------
        value (str): a string data.
        valid (bool): check for a valid result.  Default is True.
        on_exception (bool): raise Exception if it is True, otherwise, return None.

        Returns
        -------
        bool: True if value is an empty string, otherwise, False.
        """
        if str(value).upper() == '__EXCEPTION__':
            return False

        value = str(value)
        result = value == ''
        return result if valid else not result

    @classmethod
    def is_optional_empty(cls, value, valid=True, on_exception=True):   # noqa
        """Verify a provided data is an optional empty string.

        Parameters
        ----------
        value (str): a string data.
        valid (bool): check for a valid result.  Default is True.
        on_exception (bool): raise Exception if it is True, otherwise, return None.

        Returns
        -------
        bool: True if value is an optional empty string, otherwise, False.
        """
        if str(value).upper() == '__EXCEPTION__':
            return False

        value = str(value)
        result = bool(re.match(r'\s+$', value))
        return result if valid else not result

    @classmethod
    def is_true(cls, value, valid=True, on_exception=True):     # noqa
        """Verify a provided data is True.

        Parameters
        ----------
        value (bool or str): a boolean or string data.
        valid (bool): check for a valid result.  Default is True.
        on_exception (bool): raise Exception if it is True, otherwise, return None.

        Returns
        -------
        bool: True if value is a True, otherwise, False.
        """
        if str(value).upper() == '__EXCEPTION__':
            return False

        value = str(value)
        result = value.lower() == 'true'
        return result if valid else not result

    @classmethod
    def is_false(cls, value, valid=True, on_exception=True):    # noqa
        """Verify a provided data is False.

        Parameters
        ----------
        value (bool or str): a boolean or string data.
        valid (bool): check for a valid result.  Default is True.
        on_exception (bool): raise Exception if it is True, otherwise, return None.

        Returns
        -------
        bool: True if value is a False, otherwise, False.
        """
        if str(value).upper() == '__EXCEPTION__':
            return False

        value = str(value)
        result = value.lower() == 'false'
        return result if valid else not result

    @classmethod
    def is_date(cls, value, valid=True, on_exception=True):
        """Verify a provided data is a date.

        Parameters
        ----------
        value (str): a date data.
        valid (bool): check for a valid result.  Default is True.
        on_exception (bool): raise Exception if it is True, otherwise, return None.

        Returns
        -------
        bool: True if value is a date, otherwise, False.
        """
        if str(value).upper() == '__EXCEPTION__':
            return False

        try:
            if str(value).strip() == '':
                return False

            value = str(value).strip()
            parse(value, fuzzy=True)

            time_pattern = '[0-9]+:[0-9]+'
            matched_time = re.search(time_pattern, value)

            if matched_time:
                return False if valid else True

            date_pattern = '[0-9]+([/-])[0-9]+\\1[0-9]+'
            matched_date = re.search(date_pattern, value)
            if matched_date:
                return True if valid else False

            month_names_pattern = """(?ix)jan(uary)?|
                                     feb(ruary)?|
                                     mar(ch)?|
                                     apr(il)?|
                                     may|
                                     june?|
                                     july?|
                                     aug(ust)?|
                                     sep(tember)?|
                                     oct(ober)?|
                                     nov(ember)?|
                                     dec(ember)?"""
            matched_month_names = re.search(month_names_pattern, value)
            if matched_month_names:
                return True if valid else False

            day_names_pattern = '(?i)(sun|mon|tues?|wed(nes)?|thu(rs)?|fri|sat(ur)?)(day)?'
            matched_day_names = re.search(day_names_pattern, value)
            if matched_day_names:
                return True if valid else False

            return False if valid else True
        except Exception as ex:
            result = raise_exception_if(ex, on_exception=on_exception)
            return result

    @classmethod
    def is_datetime(cls, value, valid=True, on_exception=True):
        """Verify a provided data is a datetime.

        Parameters
        ----------
        value (str): a datetime data.
        valid (bool): check for a valid result.  Default is True.
        on_exception (bool): raise Exception if it is True, otherwise, return None.

        Returns
        -------
        bool: True if value is a datetime, otherwise, False.
        """
        if str(value).upper() == '__EXCEPTION__':
            return False

        try:
            if str(value).strip() == '':
                return False

            value = str(value).strip()
            parse(value, fuzzy=True)

            time_pattern = '[0-9]+:[0-9]+'
            matched_time = re.search(time_pattern, value)

            if not matched_time:
                return False if valid else True

            date_pattern = '[0-9]+([/-])[0-9]+\\1[0-9]+'
            matched_date = re.search(date_pattern, value)
            if matched_date:
                return True if valid else False

            month_names_pattern = """(?ix)jan(uary)?|
                                     feb(ruary)?|
                                     mar(ch)?|
                                     apr(il)?|
                                     may|
                                     june?|
                                     july?|
                                     aug(ust)?|
                                     sep(tember)?|
                                     oct(ober)?|
                                     nov(ember)?|
                                     dec(ember)?"""
            matched_month_names = re.search(month_names_pattern, value)
            if matched_month_names:
                return True if valid else False

            day_names_pattern = '(?i)(sun|mon|tues?|wed(nes)?|thu(rs)?|fri|sat(ur)?)(day)?'
            matched_day_names = re.search(day_names_pattern, value)
            if matched_day_names:
                return True if valid else False

            return False if valid else True
        except Exception as ex:
            result = raise_exception_if(ex, on_exception=on_exception)
            return result

    @classmethod
    def is_time(cls, value, valid=True, on_exception=True):
        """Verify a provided data is time.

        Parameters
        ----------
        value (str): time data.
        valid (bool): check for a valid result.  Default is True.
        on_exception (bool): raise Exception if it is True, otherwise, return None.

        Returns
        -------
        bool: True if value is time, otherwise, False.
        """
        if str(value).upper() == '__EXCEPTION__':
            return False

        try:
            if str(value).strip() == '':
                return False

            value = str(value).strip()
            parse(value, fuzzy=True)

            date_pattern = '[0-9]+([/-])[0-9]+\\1[0-9]+'
            matched_date = re.search(date_pattern, value)
            if matched_date:
                return False if valid else True

            month_names_pattern = """(?ix)jan(uary)?|
                                     feb(ruary)?|
                                     mar(ch)?|
                                     apr(il)?|
                                     may|
                                     june?|
                                     july?|
                                     aug(ust)?|
                                     sep(tember)?|
                                     oct(ober)?|
                                     nov(ember)?|
                                     dec(ember)?"""
            matched_month_names = re.search(month_names_pattern, value)
            if matched_month_names:
                return False if valid else True

            day_names_pattern = '(?i)(sun|mon|tues?|wed(nes)?|thu(rs)?|fri|sat(ur)?)(day)?'
            matched_day_names = re.search(day_names_pattern, value)
            if matched_day_names:
                return False if valid else True

            time_pattern = '[0-9]+:[0-9]+'
            matched_time = re.search(time_pattern, value)
            result = bool(matched_time)
            return result if valid else not result
        except Exception as ex:
            result = raise_exception_if(ex, on_exception=on_exception)
            return result

    @classmethod
    def is_isodate(cls, value, valid=True, on_exception=True):
        """Verify a provided data is ISO date.

        Parameters
        ----------
        value (str): ISO date data.
        valid (bool): check for a valid result.  Default is True.
        on_exception (bool): raise Exception if it is True, otherwise, return None.

        Returns
        -------
        bool: True if value is ISO date, otherwise, False.
        """
        if str(value).upper() == '__EXCEPTION__':
            return False

        try:
            if str(value).strip() == '':
                return False

            value = str(value).strip()
            isoparse(value)

            pattern = '[0-9]{4}((-[0-9]{2})|(-?W[0-9]{2}))$'
            match = re.match(pattern, value)
            if match:
                return True if valid else False

            pattern = ('[0-9]{4}('
                       '(-?[0-9]{2}-?[0-9]{2})|'
                       '(-?W[0-9]{2}-?[0-9])|'
                       '(-?[0-9]{3})'
                       ')')
            result = bool(re.match(pattern, value))
            return result if valid else False
        except Exception as ex:
            result = raise_exception_if(ex, on_exception=on_exception)
            return result


class VersionValidation:
    """The Version comparison validation class

    Methods
    -------
    VersionValidation.compare_version(value, op, other, valid=True, on_exception=True) -> bool
    VersionValidation.compare_semantic_version(value, op, other, valid=True, on_exception=True) -> bool
    """
    @classmethod
    def compare_version(cls, value, op, other, valid=True, on_exception=True):
        """Perform operator comparison for version.

        Parameters
        ----------
        value (str): a version.
        op (str): an operator can be lt, le, gt, ge, eq, ne, <, <=, >, >=, ==, or !=
        other (str): other version.
        valid (bool): check for a valid result.  Default is True.
        on_exception (bool): raise Exception if it is True, otherwise, return None.

        Returns
        -------
        bool: True if a version lt|le|gt|ge|eq|ne other version, otherwise, False.
                or    a version < | <= | > | >= | == | != other version
        """
        if str(value).upper() == '__EXCEPTION__':
            return False

        try:
            if str(value).strip() == '' or str(other).strip() == '':
                return False

            op = str(op).lower().strip()
            op = 'lt' if op == '<' else 'le' if op == '<=' else op
            op = 'gt' if op == '>' else 'ge' if op == '>=' else op
            op = 'eq' if op == '==' else 'ne' if op == '!=' else op
            valid_ops = ('lt', 'le', 'gt', 'ge', 'eq', 'ne')
            if op not in valid_ops:
                fmt = 'Invalid {!r} operator for validating version.  It MUST be {}.'
                raise ValidationOperatorError(fmt.format(op, valid_ops))

            value, other = str(value), str(other)
            result = version_compare([value, other], comparison=op, scheme='string')
            return result if valid else not result
        except Exception as ex:
            result = raise_exception_if(ex, on_exception=on_exception)
            return result

    @classmethod
    def compare_semantic_version(cls, value, op, other, valid=True, on_exception=True):
        """Perform operator comparison for semantic version.

        Parameters
        ----------
        value (str): a version.
        op (str): an operator can be lt, le, gt, ge, eq, ne, <, <=, >, >=, ==, or !=
        other (str): other version.
        valid (bool): check for a valid result.  Default is True.
        on_exception (bool): raise Exception if it is True, otherwise, return None.

        Returns
        -------
        bool: True if a version lt|le|gt|ge|eq|ne other version, otherwise, False.
                or    a version < | <= | > | >= | == | != other version
        """
        if str(value).upper() == '__EXCEPTION__':
            return False

        try:
            if str(value).strip() == '' or str(other).strip() == '':
                return False

            op = str(op).lower().strip()
            op = 'lt' if op == '<' else 'le' if op == '<=' else op
            op = 'gt' if op == '>' else 'ge' if op == '>=' else op
            op = 'eq' if op == '==' else 'ne' if op == '!=' else op
            valid_ops = ('lt', 'le', 'gt', 'ge', 'eq', 'ne')
            if op not in valid_ops:
                fmt = 'Invalid {!r} operator for validating version.  It MUST be {}.'
                raise ValidationOperatorError(fmt.format(op, valid_ops))

            value, other = str(value), str(other)
            result = version_compare([value, other], comparison=op, scheme='semver')
            return result if valid else not result
        except Exception as ex:
            result = raise_exception_if(ex, on_exception=on_exception)
            return result


class DatetimeResult:
    """Store a result of parsing custom datetime.

    Attributes
    ----------
    data (str): a datetime data.
    timezone (dict): a list of Linux timezone such as America/Los_Angeles.
        Default is None.
    iso (str, bool): a list of bool. Default is None.
    dayfirst (str, bool): a list of bool.  Default is None.

    Methods
    -------
    to_bool(value, default=False) -> bool
    parse_timezone() -> None

    Raises
    ------
    ParsedTimezoneError
    """
    def __init__(self, data='', timezone=None, iso=False,
                 dayfirst=True, fuzzy=True):
        self.data = data
        self.iso = self.to_bool(iso, default=False)
        self.dayfirst = self.to_bool(dayfirst, default=True)
        self.fuzzy = self.to_bool(fuzzy, default=True)
        self.timezone = timezone
        self.tzinfos = dict()
        self.parse_timezone()

    def to_bool(self, value, default=False):    # noqa
        """Return True if value is True

        Parameters
        ----------
        value (str, bool): a value is either True or False
        default (bool): if value is empty, then return a default value.
                Default is False.

        Returns
        -------
        bool: True if value is True, otherwise, False.

        """
        if isinstance(value, bool):
            return value
        value = str(value).title()
        result = default if value == '' else value == 'True'
        return result

    def parse_timezone(self):
        """Parse timezone to build tzinfos."""
        if self.timezone in [None, '']:
            return

        if not isinstance(self.timezone, (dict, str)):
            fmt = 'timezone must be an instance of dict or str, but {}'
            raise ParsedTimezoneError(fmt.format(type(self.timezone)))

        if self.timezone and isinstance(self.timezone, dict):
            self.tzinfos = dict(self.timezone)
            return

        for pair in self.timezone.split(', '):
            items = pair.split(':', maxsplit=1)
            if len(items) != 2:
                fmt = 'Invalid timezone format -- {!r}'
                raise ParsedTimezoneError(fmt.format(self.timezone))
            tzname, tzvalue = [item.strip() for item in items]

            try:
                self.tzinfos[tzname] = int(tzvalue)
            except Exception as ex:         # noqa
                try:
                    self.tzinfos[tzname] = gettz(tzvalue)
                except Exception as ex:     # noqa
                    fmt = 'Invalid timezone value -- {!r}'
                    raise ParsedTimezoneError(fmt.format(self.timezone))


class DatetimeValidation:
    """The Datetime comparison validation class

    Methods
    -------
    DatetimeValidation.get_date(datetime_value, options) -> datetime.datetime
    DatetimeValidation.do_datetime_compare(a_datetime, op, other_datetime) -> bool
    DatetimeValidation.compare_datetime(value, op, other, valid=True, on_exception=True) -> bool
    """

    @classmethod
    def parse_custom_date(cls, data):
        """parse custom datetime and return DatetimeResult instance

        Parameters
        ----------
        data (str): datetime timezone=...? iso=...? dayfirst=...? fuzzy=...?

        Returns
        -------
        DatetimeResult: a datetime result.
        """
        pattern = '(?i) +(timezone|iso|dayfirst|fuzzy)='

        if not re.search(pattern, data):
            result = DatetimeResult(data=data)
            return result

        start = 0
        date_val, timezone, iso, dayfirst, fuzzy = [''] * 5
        match_data = ''
        m = None
        for m in re.finditer(pattern, data):
            before_match = m.string[start:m.start()]
            if not date_val:
                date_val = before_match.strip()
            elif not timezone and match_data.startswith('timezone='):
                timezone = before_match.strip()
            elif not iso and match_data.startswith('iso='):
                iso = before_match.strip()
            elif not iso and match_data.startswith('dayfirst='):
                dayfirst = before_match.strip()
            elif not fuzzy and match_data.startswith('fuzzy='):
                fuzzy = before_match.strip()
            match_data = m.group().strip()
            start = m.end()
        else:
            if m:
                if not timezone and match_data.startswith('timezone='):
                    timezone = m.string[m.end():].strip()
                elif not iso and match_data.startswith('iso='):
                    iso = m.string[m.end():].strip()
                elif not dayfirst and match_data.startswith('dayfirst='):
                    dayfirst = m.string[m.end():].strip()
                elif not fuzzy and match_data.startswith('fuzzy='):
                    fuzzy = m.string[m.end():].strip()

        result = DatetimeResult(data=date_val, timezone=timezone, iso=iso,
                                dayfirst=dayfirst, fuzzy=fuzzy)
        return result

    @classmethod
    def get_date(cls, datetime_value, options):
        """parse datetime value to datetime instance

        Parameters
        ----------
        datetime_value (str): datetime data
        options (DatetimeResult): a datetime parsed options

        Returns
        -------
        datetime.datetime: a datetime.
        """
        if options.iso:
            result = isoparse(datetime_value)
            return result
        else:
            pattern = """(?ix)(.*[0-9])(
                        jan(uary)?|
                        feb(ruary)?|
                        mar(ch)?|
                        apr(il)?|
                        may|
                        june?|
                        july?|
                        aug(ust)?|
                        sep(tember)?|
                        oct(ober)?|
                        nov(ember)?|
                        dec(ember)?)([0-9].*)"""
            datetime_value = re.sub(pattern, r'\1 \2 \12', datetime_value)
            result = parse(datetime_value, dayfirst=options.dayfirst,
                           fuzzy=options.fuzzy, tzinfos=options.tzinfos)
            return result

    @classmethod
    def do_date_compare(cls, a_date, op, other_date):
        """Compare a_date lt, le, gt, ge, eq, or ne other_date

        Parameters
        ----------
        a_date (datetime.datetime): a datetime data
        op (str): a operator which can be lt, le, gt, ge, eq, ne.
        other_date (datetime.datetime): other datetime data

        Returns
        -------
        bool: True if a datetime lt|le|gt|ge|eq|ne other datetime, otherwise, False.
        """
        a_tzname = a_date.tzname()
        other_tzname = other_date.tzname()
        if not bool(a_tzname) ^ bool(other_tzname):
            result = getattr(operator, op)(a_date, other_date)
            return result
        elif not a_tzname:
            a_new_datetime = datetime(
                a_date.year, a_date.month, a_date.day,
                a_date.hour, a_date.minute, a_date.second,
                a_date.microsecond, tzinfo=UTC
            )
            result = getattr(operator, op)(a_new_datetime, other_date)
            return result
        else:
            other_new_datetime = datetime(
                other_date.year, other_date.month, other_date.day,
                other_date.hour, other_date.minute, other_date.second,
                other_date.microsecond, tzinfo=UTC
            )
            result = getattr(operator, op)(a_date, other_new_datetime)
            return result

    @classmethod
    def compare_datetime(cls, value, op, other, valid=True, on_exception=True):
        """Perform operator comparison for datetime.

        Parameters
        ----------
        value (str): a datetime.
        op (str): an operator can be lt, le, gt, ge, eq, ne, >, >=, <, <=, ==, or !=
        other (str): other datetime.
        valid (bool): check for a valid result.  Default is True.
        on_exception (bool): raise Exception if it is True, otherwise, return None.

        Returns
        -------
        bool: True if a datetime lt|le|gt|ge|eq|ne other datetime, otherwise, False.
                 or   a datetime < | <= | > | >= | == | != other datetime
        """
        if str(value).upper() == '__EXCEPTION__':
            return False

        try:
            if str(value).strip() == '' or str(other).strip() == '':
                return False

            op = 'lt' if op == '<' else 'le' if op == '<=' else op
            op = 'gt' if op == '>' else 'ge' if op == '>=' else op
            op = 'eq' if op == '==' else 'ne' if op == '!=' else op

            dt_parsed_result = DatetimeValidation.parse_custom_date(other)

            a_date_str, other_date_str = value, dt_parsed_result.data

            if other_date_str.strip() == '':
                return False

            a_date = DatetimeValidation.get_date(a_date_str, dt_parsed_result)
            other_date = DatetimeValidation.get_date(other_date_str, dt_parsed_result)

            result = DatetimeValidation.do_date_compare(a_date, op, other_date)
            return result if valid else not result
        except Exception as ex:
            result = raise_exception_if(ex, on_exception=on_exception)
            return result
