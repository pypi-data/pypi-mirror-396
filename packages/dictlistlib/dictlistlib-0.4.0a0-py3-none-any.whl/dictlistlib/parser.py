"""Module containing the logic for the parsing utility."""

import re
import logging
from functools import partial
from dictlistlib.predicate import Predicate


logger = logging.getLogger(__file__)


class SelectParser:
    """A Select Parser class.

    Attributes
    ----------
    select_statement (str): a select-statement.
    columns (list): columns
    predicate (function): a callable function.
    logger (logging.Logger): a logger
    on_exception (bool): raise `Exception` if set True, otherwise, return False.

    Properties
    ----------
    is_zero_select -> bool
    is_all_select -> bool

    Methods
    -------
    get_predicate(expression) -> function
    build_predicate() -> function
    parse_statement() -> None
    """
    def __init__(self, select_statement, on_exception=True):
        self.select_statement = select_statement
        self.columns = [None]
        self.left_operands = []
        self.predicate = None
        self.logger = logger
        self.on_exception = on_exception

    @property
    def is_zero_select(self):
        """Return True if no column is selected."""
        return self.columns == [None]

    @property
    def is_all_select(self):
        """Return True if all columns are selected"""
        return self.columns == []

    def get_predicate(self, expression):
        """Parse an expression and convert to callable predicate function.

        Parameters
        ----------
        expression (str): an expression.  It can be a left express or a right expression.

        Returns
        -------
        function: a callable function.
        """
        pattern = '''(?i)["'](?P<key>.+)['"] +(?P<op>\\S+) +(?P<value>.+)'''
        match = re.match(pattern, expression)
        if match:
            key = match.group('key').strip()
            op = match.group('op').strip()
            value = match.group('value').strip()
        else:
            key, op, value = [i.strip() for i in re.split(r' +', expression, maxsplit=2)]

        key = key.replace('_COMMA_', ',')
        op = op.lower()
        value = value.replace('_COMMA_', ',')

        key not in self.left_operands and self.left_operands.append(key)

        tbl1 = {'lt': 'lt', 'le': 'le', '<': 'lt', '<=': 'le',
                'less_than': 'lt', 'less_than_or_equal': 'le',
                'less_than_or_equal_to': 'le', 'equal_or_less_than': 'le',
                'equal_to_or_less_than': 'le',
                'gt': 'gt', 'ge': 'ge', '>': 'gt', '>=': 'ge',
                'greater_than': 'gt', 'greater_than_or_equal': 'ge',
                'greater_than_or_equal_to': 'ge', 'equal_or_greater_than': 'ge',
                'equal_to_or_greater_than': 'ge'}

        tbl2 = {'eq': 'eq', '==': 'eq', 'equal': 'eq', 'equal_to': 'eq',
                'ne': 'ne', '!=': 'ne', 'not_equal': 'ne', 'not_equal_to': 'ne'}

        if op == 'is':
            func = partial(Predicate.is_, key=key, custom=value,
                           on_exception=self.on_exception)
        elif op in ['is_not', 'isnot']:
            func = partial(Predicate.isnot, key=key, custom=value,
                           on_exception=self.on_exception)
        elif op in tbl1:
            op = tbl1.get(op)
            val = str(value).strip()
            pattern = r'''
                (?i)((?P<semantic>semantic)_)?
                version[(](?P<expected_version>.+)[)]$
            '''
            match_version = re.match(pattern, val, flags=re.VERBOSE)

            pattern = r'(?i)(datetime|date|time)[(](?P<datetime_str>.+)[)]$'
            match_datetime = re.match(pattern, val)

            if match_version:
                semantic = match_version.group('semantic')
                expected_version = match_version.group('expected_version')
                if not semantic:
                    func = partial(Predicate.compare_version, key=key,
                                   op=op, other=expected_version,
                                   on_exception=self.on_exception)
                else:
                    func = partial(Predicate.compare_semantic_version,
                                   key=key, op=op, other=expected_version,
                                   on_exception=self.on_exception)
            elif match_datetime:
                datetime_str = match_datetime.group('datetime_str')
                func = partial(Predicate.compare_datetime, key=key,
                               op=op, other=datetime_str,
                               on_exception=self.on_exception)
            else:
                func = partial(Predicate.compare_number, key=key,
                               op=op, other=value)
        elif op in tbl2:
            op = tbl2.get(op)
            val = str(value).strip()
            pattern = r'''
                (?i)((?P<semantic>semantic)_)?
                version[(](?P<expected_version>.+)[)]$
            '''
            match_version = re.match(pattern, val, flags=re.VERBOSE)

            pattern = r'(?i)(datetime|date|time)[(](?P<datetime_str>.+)[)]$'
            match_datetime = re.match(pattern, val)

            if match_version:
                semantic = match_version.group('semantic')
                expected_version = match_version.group('expected_version')
                if not semantic:
                    func = partial(Predicate.compare_version, key=key,
                                   op=op, other=expected_version,
                                   on_exception=self.on_exception)
                else:
                    func = partial(Predicate.compare_semantic_version,
                                   key=key, op=op, other=expected_version,
                                   on_exception=self.on_exception)
            elif match_datetime:
                datetime_str = match_datetime.group('datetime_str')
                func = partial(Predicate.compare_datetime, key=key,
                               op=op, other=datetime_str,
                               on_exception=self.on_exception)
            else:
                try:
                    float(value)
                    func = partial(Predicate.compare_number,
                                   key=key, op=op, other=value,
                                   on_exception=self.on_exception)
                except Exception as ex:     # noqa
                    func = partial(Predicate.compare,
                                   key=key, op=op, other=value,
                                   on_exception=self.on_exception)
        elif op == 'match':
            func = partial(Predicate.match, key=key, pattern=value,
                           on_exception=self.on_exception)
        elif op in ['not_match', 'notmatch']:
            func = partial(Predicate.notmatch, key=key, pattern=value,
                           on_exception=self.on_exception)
        elif op in ['contain', 'contains']:
            func = partial(Predicate.contain, key=key, other=value,
                           on_exception=self.on_exception)
        elif re.match('not_?contains?', op, re.I):
            func = partial(Predicate.notcontain, key=key, other=value,
                           on_exception=self.on_exception)
        elif op in ['belong', 'belongs']:
            func = partial(Predicate.belong, key=key, other=value,
                           on_exception=self.on_exception)
        elif re.match('not_?belongs?', op, re.I):
            func = partial(Predicate.notbelong, key=key, other=value,
                           on_exception=self.on_exception)
        else:
            msg = (
                '*** Return False because of an unsupported {!r} logical '
                'operator.  Contact developer to support this case.'
            ).format(op)
            self.logger.info(msg)
            func = partial(Predicate.false)
        return func

    def build_predicate(self, expressions):
        """Build a predicate by parsing expressions

        Parameters
        ----------
        expressions (str): single or multiple expressions.

        Returns
        -------
        function: a callable function.
        """
        def chain(data_, a_=None, b_=None, op_='', on_exception=False):
            try:
                result_a, result_b = a_(data_), b_(data_)
                if op_ in ['or_', '||']:
                    return result_a or result_b
                elif op_ in ['and_', '&&']:
                    return result_a and result_b
                else:
                    msg_ = (
                        '* Return False because of an unsupported {!r} logical '
                        'operator.  Contact developer to support this case.'
                    ).format(op_)
                    self.logger.info(msg_)
                    return Predicate.false(data_)
            except Exception as ex:
                if on_exception:
                    raise ex
                else:
                    return Predicate.false(data_)

        groups = []
        start = 0
        match = None
        for match in re.finditer(' +(or_|and_|&&|[|]{2}) +', expressions, flags=re.I):
            expr = match.string[start:match.start()]
            op = match.group().strip().lower()
            groups.extend([expr.strip(), op.strip()])
            start = match.end()
        else:
            if groups and match:
                expr = match.string[match.end():].strip()
                groups.append(expr)

        if groups:
            total = len(groups)
            if total % 2 == 1 and total > 2:
                result = self.get_predicate(groups[0])
                for case, expr in zip(groups[1:-1:2], groups[2::2]):
                    func_b = self.get_predicate(expr)
                    result = partial(chain, a_=result, b_=func_b, op_=case,
                                     on_exception=self.on_exception)
                return result
            else:
                msg = (
                    '* Return False because of an invalid {!r} '
                    'expression.  Contact developer for this case.'
                ).format(expressions)
                self.logger.info(msg)
                result = partial(Predicate.false)
                return result
        else:
            return self.get_predicate(expressions)

    def parse_statement(self):
        """Parse, analyze, and build a select-statement to selecting
        columns and a callable predicate"""
        statement = self.select_statement

        if statement == '':
            return

        if ' where ' in statement.lower():
            select, expressions = re.split(
                ' +where +', statement, maxsplit=1, flags=re.I
            )
            select, expressions = select.strip(), expressions.strip()
            select = re.sub('^ *select +', '', select, flags=re.I).strip()
        elif statement.lower().startswith('where'):
            select = None
            expressions = re.sub('^where +', '', statement, flags=re.I)

        else:
            select = re.sub('^ *select +', '', statement, flags=re.I).strip()
            expressions = None

        if select:
            if re.match(r'(?i) *([*]|_+all_+) *$', select):
                self.columns = []
            else:
                self.columns = re.split(' *, *', select.strip(), flags=re.I)

        if expressions:
            self.predicate = self.build_predicate(expressions)
