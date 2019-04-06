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

_MAX_PROCESS_NUMBER = 4

def process(func):
    def process_init(*args, **kwargs):
        return multiprocessing.Process(
                target = func,
                name = func.__name__ + ' process',
                args = args,
                kwargs = kwargs,
                )
    return process_init

class Workers:
    def __init__(
            self,
            target,
            inputs,
            max_workers = _MAX_PROCESS_NUMBER,
            ):

        def worker_function(initial_job, inputs_conn, outputs_conn, *args):
            try:
                job = initial_job

                while True:

                    outputs_conn.send(target(job, *args))

                    try:
                        job = inputs_conn.recv()
                    except EOFError:
                        return

            except KeyboardInterrupt:
                pass

        self._worker_function = process(worker_function)
        self._inputs = inputs
        self._workers = collections.deque()
        self._max_workers = _MAX_PROCESS_NUMBER
        self._outputs_conn = None

    def start_workers(self, initial_args = ()):
        inputs_conn1, inputs_conn2 = multiprocessing.Pipe(False)
        outputs_conn1, outputs_conn2 = multiprocessing.Pipe(False)
        self._outputs_conn = outputs_conn1, outputs_conn2

        for item in self._inputs:
            inputs_conn2.send(item)

        inputs_conn2.close()


        while len(self._workers) < self._max_workers:

            try:
                initial_job = inputs_conn1.recv()
            except EOFError:
                break

            worker = self._worker_function(
                    initial_job,
                    inputs_conn1,
                    outputs_conn2,
                    *initial_args)

            self._workers.append(worker)

            worker.start()

    def join(self):
        for worker in self._workers:
            worker.join()
        self._outputs_conn[1].close()

    @property
    def outputs(self):
        result = []
        while True:
            try:
                item = self._outputs_conn[0].recv()
            except EOFError:
                break
            result.append(item)
        return result

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

        workers = Workers(
                hash_worker,
                inputs,
                )

        workers.start_workers()
        print('workers started')

        workers.join()
        print('workers joined')

        outputs = workers.outputs

    elif sys.argv[2] == 's':

        print('hash in sequence')

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

