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


def write_rout_data(rout_data, out_file):
    rout_json = demjson.encode(rout_data)
    df = open(out_file, "w")
    df.writelines(rout_json)

    df.writelines(["\n", "\n"])  # Write a new empty line for reading by R.
    df.close()
    print "Rout data has been write to file %s" % out_file


########################################################################################################################
#
# Calculate daily runoff by convolution.
#
# uh_cell is the unit hydrograph of each cell and runoff_yield is daily runoff yield of each cell.
#
########################################################################################################################
def convolution(uh_cell, runoff_yield):
    print "Making convolution..."
    pre = np.dot(runoff_yield, uh_cell)
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
    basin = rout_data["basin"]
    uh_cell = rout_data["uh_cell"]

    print "Read data from %s" % vic_out_file
    vf = nc.Dataset(vic_out_file, "r")
    # TODO: Detect if it have variable names time, OUT_BASEFLOW and OUT_RUNOFF.

    nctime = vf.variables["time"]
    calendar = vf.variables["time"].calendar
    ts = pd.date_range(start_date, end_date)
    ts_dt = [ti.to_datetime() for ti in ts]
    t = nc.date2index(ts_dt, nctime, calendar)

    baseflow_t = vf.variables["OUT_BASEFLOW"][t, :]
    runoff_t = vf.variables["OUT_RUNOFF"][t, :]
    vf.close()

    baseflow = np.zeros((len(t), len(basin)))
    runoff = np.zeros((len(t), len(basin)))
    for c in range(len(basin)):
        baseflow[:, c] = baseflow_t[:, basin[c, 1], basin[c, 0]]
        runoff[:, c] = runoff_t[:, basin[c, 1], basin[c, 0]]

    df = nc.Dataset(domain_file, "r")
    # TODO: Detect if it have variable names area.
    area = np.zeros(len(basin))
    for c in range(len(basin)):
        area[c] = df.variables["area"][basin[c, 1], basin[c, 0]]

    # Runoff yield of mm should transfer to meters and divided by num of seconds in a day to transfer to m^3/s.
    runoff_yield = (runoff + baseflow) * area / 86400000.0

    # Convolution.
    daily_runoff = pd.Series(convolution(uh_cell, runoff_yield), index=ts)

    return daily_runoff


########################################################################################################################
#
# Transfer runoff series from daily series to monthly series.
#
########################################################################################################################
def gather_to_month(daily_runoff):
    monthly_runoff = daily_runoff.resample("M").mean()
    return monthly_runoff


########################################################################################################################
#
# Out put runoff data.
#
########################################################################################################################
def write_runoff_data(runoff_data, out_file):
    runoff_data.to_csv(out_file, sep="\t")
    print "File %s has been write." % out_file

