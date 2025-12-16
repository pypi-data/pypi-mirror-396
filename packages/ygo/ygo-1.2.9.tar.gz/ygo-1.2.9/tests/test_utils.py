# Copyright (c) ZhangYundi.
# Licensed under the MIT License. 
# Created on 2025/7/20 16:33
# Description:
import queue

# from ygo.utils import locate
from ygo.pool import run_job

# def test_locate():
    # fn = locate("functools.partial")
    # test_fn = lambda a, b: a+b
    # assert fn(test_fn, 1, 2)() == 3

def foo():
    run_job(1, 1, queue.Queue())

if __name__ == '__main__':
    foo()