
import sys

sys.path.append('package')

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
        long_desccription = read_file("README.md"),
        long_desccription_content_type = "text/markdown",

        # other settings
        
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

        packages = [],
        py_modules = ['pycro'],

        )

