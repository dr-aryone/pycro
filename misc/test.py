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
    
def _write_object(obj, outfile):
    _buffer = marshal.dumps(obj, 4)
    _write_size(len(_outfile, _buffer))
    _outfile.write(_buffer)

def _read_object(infile):
    return marshal.loads(_read_buffer(infile, _read_size(infile)), 4)

def process(func):
    def process_init(*args, **kwargs):
        return multiprocessing.Process(
                target = func,
                name = func.__name__ + ' process',
                args = args,
                kwargs = kwargs,
                )
    return process_init

class _WriterThread(threading.Thread):
    def __init__(self, obj, outfile):
        super().__init__(self)
        self._obj = obj
        self._outfile = outfile

    def run(self):
        _buffer = marshal.dumps(self._obj, 4)
        _write_size(len(self._outfile, _buffer))
        self._outfile.write(_buffer)

class _ReaderThread(threading.Thread):
    def __init__(self, obj, infile):
        super().__init__(self)
        self._obj = obj
        self._infile = infile

    def run(self):
        return marshal.loads(
                    _read_buffer(
                        self._infile, 
                        _read_size(infile)
                        )
                )

class Queue:
    def __init__(self, maxsize = 0):
        if not isinstance(maxsize, int):
            raise TypeError('maxsize must be type of int')
        if maxsize < 0:
            raise ValueError('maxsize must be greater than equal to 0')

        self._pipe_r, self._pipe_w = itertools.starmap(
                _fdopen, zip(os.pipe(), ('rb', 'wb')))

        self._maxsize = maxsize
        self._size = 0
        self._rlock = multiprocessing.RLock()

    def put(self, obj):
        with self._rlock:
            if self._maxsize and self._size >= self._maxsize:
                raise queue.Full()
            self._size += 1
            _write_object(self._pipe_w, obj)

    def get(self):
        with self._rlock:
            if self._size:
                print('self._size:', self._size)
                self._size -= 1
                return _read_object(self._pipe_r)
            else:
                raise queue.Empty()

class Workers:
    def __init__(
            self, 
            target,

            args = (), 
            kwargs = {},

            inputs = None, 
            max_workers = None,
            ):

        def process_init(
                initial_item, inputs_queue, outputs_queue, *args, **kwargs):
            item = initial_item
            while True:
                outputs_queue.put(target(item, *args, **kwargs))
                try:
                    item = inputs_queue.get()
                except queue.Empty:
                    break

        self._process_init = process(process_init)
        self._args = args
        self._kwargs = kwargs

        if max_workers is None:
            max_workers = len(os.sched_getaffinity(0))
            if max_workers == 0:
                raise OSError('os.sched_getaffinity(0) returns empty set')

        else:
            if not isinstance(max_workers, (int, None)):
                raise TypeError(
                    'max_workers argument must be type of int or None')
            if max_workers <= 0:
                raise ValueError(
                    'max_workers argument must be greater than equal to zero')

        self._max_workers = max_workers

        self._workers = collections.deque()

        self._inputs_queue = Queue()
        if inputs is not None:
            for item in inputs:
                self._inputs_queue.put(item)

        self._outputs_queue = Queue()

    def start_workers(self):
        while True:
            if len(self._workers) >= self._max_workers:
                i = 0
                while i < len(self._workers):
                    if worker.is_alive():
                        self._workers.pop(i)
                    else:
                        i += 1

            try:
                initial_item = self._inputs_queue.get()
            except queue.Empty:
                break

            worker = self._process_init(
                    initial_item, 
                    self._inputs_queue, 
                    self._outputs_queue,
                    *self._args,
                    **self._kwargs,
                    )

            self._workers.append(worker)

            worker.start()

    def apply_inputs(self, inputs):
        for item in inputs:
            self._inputs_queue.put(item)

        self.start_workers()

    def join(self, timeout=None):
        if timeout is None:
            for worker in self._workers:
                worker.join()
        else:
            deadline = time.time() + timeout
            for worker in self._workers:
                worker.join(timeout)
                if time.time() >= deadline:
                    return
                timeout = time.time() - deadline

    @property
    def outputs(self):
        outputs = collections.deque()
        while True:
            try:
                item = self._outputs_queue.get()
            except queue.Empty:
                return outputs
            outputs.append(item)

def hash_worker(path):
    hasher = hashlib.sha256()
    with open(path, 'rb', 0) as infile:
        _buffer = infile.read(io.DEFAULT_BUFFER_SIZE)
        while _buffer:
            hasher.update(_buffer)
            _buffer = infile.read(io.DEFAULT_BUFFER_SIZE)
    return (path, hasher.digest())

def main():
    if len(sys.argv) != 3:
        print('usage: {} PATH p|s'.format(sys.argv[0]))
        sys.exit(0)

    inputs = filter(os.path.isfile, glob.glob(sys.argv[1], recursive = True))

    if sys.argv[2] == 'p':
        print('[ parallel hashing ]')

        workers = Workers(
                hash_worker,
                inputs = inputs)

        workers.start_workers()
        print('workers started')

        workers.join()
        print('workers joined')

        outputs = workers.outputs

    elif sys.argv[2] == 's':

        print('[ sequence hashing ]')

        outputs = []
        for _input in inputs:
            outputs.append(hash_worker(_input))

    else:

        print('usage: {} PATH p|s'.format(sys.argv[0]))
        sys.exit(0)

    # print result
    print('-' * 80)
    for item in outputs:
        print('{:<30}: {}'.format(item[0] + ':', item[1].hex()))

if __name__ == '__main__':
    main()

