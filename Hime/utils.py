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
# Set value in a nCDF file.
#
########################################################################################################################
def set_nc_value(nc_file, variable, value, mask=None, dims=None):
    ncf = nc.Dataset(nc_file, "a")

    var = ncf.variables[variable]
    if dims is not None:
        if type(dims) == list or type(dims) == tuple:
            for dim in dims:
                var = var[dim]
        elif type(dims) == int or type(dims) == float:
            var = var[dims]
        else:
            raise ValueError("dims should be number or list of numbers.")

    val = np.array(var[:])
    val_mask = np.zeros_like(val, dtype="int32")

    if mask is None:
        val_mask[val != -9999] = 1
    else:
        for cr in mask:
            val_mask[cr[1], cr[0]] = 1

    val[val_mask > 0] = value
    var[:] = val

    ncf.close()



