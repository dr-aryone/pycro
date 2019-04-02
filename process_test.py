#!/usr/bin/python3

import multiprocessing as mp

import threading
import os
import time
import signal

def process(func):
    def process_creator(*args, **kwargs):
        return mp.Process(
                target = func,
                name = func.__name__ + ' process',

                args = args,
                kwargs = kwargs,
                )
    return process_creator

stdout_lock = threading.Lock()

def log(message):
    with stdout_lock:
        print('[{:>10}]: {}'.format(mp.current_process().name, message))

class Block:
    def __enter__(self):
        log("Block.__enter__")

    def __exit__(self, a, b, c):
        log("Block.__exit__")

def _reader(stream):
    with Block() as block:
        try:
            stream.read(1000)

        finally:
            log("finally statement")

@process
def reader(stream):
    log("start of process")

    try:
        _reader(stream)

    except KeyboardInterrupt:
        return

    log("end of process")

def sleep(t):
    log("sleep for {:.2f}s".format(t) if isinstance(t, float) \
            else "sleep for {}s".format(t))
    time.sleep(t)

def main():
    fd_pipe = os.pipe()

    pipe_r, pipe_w = open(fd_pipe[0], 'rt'), open(fd_pipe[1], 'wt')

    worker = reader(pipe_r)
    worker.start()

    log('kill child Process after 0.1s')
    time.sleep(0.1)
    os.kill(worker.pid, signal.SIGINT)

    log("end of main function")


if __name__ == '__main__':
    main()

