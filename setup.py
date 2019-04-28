
import sys

import setuptools
import pycro

def read_file(path):
    with open(path) as infile:
        return infile.read()

setuptools.setup(
        # name & version
        name = "pycro",
        version = ".".join(map(str, pycro.VERSION)),

        # author
        author = "Mohammad Amin Khakzadan",
        author_email = "mak12776@gmail.com",

        # license
        license = "WTFPL",

        # descriptions
        description = "A python integrated macro preprocessor",
        long_description = read_file("README.md"),
        long_description_content_type = "text/markdown",

        # classifiers, keywords, urls
        classifiers = [
            "Development Status :: 2 - Pre-Alpha",

            "Topic :: Text Processing",
            "Topic :: Software Development :: Code Generators",
            ],

        keywords = "macro-preprocessor code-generator pycro",

        project_urls = {

            # TODO: add "Home Page" or "Documentation"
            "Source": "https://github.com/mak12776/pycro",

            },


        # specify modules
        packages = [],
        py_modules = ['pycro'],


        # install requirements
        install_requires = [],

        # python requires
        python_requires = '~=3.0',

        # package data like: docs, ...
        package_data = {},

        # data files:
        # a list of (directory, <list of files>) that each file in
        # <list of files> will be copy in: `sys.prefix + directory`
        data_files = [],

        # entry points
        entry_points = {
                'console_scripts': [
                    'pycro=pycro:main',
                ],
            },

        )

