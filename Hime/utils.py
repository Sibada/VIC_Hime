#!/usr/bin/env python
# -*- coding: utf-8 -*-

from collections import OrderedDict
import netCDF4 as nc
import numpy as np
import json


########################################################################################################################
#
# Read output information template file.
#
########################################################################################################################
def read_template(template_file):
    tf = open(template_file)
    tem_lines = tf.readlines()
    tf.close()
    try:
        tem_str = "".join(tem_lines)
        tem = json.loads(tem_str, object_pairs_hook=OrderedDict)
    except Exception:
        raise ValueError("Format of parameter template file uncorrect.")
    return tem


########################################################################################################################
#
# Row and column to series number.
#
########################################################################################################################
def xy_to_sn(x, y, nx=None, ny=None):
    if nx is None or ny is None:
        nx, ny = x.max() + 1, y.max() + 1

    sn = (y - 1) * nx + x - 1
    return sn


########################################################################################################################
#
# Amend value in a nCDF file.
#
########################################################################################################################
def set_value_nc(nc_file, variable, value, cell_id=None, col_row=None, all=False):
    ncf = nc.Dataset(nc_file, "a")

    var = ncf.variables[variable]
    var_val = np.array(var[:])
    val_mask = np.zeros_like(var_val, dtype="int32")

    if cell_id is not None:
        val_mask[ncf.variables["gridcel"][:] in cell_id] = 1

    if col_row is not None:
        for cr in col_row:
            val_mask[cr[1], cr[0]] = 1

    if all:
        val_mask[var_val != -9999] = 1

    var_val[val_mask > 0] = value
    var[:] = var_val

    ncf.close()


########################################################################################################################
#
# Amend value in a nCDF file.
#
########################################################################################################################
def set_soil_depth(nc_file, layer, value, cell_id=None, col_row=None):
    ncf = nc.Dataset(nc_file, "a")

    var = ncf.variables["depth"]
    var_val = np.array(var[layer-1, :])
    val_mask = np.zeros_like(var_val, dtype="int32")

    if cell_id is not None:
        val_mask[ncf.variables["gridcel"][:] in cell_id] = 1

    if col_row is not None:
        for cr in col_row:
            val_mask[cr[1], cr[0]] = 1

    var_val[val_mask > 0] = value
    var[layer-1, :] = var_val

    ncf.close()


