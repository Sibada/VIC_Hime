#!/usr/bin/env python
#  -*- coding: utf-8 -*-

"""
Run VIC Image Driver.
"""

import os


def vic_exec(driver_path, global_path, log_path=None, mpi=False, n_cores=4):
    if mpi:
        sh = "mpiexec -np %d %s -g %s" % (n_cores, driver_path, global_path)
    else:
        sh = "%s -g %s" % (driver_path, global_path)
    if log_path is not None:
        sh = sh + " " + log_path
    print "Exec shell: " + sh
    return os.system(sh)

