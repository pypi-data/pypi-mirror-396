#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: wxnacy@gmail.com
"""

"""
import logging

LOGFILE = '/tmp/wpy.log'

class CustomerFilter(logging.Filter):

    def filter(self, record):
        if ':' not in record.filename:
            record.filename = '{}:{}'.format( record.filename, record.lineno)
        return True

logging.basicConfig(
    filename=LOGFILE,
    format="[%(asctime)s] [%(levelname)-5s] [%(filename)-20s] %(message)s",
    level=logging.DEBUG
)

def create_logger(name):
    logger = logging.getLogger(name)
    logger.addFilter(CustomerFilter())
    return logger
