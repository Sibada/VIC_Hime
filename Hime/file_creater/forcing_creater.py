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
import numpy as np
import pandas as pd
import datetime
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

    dates = pd.date_range(forcing_date, periods = temp.shape[0])
    years = np.unique(dates.year)
    for year in years:
        ff = nc.Dataset("%s/%s_forcing.%d.nc" % (forcing_file, proj_name, year), "w", "NETCDF4")

        ff.close()
    # Todo
########################################################################################################################
#
# Get the end date of atmospheric data.
#
########################################################################################################################
def get_end_date(proj, length, freq="D"):
    forcing_date = proj.proj_params["creater_params"]["forcing_date"]
    return pd.date_range(forcing_date, periods=length-1, freq=freq)[-1]