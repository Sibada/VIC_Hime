#!/usr/bin/env python
#  -*- coding: utf-8 -*-

"""
Run VIC Image Driver.
"""

import os

def vic_exec(driver_path, global_path, log_path = None, n_proc = 4):
    sh = "mpiexec -np %d %s -g %s" % (n_proc, driver_path, global_path)
    if log_path is not None:
        sh = sh + " " + log_path
    return os.system(sh)
