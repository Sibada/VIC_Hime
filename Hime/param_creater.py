#!/usr/bin/env python
#  -*- coding: utf-8 -*-

"""
VIC parameters file creater
"""

from Hime import log
from Hime.version import version as __version__
from Hime.utils import read_template
from Hime.ascii_grid import Grid
from Hime import templates_path
from collections import OrderedDict
from numpy import pi
import netCDF4 as nc
import numpy as np
import pandas as pd
import re, json
import datetime


########################################################################################################################
#
# creater_params should be a dict like that:
#
# creater_params = {
#     "soil_file": ".../soil.txt",
#     "fract_file": None,
#     "snow_band": 1,
#     "n_layer": 3,
#     "organic": False,
#     "compute_treeline": False,
#
#     "veg_file": ".../veg_param.txt",
#     "n_rootzones": 3,
#
#     "veg_lib_file": ".../veglib.LDAS",
#     "veg_class": 12,
#     "veglib_vegcover": False,
#
#     "dec": 6,
#     "params_file": ".../params.nc",
#     "domain_file": ".../domain.nc"
# }
#
########################################################################################################################

########################################################################################################################
#
# Read classic soil parameters file.
#
########################################################################################################################
def read_soil_file(creater_params, soil_path=None):

    n_layer = creater_params["n_layer"]
    organic = creater_params["organic"]
    compute_treeline = creater_params["compute_treeline"]

    if soil_path is None:
        soil_path = creater_params["soil_file"]

    expected_ncol = 12 * n_layer + 17
    if organic:
        expected_ncol += 9
    if compute_treeline:
        expected_ncol += 1

    soil = pd.read_table(soil_path, sep="[,\s]", comment="#", header=None)
    if soil.shape[1] < expected_ncol:
        raise ValueError("Columns of soil parameter file (%d) is not enough (%d demands)."
                         % (len(soil.columns), expected_ncol))

    return soil


########################################################################################################################
#
# Read classic vegetation parameters file.
#
########################################################################################################################
def read_veg_file(creater_params, veg_path=None):
    n_rz = creater_params["n_rootzones"]
    if veg_path is None:
        veg_path = creater_params["veg_file"]

    vf = open(veg_path, "r")
    vf_lines = vf.readlines()
    vf.close()

    l = 0
    veg = OrderedDict()
    while l < len(vf_lines):
        line = vf_lines[l]
        line_split = re.split("[\s\r\t\n]", line.strip())
        cell = int(line_split[0])
        nvegc = int(line_split[1])
        l += 1

        vegcs = []
        for t in range(nvegc):
            line = vf_lines[l]
            sub_line_split = re.split("[\s\r\t\n]", line.strip())
            sub_line_split = np.array(sub_line_split)
            veg_info = OrderedDict({"veg_class": int(sub_line_split[0])})
            veg_info.update({"Cv": float(sub_line_split[1])})
            veg_info.update({"root_depth": [float(r) for r in sub_line_split[range(2, n_rz*2+2, 2)]]})
            veg_info.update({"root_fract": [float(r) for r in sub_line_split[range(3, n_rz*2+3, 2)]]})

            vegcs.append(veg_info)
            l += 1
        veg.update({cell: vegcs})

    return veg


########################################################################################################################
#
# Read classic veg lib parameters file.
#
########################################################################################################################
def read_veg_lib(creater_params, veg_lib_path=None):
    if veg_lib_path is None:
        veg_lib_path = creater_params["veg_lib_file"]

    veg_lib = pd.read_table(veg_lib_path, sep="[,\s]", comment="#", header=None)
    veg_lib.rename(columns={"#Class": "Class"}, inplace=True)
    creater_params["veg_class"] = veg_lib.shape[0]

    return veg_lib


########################################################################################################################
#
# Create parameters file and domain file which VIC Image Driver needs.
#
########################################################################################################################
def create_params_file(creater_params, out_params_path=None, out_domain_path=None):
    snow_band = creater_params["snow_band"]
    veg_class = creater_params["veg_class"]
    root_zone = creater_params["n_rootzones"]
    n_layer = creater_params["n_layer"]
    organic = creater_params["organic"]
    compute_treeline = creater_params["compute_treeline"]
    veglib_vegcover = creater_params["veglib_vegcover"]

    soil = read_soil_file(creater_params)
    veg = read_veg_file(creater_params)
    veg_lib = read_veg_lib(creater_params)
    params_tem = read_template(templates_path + "/params_file.template")

    ncell = soil.shape[0]

    if out_params_path is None:
        out_params_path = creater_params["params_file"]
    if out_domain_path is None:
        out_domain_path = creater_params["domain_file"]

    lons_value, lats_value, cellsize, sn = make_grid(np.array(soil[3]), np.array(soil[2]), creater_params["dec"])
    nx = len(lons_value)
    ny = len(lats_value)

    #######################################################################
    # Write parameters file.
    #######################################################################
    params = nc.Dataset(out_params_path, "w", "NETCDF4")
    log.debug(out_params_path)

    params.createDimension("lon", nx)
    params.createDimension("lat", ny)
    params.createDimension("nlayer", n_layer)
    params.createDimension("snow_band", snow_band)
    params.createDimension("veg_class", veg_class)
    params.createDimension("root_zone", root_zone)
    params.createDimension("month", 12)

    for dimension in params_tem["dimensions"]:
        if dimension["format"] == "int": datatype = "i4"
        if dimension["format"] == "double": datatype = "f8"

        v = params.createVariable(dimension["variable"], datatype, (dimension["dimension"]))
        v.units = dimension["units"]
        v.long_name = dimension["long_name"]

    params["lon"][:] = lons_value
    params["lat"][:] = lats_value
    params["layer"][:] = range(n_layer)
    params["snow_band"][:] = range(snow_band)
    params["veg_class"][:] = range(veg_class)
    params["root_zone"][:] = range(root_zone)
    params["month"][:] = range(12)

    # ----------------------------------------------------------------------
    # Write soil parameters part of parameters file.
    # ----------------------------------------------------------------------
    soil_part = range(35)
    del soil_part[32:34]
    if not compute_treeline:
        del soil_part[-1]
    if not organic:
        del soil_part[21:24]

    variables = params_tem["variables"]
    col = 0
    for i in soil_part:
        variable = variables[i]
        n_value = variable["n_value"]
        if variable["format"] == "int": datatype = "i4"
        if variable["format"] == "double": datatype = "f8"

        if n_value == "Nlayer": dim = ("nlayer", "lat", "lon")
        else: dim = ("lat", "lon")
        v = params.createVariable(variable["variable"], datatype, dim, fill_value=-9999)
        v.description = variable["description"]
        v.units = variable["units"]

        log.info("Write "+variable["variable"])
        value = np.zeros(nx * ny) - 9999
        if n_value == "Nlayer":
            for l in range(n_layer):
                value[sn] = np.array(soil[col])
                v[l, :] = value
                col += 1
        else:
            value[sn] = np.array(soil[col])
            v[:] = value
            col += 1
    # ----------------------------------------------------------------------
    # Write vegetation parameters part of parameters file.
    # ----------------------------------------------------------------------
    veg_part = range(35, 39)
    for i in veg_part:
        variable = variables[i]
        varname = variable["variable"]
        if variable["format"] == "int": datatype = "i4"
        if variable["format"] == "double": datatype = "f8"

        if varname == "Nveg":
            dim = ("lat", "lon")
        elif varname == "Cv":
            dim = ("veg_class", "lat", "lon")
        else:
            dim = ("veg_class", "root_zone", "lat", "lon")
        v = params.createVariable(varname, datatype, dim, fill_value=-9999)
        v.description = variable["description"]
        v.units = variable["units"]

        log.info("Write " + variable["variable"])
        value = np.zeros(nx * ny) -9999
        if varname == "Nveg":
            value[sn] = np.array([len(vegs) for vegs in veg.values()])
            v[:] = value

        if varname == "Cv":
            other_type_Cv = np.ones(ncell)
            for cla in range(veg_class-1):
                cv = np.zeros(ncell)
                for cell in veg.keys():
                    for veg_info in veg[cell]:
                        if veg_info["veg_class"] == cla:
                            cv[cell-1] = veg_info["Cv"]
                            other_type_Cv[cell-1] -= veg_info["Cv"]
                value[sn] = cv
                v[cla, :] = value
            value[sn] = other_type_Cv
            v[11, :] = value

        if varname == "root_depth":
            for cla in range(veg_class):
                for rz in range(root_zone):
                    rd = np.zeros(ncell)
                    for cell in veg.keys():
                        for veg_info in veg[cell]:
                            if veg_info["veg_class"] == cla:
                                rd[cell-1] = veg_info["root_depth"][rz]
                    value[sn] = rd
                    v[cla, rz, :] = value

        if varname == "root_fract":
            for cla in range(veg_class):
                for rz in range(root_zone):
                    rf = np.zeros(ncell)
                    for cell in veg.keys():
                        for veg_info in veg[cell]:
                            if veg_info["veg_class"] == cla:
                                rf[cell-1] = veg_info["root_fract"][rz]
                    value[sn] = rf
                    v[cla, rz, :] = value

    # ----------------------------------------------------------------------
    # Write vegetation library part of parameters file.
    # ----------------------------------------------------------------------
    veg_lib_part = range(39, 52)
    if not veglib_vegcover:
        veg_lib_part.remove(43)

    col = 1  # Column 0 is vegetation class
    for i in veg_lib_part:
        variable = variables[i]
        n_value = variable["n_value"]
        if variable["format"] == "int": datatype = "i4"
        if variable["format"] == "double":datatype = "f8"

        if n_value == "veg_class":
            dim = ("veg_class", "lat", "lon")
        else:
            dim = ("veg_class", "month", "lat", "lon")
        v = params.createVariable(variable["variable"], datatype, dim, fill_value=-9999)
        v.description = variable["description"]
        v.units = variable["units"]

        log.info("Write " + variable["variable"])
        value = np.zeros(nx * ny) -9999
        if n_value == "veg_class":
            for cla in range(veg_class):
                vegparam = np.zeros(ncell) + veg_lib[col][cla]
                value[sn] = vegparam
                v[cla, :] = value
            col += 1

        else:
            for month in range(12):
                for cla in range(veg_class):
                    vegparam = np.zeros(ncell) + veg_lib[col][cla]
                    value[sn] = vegparam
                    v[cla, month, :] = value
                col += 1

    # Create mask.
    v = params.createVariable("mask", "i4", ("lat", "lon"), fill_value=0)
    value = np.zeros(nx * ny)
    value[sn] = np.zeros(ncell) + 1
    v[:] = value

    params.description = "VIC parameter file created by VIC Hime " + __version__ + " at " + datetime.datetime.now().\
        strftime('%Y-%m-%d, %H:%M:%S')
    params.close()

    #######################################################################
    # Write domain file.
    #######################################################################

    log.info("Writing domain file %s ..." % out_domain_path)
    domain = nc.Dataset(out_domain_path, "w", "NETCDF4")

    domain.createDimension("lon", nx)
    domain.createDimension("lat", ny)

    domain_vars = params_tem["domain"]
    fract_file = creater_params["fract_file"]

    value = np.zeros(nx * ny)
    for domain_var in domain_vars:
        varname = domain_var["variable"]
        if domain_var["format"] == "int":
            datatype = "i4"
        if domain_var["format"] == "double":
            datatype = "f8"

        if varname == "lon":
            dim = ("lon",)
        elif varname == "lat":
            dim = ("lat",)
        else:
            dim = ("lat", "lon")
        v = domain.createVariable(varname, datatype, dim, fill_value = 0)
        v.units = domain_var["units"]
        v.long_name = domain_var["long_name"]

        if varname == "lon":
            v[:] = lons_value
            v.axis = "X"
        if varname == "lat":
            v[:] = lats_value
            v.axis = "Y"
        if varname == "frac":
            if fract_file is not None:
                fract = Grid(fract_file)
                if not fract.ncol == nx and fract.nrow == ny:
                    raise ValueError("Size of fraction file grid is not suit.")
                v[:] = fract.value
            else:
                value[sn] = np.zeros(ncell) +1.0
                v[:] = value
        if varname == "mask":
            value[sn] = np.zeros(ncell) + 1
            v[:] = value
        if varname == "area":
            lats = np.array(soil[2])
            areas = 2 * (cellsize*pi/180)*6371393*6371393*np.cos(lats*pi/180)*np.sin(cellsize*pi/360)
            value[sn] = areas
            v[:] = value

        domain.description = "VIC domain file created by VIC Hime " + __version__ + " at "\
                             + datetime.datetime.now().strftime('%Y-%m-%d, %H:%M:%S')
    domain.close()
    log.info("Files have been writen.")


########################################################################################################################
#
# Transfer coordinates to grids information.
#
########################################################################################################################
def make_grid(lon, lat, dec):
    lon_uni = np.unique(np.round(lon, dec))
    lat_uni = np.unique(np.round(lat, dec))

    ncol = len(lon_uni)
    nrow = len(lat_uni)

    if ncol <= 1 and nrow <= 1:
        raise ValueError("Only a single grid is not avaliable.")

    if ncol > 1:
        xdivs = lon_uni[1:ncol] - lon_uni[0:ncol - 1]

    if nrow > 1:
        ydivs = lat_uni[1:nrow] - lat_uni[0:nrow - 1]

    if ncol > 1 and np.unique(xdivs) > 1 or nrow > 1 and np.unique(ydivs) > 1:
        raise ValueError("Coordinates of cells are not standard coordinates of grid.")

    if ncol > 1:
        cellsize = xdivs[0]
    else:
        cellsize = ydivs[0]

    xll = lon_uni.min()
    yll = lat_uni.min()

    col = (lon - xll)/cellsize + 1
    row = (lat - yll)/cellsize + 1

    sn = (row - 1) * ncol + col - 1
    sn = sn.astype("int32")  # Only integer can be used as index. (Python is significant shit than R at sth like that.)

    return lon_uni, lat_uni, cellsize, sn

