#!/usr/bin/env python
#  -*- coding: utf-8 -*-

"""
Run VIC Image Driver.
"""

import subprocess as sp


def vic_exec(driver_path, global_path, mpi=False, n_cores=4):
    if mpi:
        sh = ["mpiexec", "-np", n_cores, driver_path, "-g", global_path]
    else:
        sh = [driver_path, "-g", global_path]

    print "Exec shell: "
    print sh

    spc = sp.Popen(sh, stdout=sp.PIPE, stderr=sp.PIPE)
    status = spc.wait()
    logs = spc.stdout.readlines()
    logs.append(spc.stderr.readlines())
    return status, logs

