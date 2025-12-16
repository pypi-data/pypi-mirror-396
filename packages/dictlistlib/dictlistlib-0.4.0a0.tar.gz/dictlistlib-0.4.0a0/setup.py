"""Packaging dictlistlib."""

from setuptools import setup, find_packages

with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="dictlistlib",
    version="0.4.0a0",  # alpha versioning
    license="BSD-3-Clause",
    license_files=["LICENSE"],
    description=(
        "dictlistlib simplifies querying Python dictionaries and lists with "
        "wildcards, regex, custom keywords, and SQL-like statements, "
        "streamlining data validation, filtering, and efficient workflows"
    ),
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Tuyen Mathew Duong",
    author_email="tuyen@geekstrident.com",
    maintainer="Tuyen Mathew Duong",
    maintainer_email="tuyen@geekstrident.com",
    install_requires=[
        "compare_versions",
        "python-dateutil",
        "pyyaml",
    ],
    url="https://github.com/Geeks-Trident-LLC/dictlistlib",
    packages=find_packages(
        exclude=(
            "tests*", "testing*", "examples*",
            "build*", "dist*", "docs*", "venv*"
        )
    ),
    project_urls={
        "Documentation": "https://github.com/Geeks-Trident-LLC/dictlistlib/wiki",
        "Source": "https://github.com/Geeks-Trident-LLC/dictlistlib",
        "Tracker": "https://github.com/Geeks-Trident-LLC/dictlistlib/issues",
    },
    entry_points={
        "console_scripts": [
            "dictlistlib = dictlistlib.main:execute",
            "dictlistlib-gui = dictlistlib.application:execute",
            "dictlistlib-app = dictlistlib.application:execute",
        ]
    },
    classifiers=[
        # development status
        "Development Status :: 3 - Alpha",
        # natural language
        "Natural Language :: English",
        # intended audience
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: Information Technology",
        "Intended Audience :: Manufacturing",
        "Intended Audience :: Other Audience",
        "Intended Audience :: Science/Research",
        # operating system
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: POSIX :: Linux",
        "Operating System :: Microsoft :: Windows",
        # programming language
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        # topic
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Code Generators",
        "Topic :: Software Development :: Quality Assurance",
        "Topic :: Software Development :: Testing",
        "Topic :: Scientific/Engineering",
        "Topic :: Text Processing",
    ],
    keywords="dictionary, list, query, filter, automation, verification, testing, qa",
)