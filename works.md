
TODOs:
- '-o, --outfile', '-O, --outfolder' options functionalities.
- write main without multiprocessing
- write __walk_files function

DOING:
- None

DONEs:
- '-n, --filter-name' and '-P, --filter-name' options.
- add __argv__ variable
- write __all__ variable
- add __version__ variable
- '-N, --ignore-name' and '-P, --ignore-path' options

INTERESTs:
- None

ON_RELEASE:
- remove debuging codes



# Some notes:
# NOTE: '(?=(...))\1' works like atomic groups in other languages,
#       e.g: in perl: '(?>...)'.
#
# TODO: using re for matching for macros, statement, ... is slow, may be we
#       can do something like this:
#
#   line = line.strip(_SPACE_CHARS)
#   if line.startswith(prefix) and line.endswith(suffix):
#       ...
#
# WARNING: if we use the above mechanism, evey line that startswith(prefix) and
#          endswith(suffix) will treated as macros, statement, ...
#
# DONE: test speed of both ways:
#       speed of using str.startswith & str.endswith is faster.


# if '-O, --outfolder OUTFOLDER' specified:

#   if there is just one input folder:
#       pycro input folder to output folder

#       example:

#       $ tree src
#       src
#       +--- main.c
#       +--- buffer.c
#
#       $pycro src/ -O new_src/
#
#       $ tree new_src/
#       new_src
#       +--- main.c
#       +--- buffer.c

#   if there is more than one input folder or file:
#       pycro inputs to output folder

#       example:

#       $ tree src
#       src
#       +--- main.c
#       +--- buffer.c
#
#       $ tree lib
#       lib
#       +--- lib.c
#       +--- lib.h
#
#       $pycro src/ -O new_src/
#
#       $ tree new_src/
#       new_src
#       +--- src
#            +--- main.c
#            +--- buffer.c
#       +--- lib
#            +--- lib.c
#            +--- lib.h

# if '-o, --outfile OUTFILE' specified:
#   pycro all files into OUTFILE

