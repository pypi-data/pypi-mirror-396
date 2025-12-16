"""Module containing the logic for the dictlistlib entry-points."""

import sys
import argparse
from os import path
from dictlistlib.application import Application
from dictlistlib import create_from_csv_file
from dictlistlib import create_from_json_file
from dictlistlib import create_from_yaml_file

from dictlistlib.utils import print_data_as_tabular

import dictlistlib.tutorial as tu


def run_tutorial(options):
    """Run a selection dictlistlib console CLI tutorial.

    Parameters
    ----------
    options (argparse.Namespace): a argparse.Namespace instance.

    Returns
    -------
    None: will call ``sys.exit(0)`` if end user requests a tutorial
    """

    tutorial = options.tutorial.lower()

    if tutorial not in ['base', 'csv', 'json', 'yaml']:
        return None

    tutorial == 'base' and tu.show_tutorial_dlquery()
    tutorial == 'csv' and tu.show_tutorial_csv()
    tutorial == 'json' and tu.show_tutorial_json()
    tutorial == 'yaml' and tu.show_tutorial_yaml()
    sys.exit(0)


def run_gui_application(options):
    """Run dictlistlib GUI application.

    Parameters
    ----------
    options (argparse.Namespace): a argparse.Namespace instance.

    Returns
    -------
    None: will invoke ``dictlistlib.Application().run()`` and ``sys.exit(0)``
    if end user requests `--application`
    """
    if options.gui:
        app = Application()
        app.run()
        sys.exit(0)


def show_dependency(options):
    if options.dependency:
        from platform import uname, python_version
        from dictlistlib.utils import Printer
        from dictlistlib.config import Data
        lst = [
            Data.main_app_text,
            'Platform: {0.system} {0.release} - Python {1}'.format(
                uname(), python_version()
            ),
            '--------------------',
            'Dependencies:'
        ]

        for pkg in Data.get_dependency().values():
            lst.append('  + Package: {0[package]}'.format(pkg))
            lst.append('             {0[url]}'.format(pkg))

        Printer.print(lst)
        sys.exit(0)


class Cli:
    """dictlistlib console CLI application."""
    def __init__(self):
        self.filename = ''
        self.filetype = ''
        self.result = None

        parser = argparse.ArgumentParser(
            prog='dictlistlib',
            usage='%(prog)s [options]',
            description='%(prog)s application',
        )

        parser.add_argument(
            '--gui', action='store_true',
            help='Launch a dictlistlib GUI application.'
        )

        parser.add_argument(
            '-f', '--filename', type=str,
            default='',
            help='JSON, YAML, or CSV file name.'
        )

        parser.add_argument(
            '-e', '--filetype', type=str, choices=['csv', 'json', 'yaml', 'yml'],
            default='',
            help='File type can be either json, yaml, yml, or csv.'
        )

        parser.add_argument(
            '-l', '--lookup', type=str, dest='lookup',
            default='',
            help='Lookup criteria for searching list or dictionary.'
        )

        parser.add_argument(
            '-s', '--select', type=str, dest='select_statement',
            default='',
            help='Select statement to enhance multiple searching criteria.'
        )

        parser.add_argument(
            '-t', '--tabular', action='store_true', dest='tabular',
            help='Show result in tabular format.'
        )

        parser.add_argument(
            '-d', '--dependency', action='store_true', dest='dependency',
            help='Show Python package dependencies.'
        )

        parser.add_argument(
            '-u', '--tutorial', type=str, choices=['base', 'csv', 'json', 'yaml'],
            default='',
            help='Tutorial can be either base, csv, json, or yaml.'
        )

        self.parser = parser

    @property
    def is_csv_type(self):
        """Return True if filetype is csv, otherwise, False."""
        return self.filetype == 'csv'

    @property
    def is_json_type(self):
        """Return True if filetype is json, otherwise, False."""
        return self.filetype == 'json'

    @property
    def is_yaml_type(self):
        """Return True if filetype is yml or yaml, otherwise, False."""
        return self.filetype in ['yml', 'yaml']

    def validate_cli_flags(self, options):
        """Validate argparse `options`.

        Parameters
        ----------
        options (argparse.Namespace): an argparse.Namespace instance.

        Returns
        -------
        bool: show ``self.parser.print_help()`` and call ``sys.exit(1)`` if
        all flags are empty or False, otherwise, return True
        """

        chk = any(bool(i) for i in vars(options).values())

        if not chk:
            self.parser.print_help()
            sys.exit(1)

        return True

    def validate_filename(self, options):
        """Validate `options.filename` flag which is a file type of `csv`,
        `json`, `yml`, or `yaml`.

        Parameters
        ----------
        options (argparse.Namespace): an argparse.Namespace instance.

        Returns
        -------
        bool: True if `options.filename` is valid, otherwise, ``sys.exit(1)``
        """
        filename, filetype = str(options.filename), str(options.filetype)
        if not filename:
            print('*** --filename flag CAN NOT be empty.')
            sys.exit(1)

        self.filename = filename
        self.filetype = filetype

        _, ext = path.splitext(filename)
        ext = ext.lower()
        if ext in ['.csv', '.json', '.yml', '.yaml']:
            self.filetype = ext[1:]
            return True

        if not filetype:
            if ext == '':
                fmt = ('*** {} file doesnt have an extension.  '
                       'System cant determine a file type.  '
                       'Please rerun with --filetype=<filetype> '
                       'where filetype is csv, json, yml, or yaml.')

            else:
                fmt = ('*** {} file has an extension but its extension is not '
                       'csv, json, yml, or yaml.  If you think this file is '
                       'csv, json, yml, or yaml file, '
                       'please rerun with --filetype=<filetype> '
                       'where filetype is csv, json, yml, or yaml.')
            print(fmt.format(filename))
            sys.exit(1)
        else:
            self.filetype = filetype

    def run_cli(self, options):
        """Execute dictlistlib command line.

        Parameters
        ----------
        options (argparse.Namespace): a argparse.Namespace instance.
        """
        lookup, select = options.lookup, options.select_statement
        if not options.lookup:
            print('*** --lookup flag CANNOT be empty.')
            sys.exit(1)

        if self.is_csv_type:
            func = create_from_csv_file
        elif self.is_json_type:
            func = create_from_json_file
        elif self.is_yaml_type:
            func = create_from_yaml_file
        else:
            print('*** invalid filetype.  Check with DEV.')
            sys.exit(1)

        query_obj = func(self.filename)
        result = query_obj.find(lookup=lookup, select=select)
        if result:
            print_data_as_tabular(result) if options.tabular else print(result)
        else:
            print('*** No record is found.')

        sys.exit(0)

    def run(self):
        """Take CLI arguments, parse it, and process."""
        options = self.parser.parse_args()
        show_dependency(options)
        run_tutorial(options)
        run_gui_application(options)
        self.validate_cli_flags(options)
        self.validate_filename(options)
        self.run_cli(options)


def execute():
    """Execute dictlistlib console CLI."""
    app = Cli()
    app.run()
