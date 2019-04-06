#!/usr/bin/python3

import random
import time
import multiprocessing
import glob
import collections
import hashlib
import io
import sys
import os
import queue

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

        self._pipe_r, self._pipe_w = map(
                __fdopen, zip(os.pipe(), ('rb', 'wb')))

        self._maxsize = maxsize
        self._size = 0
        self._rlock = multiprocessing.RLock()

    def put(self, obj):
        with self._rlock:
            if self._maxsize and self._size >= self._maxsize:
                raise queue.Full()
            self._size += 1
            marshal.dump(obj, self._pipe_w, 4)

    def get(self):
        with self._rlock:
            if self._size:
                self._size -= 1
                return marshal.load(obj)
            else:
                raise queue.Empty()

class Workers:
    def __init__(
            self, 
            function,

            args = (), 
            kwargs = {},

            inputs = None, 
            max_workers = None,
            ):

        def process_init(
                initial_item, inputs_queue, outputs_queue, *args, **kwargs):
            item = initial_item
            while True:
                outputs_queue.put(function(item, *args, **kwargs))
                try:
                    item = inputs_queue.get()
                except queue.Empty:
                    break

        self._process_init = process(process_init)
        self._args = args
        self._kwargs = kwargs

        if max_workers is None:
            self._max_workers = os.sched_getaffinity(0)

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
                self._inputs_queue.append(item)

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
                    )

            self._workers.append(worker)

            worker.start()

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
                hash_worker)

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

