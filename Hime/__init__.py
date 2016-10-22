#!/usr/bin/env python
#  -*- coding: utf-8 -*-

from .version import version

import os
import logging

templates_path = os.path.split(os.path.realpath(__file__)) [0] + "/templates"

# Set logger
logging.basicConfig(level=logging.DEBUG)
console_log = logging.StreamHandler()
console_log.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s',
                                           datefmt='%Y-%m-%d %H:%M:%S'))

file_log = logging.FileHandler(os.path.split(os.path.realpath(__file__))[0] + "/calib_info.log")
file_log.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s',
                                        datefmt='%Y-%m-%d %H:%M:%S'))

log = logging.getLogger("Hime")

log.addHandler(console_log)
log.addHandler(file_log)