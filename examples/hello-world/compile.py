#!/usr/bin/python3

import pycro

env = ExecutorEnvironment()

with open('main.c.py') as infile:
    with open('_main.c', 'w') as outfile:
        pycro.execute_code_object(infile, outfile, env)

