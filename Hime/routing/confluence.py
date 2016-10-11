#!/usr/bin/env python
# -*- coding: utf-8 -*-

from Hime.ascii_grid import Grid
from Hime import templates_path
from Hime.utils import xy_to_sn
from Hime.routing.uh_creater import create_rout
from math import acos, sin, cos, pi
from collections import OrderedDict
import numpy as np
import demjson


########################################################################################################################
#
# Load and save rout data.
#
########################################################################################################################
def load_rout_data(file_path):
    df = open(file_path, "r")
    rout_data = demjson.decode(df.readlines(), object_pairs_hook=OrderedDict)
    df.close()

    rout_data["basin"] = np.array(rout_data["basin"])
    rout_data["uh_cell"] = np.array(rout_data["uh_cell"])
    return rout_data


def write_rout_data(rout_data, file_path):
    rout_json = demjson.encode(rout_data)
    df = open(file_path, "w")
    df.writelines(rout_json)
    df.close()


########################################################################################################################
#
# Calculate daily runoff by convolution.
#
# uh_cell is the unit hydrograph of each cell and runoff_yield is daily runoff yield of each cell.
#
########################################################################################################################
def convolution(uh_cell, runoff_yield):

    pre = np.dot(uh_cell, runoff_yield)
    nrow = pre.shape[0]

    for c in range(1, pre.shape[1]):
        pre[c:, c] = pre[:nrow-c, c]
        pre[:c, c] = 0.0

    daily_runoff = pre.sum(axis=1)
    return daily_runoff

