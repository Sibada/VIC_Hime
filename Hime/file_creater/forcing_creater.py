#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
VIC forcing file creater

Using Konzelmann formula to estimate long wave radiation.

Reference:
Konzelmann T, Wal R S W V D, Greuell W, et al. Parameterization of global and longwave incoming radiation for the
Greenland Ice Sheet[J]. Global & Planetary Change, 1994, 9(1–2):143-164.

Yang H, Huafang L V, Qingfang H U, et al. Comparison of parametrization methods for calculating the downward long-wave
radiation over the North China Plain[J]. Qinghua Daxue Xuebao/journal of Tsinghua University, 2014, 54(5):590-595.
"""

from Hime import log
from Hime.version import version as __version__
from Hime import templates_path
from Hime.utils import read_template

from math import pi
from collections import OrderedDict
import numpy as np
import pandas as pd
import datetime as dt
import functools
import netCDF4 as nc

########################################################################################################################
#
# Read in atmospheric data of stations and coordinates of stations from text file.
#
# If incoming long and short wave radiations could not be provided, can choose to
# estimate them by provide sunshine durations.
########################################################################################################################

# forcing_params is a dict or OrderedDict include those:
#
# {
#   "variables": [{"data_path": "path", "coords_path": "path", "var_name": "var_name", "type": "desc"}, ...],
#   "start_time": [year, month, day],
#   "end_time": [year, month, day],
#   "use_sh": ["coords_path": "coords_path", "sh_path", "temp_path", "vp_path", "sw_var_name", "lw_var_name"],
# }
# type must be one of those: TEMP, PREC, PRESS, SWDOWN, LWDOWN, VP, WIND
def read_stn_data(forcing_params):
    variables = forcing_params["variables"]
    st_ymd = forcing_params["start_time"]
    start_time = dt.datetime(st_ymd[0], st_ymd[1], st_ymd[2])
    ed_ymd = forcing_params["end_time"]
    end_time = dt.datetime(ed_ymd[0], ed_ymd[1], ed_ymd[2])
    freq = forcing_params["freq"]
    use_sh = forcing_params["use_sh"]

    # ###################################################################################
    #
    # Read atmospheric data.
    #
    # ###################################################################################
    if len(variables) < 1:
        raise ValueError("Must provide at lease one variable.")

    var_data = []
    for variable in variables:
        log.info("Reading %s" % variable["data_path"])
        data = np.array(pd.read_table(variable["data_path"], sep=r"[\s,;]", header=None))
        coords = np.array(pd.read_table(variable["coords_path"], sep=r"[\s,;]", header=None))
        new_var = OrderedDict({
            "data": data,
            "coords": coords,
            "var_name": variable["var_name"],
            "type": variable["type"]
        })
        var_data.append(new_var)

    data_length = var_data[0]["data"].shape[0]

    # TODO: Check if the length and col nums are equal

    ts = pd.date_range(start_time, periods=data_length)

    # ###################################################################################
    #
    # Estimate incoming short and long wave radiation by providing sunshine hours data.
    #
    # ###################################################################################
    if use_sh is not None:
        coords_path = use_sh[0]
        sh_path = use_sh[1]
        temp_path = use_sh[2]
        vp_path = use_sh[3]

        sw_var_name = use_sh[4]
        lw_var_name = use_sh[5]

        # TODO: Check if those before is empty string.
        coords = np.array(pd.read_table(coords_path, sep=r"[\s,;]", header=None))
        sh = np.array(pd.read_table(sh_path, sep=r"[\s,;]", header=None))
        temp = np.array(pd.read_table(temp_path, sep=r"[\s,;]", header=None))
        vp = np.array(pd.read_table(vp_path, sep=r"[\s,;]", header=None))

        swdown = np.ndarray(sh.shape)
        lwdown = np.ndarray(sh.shape)

        a_s, b_s = 0.25, 0.50

        J = np.array([float(date.strftime("%j")) for date in ts])
        delta = 0.408 * np.sin(2*pi*J/365-1.39)
        dr = 1 + 0.033*np.cos(2*pi/365*J)

        for i in range(sh.shape[1]):
            lat = coords[i, 1] * pi / 180
            omegas = np.arccos(-np.tan(delta) * lat)
            Ra = 1366.66 / pi * dr * (omegas * np.sin(lat) * np.sin(delta) +
                                      np.cos(lat) * np.cos(delta) * np.sin(omegas))
            N = omegas * 24 / pi
            Rs = (a_s + b_s * sh[:, i] / N) * Ra

            # Estimate incoming long wave radiation using Konzelmann equation.

            eps_ac = 0.23 + 0.848 * np.power(vp[:, i] * 10 / (temp[:, i] + 273.15), 1.0 / 7.0)
            s = (a_s + b_s * sh[:, i] / N) / (a_s + b_s)
            eps_a = 1 - s + s * eps_ac
            Rld = eps_a * 5.67e-8 * np.power((temp[:, 1] + 273.15), 4)

            swdown[:, i] = Rs
            lwdown[:, i] = Rld

        swdown_var = OrderedDict({
            "data": swdown,
            "coords": coords,
            "var_name": sw_var_name,
            "type": "SWDOWN"
        })
        lwdown_var = OrderedDict({
            "data": lwdown,
            "coords": coords,
            "var_name": lw_var_name,
            "type": "LWDOWN"
        })
        var_data.append(swdown_var)
        var_data.append(lwdown_var)

    forcing_data = OrderedDict()
    forcing_data["variables"] = var_data
    forcing_data["start_time"] = start_time
    forcing_data["end_time"] = end_time
    forcing_data["freq"] = freq

    return forcing_data


########################################################################################################################
#
# Create forcing files by interpolation.
#
########################################################################################################################

# create_params is a dict or OrderedDict include those:
#
# {
#   "forcing_path": "domain_file",
#   "domain_file": "domain_file",
#   "idw_params": [idp, maxd, maxp],
#   "krige_params": ["vgm_model"]
# }
def create_forcing(forcing_data, create_params):
    start_time = forcing_data["start_time"]
    end_time = forcing_data["end_time"]
    freq = forcing_data["freq"]

    ts = pd.date_range(start_time, end=end_time, freq=freq)

    forcing_path = create_params["forcing_path"]
    domain_file = create_params["domain_file"]

    # ######################################################### Read mask grid.
    domain = nc.Dataset(domain_file, "r", "NETCDF4")
    nlon = domain.dimensions['lon'].size
    nlat = domain.dimensions['lat'].size
    lons = np.array(domain["lon"])
    lats = np.array(domain["lat"])
    fv = domain["mask"]._FillValue
    mask = np.array(domain["mask"])
    mask[mask == fv], mask[mask != fv] = 0, 1
    domain.close()

    # Get coordinates of grids to be interpolated.
    sn, grid_lons, grid_lats = [], [], []; s = -1
    for r in range(mask.shape[0]):
        for c in range(mask.shape[1]):
            s += 1
            if mask[r, c] == 0:
                continue
            sn.append(s)
            grid_lons.append(lons[c])
            grid_lats.append(lats[r])
    grid_coords = np.concatenate(([grid_lons], [grid_lats])).T

    # ############################################ Choose interpolation method.
    if create_params["idw_params"] is not None:
        idp = create_params["idw_params"][0]
        maxd = create_params["idw_params"][1]
        maxp = create_params["idw_params"][2]
        itp = functools.partial(idw, idp=idp, maxd=maxd)

    # #################################### Create forcing files for every year.
    time_step = "days"
    years = np.unique(ts.year)
    for year in years:
        in_this_year = ts.year == year
        sub_ts = ts[in_this_year]
        time_len = len(sub_ts)
        since = dt.datetime.strftime(sub_ts[0], "%Y-%m-%d")

        nc_file_name = "%s%d.nc" % (forcing_path, year)

        # ######################################## Create and open netCDF file.
        ff = nc.Dataset(nc_file_name, "w", "NETCDF4")
        ff.description = "VIC parameter file created by VIC Hime " + __version__ + " at " +\
                         dt.datetime.now().strftime('%Y-%m-%d, %H:%M:%S')

        log.info(nc_file_name + " has been created to write.")

        ff.createDimension("lon", nlon)
        ff.createDimension("lat", nlat)
        ff.createDimension("time", time_len)

        v = ff.createVariable("lon", "f8", ("lon",))
        v[:] = lons
        v.standard_name = "longitude"
        v.units = "degrees_east"
        v.axis = "X"

        v = ff.createVariable("lat", "f8", ("lat",))
        v[:] = lats
        v.standard_name = "latitude"
        v.units = "degrees_north"
        v.axis = "Y"

        v = ff.createVariable("time", "i4", ("time",))
        v[:] = range(time_len)
        v.units = "%s since %s" % (time_step, since)
        v.calendar = "proleptic_gregorian"

        v = ff.createVariable("mask", "f8", ("lat", "lon"), fill_value=0.0)
        v[:] = mask
        v.long_name = "fraction of grid cell that is active domain mask."
        v.comment = "0 value indicates cell is not active."

        forc_tem = read_template(templates_path + "/forc_file.template")
        #######################################################################
        # Write in atmospheric data.
        #######################################################################
        for variable in forcing_data["variables"]:
            var_name = variable["var_name"]
            data = variable["data"]
            coords = variable["coords"]
            var_type = variable["type"]
            v = ff.createVariable(var_name, "f8", ("time", "lat", "lon"), fill_value=-9999)

            if forc_tem.get(var_type) is not None:
                v.units = forc_tem.get(var_type)[0]
                v.long_name = forc_tem.get(var_type)[1]

            # Interpolation
            itp_data = itp(data[in_this_year], coords, grid_coords)
            values = np.zeros((time_len, mask.shape[0] * mask.shape[1])) - 9999.0
            values[:, sn] = itp_data
            v[:] = values

        ff.close()
    log.info("Forcing file creating completed.")


########################################################################################################################
#
# Inverse distance weight interpolation.
#
########################################################################################################################
def idw(stn_data, stn_coords, grid_coords, idp=2, maxd=np.inf):

    n_grids = grid_coords.shape[0]

    # Creat weight matrix.
    W_o = np.ndarray((stn_coords.shape[0], n_grids))
    for c in range(W_o.shape[1]):
        w = np.array([np.linalg.norm(grid_coords[c]-stn_coord) for stn_coord in stn_coords])
        w[w > maxd] = np.inf
        w = 1/np.power(w, idp)
        W_o[:, c] = w
    W_mask = ~np.isnan(stn_data) * 1
    stn_data[np.isnan(stn_data)] = 0

    # Interpolation.
    itp_data_o = np.dot(stn_data, W_o)
    itp_data_b = np.dot(W_mask, W_o)
    itp_data = itp_data_o / itp_data_b

    return itp_data
