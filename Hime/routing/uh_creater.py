#!/usr/bin/env python
# -*- coding: utf-8 -*-

from Hime.ascii_grid import Grid
from Hime import templates_path
from Hime.utils import xy_to_sn
from math import acos, sin, cos, pi
from collections import OrderedDict
import numpy as np


########################################################################################################################
#
# Read direction grid file and transfer to integer.
#
########################################################################################################################
def read_direc(direc_path):
    direc = Grid(direc_path)
    direc.value = direc.value.astype("int32")
    direc.value[direc.value < 0] = 0
    return direc


########################################################################################################################
#
# Create site of the next cell.
#
########################################################################################################################
def next_cell(direc, arc_dir_code=False):
    # Direction code.
    if arc_dir_code:
        dx = {64: 0,
              128: 1,
              1: 1,
              2: 1,
              4: 0,
              8: -1,
              16: -1,
              32: -1}
        dy = {64: 1,
              128: 1,
              1: 0,
              2: -1,
              4: -1,
              8: -1,
              16: 0,
              32: 1}
        print "Use ArcInfo direction code."
    else:
        dx = {1: 0,
              2: 1,
              3: 1,
              4: 1,
              5: 0,
              6: -1,
              7: -1,
              8: -1}
        dy = {1: 1,
              2: 1,
              3: 0,
              4: -1,
              5: -1,
              6: -1,
              7: 0,
              8: 1}
        print "Use default direction code."

    next_x = direc.value.copy()
    next_y = direc.value.copy()

    # Find x y site of next cell.
    for x in range(direc.ncol):
        for y in range(direc.nrow):
            if direc.value[y, x] == 0:
                continue
            direc_v = int(direc.value[y, x])
            next_x[y, x] = x + dx[direc_v]
            next_y[y, x] = y + dy[direc_v]

    return next_x, next_y


########################################################################################################################
#
# Find out all cells belong to the basin control by the hydrology station.
#
# station is a dict like that:
# station = {"name": "Boluo",
#  "x": 45, # Column of the grid cell where station located in.
#  "y": 26  # Row of the grid cell where station located in.
# }
#
########################################################################################################################
def discovery_basin(station, next_x, next_y):
    stn_x = station["x"]
    stn_y = station["y"]

    nrow = next_x.shape[0]
    ncol = next_x.shape[1]

    in_basin = np.zeros_like(next_x)
    in_basin[stn_y, stn_x] = 1

    basin = []

    for y in range(nrow):
        for x in range(ncol):
            if next_x[y, x] <= 0:
                continue

            prev_xy = [[-1, -1], [-1, -1], [-1, -1], [-1, -1], [-1, -1]]  # A list used for detect circle.
            ix, iy = x, y
            while True:
                # Detect circle.
                if [ix, iy] in prev_xy:
                    print "Warning: circle detected at grid cell (%d, %d). This cell will set to 0." % (ix, iy)
                    next_x[iy, ix] = 0
                    next_y[iy, ix] = 0
                    break

                if ix >= ncol or ix < 0 or iy >= nrow or iy < 0:
                    break
                if in_basin[iy, ix] > 0:
                    basin.append([x, y])
                    in_basin[iy, ix] = 1
                    break
                if next_x[iy, ix] <= 0:
                    break

                # Refresh list for circle detection.
                prev_xy.pop()
                prev_xy.insert(0, [ix, iy])

                # Go to next grid cell.
                ix, iy = next_x[iy, ix], next_y[iy, ix]

    basin = np.array(basin)
    print "%d cells in this basin." % len(basin)
    return basin


def get_uh_m(basin, direc, veloc, diffu, next_x, next_y):
    nrow = next_x.shape[0]
    ncol = next_x.shape[1]
    xcor = direc.xcor
    ycor = direc.ycor
    csize = direc.csize

    R = 6371393.0
    dt = 3600.0
    le = 48

    t = np.arange(0.0, dt * (le+1), dt)

    uh_m = np.zeros((le+1, nrow, ncol))

    for cell in basin:
        x, y = cell[0], cell[1]

        lng = (x * csize + csize/2 + xcor) * pi/180
        nlng = (next_x[y, x] * csize + csize/2 + xcor) * pi/180
        lat = (y * csize + csize/2 + ycor) * pi/180
        nlat = (next_y[y, x] * csize + csize/2 + ycor) * pi/180

        v = veloc[y, x]
        D = diffu[y, x]

        # Distance between two grid cells' center.
        dis = R * acos(sin(lat)*sin(nlat)+cos(lat)*cos(nlat)*cos(lng-nlng))

        # Green's equation
        e = -1 * np.power(v * t - dis, 2) / (4 * D * t)
        h = dis / (2 * t * np.sqrt(pi * t * D)) * np.exp(e)
        h[0] = 0.0
        uh_m[:, y, x] = h / h.sum()

    return uh_m


def create_uh_cell(basin, station, uh_m, next_x, next_y, uh_slope):
    stn_x = station["x"]
    stn_y = station["y"]
    ncell = len(basin)

    days = 96
    t_max = days * 24

    uh_cell = np.zeros((ncell, days + len(uh_slope) - 1))
    i = 0
    for cell in basin:
        x, y = cell[0], cell[1]

        uh_hour = np.zeros(t_max)
        uh_hour[0:24] = 1.0/24.0

        while(True):
            if x == stn_x and y == stn_y:
                break
            uh_hour[:] = np.convolve(uh_hour, uh_m[:, y, x])[:t_max]
            x, y = next_x[y, x], next_y[y, x]

        uh_hour = uh_hour / uh_hour.sum()

        uh_day = np.zeros(days)
        for d in range(days):
            uh_day[d] = uh_hour[d*24:(d+1)*24].sum()
        uh_day = uh_day / uh_day.sum()

        uh_cell[i, :] = np.convolve(uh_slope, uh_day)
        uh_cell[i, :] = uh_cell[i, :] / uh_cell[i, :].sum()
        i += 1

        # Log when complete 10 percent.
        if i % (len(basin)/10) == 0:
            print "Cell %d dealed." % i

    return uh_cell


########################################################################################################################
#
# Create relative data for routing.
#
# rout_info is a dict like that:
#rout_info = {
#     "arc_dir_code": True or False
#     "direc": file_path,
#     "veloc": file path or value,
#     "diffu": file path or value,
#     "station": station likes before,
#     "uh_slope": filepath or from_template
# }
#
########################################################################################################################
def create_rout(rout_info):
    direc = read_direc(rout_info["direc"])
    station = rout_info["station"]

    if type(rout_info["veloc"]) is float:
        veloc = Grid(value=rout_info["veloc"], shape=direc.shape).value
    else:
        veloc = Grid(rout_info["veloc"]).value
    if type(rout_info["diffu"]) is float:
        diffu = Grid(value=rout_info["diffu"], shape=direc.shape).value
    else:
        diffu = Grid(rout_info["diffu"]).value

    if rout_info["uh_slope"] == "from_template":
        uh_slope = np.loadtxt(templates_path + "/uh_slope.template")
    else:
        uh_slope = np.loadtxt(rout_info["uh_slope"])

    next_x, next_y = next_cell(direc, rout_info["arc_dir_code"])
    basin = discovery_basin(station, next_x, next_y)
    uh_m = get_uh_m(basin, direc, veloc, diffu, next_x, next_y)
    uh_cell = create_uh_cell(basin, station, uh_m, next_x, next_y, uh_slope)

    rout_data = OrderedDict()
    rout_data["basin"] = basin
    sn = xy_to_sn(basin[:, 0], basin[:, 1])
    rout_data["sn"] = sn
    rout_data["uh_cell"] = uh_cell

    return rout_data



