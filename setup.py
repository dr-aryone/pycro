
import sys

sys.path.append('package')

import setuptools
import pycro

def read_file(path):
    with open(path) as infile:
        return infile.read()

setuptools.setup(
        name = "pycro",
        version = ".".join(map(str, pycro.VERSION)),

        author = "Mohammad Amin Khakzadan",
        author_email = "mak12776@gmail.com",

        license = "WTFPL",

        description = "A python integrated macro preprocessor",
        long_desccription = read_file("README.md"),
        long_desccription_content_type = "text/markdown",

        classifiers = [
            "Development Status :: 2 - Pre-Alpha",

            "Topic :: Text Processing",
            ],

        keywords = "macro-preprocessor code-generator pycro",

        project_urls = {
            # TODO: add "Home Page" or "Documentation"
            "Source": "https://github.com/mak12776/pycro",
            },

        packages = [
                "pycro",
            ]

        )

