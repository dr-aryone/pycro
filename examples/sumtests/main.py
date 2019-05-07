#!/usr/bin/python3

import timeit

#@ divert 'code'

from itertools import accumulate
from random import choice

functions = {
        'func1': "sum(map(len, map(str, range({m}))))",
        'func2': "sum(accumulate(range({m})))"
        'func3': "sum(map(ord, " + 
                 "choice(string.ascii_letters) for i in range({m})))"
        }

for name in functions:
    functions[name] = functions[name].format(100)

#@ divert
## exec(__pipes__['code'].getvalue())

#@ for name, job in functions.items():
def ${name}():
	return ${job}
#@ end for

