#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import os

logging.basicConfig(level=logging.DEBUG)
console_log = logging.StreamHandler()
console_log.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s',
                                           datefmt='%a, %d %b %Y %H:%M:%S'))

file_log = logging.FileHandler(os.path.split(os.path.realpath(__file__))[0] + "/calib_info.log")
file_log.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s',
                                        datefmt='%a, %d %b %Y %H:%M:%S'))

log = logging.getLogger("calib")

log.addHandler(console_log)
log.addHandler(file_log)