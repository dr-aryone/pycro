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

            self._workers[i]._kwargs = kwargs

    def start(self, inputs, *args, **kwargs):

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

