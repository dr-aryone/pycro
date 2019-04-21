#!/usr/bin/python3
# -*- coding: utf-8 -*-


#              DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE
#                      Version 2, December 2004
#
#   Copyright (C) 2019 Mohammad Amin Khakzadan <mak12776@gmail.com>
#
#   Everyone is permitted to copy and distribute verbatim or modified
#   copies of this license document, and changing it is allowed as long
#   as the name is changed.
#
#              DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE
#     TERMS AND CONDITIONS FOR COPYING, DISTRIBUTION AND MODIFICATION
#
#     0. You just DO WHAT THE FUCK YOU WANT TO.


# --- modules ---

import sys
import os
import io
import re
import collections
import inspect
import marshal
import pickle
import subprocess
import configparser
import shutil
import fnmatch
import types

import queue
import multiprocessing
import signal

# --- exit error code ---

# NOTE: cross-python-version flags
_EXIT_ERROR = 1
_EXIT_FATAL_ERROR = 2
_EXIT_SUCCESS = 0
_EXIT_ARGUMENT_ERROR = -1

# --- some initial utilities ---

def __print_error(line, file = sys.stdout):
    print('pycro: error:', line, file=file)

# --- better main exception handling ---

def __print_source(index = 0, context = 1, indent=False, file = sys.stdout):
    if context <= 0:
        return
    frame_info = inspect.stack(context)[index + 1]
    start_lnum = frame_info.lineno - (context // 2)
    num_width = len(str(frame_info.lineno + ((context + 1) // 2)))
    for n, line in enumerate(frame_info.code_context):
        print('{0:>{2}} {1}'.format(n + start_lnum, line, num_width), end='')

def __create_error_function(exception):
    def __error_function(error):
        if __name__ == '__main__':
            __print_error(error)
            __print_source(1, context=5, file=sys.stderr)
            sys.exit(_EXIT_FATAL_ERROR)

        else:
            raise exception(error)
    return __error_function

__not_implemented = __create_error_function(NotImplementedError)
__import_error = __create_error_function(ImportError)

if sys.version_info[0] == 3:
    import builtins

elif sys.version_info[0] == 2:
    import __builtins__ as builtins

else:
    __import_error(
            "No module named `builtins` for your python version: {}".format(
                ','.join(n for n in sys.version_info[:3]),
            )
        )


# --- home directory & cache folder ---

if sys.platform.startswith('linux') or sys.platform.startswith('freebsd'):
    _HOME_DIRECTORY = os.environ['HOME']

elif sys.platform == 'win32':
    _HOME_DIRECTORY = os.environ['USERPROFILE']

else:
    raise NotImplemented('implement _HOME_DIRECTORY '
            'for your platform: {}'.format(sys.platform))

_CACHE_FOLDER_NAME = '.pycro_cache'


_CONFIG_FILE_NAME = '.pycro'

_DEFAULT_STDIN_FILENAME = '<stdin>'


# --- patterns ---

_MACRO_PATTERN = r'\s*(?P<macro>{macros})\s*(?P<args>.*?)\s*'

_VARIABLE_NAME_PATTERN = r'[a-zA-Z_][a-zA-Z_0-9]*'
_VARIABLE_NAME_RE = re.compile(_VARIABLE_NAME_PATTERN)

_VARIABLE_PATTERN = r'{prefix}(?P<name>{pattern}){suffix}'
_EVALUATION_PATTERN = r'{prefix}\s*(?P<eval>.*?)\s*{suffix}'



# --- default variable value & space chars ---

_DEFAULT_VARIABLE_VALUE = None
_SPACE_CHARS = ' \t\n'


# --- pycro default variable & function names ---

_DEFAULT_OUTFILE_VARIABLE_NAME = '__outfile__'

_DEFAULT_PIPES_VARIABLE_NAME = '__pipes__'
_DEFAULT_DIVERT_FUNCTION_NAME = '__divert__'
_DEFAULT_UNDIVERT_FUNCTION_NAME = '__undivert__'

_DEFAULT_RUN_FUNCTION_NAME = '__run__'

_DEFAULT_INCLUDE_FUNCTION_NAME = '__include__'
_DEFAULT_PLACE_FUNCTION_NAME = '__place__'

_DEFAULT_VERSION_VARIABLE_NAME = '__version__'

_DEFAULT_COMMAND_VARIABLE_NAME = '__command__'

# --- other settings ---

_CACHE_FILE_MAGIC_NUMBER = b'.pycroche'

_COMPILE_FLAGS = 0
_OPTIMIZE_LEVEL = -1
_MARSHAL_VERSION = 4
_PICKLE_VERSION = pickle.HIGHEST_PROTOCOL

try:
    _MAX_PROCESS_NUMBER = len(os.sched_getaffinity(0))

except AttributeError:
    _MAX_PROCESS_NUMBER = os.cpu_count()

if _MAX_PROCESS_NUMBER <= 0:
    raise BaseException('invalid _MAX_PROCESS_NUMBER value: {}'.format(
        _MAX_PROCESS_NUMBER))

_SIZE_LEN = 4

# --- debuging code ---

if __debug__:
    from pprint import pprint

    def print_line(title = None, fill='-', width=80, lside=' ', rside=' '):
        if title:
            print('{:{fill}^{width}}'.format(
                    lside + title.strip() + rside,
                    width=width,
                    fill=fill,
                    )
                )
        else:
            print(fill * width)

    def rprint(*objects, sep=', ', end='\n', file=sys.stdout):
        if objects:
            file.write(repr(objects[0]))
            for obj in objects[1:]:
                file.write(sep)
                file.write(repr(obj))
        file.write(end)

    def print_options(options):
        # jobs
        print_line('jobs', width=40)
        for job in options.jobs:
            print(
                    '{}{}'.format(
                        ' ' * 4,
                        ', '.join([ __job_flag_name(job[0]),
                            *map(repr, job[1:]) ]),
                    )
                )
        # name ignores
        print_line('name ignores', width=40)
        for pattern in options.name_ignores:
            print('{}{!r}'.format(' ' * 4, pattern))
        # path ignores
        print_line('path ignores', width=40)
        for pattern in options.path_ignores:
            print('{}{!r}'.format(' ' * 4, pattern))
        # switchs
        print_line('switchs', width=40)
        switchs = options.switchs
        for flag in (
                _ARRANGE_PROCESS_FLAG,
                _FORCE_FLAG,
                _RECURSIVE_FLAG,
                _CLEAR_CACHE_FLAG,):
            if switchs & flag:
                switchs &= ~flag
                print('{}{}'.format(' ' * 4, __bit_flag_name(flag)))
        if switchs:
            print("error: some bits on switchs is on")
        # outfile & outfolder
        print_line('output', width=40)
        if options.output is not None:
            print(
                '{}{}'.format(
                    ' ' * 4,
                    ', '.join(
                        [ __output_flag_name(options.output[0]),
                            *map(repr, options.output[1:]) ]
                    )
                )
            )


# --- utilities ---

__joinpath = os.path.join
__abspath = os.path.abspath
__normpath = os.path.normpath
__realpath = os.path.realpath
__splitpath = os.path.split
__isdir = os.path.isdir
__isfile = os.path.isfile

if sys.version_info >= (3, 4):
    __fullmatch = re._pattern_type.fullmatch

else:
    def __fullmatch(pattern, string):
        m = pattern.match(string)
        if m and m.end() == len(string):
            return m

if sys.version_info[0] == 3:
    _fdopen = open

elif sys.version_info[0] == 2:
    _fdopen = os.fdopen

else:
    raise NotImplemented(
            "implement _fdopen function for your python version: {}".format(
                ','.join(n for n in sys.version_info[:3]),
            )
        )

def _create_pipe(read_mode = 'rt', write_mode = 'wt'):
    return map(_fdopen, zip(os.pipe(), (read_mode, write_mode)))

class dotdict(dict):
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

class FileStructError(Exception):
    pass

def __prettify_items(items, indent = '    ', width = 80):
    if not items:
        return ''

    lines = collections.deque([indent + items[0]])

    for item in items[1:]:
        if len(lines[-1]) + len(item) + 1 >= width:
            lines[-1] += ','
            lines.append(indent + item)

        else:
            lines[-1] += ', ' + item

    return '\n'.join(lines)

# *** binary file operations ***

# --- objects ---

def _write_pickle_object(outfile, obj):
    _buffer = pickle.dumps(obj, _PICKLE_VERSION, fix_imports=False)
    _write_size(outfile, len(_buffer))
    outfile.write(_buffer)

def _read_pickle_object(outfile, obj):
    _buffer_size = _read_size(infile)
    _buffer = infile.read(_buffer_size)
    if len(_buffer) != _buffer_size:
        raise EOFError("End of file while reading pickle object")
    return pickle.loads(_buffer, fix_imports=False)

def _write_marshal_object(outfile, obj):
    _buffer = marshal.dumps(obj, _MARSHAL_VERSION)
    _write_size(outfile, len(_buffer))
    outfile.write(_buffer)

def _read_marshal_object(infile):
    _buffer_size = _read_size(infile)
    _buffer = infile.read(_buffer_size)
    if len(_buffer) != _buffer_size:
        raise EOFError("End of file while reading object")
    return marshal.loads(_buffer)

# --- code objects ---

_write_code_object = _write_marshal_object

def _read_code_object(infile):
    code_object = _read_marshal_object(infile)
    if not isinstance(code_object, types.CodeType):
        raise FileStructError("invalid object type returned by marshal "
                "while reading code object")
    return code_object

# --- integers ---

def _write_int(outfile, integer, size = 1):
    outfile.write(integer.to_bytes(size, 'big', signed = True))

def _write_uint(outfile, integer, size = 1):
    outfile.write(integer.to_bytes(size, 'big', signed = False))

def _read_int(infile, size = 1):
    _buffer = infile.read(size)
    if len(_buffer) != size:
        raise EOFError(
                "End of file while reading {} byte integer".format(size))
    return int.from_bytes(_buffer, 'big', signed = True)

def _read_uint(infile, size = 1):
    _buffer = infile.read(size)
    if len(_buffer) != size:
        raise EOFError(
                "End of file while reading {} byte integer".format(size))
    return int.from_bytes(_buffer, 'big', signed = False)

# --- size type ---

def _write_size(outfile, size):
    outfile.write(size.to_bytes(_SIZE_LEN, 'big', signed=False))

def _read_size(infile):
    _buffer = infile.read(_SIZE_LEN)
    if len(_buffer) != _SIZE_LEN:
        raise EOFError("End of file while reading size")
    return int.from_bytes(_buffer, 'big', signed = False)

# --- strings ---

def _write_string(outfile, string):
    _buffer = string.encode('utf-8')

    while len(_buffer) >= 0xFFFF:

        outfile.write(b'\xFF\xFF')
        outfile.write(_buffer[:0xFFFF])
        _buffer = _buffer[0xFFFF:]

    outfile.write(len(_buffer).to_bytes(2, 'big', signed = False))
    outfile.write(_buffer)

def _read_string(infile):
    _buffer = infile.read(2)
    if len(_buffer) != 2:
        raise EOFError("End of file while reading string")
    _buffer_size = int.from_bytes(_buffer, 'big', signed = False)

    _buffer = infile.read(_buffer_size)
    if len(_buffer) != _buffer_size:
        raise EOFError("End of file while reading string")
    _result = bytearray(_buffer)

    while _buffer_size == 0xFFFF:
        _buffer = infile.read(2)
        if len(_buffer) != 2:
            raise EOFError("End of file while reading string")
        _buffer_size = int.from_bytes(_buffer, 'big', signed = False)

        _buffer = infile.read(_buffer_size)
        if len(_buffer) != _buffer_size:
            raise EOFError("End of file while reading string")

        _result += _buffer

    return _result.decode('utf-8')

# --- Queue & Workers classes ---

def __queue_maker(write_object, read_object):
    class Queue:
        def __init__(self):
            self._lock = multiprocessing.RLock()
            self._size = multiprocessing.Value(ctypes.c_ulong, 0, lock=False)
            self._pipe_r, self_pipe_w = itertools.starmap(
                _fdopen,
                zip(os.pipe(), ('rb', 'wb'), (0, 0))
            )

        def qsize():
            return self._size.value

        def put(self, obj):
            with self._lock:
                self._size.value += 1
                write_object(self._pipe_w, obj)

        def get(self):
            with self._lock:
                if self._size.value:
                    self._size.value -= 1
                    return read_object(self,_pipe_r)
                else:
                    raise queue.Empty()
    return Queue

MarshalQueue = __queue_maker(_write_marshal_object, _read_marshal_object)

PickleQueue = __queue_maker(_write_pickle_object, _read_pickle_object)

class Workers:
    def __init__(self, func, workers_number=None):

        if args is None:
            args = ()

        if kwargs is None:
            kwargs = kwargs

        if workers_number is None:
            workers_number = os.sched_getaffinity(0)

        def process_init(
                inputs_queue,
                outputs_queue,
                errors_queue,
                workers_pid,
                *args,
                **kwargs
                ):
            try:

                while True:
                    try:
                        inputs_queue.get()
                    except queue.Empty:
                        break

                    try:
                        result = func(item, *args, **kwargs)
                    except BaseException as e:
                        errors_queue.put(e)
                        # TODO: signal other workers

                    outputs_queue.put(result)
            except KeyboardInterrupt:
                pass

        self._workers_number = workers_number
        self._workers = [None] * workers_number
        workers_pid = [None] * (workers_number + 1)

        workers_pid[0] = multiprocessing.current_process().pid

        # --- create Process and save its pid ---
        for i in range(workers_number):
            worker = multiprocessing.Process(
                    target = process_init,
                    name = '{} worker-{}'.format(func.__name__, i),
                    )

            workers_pid[i] = worker.pid

            workers[i] = worker

        self._outputs_queues = [None] * workers_number
        self._errors_queue = None

        # --- now set args, kwargs of each process ---
        for i in range(workers_number):
            self._outputs_queues[i] = MarshalQueue()

            self._workers[i]._args = (
                    self._inputs_queues[i],
                    self._outputs_queues[i],
                    errors_queue,
                    workers_pid,
                    ) + args

            self._workers[i]._kwargs = {kwargs}

    def start(self, inputs):

        inputs_len = len(inputs) // self._max_workers
        remaining = (inputs_len * self._max_workers) - inputs_len

        start_i = 0
        if remaining:
            end_i = inputs_len + 1
            remaining -= 1
        else:
            end_i = inputs_len

        for i in range(self._max_workers):
            worker = process_init(
                    inputs[start_i:end_i],
                    self._outputs_queue,
                    *args, **kwargs)


            self._workers.append(worker)

            worker.start()

    def free_workers(self):
        i = 0
        while i < len(self._workers):
            if not self._workers.is_alive():
                del self._workers[i]

# --- command line help & options ---

VERSION = collections.namedtuple('VersionType', ['major', 'minor', 'micro']) \
        (0, 0, 0)

__USAGE = "usage: {} [OPTION]... [[--] FILE | -]..."
__HELP = """\
Pycro FILEs to standard output. if no FILE or if FILE is '-', standard input is
read.

Operation modes:
    -h, --help                      display this help and exit
    --version                       display version and exit
    -a, --arrange-process           perform Sortable OPTIONs and FILEs
                                      according to their orders

Sortable options:
    -D, --define NAME[=VAR]         define NAME variable as having VALUE, or
                                      {default_variable_value}
    -U, --undefine NAME             undefine NAME variable
    -S, --set KEY=VALUE             set KEY setting to VALUE
    -L, --lang LANGUAGE             set prefixes and suffixes for LANGUAGE
                                      specification
    -l, --load JSONFILE             load JSONFILE and update variables
    -I, --import MODULE             import MODULE to interpreter environment
    -- FILE                         read input FILE (don't treats '-' as
                                      standard input)

Common options:
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
{language_specifications}

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
"""

def __print_help():
    print(__HELP.format(
            default_variable_value = _DEFAULT_VARIABLE_VALUE,
            language_specifications =
                __prettify_items(sorted(__language_specifications.keys())),
        ),
        end = '')

__TRY = "try '{} --help' for more information."

def __print_try(name, file = sys.stderr):
    print(__TRY.format(name), file=sys.stderr)

__VERSION = "pycro v{}.{}.{}"

def __print_version():
    print(__VERSION.format(*VERSION))

# TODO: write '--outfile', '--outfolder' functionality

__setting_keys = {
    'mp', 'macro_prefix'
    'ms', 'macro_suffix',

    'sp', 'statement_prefix',
    'ss', 'statement_suffix',

    'cp', 'comment_prefix',
    'cs', 'comment_suffix',

    'vp', 'variable_prefix',
    'vs', 'variable_suffix',

    'ep', 'evaluation_prefix',
    'es', 'evaluation_suffix',
}

__language_specifications = {
    **dict.fromkeys(
        ['c', 'cpp', 'java', 'javascript'],
        dotdict(
            macro_prefix =          '//@',
            macro_suffix =          '',

            statement_prefix =      '//#',
            statement_suffix =      '',

            comment_prefix =        '//%',
            comment_suffix =        '',

            variable_prefix =       '${',
            variable_suffix =       '}',

            evaluation_prefix =     '$${{',
            evaluation_suffix =     '}}',
        ),
    ),

    **dict.fromkeys(
        ['perl', 'python'],
        dotdict(
            macro_prefix =          '#@',
            macro_suffix =          '',

            statement_prefix =      '##',
            statement_suffix =      '',

            comment_prefix =        '#%',
            comment_suffix =        '',

            variable_prefix =       '${',
            variable_suffix =       '}',

            evaluation_prefix =     '$${{',
            evaluation_suffix =     '}}',
        ),
    ),

    **dict.fromkeys(
        ['html'],
        dotdict(
            macro_prefix =          '<!--@',
            macro_suffix =          '-->',

            statement_prefix =      '<!--#',
            statement_suffix =      '-->',

            comment_prefix =        '<!--%',
            comment_suffix =        '-->',

            variable_prefix =       '${',
            variable_suffix =       '}',

            evaluation_prefix =     '$${{',
            evaluation_suffix =     '}}',
        ),
    )
}

# --- switchs bit flags ---

# NOTE: cross-python-version flags
_ARRANGE_PROCESS_FLAG =     0x01
_RECURSIVE_FLAG =           0x02
_CLEAR_CACHE_FLAG =         0x04
_FORCE_FLAG =               0x08

# --- jobs unique flags ---

# NOTE: cross-python-version flags
_IMPORT_FLAG =              0x01
_LANG_FLAG =                0x02
_JSONFILE_FLAG =            0x03

_INPUT_FLAG =               0x04

_DEFINE_FLAG =              0x05
_UNDEFINE_FLAG =            0x06
_SETTING_FLAG =             0x07

# used in __parse_argv:
_IGNORE_NAME_FLAG =         0x0a
_IGNORE_PATH_FLAG =         0x0b

# used in __parse_argv:
_OUTFILE_FLAG =             0x0c
_OUTFOLDER_FLAG =           0x0d

# *** argument parser ***

if __debug__:

    def __bit_flag_name(flag):
        if flag == _ARRANGE_PROCESS_FLAG:
            return '_ARRANGE_PROCESS_FLAG'

        elif flag == _RECURSIVE_FLAG:
            return '_RECURSIVE_FLAG'

        elif flag == _CLEAR_CACHE_FLAG:
            return '_CLEAR_CACHE_FLAG'

        elif flag == _FORCE_FLAG:
            return '_FORCE_FLAG'

        else:
            raise ValueError('unknown flag: {}'.format(flag))

    def __job_flag_name(flag):
        if flag == _IMPORT_FLAG:
            return '_IMPORT_FLAG'

        elif flag == _LANG_FLAG:
            return '_LANG_FLAG'

        elif flag == _JSONFILE_FLAG:
            return '_JSONFILE_FLAG'

        elif flag == _INPUT_FLAG:
            return '_INPUT_FLAG'

        elif flag == _DEFINE_FLAG:
            return '_DEFINE_FLAG'

        elif flag == _UNDEFINE_FLAG:
            return '_UNDEFINE_FLAG'

        elif flag == _SETTING_FLAG:
            return '_SETTING_FLAG'

        elif flag == _OUTFOLDER_FLAG:
            return '_OUTFOLDER_FLAG'

        elif flag == '_IGNORE_NAME_FLAG':
            return '_IGNORE_NAME_FLAG'

        else:
            raise ValueError('unknown flag: {}'.format(flag))

    def __output_flag_name(flag):
        if flag == _OUTFILE_FLAG:
            return '_OUTFILE_FLAG'

        elif flag == _OUTFOLDER_FLAG:
            return '_OUTFOLDER_FLAG'

        else:
            raise ValueError('unknown flag: {}'.format(flag))

# HACK: some interesting options:
#       -i, --isolate                   isolate preprocessing each input file

def __parse_argv(argv):
    result = dotdict(
            jobs = collections.deque(),
            name_ignores = collections.deque(),
            path_ignores = collections.deque(),
            switchs = 0,
            output = None,
            )

    next_args = collections.deque()

    has_output = False
    input_number = 0

    for i, arg in enumerate(argv[1:]):

        # --- read next arg ---
        # ---------------------

        if next_args:
            next_arg = next_args.popleft()
            if next_arg[0] in (_IMPORT_FLAG, _LANG_FLAG, _JSONFILE_FLAG):
                result.jobs.append((next_arg[0], arg))

            elif next_arg[0] == _INPUT_FLAG:
                result.jobs.append( [_INPUT_FLAG, arg] )
                input_number += 1

            elif next_arg[0] == _OUTFILE_FLAG:

                # previously (duplicate '-o, --outfile' or '-O, --outfolder')
                # checked
                result.output = (_OUTFILE_FLAG, arg)

            elif next_arg[0] == _OUTFOLDER_FLAG:

                # previously (duplicate '-o, --outfile' or '-O, --outfolder')
                # checked
                result.output = (_OUTFOLDER_FLAG, arg)

            elif next_arg[0] == _DEFINE_FLAG:

                # --- parsing definition ---
                arg = arg.split('=', maxsplit=1)
                if len(arg) != 2:
                    __print_error(
                        "{!r} option requires a 'NAME=VALUE' pair.".format(
                            next_arg[1],
                        )
                    )
                    __print_try(argv[0])
                    return 1

                # --- checking variable name pattern ---
                if not __fullmatch(_VARIABLE_NAME_RE, arg[0]):
                    __print_error(
                        "invalid variable name: {!r} for option: {!r}".format(
                            arg[0],
                            next_arg[1],
                        )
                    )
                    __print_try(argv[0])
                    return 1

                result.jobs.append((_DEFINE_FLAG, arg))

            elif next_arg[0] == _UNDEFINE_FLAG:

                # --- parsing undefinition ---
                if not __fullmatch(_VARIABLE_NAME_RE, arg):
                    __print_error(
                        "invalid variable name: {!r} for option: {!r}".format(
                            arg,
                            next_arg[1],
                        )
                    )
                    __print_try(argv[0])
                    return 1

                result.jobs.append((_UNDEFINE_FLAG, arg))

            elif next_arg[0] == _SETTING_FLAG:

                # --- parsing setting ---
                arg = arg.split('=', maxsplit=1)
                if len(arg) != 2:
                    __print_error(
                        "{!r} option requires a 'KEY=VALUE' pair.".format(
                            next_arg[1],
                        )
                    )
                    __print_try(argv[0])
                    return 1

                # --- checking valid keys ---
                if arg[0] not in __setting_keys:
                    __print_error(
                        "invalid setting key: {!r} for option: {!r}".format(
                            arg[0],
                            next_arg[1],
                        )
                    )
                    __print_try(argv[0])
                    return 1

                result.jobs.append((_SETTING_FLAG, arg))

            elif next_arg[0] == _IGNORE_NAME_FLAG:

                # --- append file name filter ---
                result.name_ignores.append(arg)

            elif next_arg[0] == _IGNORE_PATH_FLAG:

                # --- append file path filter ---
                result.path_ignores.append(arg)

            else:
                raise BaseException("unknown argument name pushed to "
                        "next_args: {}".format(next_arg))

            continue

        # empty argument
        if not arg:
            __print_error("empty argument: #{} argument".format(i + 1))
            __print_try(argv[0])
            return 1

        if arg[0] == '-':

            # append stdin as input
            if len(arg) == 1:
                result.jobs.append( [_INPUT_FLAG, sys.stdin] )
                input_number += 1
                continue

            if arg[1] == '-':

                # read next argument as input file name
                if len(arg) == 2:
                    next_args.append((_INPUT_FLAG, '--'))
                    continue

                option = arg[2:]

                # --- check long options ---
                # --------------------------

                # show help
                if option == 'help':
                    print(__USAGE.format(argv[0]))
                    __print_help()
                    return 0

                # show version
                elif option == 'version':
                    __print_version()
                    return 0

                # arrange performances
                elif option == 'arrange-process':
                    result.switchs |= _ARRANGE_PROCESS_FLAG

                # ignore file names
                elif option == 'ignore-name':
                    next_args.append((_IGNORE_NAME_FLAG, '--ignore-name'))

                # ignore file paths
                elif option == 'ignore-path':
                    next_args.append((_IGNORE_PATH_FLAG, '--ignore-path'))

                # force overwrite
                elif option == 'force':
                    result.switchs |= _FORCE_FLAG

                # read directories recursively
                elif option == 'recursive':
                    result.switchs |= _RECURSIVE_FLAG

                # clear cache
                elif option == 'clear-cache':
                    result.switchs |= _CLEAR_CACHE_FLAG

                # set output file
                elif option == 'outfile':
                    if has_output:
                        __print_error("more than one output specified by "
                                "option: {!r}".format(arg))
                        return 1
                    next_args.append((_OUTFILE_FLAG, '--outfile'))
                    has_output = True

                # set output folder
                elif option == 'outfolder':
                    if has_output:
                        __print_error("more than one output specified by "
                                "option: {!r}".format(arg))
                        return 1
                    next_args.append((_OUTFOLDER_FLAG, '--outfolder'))
                    has_output = True

                # define variable
                elif option == 'define':
                    next_args.append((_DEFINE_FLAG, '--define'))

                # undefine variable
                elif option == 'undefine':
                    next_args.append((_UNDEFINE_FLAG, '--undefine'))

                # change settings
                elif option == 'set':
                    next_args.append((_SETTING_FLAG, '--set'))

                # specify language
                elif option == 'lang':
                    next_args.append((_LANG_FLAG, '--lang'))

                # load json files
                elif option == 'load':
                    next_args.append((_JSONFILE_FLAG, '--load'))

                # import module
                elif option == 'import':
                    next_args.append((_IMPORT_FLAG, '--import'))

                else:
                    __print_error("unknown option: '{}'".format(arg))
                    __print_try(argv[0])
                    return 1

            else: # if arg[1] == '-'
                for ch in arg[1:]:

                    # --- check short options ---
                    # ---------------------------

                    # show help
                    if ch == 'h':
                        print(__USAGE.format(sys.argv[0]))
                        __print_help()
                        return 0

                    # arrange performances
                    elif ch == 'a':
                        result.switchs |= _ARRANGE_PROCESS_FLAG

                    # ignore file names
                    elif ch == 'N':
                        next_args.append((_IGNORE_NAME_FLAG, '-N'))

                    # ignore file paths
                    elif ch == 'P':
                        next_args.append((_IGNORE_PATH_FLAG, '-P'))

                    # force overwrite
                    elif ch == 'f':
                        result.switchs |= _FORCE_FLAG

                    # read directories recursively
                    elif ch == 'r':
                        result.switchs |= _RECURSIVE_FLAG

                    # clear cache
                    elif ch == 'C':
                        result.switchs |= _CLEAR_CACHE_FLAG

                    # set output file
                    elif ch == 'o':
                        if has_output:
                            __print_error("more than one output specified by "
                                    "option: {!r}".format('-o'))
                            return 1
                        next_args.append((_OUTFILE_FLAG, '-o'))
                        has_output = True

                    # set output folder
                    elif ch == 'O':
                        if has_output:
                            __print_error("more than one output specified by "
                                    "option: {!r}".format('-O'))
                            return 1
                        next_args.append((_OUTFOLDER_FLAG, '-O'))
                        has_output = True

                    # define variable
                    elif ch == 'D':
                        next_args.append((_DEFINE_FLAG, '-D'))

                    # undefine variable
                    elif ch == 'U':
                        next_args.append((_UNDEFINE_FLAG, '-U'))

                    # change settings
                    elif ch == 'S':
                        next_args.append((_SETTING_FLAG, '-S'))

                    # specify language
                    elif ch == 'L':
                        next_args.append((_LANG_FLAG, '-L'))

                    # load json files
                    elif ch == 'l':
                        next_args.append((_JSONFILE_FLAG, '-l'))

                    # import module
                    elif ch == 'i':
                        next_args.append((_IMPORT_FLAG, '-I'))

                    else:
                        __print_error("unknown option: '{}'".format('-' + ch))
                        __print_try(argv[0])
                        return 1

        else: # (arg[0] != '-')
            result.jobs.append( [_INPUT_FLAG, arg] )
            input_number += 1

    if next_args:
        __print_error(
                "{!r} option requires an argument".format(next_args[0][1]))
        __print_try(argv[0])
        return 1

    if input_number == 0:
        result.jobs.append( [_INPUT_FLAG, sys.stdin] )

    result.jobs = list(result.jobs)
    result.name_ignores = list(result.name_ignores)
    result.path_ignores = list(result.path_ignores)
    return result

# *** errors ***

# NOTE: cross-python-version error values
_MACRO_REQUIRES = 1
_WITHOUT_PRECEDING = 2
_END_DOES_NOT_MATCH = 3
_UNTERMINATED_BLOCK = 4

class CompilerError(Exception):
    pass

# *** macros ***

# --- if macro ---

def _generate_if(args, outfile, env):
    if not args:
        raise CompilerError(_MACRO_REQUIRES, 'if', 'a condition')

    outfile.write('{}{} {}\n'.format(env.tabs(), 'if', args))
    env.indent += 1

    env.macro_stack.append('if')

# --- elif macro ---

def _generate_elif(args, outfile, env):
    if not args:
        raise CompilerError(_MACRO_REQUIRES, 'elif', 'a condition')

    if env.macro_stack and env.macro_stack[-1] in ('if', 'elif'):

        env.indent -= 1
        outfile.write('{}{} {}\n'.format(env.tabs(), 'elif', args))
        env.indent += 1

        env.macro_stack[-1] = 'elif'

    else:
        raise CompilerError(_WITHOUT_PRECEDING, 'elif', 'if/elif')

# --- for macro ---

def _generate_for(args, outfile, env):
    if not args:
        raise CompilerError(_MACRO_REQUIRES, 'for', 'an iterable statement')

    outfile.write('{}{} {}\n'.format(env.tabs(), 'for', args))
    env.indent += 1

    env.macro_stack.append('for')

# --- while macro ---

def _generate_while(args, outfile, env):
    if not args:
        raise CompilerError(_MACRO_REQUIRES, 'while', 'a condition')

    outfile.write('{}{} {}\n'.format(env.tabs(), 'while', args))
    env.indent += 1

    env.macro_stack.append('while')

# --- try macro ---

def _generate_try(args, outfile, env):
    outfile.write('{}{}:\n'.format(env.tabs, 'try'))
    env.indent += 1

    env.macro_stack.append('try')

# -- except macro ---

def _generate_except(args, outfile, env):
    if not args:
        raise CompilerError(_MACRO_REQUIRES, 'except', 'an expression')

    if env.macro_stack and env.macro_stack[-1] in ('try', 'except'):

        env.indent -= 1
        outfile.write('{}{} {}\n'.format(env.tabs(), 'except', args))
        env.indent += 1

        env.macro_stack[-1] = 'except'

    else:
        raise CompilerError(_WITHOUT_PRECEDING, 'except', 'try/except')

# --- finally macro ---

def _generate_finally(args, outfile, env):
    if env.macro_stack and env.macro_stack[-1] in ('try', 'except', 'else'):

        env.indent -= 1
        outfile.write('{}{}:\n'.format(env.tabs(), 'finally'))
        env.indent += 1

        env.macro_stack[-1] = 'finally'

    else:
        raise CompilerError(_WITHOUT_PRECEDING, 'finally', 'try/except/else')

# --- else macro ---

def _generate_else(args, outfile, env):
    if env.macro_stack and env.macro_stack[-1] in \
            ('if', 'elif', 'for', 'while', 'except'):

        env.indent -= 1
        outfile.write('{}{}:\n'.format(env.tabs(), 'else'))
        env.indent += 1

        env.macro_stack[-1] = 'else'

    else:
        raise CompilerError(_WITHOUT_PRECEDING,
                'else', 'if/elif/for/while/except')

# --- with macro ---

def _generate_with(args, outfile, env):
    if not args:
        raise CompilerError(_MACRO_REQUIRES, 'with', 'an expression')

    outfile.write('{}{} {}\n'.format(env.tabs(), 'with', args))
    env.indent += 1

    env.macro_stack.append('with')

# --- def macro ---

def _generate_def(args, outfile, env):
    if not args:
        raise CompilerError(_MACRO_REQUIRES, 'def', 'a function definition')

    outfile.write('{}{} {}\n'.format(env.tabs(), 'def', args))
    env.indent += 1

    env.macro_stack.append('def')

# --- end macro ---

def _generate_end(args, outfile, env):
    if not env.macro_stack:
        raise CompilerError(_WITHOUT_PRECEDING, 'end', 'if/for/while/...')

    last_macro = env.macro_stack.pop()

    if args:
        if args != last_macro:
            raise CompilerError(_END_DOES_NOT_MATCH, 'end', last_macro, args)

    env.indent -= 1

# --- divert macro ---

def _generate_divert(args, outfile, env):
    outfile.write(
        '{}{}({})\n'.format(
            env.tabs(),
            env.divert_function_name,
            args
        )
    )

# -- undivert macro ---

def _generate_undivert(args, outfile, env):
    outfile.write(
        '{}{}({})\n'.format(
            env.tabs(),
            env.undivert_function_name,
            args
        )
    )

# --- place macro ---

def _generate_place(args, outfile, env):
    if not args:
        raise CompilerError(_MACRO_REQUIRES, 'place', 'a filename')

    outfile.write(
        '{}{}({})\n'.format(
            env.tabs(),
            env.place_function_name,
            args,
        )
    )

# --- include macro ---

# TODO: complete _generator_include()

def _generate_include(args, outfile, env):
    if not args:
        raise CompilerError(_MACRO_REQUIRES, 'for', 'a filename')

    outfile.write(
        '{}{}({})\n'.format(
            env.tabs(),
            env.include_function_name,
            args,
        )
    )


# --- run macro ---

def _generate_run(args, outfile, env):
    if not args:
        raise CompilerError(_MACRO_REQUIRES, 'run', 'a command')

    outfile.write(
        '{}{}({})\n'.format(
            env.tabs(),
            env.run_function_name,
            args,
        )
    )

# --- load macro ---

# TODO: write _generate_load()

def _generate_load(args, outfile, env):
    pass

_default_code_generators = {
        'if': _generate_if,
        'elif': _generate_elif,

        'for': _generate_for,
        'while': _generate_while,

        'try': _generate_try,
        'except': _generate_except,
        'finally': _generate_finally,

        'else': _generate_else,
        'with': _generate_with,

        'def': _generate_def,
        'end': _generate_end,

        'divert': _generate_divert,
        'undivert': _generate_undivert,

        'place': _generate_place,
        # TODO: add 'include' when ready

        'run': _generate_run,

        # TODO: add 'load' when ready
}

class CompilerEnvironment:
    def __init__(
            self,

            code_generators = None,

            macro_prefix = '@',
            macro_suffix = '',

            statement_prefix = '#',
            statement_suffix = '',

            comment_prefix = '%',
            comment_suffix = '',

            variable_prefix = '${',
            variable_suffix = '}',

            evaluation_prefix = '$${{',
            evaluation_suffix = '}}',

            tab = '\t',
            indent = 0,

            # --- varaible names ---
            outfile_variable_name = _DEFAULT_OUTFILE_VARIABLE_NAME,

            pipes_varaible_name = _DEFAULT_PIPES_VARIABLE_NAME,
            divert_function_name = _DEFAULT_DIVERT_FUNCTION_NAME,
            undivert_function_name = _DEFAULT_UNDIVERT_FUNCTION_NAME,

            run_function_name = _DEFAULT_RUN_FUNCTION_NAME,

            include_function_name = _DEFAULT_INCLUDE_FUNCTION_NAME,
            place_function_name = _DEFAULT_PLACE_FUNCTION_NAME,

            compile_flags = _COMPILE_FLAGS,
            optimize_level = _OPTIMIZE_LEVEL,
            ):
        """intialize code generator environment"""

        self.code_generators = \
            code_generators or _default_code_generators.copy()

        self.macro_stack = collections.deque()


        # --- macro ---
        self.macro_prefix = macro_prefix
        self.macro_suffix = macro_suffix

        self.macro_re = re.compile(
            _MACRO_PATTERN.format(
                macros = '|'.join(macro for macro in self.code_generators),
            )
        )

        # --- statement ---
        self.statement_prefix = statement_prefix
        self.statement_suffix = statement_suffix

        # --- comment ---
        self.comment_prefix = comment_prefix
        self.comment_suffix = comment_suffix


        # --- evaluation & variable ---
        if (not variable_prefix) or (not variable_suffix):
            raise ValueError(
                    "variable_prefix & variable_suffix can't be empty")

        if (not evaluation_prefix) or (not evaluation_suffix):
            raise ValueError(
                    "evaluation_prefix & evaluation_suffix can't be empty")

        self.evaluation_variable_re = re.compile(
            _EVALUATION_PATTERN.format(
                prefix = re.escape(evaluation_prefix),
                suffix = re.escape(evaluation_suffix),
            ) + '|' +

            _VARIABLE_PATTERN.format(
                prefix = re.escape(variable_prefix),
                pattern = _VARIABLE_NAME_PATTERN,
                suffix = re.escape(variable_suffix),
            )
        )

        # --- variable names ---
        self.outfile_variable_name = outfile_variable_name

        self.pipes_varaible_name = pipes_varaible_name
        self.divert_function_name = divert_function_name
        self.undivert_function_name = undivert_function_name

        self.run_function_name = run_function_name

        self.include_function_name = include_function_name
        self.place_function_name = place_function_name

        # --- indent & tabs ---

        self.indent = indent
        self.tab = tab

        # --- optimize level & compile flag ---

        self.compile_flags = compile_flags
        self.optimize_level = optimize_level

    def tabs(self):
        return self.tab * self.indent

def generate_code(infile, outfile, env):
    """read from infile and generats python code to outfile"""

    code_generators = env.code_generators

    # --- macro ---
    macro_prefix = env.macro_prefix
    macro_suffix = env.macro_suffix

    macro_re = env.macro_re

    # --- statement ---
    statement_prefix = env.statement_prefix
    statement_suffix = env.statement_suffix

    # --- comment ---
    comment_prefix = env.comment_prefix
    comment_suffix = env.comment_suffix

    # --- evaluation variable ---
    evaluation_variable_re = env.evaluation_variable_re

    # --- outfile variable name ---
    outfile_variable_name = env.outfile_variable_name

    for line in infile:

        striped_line = line.strip(_SPACE_CHARS)

        # --- check macro ---
        if striped_line.startswith(macro_prefix) and \
                striped_line.endswith(macro_suffix):

            macro_striped_line = \
                striped_line[   len(macro_prefix): \
                                len(striped_line) - len(macro_suffix)]

            m = __fullmatch(macro_re, macro_striped_line)
            if m:

                generate_code = code_generators[m.group('macro')]
                generate_code(m.group('args'), outfile, env)

                continue

        # --- check statement ---
        if striped_line.startswith(statement_prefix) and \
                striped_line.endswith(statement_suffix):
            outfile.write(
                '{}{}\n'.format(
                    env.tabs(),
                    striped_line[
                            len(statement_prefix): \
                            len(striped_line) -len(statement_suffix)] \
                                .strip(_SPACE_CHARS),
                    )
                )

            continue

        # --- check comment ---
        if striped_line.startswith(comment_prefix) and \
                striped_line.endswith(comment_suffix):
            outfile.write('\n')

            continue

        # --- check for evaluations & variables ---
        outfile.write(env.tabs())

        m = evaluation_variable_re.search(line)
        while m:

            # --- write primitive remains ---
            if m.start() != 0:
                outfile.write(
                    '{}.write({});'.format(
                        outfile_variable_name,
                        repr(line[:m.start()]),
                    )
                )

            name = m.group('name')

            if name is None:
                # --- write evaluation ---
                outfile.write(
                    '{}.write(str({}));'.format(
                        outfile_variable_name,
                        m.group('eval'),
                    )
                )

            else:
                # --- write variable ---
                outfile.write(
                    '{}.write(str({}));'.format(
                        outfile_variable_name,
                        name,
                    )
                )

            # --- check remaining line ---
            if m.end() == len(line):
                outfile.write('\n')
                break

            line = line[m.end():]
            m = evaluation_variable_re.search(line)

        else:

            # --- writing text ---
            outfile.write(
                '{}.write({});\n'.format(
                    outfile_variable_name,
                    repr(line),
                )
            )

    if env.macro_stack:
        raise CompilerError(_UNTERMINATED_BLOCK, env.macro_stack[-1])

def compile_generated_code(
        code,
        infile_name,
        flags = _COMPILE_FLAGS,
        optimize = _OPTIMIZE_LEVEL,
        ):

    return compile(code, infile_name, 'exec', compile_flags, True, optimize)

def compile_file(infile, env):

    string_buffer = io.StringIO()
    with string_buffer:
        generate_code(infile, string_buffer, env)

    return compile(string_buffer.getvalue(), infile.name, 'exec',
            env.compile_flags, True, env.optimize_level)

_default_builtins = builtins

class ExecutorEnvironment:
    def __init__(self,
            variables = None,
            builtins = None,

            pipes = None,

            # --- variable names ---
            outfile_variable_name = _DEFAULT_OUTFILE_VARIABLE_NAME,

            pipes_varaible_name = _DEFAULT_PIPES_VARIABLE_NAME,
            divert_function_name = _DEFAULT_DIVERT_FUNCTION_NAME,
            undivert_function_name = _DEFAULT_UNDIVERT_FUNCTION_NAME,

            run_function_name = _DEFAULT_RUN_FUNCTION_NAME,

            include_function_name = _DEFAULT_INCLUDE_FUNCTION_NAME,
            place_function_name = _DEFAULT_PLACE_FUNCTION_NAME,

            version_variable_name = _DEFAULT_VERSION_VARIABLE_NAME,
            command_variable_name = _DEFAULT_COMMAND_VARIABLE_NAME,
            ):

        if variables is None:
            variables = {}

        if '__builtins__' not in variables:
            if builtins is None:
                builtins = _default_builtins

            variables['__builtins__'] = builtins

        self.variables = variables

        self.pipes = pipes or collections.defaultdict(io.StringIO)

        # --- variable names ---
        self.outfile_variable_name = outfile_variable_name

        self.pipes_varaible_name = pipes_varaible_name
        self.divert_function_name = divert_function_name
        self.undivert_function_name = undivert_function_name

        self.run_function_name = run_function_name

        self.include_function_name = include_function_name
        self.place_function_name = place_function_name

        self.version_variable_name = version_variable_name
        self.command_variable_name = command_variable_name

def execute_code_object(
        code_object,
        outfile,
        env,

        working_directory = '.',
        command = None,
        ):

    variables = env.variables

    pipes = env.pipes

    pipes[None] = outfile

    # --- outfile variable ---

    variables[env.outfile_variable_name] = outfile

    # --- pipes variable ---

    variables[env.pipes_varaible_name] = pipes

    # --- version variable ---

    variables[env.version_variable_name] = VERSION

    # --- command variable ---

    if command is not None:
        variables[env.command_variable_name] = command

    # --- divert function ---

    def _divert_function(target = None):
        if not (isinstance(target, (str, int)) or target is None):
            raise TypeError(
                    "divert target must be type of str or int or None")
        variables[env.outfile_variable_name] = pipes[target]

    variables[env.divert_function_name] = _divert_function

    # --- undivert function ---

    def _undivert_function(target):
        if not isinstance(target, (str, int)):
            raise TypeError(
                    "undivert target must be type of str or int")
        outfile.write(pipes[target].getvalue())

    variables[env.undivert_function_name] = _undivert_function

    # --- place function ---

    def _place_function(file_name, output = None):
        output = env.pipes[output]
        with open(__joinpath(working_directory, file_name)) as infile:
            output.write(infile.read())

    variables[env.place_function_name] = _place_function

    # --- include function ---

    # TODO: write _include_function

    # --- run function ---

    def _run_function(command,
            stdin = None,
            stdout = None,
            stderr = None,
            check = True
            ):

        if stdin is None:
            _input = ''
        elif isinstance(stdin, (str, int)):
            _input = pipes[stdin].getvalue()
        else:
            raise TypeError(
                    "run stdin argument must be type of str or int")

        if stdout is None or isinstance(stdout, (str, int)):
            stdout = pipes[stdout]
        else:
            raise TypeError(
                    "run stdout argument must be None or type of str or int")

        if stderr is None or isinstance(stderr, (str, int)):
            stderr = pipes[stderr]
        else:
            raise TypeError(
                    "run stderr argument must be None or type of str or int")

        subprocess.run(command, input=_input, stdout=stdout, stderr=stderr)

    variables[env.run_function_name] = _run_function

    # --- load function ---

    # TODO: write load function

    # --- executing code_object ---

    return exec(code_object, variables)


# --- main functions ---

if sys.platform.startswith('linux') or sys.platform.startswith('freebsd'):
    def __get_cache_file_path(cache_folder_path, file_real_path):
        parts = file_real_path.split(os.sep)
        return __joinpath(cache_folder_path, *parts[1:])

elif sys.platform == 'win32':
    def __get_cache_file_path(cache_folder_path, file_real_path):
        parts = file_real_path.split(os.sep)
        return __joinpath(cache_folder_path, parts[0][0].lower(), *parts[1:])

else:
    raise NotImplemented(
            'implement __get_cache_file_path() for your platform: {}'.format(
                sys.platform))

def __walk_files(root, name_ignores, path_ignores, sort_func):
    # root is a real path
    result = [root]
    i = 0
    while i < len(result):
        path = result[i]

        if __isdir(path):
            new_result = collections.deque()

            # walk into directory
            names = sort_func(os.listdir(path))
            for name in names:
                # filter file name
                matched = False
                for pattern in name_ignores:
                    if fnmatch.fnmatch(name, pattern):
                        matched = True
                        break

                if matched:
                    continue # continue os.listdir

                new_path = __joinpath(path, name)

                # filter file path
                for pattern in path_ignores:
                    if fnmatch.fnmatch(new_path, pattern):
                        matched = True
                        break

                if matched:
                    continue # continue os.listdir

                new_result.append(new_path)

            # pop the path
            result.pop(i)

            # now extend result
            result.extend(new_result)

            continue
        i += 1
    return result

def __write_compiled_code_env(code_object, env, outfile):
    # --- writing to file ---
    outfile.write(_CACHE_FILE_MAGIC_NUMBER)

    _write_string(outfile, env.macro_prefix)
    _write_string(outfile, env.macro_suffix)

    _write_string(outfile, env.statement_prefix)
    _write_string(outfile, env.statement_suffix)

    _write_string(outfile, env.comment_prefix)
    _write_string(outfile, env.comment_suffix)

    _write_string(outfile, env.variable_prefix)
    _write_string(outfile, env.variable_suffix)

    _write_string(outfile, env.evaluation_prefix)
    _write_string(outfile, env.evaluation_suffix)

    _write_code_object(outfile, code_object)

def __read_compiled_code(infile, env):
    if infile.read(len(_CACHE_FILE_MAGIC_NUMBER)) != _CACHE_FILE_MAGIC_NUMBER:
        raise FileStructError('file magic number mismatch')

    if \
            env.macro_prefix == _read_string(infile) and \
            env.macro_suffix == _read_string(infile) and \
            env.statement_prefix == _read_string(infile) and \
            env.statement_suffix == _read_string(infile) and \
            env.comment_prefix == _read_string(infile) and \
            env.comment_suffix == _read_string(infile) and \
            env.variable_prefix == _read_string(infile) and \
            env.variable_suffix == _read_string(infile) and \
            env.evaluation_prefix == _read_string(infile) and \
            env.evaluation_suffix == _read_string(infile):

        return _read_code_object(infile)

    return None

# __compile_if_needed() will call the following functions:
#   os.stat
#   open

def __compile_if_needed(code_path, cache_path, compiler_env):
    code_stat = os.stat(code_path)
    try:
        # may raise FileNotFoundError
        cache_stat = os.stat(cache_path)

        if code_stat.st_mtime_ns < cache_stat.st_mtime_ns:

            # this also may raise FileNotFoundError
            with open(cache_path, 'rb') as cache_file:

                # may raise FileStructError or EOFError
                code_object = __read_compiled_code(cache_file, compiler_env)

                # __read_compiled_code() return None if prefixes & suffixes
                # mismatch.
                if code_object is not None:
                    return code_object

    except (FileNotFoundError, EOFError, FileStructError):
        pass

    # compile the file
    with open(code_path, 'rt') as code_file:
        code_object = compile_file(code_file, compiler_env)

    # cache the compiled code_object
    with open(cache_path, 'wb') as cache_file:
        __write_compiled_code_env(code_object, compiler_env, cache_file)

    # return the result
    return code_object

def __apply_language(lang, compiler_env):
    for key, value in __language_specifications[lang]:
        setattr(compiler_env, key, value)

def __apply_settings(key, value, compiler_env):
    if key in ('mp', 'macro_prefix'):
        compiler_env.macro_prefix = value

    elif key in ('ms', 'macro_suffix'):
        compiler_env.macro_suffix = value

    elif key in ('sp', 'statement_prefix'):
        compiler_env.statement_prefix = value

    elif key in ('ss', 'statement_suffix'):
        compiler_env.statement_suffix = value

    elif key in ('cp', 'comment_prefix'):
        compiler_env.comment_prefix = value

    elif key in ('cs', 'comment_suffix'):
        compiler_env.comment_suffix = value

    elif key in ('vp', 'variable_prefix'):
        compiler_env.variable_prefix = value

    elif key in ('vs', 'variable_suffix'):
        compiler_env.variable_suffix = value

    elif key in ('ep', 'evaluation_prefix'):
        compiler_env.evaluation_prefix = value

    elif key in ('es', 'evaluation_suffix'):
        compiler_env.evaluation_suffix = value

    else:
        raise KeyError('unknown keyword: {!r}'.format(key))

def __create_config_parser():
    return configparser.ConfigParser(
            defaults = None,

            dict_type = dict,
            allow_no_value = False,

            delimiters = ('=', ),

            comment_prefixes = ('#', ),
            inline_comment_prefixes = None,

            strict = True,

            empty_lines_in_values = False,

            default_section = "DEFAULT",

            interpolation = None,

            converters = {},
            )

def __apply_config_compiler_env(config, compiler_env):
    try:
        settings = config['settings']
        for name in (
                'macro_prefix',
                'macro_suffix',
                'statement_prefix',
                'statement_suffix',
                'comment_prefix',
                'comment_suffix',
                'variable_prefix',
                'variable_suffix',
                'evaluation_prefix',
                'evaluation_suffix',
                ):
            setattr(
                    compiler_env,
                    name,
                    settings.get(name, fallback=getattr(compiler_env, name)),
                    )
    except KeyError:
        pass

def __apply_config_filters(config, filters):
    try:
        filters = config['filters']
    except KeyError:
        pass

def __compiler_worker(
        file_real_path,
        cache_folder_path,
        ):
    cache_file_path = \
        __get_cache_file_path(cache_folder_path, file_real_path)

def main(argv):

    options = __parse_argv(argv)
    if isinstance(options, int):
        return options

    # ['jobs', 'switchs', 'output'] is in dir(options)

    # possible values that can be found in (tup[0] for tup in options.jobs):
    #   _LANG_FLAG, _IMPORT_FLAG, _JSONFILE_FLAG,
    #   _INPUT_FLAG,
    #   _DEFINE_FLAG, _UNDEFINE_FLAG, _SETTING_FLAG

    # options.switchs ORed values:
    #   _ARRANGE_PROCESS_FLAG
    #   _RECURSIVE_FLAG
    #   _CLEAR_CACHE_FLAG
    #   _FORCE_FLAG

    # (tup[0] for tup in options.output) possible values:
    #   _OUTFILE_FLAG, _OUTFOLDER_FLAG


    # other notes:

    # compile-time jobs:
    #   _LANG_FLAG
    #   _SETTING_FLAG

    # execution-time jobs:
    #   _IMPORT_FLAG
    #   _JSONFILE_FLAG
    #
    #   _DEFINE_FLAG
    #   _UNDEFINE_FLAG

    if __debug__:
        print_options(options)
        print_line(fill='=')

    # --- join cache folder path ---
    cache_folder_path = __joinpath(_HOME_DIRECTORY, _CACHE_FOLDER_NAME)

    # --- remove cache folder ---
    if _CLEAR_CACHE_FLAG & options.switchs:
        shutil.rmtree(cache_folder_path)

    # --- read config file ---
    try:
        config_file_path = __abspath(_CONFIG_FILE_NAME)
        with open(config_file_path) as config_file:
            config = __create_config_parser()
            config.read_file(config_file)
    except FileNotFoundError:
        config = None

    # config can be:
    #   None or ConfigParser

    # options.jobs contains:
    #   [_INPUT_FLAG, 'path']
    #   [_INPUT_FLAG, sys.stdin]

    # --- append abs path & real path, filter files ---
    i = 0
    while i < len(options.jobs):
        item = options.jobs[i]

        if item[0] == _INPUT_FLAG and isinstance(item[1], str):

            # options.jobs contains:
            #   [_INPUT_FLAG, 'path']
            #   [_INPUT_FLAG, sys.stdin]

            # remove input FILE names
            for pattern in options.name_ignores:
                if fnmatch.fnmatch(__splitpath(item[1])[1], pattern):
                    # pop matched file name
                    options.jobs.pop(i)
                    continue

            # --- append abs path ---
            item.append(__abspath(item[1]))

            # options.jobs contains:
            #   [_INPUT_FLAG, 'path', 'abs_path']
            #   [_INPUT_FLAG, sys.stdin]

            # remove input FILE paths
            for pattern in options.path_ignores:
                if fnmatch.fnmatch(item[2], pattern):
                    # pop matched file path
                    options.jobs.pop(i)
                    continue

            # --- append real path ---
            item.append(__realpath(item[2]))
        i += 1

    # options.jobs contains:
    #   [_INPUT_FLAG, 'path', 'abs_path', 'real_path] filtered by name, path
    #   [_INPUT_FLAG, sys.stdin]

    # --- check directories ---
    if _RECURSIVE_FLAG & options.switchs:
        i = 0
        while i < len(options.jobs):
            item = options.jobs[i]
            if \
                    item[0] == _INPUT_FLAG and \
                    isinstance(item[1], str) and \
                    __isdir(item[3]):
                files = __walk_files(
                    item[3],
                    options.name_ignores,
                    options.path_ignores,
                    sorted,
                    )
                options.jobs[i] = [_INPUT_FLAG, tuple(files)]
            i += 1

    else:
        _LINE = 'pycro: -r not specified; omitting {!r} directory'
        i = 0
        while i < len(options.jobs):
            item = options.jobs[i]
            if \
                    item[0] == _INPUT_FLAG and \
                    isinstance(item[1], str) and \
                    __isdir(item[3]):
                print(_LINE.format(item[1]), file=sys.stderr)
                options.jobs.pop(i)
                continue
            i += 1

    # options.jobs contains:
    #   [_INPUT_FLAG, [walked files]] filtered by name, path
    #   [_INPUT_FLAG, 'path', 'abs_path', 'real_path'] filtered by name, path
    #   [_INPUT_FLAG, sys.stdin]

    print_line('jobs')
    for item in options.jobs:
        print(item)
    sys.exit(1)

    if _ARRANGE_PROCESS_FLAG & options.switchs:

        # --- arranged performace ---
        raise BaseException('unimplemented code')

    else: # not (_ARRANGE_PROCESS_FLAG & options.switchs)

        # --- apply config ---
        if config is not None:
            __apply_config_compiler_env(config, compiler_env)

        # --- initialize compiler environment ---
        compiler_env = CompilerEnvironment()

        # --- apply settings & languages ---
        for item in ( tup[1] for tup in options.jobs if tup[0] in \
                (_SETTING_FLAG, _LANG_FLAG) ):

            if isinstance(item, tuple):
                # item is a (Key, Value)
                __apply_settings(item[0].lower(), item[1], compiler_env)

            else:
                # item is language specification
                __apply_language(lang, compiler_env)

        # options.jobs contains:
        #   [_INPUT_FLAG, 'path', 'real_path']
        #   [_INPUT_FLAG, sys.stdin]

        # --- first compile the inputs ---
        # TODO: complete here

        print("I'm here")

if __name__ == '__main__':
    sys.exit(main(sys.argv))

