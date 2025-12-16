#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: wxnacy@gmail.com
"""

"""


import multiprocessing as mp

import time

def test(i):
    print(i, time.time())
    time.sleep(i)


class MultiProcessWrok(object):
    done = False
    success_count = 0
    total_count = 100
    def __init__(self):
        pool = mp.Pool(processes = 4)
        pass

    def run(self):
        while not self.done:
            self.pool.apply_async(self.work)

    def work(self):

        self._check_done()

    def _check_done(self):
        if self.success_count >= self.total_count:
            self.done = True
            print('Done')

    def start(self):
        self.run()

if __name__ == "__main__":
    pool = mp.Pool(processes = 4)
    while True:
        for i in range(6):
            pool.apply_async(test, (i, ))
