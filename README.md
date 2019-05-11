
> this file is generated by `$ m4 README.m4.md > README.md` command.

# pycro

> $ wc pycro \
   2503  5721 70090 pycro

list of contents:
- [introduction](#introduction)
- [usage example](#usage-example)
- [documentation](#documentation)
- [contributing](#contributing)

## introduction
Pycro is a python integrated macro preprocessor. It will interpret input texts
and generates a corresponding python code that will generate the intended
result, if we compile and execute that.

## usage example
imagine we have this `main.c`:
```c

#include <stdio.h>

//# names = ['Oliver', 'Jack', 'Harry', 'James', 'John']

int main()

	//@ for name in names:
	printf("Hello ${name}!\n");
	//@ end for
	return 0;


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
usage: ./pycro [OPTION]... [[--] FILE | -]...
Pycro FILEs. if no FILE or if FILE is '-', standard input is read. write to
standard output if no output specified.

Operation modes:
    -h, --help                      display this help and exit
    --version                       display pycro version and exit
    -a, --arrange-process           perform Sortable OPTIONs and FILEs
                                      according to their orders

Sortable options:
    -D, --define NAME[=VAR]         define NAME variable as having VALUE, or
                                      None
    -U, --undefine NAME             undefine NAME variable
    -S, --set KEY=VALUE             set KEY setting to VALUE
    -L, --lang LANGUAGE             set prefixes and suffixes for LANGUAGE
                                      specification
    -l, --load JSONFILE             load JSONFILE and update variables
    -I, --import MODULE             import MODULE to interpreter environment
    -- FILE                         read input FILE (don't treats '-' as
                                      standard input)

Common options:
    -n, --filter-name PATTERN       filter input FILEs by its name match
                                      shell PATTERN
    -p, --filter-path PATTERN       filter input FILEs by its path match
                                      shell PATTERN
    -N, --ignore-name PATTERN       ignore any input FILEs that its name match
                                      shell PATTERN
    -P, --ignore-path PATTERN       ignore any input FILEs that its path match
                                      shell PATTERN
    -f, --force                     overwrite existing files
    -r, --recursive                 pycro directories recursively
    -C, --clear-cache               first clear compiler cache
    -d, --dereference               follow symbolic links
    -o, --outfile OUTFILE           set output file to OUTFILE
    -O, --outfolder OUTFOLDER       set output folder to OUTFOLDER

Known language specifications:
    c, cpp, html, java, javascript, markdown, perl, python

Setting keys:
    mp, macro_prefix                macro line prefix
    ms, macro_suffix                macro line suffix

    sp, statement_prefix            statement line prefix
    ss, statement_suffix            statement line suffix

    cp, comment_prefix              comment line prefix
    cs, comment_suffix              comment line suffix

    vp, variable_prefix             variable substitution prefix
    vs, variable_suffix             variable substitution suffix

    ep, evaluation_prefix           evaluation substitution prefix
    es, evaluation_suffix           evaluation substitution suffix
```

## contributing

__notes:__

- first take look at the [makefile](makefile).

__todos:__

in `pycro`:
```
231: # TODO: remove debugging codes on final release
1386: # TODO: complete _generator_include()
1417: # TODO: write _generate_load()
1444: # TODO: add 'include' when ready
1448: # TODO: add 'load' when ready
1845: # TODO: write _include_function
1895: # TODO: write _load_function
1955: # TODO: complete __apply_config_filters
2299: # TODO: walk into directories
2325: # TODO: complete arranged performace
2354: # TODO: complete multiprocessing
2397: # TODO: write '--outfile', '--outfolder' functionality
```

