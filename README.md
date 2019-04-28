
# pycro

> $wc pycro
 2432  5611 67886 pycro

list of contents:
- [introduction](#introduction)
- [usage example](#usage-example)
- [documentation](#documentation)

## introduction
Pycro is a python integrated macro preprocessor. It will interpret input texts
and generates a corresponding python code that will generate the intended
result, if we compile and execute that.

## usage example
> TODO

## documentation

- [API](#API)
- [command line interface](#command-line-interface)

### module API

### command line interface
__pycro --help__:
```
usage: ./pycro [OPTION]... [[--] FILE | -]...
Pycro FILEs to standard output. if no FILE or if FILE is '-', standard input is
read.

Operation modes:
    -h, --help                      display this help and exit
    --version                       display version and exit
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
    -o, --outfile OUTFILE           set output file to OUTFILE
    -O, --outfolder OUTFOLDER       set output folder to OUTFOLDER

Known language specifications:
    c, cpp, html, java, javascript, perl, python

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

