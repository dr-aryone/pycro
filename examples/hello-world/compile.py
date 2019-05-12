#!/usr/bin/python3

import pycro

env = pycro.ExecutorEnvironment()

with open('main.c.py') as infile:
    with open('_main.c', 'w') as outfile:

        code_object = pycro.compile_generated_code(infile.read(), infile.name)

        pycro.execute_code_object(code_object, outfile, env)

