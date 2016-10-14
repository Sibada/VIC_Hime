#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import os

log = logging.getLogger("calib_log")

cmd_log = logging.StreamHandler()
cmd_log.setLevel(logging.DEBUG)

file_log = logging.FileHandler(os.path.split(os.path.realpath(__file__))[0] + "/calib_info.log")
file_log.setLevel(logging.INFO)

log.addHandler(cmd_log)
log.addHandler(file_log)