"""Module containing the tutorial functions."""

from textwrap import dedent


def get_tutorial_examples():
    """Return the dictlistlib tutorial examples text."""
    text = '''
        Example 1:
        ---------
        we need to find any item in a list_of_dict where
        key of item (i.e dict) has a value starting with Ap

        In this case, we need to look into every item of a list_of_dict,
        and then grab (key, value) pair that key is equal to "a" and
        value need to have a prefix of Ap.

        first criteria is that traverses lst_of_dict and report any item
        has key is equal "a"
            >>> result = query_obj.find(lookup='a', select='')
            >>> result
            ['Apple', 'Apricot', 'Avocado']
            >>>

        second criteria is that value of key "a" must have a "Ap" prefix.
        To be able to achieve this case, we can either use regular
        expression or wildcard filtering algorithm in lookup argument.

            >>> result = query_obj.find(lookup='a=_wildcard(Ap*)', select='')
            >>> result
            ['Apple', 'Apricot']
            >>> # or use regex
            >>> result = query_obj.find(lookup='a=_regex(Ap.+)', select='')
            >>> result
            ['Apple', 'Apricot']
            >>>

        there is another way to achieve the same result by using select-statement
        WHERE clause
            >>> result = query_obj.find(lookup='a', select='WHERE a match Ap.+')
            >>> result
            ['Apple', 'Apricot']
            >>>

        Example 2:
        ---------
        Find values where items of lst_of_dict have key "a" or "c"
            >>> result = query_obj.find(lookup='_wildcard([ac])', select='')
            >>> result
            ['Apple', 'Cherry', 'Apricot', 'Cantaloupe', 'Avocado', 'Clementine']
            >>>
            >>> result = query_obj.find(lookup='_regex([ac])', select='')
            >>> result
            ['Apple', 'Cherry', 'Apricot', 'Cantaloupe', 'Avocado', 'Clementine']

        Example 3:
        ---------
        Find values where items of lst_of_dict have key "a" or "c" where items
        value have letter i or y

            >>> result = query_obj.find(lookup='_wildcard([ac])=_wildcard(*[iy]*)', select='')
            >>> result
            ['Cherry', 'Apricot', 'Clementine']
            >>>
            >>> result = query_obj.find(lookup='_wildcard([ac])=_regex(.*[iy].*)', select='')
            >>> result
            ['Cherry', 'Apricot', 'Clementine']
            >>> result = query_obj.find(lookup='_regex([ac])=_wildcard(*[iy]*)', select='')
            >>> result
            ['Cherry', 'Apricot', 'Clementine']
            >>>
            >>> result = query_obj.find(lookup='_regex([ac])=_regex(.*[iy].*)', select='')
            >>> result
            ['Cherry', 'Apricot', 'Clementine']

        Note: in this case, the lookup argument contains two expressions:
        a left expression and a right expression, a separator between
        left and right expression is "=" symbol.

        lookup          : _wildcard([ac])=_regex(.*[iy].*)
        left expression : _wildcard([ac])
        right expression: _regex(.*[iy].*)

        Example 3.1:
        -----------
        Find values where items of lst_of_dict have key "a" or "c" where items
        value have letter i or y and select a, c

            >>> # this is a result without select a, c
            >>> result = query_obj.find(lookup='_wildcard([ac])=_wildcard(*[iy]*)', select='')
            >>> result
            ['Cherry', 'Apricot', 'Clementine']
            >>>
            >>> # this is a result after select a, c
            >>> result = query_obj.find(lookup='_wildcard([ac])=_wildcard(*[iy]*)', select='SELECT a, c')
            >>> result
            [{'a': 'Apple', 'c': 'Cherry'}, {'a': 'Apricot', 'c': 'Cantaloupe'}, {'a': 'Avocado', 'c': 'Clementine'}]
            >>>
        ########################################
    '''

    return dedent(text)


def show_tutorial_dlquery():
    """Print a dictlistlib tutorial."""
    text = '''
        ########################################
        # tutorial: dictlistlib                    #
        ########################################
        Assuming there is a list of dictionary

            >>> lst_of_dict = [
            ...     {"a": "Apple", "b": "Banana", "c": "Cherry"},
            ...     {"a": "Apricot", "b": "Boysenberry", "c": "Cantaloupe"},
            ...     {"a": "Avocado", "b": "Blueberry", "c": "Clementine"},
            ... ]
            >>>

        We need to instantiate dictlistlib.DLQuery object

            >>> from dictlistlib import DLQuery
            >>> query_obj = DLQuery(lst_of_dict)
    '''

    data = '{}\n{}'.format(dedent(text), get_tutorial_examples())

    print(data)


def show_tutorial_csv():
    """Print a dictlistlib tutorial - case csv file."""
    text = '''
        ########################################
        # tutorial: CSV                        #
        ########################################
        Assuming there is a sample.csv file

        ----------------------------------------
        Console usage: try the following
            $ dictlistlib --filename=sample.csv --lookup="a" --select="WHERE a match Ap.+"
            ['Apple', 'Apricot']
            $
            $
            $ dictlistlib --filename=sample.csv --lookup="a"  --select="WHERE c not_match [Cc]a.+"
            ['Apple', 'Avocado']
            $
            $
            $ dictlistlib --filename=sample.csv --lookup="a"  --select="SELECT a, c WHERE c not_match [Cc]a.+"
            [OrderedDict([('a', 'Apple'), ('c', 'Cherry')]), OrderedDict([('a', 'Avocado'), ('c', 'Clementine')])]

        ----------------------------------------

            >>> fn = 'sample.csv'
            >>> content = open(fn).read()
            >>> print(content)
            a,b,c
            Apple,Banana,Cherry
            Apricot,Boysenberry,Cantaloupe
            Avocado,Blueberry,Clementine
            >>>

        We need to instantiate dictlistlib.DLQuery object using create_from_csv_file function

            >>> from dictlistlib import create_from_csv_file
            >>> query_obj = create_from_csv_file('sample.csv')
    '''

    data = '{}\n{}'.format(dedent(text), get_tutorial_examples())

    print(data)


def show_tutorial_json():
    """Print a dictlistlib tutorial - case json file."""
    text = '''
        ########################################
        # tutorial: JSON                       #
        ########################################
        Assuming there is a sample.json file

        ----------------------------------------
        Console usage: try the following
            $ dictlistlib --filename=sample.json --lookup="a" --select="WHERE a match Ap.+"
            ['Apple', 'Apricot']
            $
            $
            $ dictlistlib --filename=sample.json --lookup="a"  --select="WHERE c not_match [Cc]a.+"
            ['Apple', 'Avocado']
            $
            $
            $ dictlistlib --filename=sample.json --lookup="a"  --select="SELECT a, c WHERE c not_match [Cc]a.+"
            [OrderedDict([('a', 'Apple'), ('c', 'Cherry')]), OrderedDict([('a', 'Avocado'), ('c', 'Clementine')])]

        ----------------------------------------

            >>> fn = 'sample.json'
            >>> content = open(fn).read()
            >>> print(content)
            [
                {"a": "Apple", "b": "Banana", "c": "Cherry"},
                {"a": "Apricot", "b": "Boysenberry", "c": "Cantaloupe"},
                {"a": "Avocado", "b": "Blueberry", "c": "Clementine"}
            ]
            >>>

        We need to instantiate dictlistlib.DLQuery object using create_from_json_file function

            >>> from dictlistlib import create_from_json_file
            >>> query_obj = create_from_json_file('sample.json')
    '''

    data = '{}\n{}'.format(dedent(text), get_tutorial_examples())

    print(data)


def show_tutorial_yaml():
    """Print a dictlistlib tutorial - case yaml file."""
    text = '''
        ########################################
        # tutorial: yaml                        #
        ########################################
        Assuming there is a sample.yaml file

        ----------------------------------------
        Console usage: try the following
            $ dictlistlib --filename=sample.yaml --lookup="a" --select="WHERE a match Ap.+"
            ['Apple', 'Apricot']
            $
            $
            $ dictlistlib --filename=sample.yaml --lookup="a"  --select="WHERE c not_match [Cc]a.+"
            ['Apple', 'Avocado']
            $
            $
            $ dictlistlib --filename=sample.yaml --lookup="a"  --select="SELECT a, c WHERE c not_match [Cc]a.+"
            [OrderedDict([('a', 'Apple'), ('c', 'Cherry')]), OrderedDict([('a', 'Avocado'), ('c', 'Clementine')])]

        ----------------------------------------

            >>> fn = 'sample.yaml'
            >>> content = open(fn).read()
            >>> print(content)
            - a: Apple
              b: Banana
              c: Cherry
            - a: Apricot
              b: Boysenberry
              c: Cantaloupe
            - a: Avocado
              b: Blueberry
              c: Clementine
            >>>

        We need to instantiate dictlistlib.DLQuery object using create_from_yaml_file function

            >>> from dictlistlib import create_from_yaml_file
            >>> query_obj = create_from_yaml_file('sample.yaml')
    '''

    data = '{}\n{}'.format(dedent(text), get_tutorial_examples())

    print(data)
