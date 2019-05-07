
> this file is generated by `$ m4 README.m4.md > README.md` command.

# pycro

> $ wc pycro \
   2348  5454 65486 pycro

list of contents:
- [introduction](#introduction)
- [usage example](#usage-example)
- [documentation](#documentation)

## introduction
Pycro is a python integrated macro preprocessor. It will interpret input texts
and generates a corresponding python code that will generate the intended
result, if we compile and execute that.

## usage example
imagine we have this `main.c`:
```python
#!/usr/bin/python3

import timeit

#@ divert 'code'

from itertools import accumulate
from random import choice

functions = 
        'func1': "sum(map(len, map(str, range({m}))))",
        'func2': "sum(accumulate(range({m})))"
        'func3': "sum(map(ord, " + 
                 "choice(string.ascii_letters) for i in range({m})))"
        

for name in functions:
    functions[name] = functions[name].100

#@ divert
## exec(__pipes__['code'].getvalue())

#@ for name, job in functions.items():
def $name():
	return $job
#@ end for

```

## documentation
- [How pycro works](#How-pycro-works)
- [API](#API)
- [command line interface](#command-line-interface)

### How pycro works
> coming soon

### API
> coming soon ...

### command line interface
__`$ pycro --help`__:
```
```

## contributing
__notes:__
- first take look at the [makefile](makefile).

__todos:__

in `pycro`:
```
229: # TODO: remove debugging codes on final release
1372: # TODO: complete _generator_include()
1403: # TODO: write _generate_load()
1430: # TODO: add 'include' when ready
1434: # TODO: add 'load' when ready
1824: # TODO: write _include_function
1863: # TODO: write _load_function
1923: # TODO: complete __apply_config_filters
2223: # TODO: walk into directories
2252: # TODO: write '--outfile', '--outfolder' functionality
2258: # TODO: complete arranged performace
2294: # TODO: complete multiprocessing
```


