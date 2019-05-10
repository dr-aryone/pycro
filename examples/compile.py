#!/usr/bin/python3

import sys
import pycro

if __name__ == '__main__':

    if len(sys.argv) != 2:
        print(
            'usage: {} <FILE>'.format(
                sys.argv[0],
                file=sys.stderr,
            )
        )
        sys.exit(1)

    _file = sys.argv[1]

    env = pycro.ExecutorEnvironment()

    with open(_file) as infile:

        code_object = pycro.compile_generated_code(infile.read(), infile.name)

        pycro.execute_code_object(
                code_object,
                sys.stdout,
                env,
                )

