#!/usr/bin/python3

import random
import time
import multiprocessing

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

        def worker_function(inital_job, inputs_conn, outputs_conn, *args):
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

        self._iterable = iterable
        self._workers = collections.deque()

    def start_workers(self):
        inputs_conn1, inputs_conn2 = multiprocessing.Pipe(False)
        outputs_conn1, outputs_conn2 = multiprocessing.Pipe(False)

        for item in self._iterable:
            inputs_conn1.send(item)

        inputs_conn1.close()

        while len(self._workers) < _MAX_PROCESS_NUMBER:

            try:
                item = inputs_conn1.recv()
            except EOFError:
                break

            self._workers.append(worker)

            worker.start()

def hash_worker(path):
    hasher = hashlib.sha256()
    with open(path, 'rb', 0) as infile:
        _buffer = infile.read(io.DEFAULT_BUFFER_SIZE)
        while _buffer:
            hasher.update(_buffer)
            _buffer = infile.read(io.DEFAULT_BUFFER_SIZE)
    return hasher.digect()

def main():
    workers = Workers(
            target = hash_worker,


if __name__ == '__main__':
    main()

