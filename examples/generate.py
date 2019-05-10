#!/usr/bin/python3

import sys
import pycro

if __name__ == '__main__':

    if len(sys.argv) != 3:
        print(
            'usage: {} <LANG> <FILE>'.format(
                sys.argv[0], 
                file=sys.stderr,
            )
        )
        sys.exit(1)

    lang, _file = sys.argv[1:]

    env = pycro.CompilerEnvironment(
            **pycro.__language_specifications[lang],
            )

    with open(_file) as infile:
        pycro.generate_code(infile, sys.stdout, env)

