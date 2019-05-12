#!/usr/bin/python3

import pycro

env = pycro.CompilerEnvironment(language = 'c')

with open('main.c') as infile:
    with open('main.c.py', 'w') as outfile:
        pycro.generate_code(infile, outfile, env)

