#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: wxnacy(wxnacy@gmail.com)
# Description:


import sys
import time
import random
import threading

STR = [
    'a' , 'b' , 'c' , 'd' , 'e' , 'f' , 'g' , 'h' ,
    'i' , 'j' , 'k' , 'l' , 'm' , 'n' , 'o' , 'p' ,
    'q' , 'r' , 's' , 't' , 'u' , 'v' , 'w' , 'x' ,
    'y' , 'z' , '0' , '1' , '2' , '3' , '4' , '5' ,
    '6' , '7' , '8' , '9' , 'A' , 'B' , 'C' , 'D' ,
    'E' , 'F' , 'G' , 'H' , 'I' , 'J' , 'K' , 'L' ,
    'M' , 'N' , 'O' , 'P' , 'Q' , 'R' , 'S' , 'T' ,
    'U' , 'V' , 'W' , 'X' , 'Y' , 'Z'
]

INT = [
    '0', '1', '2', '3', '4', '5',
    '6', '7', '8', '9'
]

def random_str(str_len):
    """
    获取随机字符串
    :param str_len: 需要获取的长度
    :return:
    """
    def _create():
        return str(STR[int(random.uniform(0, len(STR)))])
    res = [_create() for x in range(0, str_len)]
    return ''.join(res)

def random_int(int_len):
    """
    获取随机数字
    :param int_len: 需要获取的长度
    :return:
    """
    def _create(i):
        begin = 0
        if i == 0:
            begin = 1
        return str(INT[int(random.uniform(begin, len(INT)))])
    res = [_create(x) for x in range(0, int_len)]
    return int(''.join(res))

class Snowflake(object):
    region_id_bits = 2
    worker_id_bits = 10
    sequence_bits = 11

    MAX_REGION_ID = -1 ^ (-1 << region_id_bits)
    MAX_WORKER_ID = -1 ^ (-1 << worker_id_bits)
    SEQUENCE_MASK = -1 ^ (-1 << sequence_bits)

    WORKER_ID_SHIFT = sequence_bits
    REGION_ID_SHIFT = sequence_bits + worker_id_bits
    TIMESTAMP_LEFT_SHIFT = (sequence_bits + worker_id_bits + region_id_bits)

    def __init__(self, worker_id, region_id=0):
        self.twepoch = 1532436731000
        self.last_timestamp = -1
        self.sequence = 0

        # assert 0 <= worker_id <= Snowflake.MAX_WORKER_ID
        # assert 0 <= region_id <= Snowflake.MAX_REGION_ID

        self.worker_id = worker_id
        self.region_id = region_id

        self.lock = threading.Lock()

    def generate(self, bus_id=None):
        return self.next_id(
            True if bus_id is not None else False,
            bus_id if bus_id is not None else 0
        )

    def next_id(self, is_padding, bus_id):
        with self.lock:
            timestamp = self.get_time()
            padding_num = self.region_id

            if is_padding:
                padding_num = bus_id

            if timestamp < self.last_timestamp:
                try:
                    raise ValueError(
                        'Clock moved backwards. Refusing to'
                        'generate id for {0} milliseconds.'.format(
                            self.last_timestamp - timestamp
                        )
                    )
                except ValueError:
                    print(sys.exc_info[2])

            if timestamp == self.last_timestamp:
                self.sequence = (
                                    self.sequence + 1) & Snowflake.SEQUENCE_MASK
                if self.sequence == 0:
                    timestamp = self.tail_next_millis(self.last_timestamp)
            else:
                self.sequence = random.randint(0, 9)

            self.last_timestamp = timestamp

            res_id = (
                (
                    timestamp - self.twepoch) << Snowflake.TIMESTAMP_LEFT_SHIFT |
                (padding_num << Snowflake.REGION_ID_SHIFT) |
                (self.worker_id << Snowflake.WORKER_ID_SHIFT) |
                self.sequence
            )

            return res_id

    def tail_next_millis(self, last_timestamp):
        timestamp = self.get_time()
        while timestamp <= last_timestamp:
            timestamp = self.get_time()
        return timestamp

    def get_time(self):
        return int(time.time() * 1000)



if __name__ == '__main__':
    print(Snowflake(0).generate())
    print(Snowflake(1).generate())
    print(Snowflake(2).generate())
    print(Snowflake(3).generate())
    print(Snowflake(3, 1).generate())
    pass
