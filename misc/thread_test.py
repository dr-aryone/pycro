#!/usr/bin/python3

import threading
import os
import time

thread = lambda func: \
        (lambda *args, **kwargs: threading.Thread(
            target = func,
            args = args,
            kwargs = kwargs,
            name = func.__name__ + ' thread',
            ) )
def thread(func):
    def thread_creator(*args, **kwargs):
        return threading.Thread(
                target = func,
                name = func.__name__ + ' thread',

                args = args,
                kwargs = kwargs,
                )
    return thread_creator

stdout_lock = threading.Lock()

def log(message):
    with stdout_lock:
        print('[{:>10}]: {}'.format(threading.current_thread().name, message))

def thread_name():
    return threading.current_thread().name

@thread
def reader(stream):
    log("start of thread")
    line = stream.readline()
    while line:
        log("readed: {!r}".format(line))
        line = stream.readline()
    log("end of thread")

def sleep(t):
    log("sleep for {:.2f}s".format(t) if isinstance(t, float) \
            else "sleep for {}s".format(t))
    time.sleep(t)

def main():
    fd_pipe = os.pipe()

    pipe_r, pipe_w = open(fd_pipe[0], 'rt'), open(fd_pipe[1], 'wt')

    worker = reader(pipe_r)

    worker.start()

    sleep(3)

    worker.interrupt()


    worker.join()
    
    log("end of main function")


if __name__ == '__main__':
    main()

