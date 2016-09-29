#!/usr/bin/env python
#  -*- coding: utf-8 -*-

"""
VIC forcing file creater

Using Konzelmann formula to estimate long wave radiation.

Reference:
Konzelmann T, Wal R S W V D, Greuell W, et al. Parameterization of global and longwave incoming radiation for the
Greenland Ice Sheet[J]. Global & Planetary Change, 1994, 9(1–2):143-164.

Yang H, Huafang L V, Qingfang H U, et al. Comparison of parametrization methods for calculating the downward long-wave
radiation over the North China Plain[J]. Qinghua Daxue Xuebao/journal of Tsinghua University, 2014, 54(5):590-595.
"""

from math import pi
from collections import OrderedDict
from scipy import interpolate as intp
import numpy as np
import pandas as pd
import datetime
import functools
import netCDF4 as nc

########################################################################################################################
#
# Read in atmospheric data of stations and coordinates of stations from text file.
#
# If incoming long and short wave radiations could not be provided, can choose to
# estimate them by provide sunshine durations.
########################################################################################################################
def read_stn_data(proj):
    creater_params=proj.proj_params["creater_params"]

    forcing_date = creater_params["forcing_date"]
    temp_file = creater_params["temp_file"]
    prec_file = creater_params["prec_file"]
    press_file = creater_params["press_file"]
    swdown_file = creater_params["swdown_file"]
    lwdown_file = creater_params["lwdown_file"]
    vp_file = creater_params["vp_file"]
    wind_file = creater_params["wind_file"]
    sh_file = creater_params["sh_file"]
    stn_coords_file = creater_params["stn_coords_file"]

    use_sh = creater_params["use_sh"]

    if stn_coords_file is None:
        raise ValueError("Stations coordinates file should be provided.")

    if temp_file is None or prec_file is None or press_file is None or vp_file is None or wind_file is None:
        raise ValueError("Atmospheric data type is not enough.")

    temp = np.array(pd.read_table(temp_file, sep = r"[\s,;]", header = None))
    prec = np.array(pd.read_table(prec_file, sep = r"[\s,;]", header = None))
    press = np.array(pd.read_table(press_file, sep = r"[\s,;]", header = None))
    vp = np.array(pd.read_table(vp_file, sep = r"[\s,;]", header = None))
    wind = np.array(pd.read_table(wind_file, sep = r"[\s,;]", header = None))

    coords = np.array(pd.read_table(stn_coords_file, sep = r"[\s,;]", header = None))

    if use_sh:
        if sh_file is None:
            raise ValueError("Sunshine hours data should be provided.")

        a_s = 0.25; b_s = 0.50
        sh = np.array(pd.read_table(sh_file, sep = r"[\s,;]", header = None))
        dates = pd.date_range(forcing_date, periods = sh.shape[0])

        swdown = np.ndarray(sh.shape)
        lwdown = np.ndarray(sh.shape)
        J = np.array([float(date.strftime("%j")) for date in dates])
        delta = 0.408 * np.sin(2*pi*J/365-1.39)
        dr = 1 + 0.033*np.cos(2*pi/365*J)
        for i in range(sh.shape[1]):
            lat = coords[i,1]*pi/180
            omegas = np.arccos(-np.tan(delta) * lat)
            Ra = 1366.66/pi*dr*(omegas*np.sin(lat)*np.sin(delta)+np.cos(lat)*np.cos(delta)*np.sin(omegas))
            N = omegas*24/pi
            Rs = (a_s + b_s*sh[:,i]/N)*Ra

            # Estimate incoming long wave radiation using Konzelmann equation.

            eps_ac = 0.23 + 0.848 * np.power(vp[:, i]*10/(temp[:, i]+273.15),1.0/7.0)
            s = (a_s + b_s*sh[:, i]/N)/(a_s + b_s)
            eps_a = 1-s+s*eps_ac
            Rld = eps_a * 5.67e-8 * np.power((temp[:,1]+273.15),4)

            swdown[:, i] = Rs
            lwdown[:, i] = Rld

    else:
        if swdown_file is None or lwdown_file is None:
            raise ValueError("Both incoming short wave and long wave radiation data should be provided.")
        lwdown = np.array(pd.read_table(lwdown_file, sep = r"[\s,;]", header = None))
        swdown = np.array(pd.read_table(swdown_file, sep = r"[\s,;]", header = None))

    return coords, temp, prec, press, swdown, lwdown, vp, wind

def create_forcing(proj, coords, temp, prec, press, swdown, lwdown, vp, wind):
    proj_name = proj.proj_params["proj_name"]
    creater_params=proj.proj_params["creater_params"]
    forcing_date = creater_params["forcing_date"]
    forcing_file = creater_params["forcing_file"]

    domain_file = proj.global_params["domain"][ "file_path"]
    if domain_file is None:
        raise ValueError("Domain file not set.")

    df = nc.Dataset(domain_file, "r", "NETCDF4")
    lon_size = df.dimensions['lon'].size
    lat_size = df.dimensions['lat'].size
    lons = np.array(df["lon"])
    lats = np.array(df["lat"])
    fv = df["mask"]._FillValue
    mask = np.array(df["mask"])
    mask[mask == fv], mask[mask != fv] = 0, 1
    df.close()

    # Choose interpolation method.
    if proj.proj_params["creater_params"]["itp_method"] == "idw":
        idp = proj.proj_params["creater_params"]["idw_params"]["idp"]
        maxd = proj.proj_params["creater_params"]["idw_params"]["maxd"]
    itp = functools.partial(idw, idp=idp, maxd=maxd)

    # Create forcing files for every year.
    dates = pd.date_range(forcing_date, periods = temp.shape[0])
    time_step = "days"
    years = np.unique(dates.year)
    for year in years:
        in_this_year = dates.year == year
        sub_dates = dates[in_this_year]
        time_len = len(sub_dates)
        since = datetime.datetime.strftime(sub_dates[0],  "%Y-%m-%d")

        nc_file_name = "%s/%s_forcing.%d.nc" % (forcing_file, proj_name, year)
        ff = nc.Dataset(nc_file_name, "w", "NETCDF4")
        print nc_file_name+" has been created to write."

        ff.createDimension("lon", lon_size)
        ff.createDimension("lat", lat_size)
        ff.createDimension("time", time_len)

        v = ff.createVariable("lon", "f8", ("lon"))
        v[:] = lons
        v.standard_name = "longtitude"
        v.units = "degrees_east"
        v.axis = "X"

        v = ff.createVariable("lat", "f8", ("lat"))
        v[:] = lats
        v.standard_name = "latitude"
        v.units = "degrees_north"
        v.axis = "Y"

        v = ff.createVariable("time", "i4", ("time"))
        v[:] = range(time_len)
        v.units = "%s since %s"% (time_step, since)
        v.calendar = "proleptic_gregorian"

        v = ff.createVariable("mask", "f8", ("lat", "lon"), fill_value=0.0)
        v[:] = mask
        v.long_name = "fraction of grid cell that is active domain mask."
        v.comment = "0 value indicates cell is not active."

        #############################################################
        # Write in atmospheric data.
        #############################################################
        v = ff.createVariable("tas", "f8", ("time", "lat", "lon"), fill_value=-9999)
        v.long_name = v.decsription = "AIR_TEMP"
        v.units = "C"
        itp(v, temp[in_this_year], coords, mask, lons, lats)

        v = ff.createVariable("prcp", "f8", ("time", "lat", "lon"), fill_value=-9999)
        v.long_name = v.decsription = "PREC"
        v.units = "mm/step"
        itp(v, prec[in_this_year], coords, mask, lons, lats)

        v = ff.createVariable("pres", "f8", ("time", "lat", "lon"), fill_value=-9999)
        v.long_name = v.decsription = "PRESSURE"
        v.units = "kPa"
        itp(v, press[in_this_year], coords, mask, lons, lats)

        v = ff.createVariable("dswrf", "f8", ("time", "lat", "lon"), fill_value=-9999)
        v.long_name = v.decsription = "SWDOWN"
        v.units = "W/m2"
        itp(v, swdown[in_this_year], coords, mask, lons, lats)

        v = ff.createVariable("dlwrf", "f8", ("time", "lat", "lon"), fill_value=-9999)
        v.long_name = v.decsription = "LWDOWN"
        v.units = "W/m2"
        itp(v, lwdown[in_this_year], coords, mask, lons, lats)

        v = ff.createVariable("vp", "f8", ("time", "lat", "lon"), fill_value=-9999)
        v.long_name = v.decsription = "VP"
        v.units = "kPa"
        itp(v, vp[in_this_year], coords, mask, lons, lats)

        v = ff.createVariable("wind", "f8", ("time", "lat", "lon"), fill_value=-9999)
        v.long_name = v.decsription = "WIND"
        v.units = "m/s"
        itp(v, wind[in_this_year], coords, mask, lons, lats)

        ff.close()

########################################################################################################################
#
# Inverse distance weight interpolation.
#
########################################################################################################################
def idw(nc_variable, stn_data, stn_coords, mask, lons, lats, idp=2, maxd=np.inf):
    # Find coordinates.
    sn = []
    cell_lons = []
    cell_lats = []
    s = -1
    for r in range(mask.shape[0]):
        for c in range(mask.shape[1]):
            s += 1
            if mask[r, c] == 0: continue
            sn.append(s)
            cell_lons.append(lons[c])
            cell_lats.append(lats[r])
    cell_coords = np.concatenate(([cell_lons], [cell_lats])).T

    # Creat weight matrix.
    W_o = np.ndarray((stn_coords.shape[0], len(sn)))
    for c in range(W_o.shape[1]):
        w = np.array([np.linalg.norm(cell_coords[c]-stn_coord) for stn_coord in stn_coords])
        w[w > maxd] = np.inf
        w = 1/np.power(w, idp)
        W_o[:, c] = w
    W_mask = ~np.isnan(stn_data) * 1
    stn_data[np.isnan(stn_data)] = 0

    # Interpolation.
    itp_data_o = np.dot(stn_data, W_o)
    itp_data_b = np.dot(W_mask, W_o)
    itp_data = itp_data_o / itp_data_b

    # Write in nCDF file.
    value = np.zeros(mask.shape[0] * mask.shape[1]) -9999
    for t in range(itp_data.shape[0]):
        value[sn] = itp_data[t]
        nc_variable[t, :] = value


########################################################################################################################
#
# Get the end date of atmospheric data.
#
########################################################################################################################
def get_end_date(proj, length, freq="D"):
    forcing_date = proj.proj_params["creater_params"]["forcing_date"]
    return pd.date_range(forcing_date, periods=length-1, freq=freq)[-1]