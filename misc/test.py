#!/usr/bin/python3

import threading
import random
import time

def sleep(t):
    log("sleep for {:.2f}s".format(t) if isinstance(t, float) \
            else "sleep for {}s".format(t))
    time.sleep(t)

def f(name, t):
    log("started")
    sleep(t)
    log("name is: {}".format(name))

_names = ['foo', 'bar', 'car', 'gate']

def rand_name():
    return random.choice(_names)

def log(message):
    print('[{:<12}]: {}'.format(threading.current_thread().name, message))

def main():
    thread = threading.Thread(
            target = f,
            name = 'thread-1',
            args = (
                rand_name(), 
                random.uniform(1, 3),
                ),
            )

    thread.start()

    log("wait for {}".format(thread.name))

    thread.join()

    log("{} joined".format(thread.name))

if __name__ == '__main__':
    main()

