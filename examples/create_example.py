#!/usr/bin/python3

import sys

sys.path.append('..')

import pycro

def generate(infile, outfile):

    env = pycro.CompilerEnvironment(
        **pycro.__language_specifications['python']
    )

    pycro.generate_code(infile, outfile, env)

def main():

    if len(sys.argv) != 3:
        print("""\
usage: {0} g[enerate] [FILE]
       {0} c[ompile] [FILE]
""".format(sys.argv[0]))
        sys.exit(0)

    if sys.argv[1] in ('g', 'generate'):

        with open(sys.argv[2]) as infile:
            generate(infile, sys.stdout)

if __name__ == '__main__':
    main()
