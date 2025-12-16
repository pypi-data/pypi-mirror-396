"""Module containing the logic for creating dictlistlib."""

import yaml
import json
import csv
from dictlistlib import DLQuery


def create_from_json_file(filename, **kwargs):
    """Create a dictlistlib instance from JSON filename.

    Parameters
    ----------
    filename (str): JSON filename.
    kwargs (dict): keyword arguments which would use for JSON instantiation.

    Returns
    -------
    DLQuery: a DLQuery instance.
    """
    from io import IOBase
    if isinstance(filename, IOBase):
        obj = json.load(filename, **kwargs)
    else:
        with open(filename) as stream:
            obj = json.load(stream, **kwargs)

    query_obj = DLQuery(obj)
    return query_obj


def create_from_json_data(data, **kwargs):
    """Create a dictlistlib instance from JSON data.

    Parameters
    ----------
    data (str): JSON data in string format.
    kwargs (dict): keyword arguments which would use for JSON instantiation.

    Returns
    -------
    DLQuery: a DLQuery instance.
    """
    obj = json.loads(data, **kwargs)
    query_obj = DLQuery(obj)
    return query_obj


def create_from_yaml_file(filename, loader=yaml.SafeLoader):
    """Create a dictlistlib instance from YAML file.

    Parameters
    ----------
    filename (str): a YAML file.
    loader (yaml.loader.Loader): a YAML loader.

    Returns
    -------
    DLQuery: a DLQuery instance.
    """
    with open(filename) as stream:
        obj = yaml.load(stream, Loader=loader)
        query_obj = DLQuery(obj)
        return query_obj


def create_from_yaml_data(data, loader=yaml.SafeLoader):
    """Create a dictlistlib instance from YAML data.

    Parameters
    ----------
    data (str): a YAML data in string format.
    loader (yaml.loader.Loader): a YAML loader.

    Returns
    -------
    DLQuery: a DLQuery instance.
    """
    obj = yaml.load(data, Loader=loader)
    query_obj = DLQuery(obj)
    return query_obj


def create_from_csv_file(filename, fieldnames=None, restkey=None,
                         restval=None, dialect='excel', *args, **kwds):
    """Create a dictlistlib instance from CSV file.

    Parameters
    ----------
    filename (str): a CSV file.
    fieldnames (list): list of keys for the dict.
    restkey (str): key to catch long rows.
    restval (Any): default value for short rows.
    dialect (str): a CSV dialect.  Default is excel.
    args (tuple): any argument for csv.DictReader.
    kwds (dict): any keyword argument for csv.DictReader.

    Returns
    -------
    DLQuery: a DLQuery instance.
    """
    with open(filename, newline='') as stream:
        csv_reader = csv.DictReader(
            stream, fieldnames=fieldnames, restkey=restkey,
            restval=restval, dialect=dialect, *args, **kwds
        )
        lst_of_dict = [row for row in csv_reader]
        query_obj = DLQuery(lst_of_dict)
        return query_obj


def create_from_csv_data(data, fieldnames=None, restkey=None,
                         restval=None, dialect='excel', *args, **kwds):
    """Create a dictlistlib instance from CSV data.

    Parameters
    ----------
    data (str): a CSV data.
    fieldnames (list): list of keys for the dict.
    restkey (str): key to catch long rows.
    restval (Any): default value for short rows.
    dialect (str): a CSV dialect.  Default is excel.
    args (tuple): any argument for csv.DictReader.
    kwds (dict): any keyword argument for csv.DictReader.

    Returns
    -------
    DLQuery: a DLQuery instance.
    """
    from io import StringIO
    data = str(data).strip()
    stream = StringIO(data)
    csv_reader = csv.DictReader(
        stream, fieldnames=fieldnames, restkey=restkey,
        restval=restval, dialect=dialect, *args, **kwds
    )
    lst_of_dict = [row for row in csv_reader]
    query_obj = DLQuery(lst_of_dict)
    return query_obj
