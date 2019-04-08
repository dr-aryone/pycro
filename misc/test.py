#!/usr/bin/python3

import time
import multiprocessing
import glob
import collections
import hashlib
import io
import sys
import os
import queue
import itertools
import marshal
import threading
import ctypes

stdout_lock = multiprocessing.Lock()
def log(*objects, sep = ' '):
    print('[{:<20}]: {}'.format(
        multiprocessing.current_process().name,
        sep.join(str(obj) for obj in objects)
        ))

_fdopen = open
_SIZE_LEN = 4

def _write_size(outfile, size):
    outfile.write(size.to_bytes(_SIZE_LEN, 'big', signed=False))

def _read_size(infile):
    _buffer = infile.read(_SIZE_LEN)
    if len(_buffer) != _SIZE_LEN:
        raise EOFError("End of file while reading size")
    return int.from_bytes(_buffer, 'big', signed = False)

def _read_buffer(infile, size):
    _buffer = infile.read(size)
    if len(_buffer) != size:
        raise EOFError("End of file while reading buffer")
    return _buffer

def _write_object(outfile, obj):
    _buffer = marshal.dumps(obj, 4)
    _write_size(outfile, len(_buffer))
    outfile.write(_buffer)

def _read_object(infile):
    return marshal.loads(_read_buffer(infile, _read_size(infile)))

def process(func):
    def process_init(*args, **kwargs):
        return multiprocessing.Process(
                target = func,
                name = func.__name__ + ' process',
                args = args,
                kwargs = kwargs,
                )
    return process_init

class Queue:
    def __init__(self, maxsize = 0):
        if not isinstance(maxsize, int):
            raise TypeError('maxsize must be type of int')
        if maxsize < 0:
            raise ValueError('maxsize must be greater than equal to 0')

        self._maxsize = maxsize
        self._rlock = multiprocessing.RLock()

        self._size = multiprocessing.Value(ctypes.c_ulong, 0, 
                lock = self._rlock)

        self._pipe_r, self._pipe_w = \
                itertools.starmap(
                        _fdopen, 
                        zip(os.pipe(), ('rb', 'wb'), (0, 0)),
                        )

    def put(self, obj):
        with self._rlock:
            if self._maxsize and self._size.value >= self._maxsize:
                raise queue.Full()
            self._size.value += 1
            _write_object(self._pipe_w, obj)

    def get(self):
        with self._rlock:
            if self._size.value:
                self._size.value -= 1
                return _read_object(self._pipe_r)
            else:
                raise queue.Empty()

