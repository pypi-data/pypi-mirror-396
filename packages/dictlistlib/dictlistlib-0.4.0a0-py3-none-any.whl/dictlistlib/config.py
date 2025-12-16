"""Module containing the attributes for dictlistlib."""

from os import path
from textwrap import dedent

import compare_versions
import dateutil
import yaml

__version__ = '0.4.0a0'
version = __version__
__edition__ = 'Community'
edition = __edition__

__all__ = [
    'version',
    'edition',
    'Data'
]


class Data:
    # main app
    main_app_text = 'dictlistlib {}'.format(version)

    # packages
    compare_versions_text = 'compare_versions v{}'.format(compare_versions.__version__)
    compare_versions_link = 'https://pypi.org/project/compare_versions/'

    python_dateutil_text = 'python-dateutil v{}'.format(dateutil.__version__)   # noqa
    python_dateutil_link = 'https://pypi.org/project/python_dateutil/'

    pyyaml_text = 'pyyaml v{}'.format(yaml.__version__)
    pyyaml_link = 'https://pypi.org/project/PyYAML/'

    # company
    company = 'Geeks Trident LLC'
    company_url = 'https://www.geekstrident.com/'

    # URL
    repo_url = 'https://github.com/Geeks-Trident-LLC/dictlistlib'
    documentation_url = path.join(repo_url, 'blob/develop/README.md')
    license_url = path.join(repo_url, 'blob/develop/LICENSE')

    # License
    years = '2022-2080'
    license_name = 'BSD-3-Clause License'
    copyright_text = 'Copyright @ {}'.format(years)
    license = dedent(
        """
BSD 3-Clause License

Copyright (c) 2021-2040, Geeks Trident LLC
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its
   contributors may be used to endorse or promote products derived from
   this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
        """
    ).strip()

    @classmethod
    def get_dependency(cls):
        dependencies = dict(
            compare_versions=dict(
                package=cls.compare_versions_text,
                url=cls.compare_versions_link
            ),
            dateutil=dict(
                package=cls.python_dateutil_text,
                url=cls.python_dateutil_link
            ),
            pyyaml=dict(
                package=cls.pyyaml_text,
                url=cls.pyyaml_link
            )
        )
        return dependencies
