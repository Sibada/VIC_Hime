#!/usr/bin/env python
# -*- coding: utf-8 -*-

from Hime.ascii_grid import Grid
from Hime import templates_path
from collections import OrderedDict
import numpy as np
import pandas as pd
import netCDF4 as nc
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


########################################################################################################################
#
# Provide a VIC output nCDF file with runoff variables, domain file and date range to output runoff data of the basin.
#
########################################################################################################################
def confluence(vic_out_file, rout_data, domain_file, start_date, end_date):
    sn = rout_data["sn"]
    uh_cell = rout_data["uh_cell"]

    vf = nc.Dataset(vic_out_file, "r")
    # TODO: Detect if it have variable names time, OUT_BASEFLOW and OUT_RUNOFF.

    time_units = vf.variables["time"].units
    calendar = vf.variables["time"].calendar
    ts = pd.date_range(start_date, end_date)
    t = nc.date2index(ts, time_units, calendar)

    baseflow = vf.variables["OUT_BASEFLOW"][t, sn]
    runoff = vf.variables["OUT_RUNOFF"][t, sn]
    vf.close()

    df = nc.Dataset(domain_file, "r")
    # TODO: Detect if it have variable names area.
    area = df.variables["area"][sn]

    runoff_yield = (runoff + baseflow) * area / 2073600000.0

    daily_runoff = convolution(uh_cell, runoff_yield)
    return daily_runoff


########################################################################################################################
#
# Transfer runoff series from daily series to monthly series.
#
########################################################################################################################
def gather_to_month(daily_runoff, start_date, end_date):
    ts = pd.date_range(start_date, end_date)
    d_runoff = pd.Series(daily_runoff, index=ts)
    monthly_runoff = d_runoff.resample("M", how="mean")
    return monthly_runoff