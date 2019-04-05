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

def main():
    conn1, conn2 = multiprocessing.Pipe()
    
    conn1.send( (1, 2) )
    conn1.close()

    print(conn2.recv())
    print(conn2.recv())

if __name__ == '__main__':
    main()

