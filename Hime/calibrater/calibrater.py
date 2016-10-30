#!/usr/bin/env python
# -*- coding: utf-8 -*-

from Hime.statistic import nmse, bias
from Hime.model_execer.vic_execer import vic_exec
from Hime.routing.confluence import load_rout_data, confluence, gather_to_month
from Hime.utils import set_value_nc, set_soil_depth
from Hime import log

from datetime import datetime
from collections import OrderedDict
import numpy as np
import pandas as pd
import copy


########################################################################################################################
# calibrate parameters should look like this.
# calib_params = {
#     "driver_path": "file_path",
#     "global_file": "file_path",
#     "params_file": "file_path",
#     "mpi": False,
#     "ncores": 4,
#
#     "start_date": [1960, 1, 1],
#     "end_date": [1970, 1, 1],
#     "calib_start_date": [1961, 1, 1],
#
#     "rout_data_file": "file_path",
#     "domain_file": "file_path",
#     "vic_out_file": "file_path",
#     "time_scale": "D",
#     "obs_data_file": "file_path",
#     "obs_start_date": [1960, 1, 1],
#
#     "calib_range" = NONE / "file_path"
#     "BPC": 0.5,
#     "only_bias": False,
#     "turns": 2,
#     "max_itr": 20,
#     "toler": 0.005,
#
#     "rout_data": None,
#     "obs_data": None,
#     "p_init": [[0.05, 0.25, 0.45],[...],[...]...]
# }
########################################################################################################################

########################################################################################################################
#
# Run vic and routing and return a accuracy index of the simulation.
#
########################################################################################################################
def try_run_vic(calib_params):
    time_scale = calib_params["time_scale"]

    global_file = calib_params["global_file"]
    domain_file = calib_params["domain_file"]
    vic_out_file = calib_params["vic_out_file"]

    ymd = calib_params["obs_start_date"]
    obs_start_date = datetime(ymd[0], ymd[1], ymd[2])

    ymd = calib_params["start_date"]
    start_date = datetime(ymd[0], ymd[1], ymd[2])

    ymd = calib_params["calib_start_date"]
    calib_start_date = datetime(ymd[0], ymd[1], ymd[2])

    ymd = calib_params["end_date"]
    end_date = datetime(ymd[0], ymd[1], ymd[2])

    driver = calib_params["driver_path"]
    mpi = calib_params["mpi"]
    ncores = calib_params["ncores"]

    BPC = calib_params["BPC"]
    only_bias = calib_params["only_bias"]

    rout_data = calib_params["rout_data"]
    obs_data = calib_params["obs_data"]

    # Load observation runoff data
    obs = obs_data
    if len(obs.shape) > 1:
        obs = obs[:, -1]
    ts_obs = pd.date_range(obs_start_date, periods=len(obs), freq=time_scale)
    obs = pd.Series(obs, ts_obs)
    obs = obs[calib_start_date: end_date]

    # Run VIC
    status_code, logs, logs_err = vic_exec(driver, global_file, mpi=mpi, n_cores=ncores)
    if status_code != 0:
        log.info(logs_err)
        raise ValueError("VIC run fail. Return %d" % status_code)

    # Confluence.
    sim = confluence(vic_out_file, rout_data, domain_file, start_date, end_date)
    sim = sim[calib_start_date: end_date]
    if time_scale == "M":
        sim = gather_to_month(sim)

    # Calculate statistic indexes.
    NMSE = nmse(obs, sim)
    BIAS = bias(obs, sim)

    if only_bias:
        e = BIAS
    else:
        e = np.abs(BIAS) * BPC + NMSE

    log.debug("VIC runs result  E: %.3f   NMSE: %.3f BIAS: %.3f" % (e, NMSE, BIAS))
    return e, NMSE, BIAS


def set_nc_calib_params(params_file, calib_range, calib_var, value):

    if calib_var == "infilt":
        set_value_nc(params_file, "infilt", value, col_row=calib_range)

    if calib_var == "Ds":
        set_value_nc(params_file, "Ds", value, col_row=calib_range)

    if calib_var == "Dsmax":
        set_value_nc(params_file, "Dsmax", value, col_row=calib_range)

    if calib_var == "Ws":
        set_value_nc(params_file, "Ws", value, col_row=calib_range)

    if calib_var == "d2":
        set_soil_depth(params_file, 2, value, col_row=calib_range)

    if calib_var == "d3":
        set_soil_depth(params_file, 3, value, col_row=calib_range)


def run_adjust(calib_params, calib_var, value):
    params_file = calib_params["params_file"]
    calib_range = calib_params["calib_range"]
    set_nc_calib_params(params_file, calib_range, calib_var, value)

    e, NMSE, BIAS = try_run_vic(calib_params)
    return e, NMSE, BIAS


########################################################################################################################
#
# Auto-calibrate VIC model
#
########################################################################################################################
def calibrate(proj, calib_configs):
    params_file = calib_configs["params_file"]
    rout_data_file = calib_configs["rout_data_file"]

    start_date = calib_configs["start_date"]
    # calib_start_date = calib_configs["calib_start_date"]
    end_date = calib_configs["end_date"]

    p_init = calib_configs["p_init"]

    rout_data = load_rout_data(rout_data_file)
    calib_configs["rout_data"] = rout_data

    if calib_configs.get("calib_range") is None:
        calib_range = rout_data["basin"]
    else:
        calib_range = np.loadtxt(calib_configs.get["calib_range"], dtype=float, delimiter=r"[/s,]")
    calib_configs["calib_range"] = calib_range

    calib_configs["obs_data"] = np.loadtxt(calib_configs["obs_data_file"])

    ###########################################################################
    # Create a single global file.
    ###########################################################################
    proj_calib = copy.deepcopy(proj)
    proj_path = proj_calib.proj_params["proj_path"]
    if proj_path[-1] != "/":
        proj_path += "/"

    proj_calib.set_start_time(start_date)
    proj_calib.set_end_time(end_date)

    proj_calib.global_params["out_path"] = proj_path
    out_file_calib = OrderedDict({
            "out_file": "for_calibrate",
            "out_format": "NETCDF4",
            "compress": "FALSE",
            "aggfreq": "NDAYS 1",
            "out_var": ["OUT_RUNOFF",
                        "OUT_BASEFLOW"]
        })
    proj_calib.global_params["out_file"] = [out_file_calib]

    global_file = proj_path + "global_calibrate.txt"
    vic_out_file = "%sfor_calibrate.%04d-%02d-%02d.nc" % (proj_path,
                                                          start_date[0], start_date[1], start_date[2])
    proj_calib.write_global_file(global_file)

    calib_configs["global_file"] = global_file
    calib_configs["vic_out_file"] = vic_out_file
    ###########################################################################

    calib_params = ["infilt", "Ds", "Dsmax", "Ws", "d2", "d3"]
    lob = [0, 0, 0, 0, -1, -1]
    rob = [1, 1, -1, 1, -1, -1]
    lcb = [-1, -1, -1, -1, 0.1, 0.1]
    rcb = [-1, -1, -1, -1, 10, 10]

    opt_site = [1, 1, 1, 1, 1, 1]

    set_value_nc(params_file, "run_cell", 0, all=True)
    set_value_nc(params_file, "run_cell", 1, col_row=calib_range)

    p_init = np.array(p_init)
    set_value_nc(params_file, "infilt", p_init[0, 1], col_row=calib_range)
    set_value_nc(params_file, "Ds", p_init[1, 1], col_row=calib_range)
    set_value_nc(params_file, "Dsmax", p_init[2, 1], col_row=calib_range)
    set_value_nc(params_file, "Ws", p_init[3, 1], col_row=calib_range)
    set_soil_depth(params_file, 2, p_init[4, 1], col_row=calib_range)
    set_soil_depth(params_file, 3, p_init[5, 1], col_row=calib_range)

    turns = calib_configs["turns"]
    max_itr = calib_configs["max_itr"]
    toler = calib_configs["toler"]
    BPC = calib_configs["BPC"]

    log.info("Turns: %d, max itr: %d, toler: %.5f, BPC: %.2f" % (turns, max_itr, toler, BPC))

    step_E = None
    step_NMSE = [0, 0, 0]
    step_BIAS = [0, 0, 0]

    log.info("Calibrating start.")
    for turn in range(turns):
        log.info("Turns %d" % (turn+1))
        for calib_param in calib_params:
            log.info("Calibrate %s" % calib_param)
            pid = calib_params.index(calib_param)

            left_x = p_init[pid, 0]
            median_x = p_init[pid, 1]
            right_x = p_init[pid, 2]

            if step_E is not None and opt_site[pid] == 0:
                left_y = step_E
            else:
                left_y, step_NMSE[0], step_BIAS[0] = run_adjust(calib_configs, calib_param, left_x)

            if step_E is not None and opt_site[pid] == 1:
                median_y = step_E
            else:
                median_y, step_NMSE[1], step_BIAS[1] = run_adjust(calib_configs, calib_param, median_x)

            if step_E is not None and opt_site[pid] == 2:
                right_y = step_E
            else:
                right_y, step_NMSE[2], step_BIAS[2] = run_adjust(calib_configs, calib_param, right_x)

            sorted_y = sorted([left_y, median_y, right_y])
            dy = sorted_y[1] - sorted_y[0]

            itr = 0
            while dy > toler and itr < max_itr:
                log.debug("Calibrate %s, (x,y)1 = (%.3f, %.3f), (x,y)2 = (%.3f, %.3f), (x,y)3 = (%.3f, %.3f)"
                          % (calib_param, left_x, left_y, median_x, median_y, right_x, right_y))
                if median_y < left_y and median_y < right_y:
                    left_x = (left_x + median_x) / 2
                    right_x = (right_x + median_x) / 2

                    left_y, step_NMSE[0], step_BIAS[0] = run_adjust(calib_configs, calib_param, left_x)
                    right_y, step_NMSE[2], step_BIAS[2] = run_adjust(calib_configs, calib_param, right_x)

                elif left_y < median_y < right_y:
                    if lcb[pid] != -1 and left_x == lcb[pid]:
                        break

                    left_x_o = left_x
                    left_x -= (right_x - left_x) / 2

                    if lcb[pid] != -1 and left_x < lcb[pid]:
                        left_x = lcb[pid]
                        right_x = median_x
                        median_x = left_x_o

                        right_y = median_y
                        median_y = left_y
                        step_NMSE[2] = step_NMSE[1]
                        step_NMSE[1] = step_NMSE[0]
                        step_BIAS[2] = step_BIAS[1]
                        step_BIAS[1] = step_BIAS[0]
                        left_y, step_NMSE[0], step_BIAS[0] = run_adjust(calib_configs, calib_param, left_x)

                    elif lob[pid] != -1 and left_x <= lob[pid]:
                        left_x = (lob[pid] + left_x_o) / 2
                        right_x = median_x
                        median_x = left_x_o

                        right_y = median_y
                        median_y = left_y
                        step_NMSE[2] = step_NMSE[1]
                        step_NMSE[1] = step_NMSE[0]
                        step_BIAS[2] = step_BIAS[1]
                        step_BIAS[1] = step_BIAS[0]
                        left_y, step_NMSE[0], step_BIAS[0] = run_adjust(calib_configs, calib_param, left_x)

                    else:
                        right_x = median_x
                        median_x = left_x_o

                        right_y = median_y
                        median_y = left_y
                        step_NMSE[2] = step_NMSE[1]
                        step_NMSE[1] = step_NMSE[0]
                        step_BIAS[2] = step_BIAS[1]
                        step_BIAS[1] = step_BIAS[0]
                        left_y, step_NMSE[0], step_BIAS[0] = run_adjust(calib_configs, calib_param, left_x)

                elif left_y > median_y > right_y:
                    if rcb[pid] != -1 and right_x == rcb[pid]:
                        break

                    right_x_o = right_x
                    right_x += (right_x - left_x) / 2

                    if rcb[pid] != -1 and right_x > rcb[pid]:
                        right_x = rcb[pid]
                        left_x = median_x
                        median_x = right_x_o

                        left_y = median_y
                        median_y = right_y
                        step_NMSE[0] = step_NMSE[1]
                        step_NMSE[1] = step_NMSE[2]
                        step_BIAS[0] = step_BIAS[1]
                        step_BIAS[1] = step_BIAS[2]
                        right_y, step_NMSE[2], step_BIAS[2] = run_adjust(calib_configs, calib_param, right_x)

                    elif rob[pid] != -1 and right_x >= rob[pid]:
                        right_x = (rob[pid] + right_x_o) / 2
                        left_x = median_x
                        median_x = right_x_o

                        left_y = median_y
                        median_y = right_y
                        step_NMSE[0] = step_NMSE[1]
                        step_NMSE[1] = step_NMSE[2]
                        step_BIAS[0] = step_BIAS[1]
                        step_BIAS[1] = step_BIAS[2]
                        right_y, step_NMSE[2], step_BIAS[2] = run_adjust(calib_configs, calib_param, right_x)

                    else:
                        left_x = median_x
                        median_x = right_x_o

                        left_y = median_y
                        median_y = right_y
                        step_NMSE[0] = step_NMSE[1]
                        step_NMSE[1] = step_NMSE[2]
                        step_BIAS[0] = step_BIAS[1]
                        step_BIAS[1] = step_BIAS[2]
                        right_y, step_NMSE[2], step_BIAS[2] = run_adjust(calib_configs, calib_param, right_x)

                p_init[pid, :] = [left_x, median_x, right_x]

                if median_y < left_y and median_y < right_y:
                    step_E = median_y
                    opt_site[pid] = 1
                elif left_y < median_y < right_y:
                    step_E = left_y
                    opt_site[pid] = 0
                elif left_y > median_y > right_y:
                    step_E = right_y
                    opt_site[pid] = 2

                sorted_y = sorted([left_y, median_y, right_y])
                dy = sorted_y[1] - sorted_y[0]

                NMSE, BIAS = step_NMSE[opt_site[pid]], step_BIAS[opt_site[pid]]

                itr += 1
                log.info("%s iteration %d, value = %.3f, E = %.3f, NSCE = %.3f, BIAS = %.3f" %
                         (calib_param, itr, p_init[pid, opt_site[pid]], step_E, 1 - NMSE, BIAS))

            log.info("%s calibrated, value = %.3f, E = %.3f, NSCE = %.3f, BIAS = %.3f" %
                     (calib_param, p_init[pid, opt_site[pid]], step_E, 1 - NMSE, BIAS))

        log.info("Calibrate result of turns %d:  Infilt: %.3f, Ds: %.3f, Dsmax: %.3f, Ws: %.3f,"
                 " d2: %.3f, d3: %.3f, E: %.3f, NSC: %.3f, BIAS: %.3f"
                 % (turn+1, p_init[0, opt_site[0]], p_init[1, opt_site[1]], p_init[2, opt_site[2]],
                    p_init[3, opt_site[3]], p_init[4, opt_site[4]], p_init[5, opt_site[5]],
                    step_E, 1-NMSE, BIAS))

    return [p_init[0, opt_site[0]], p_init[1, opt_site[1]], p_init[2, opt_site[2]],
            p_init[3, opt_site[3]], p_init[4, opt_site[4]], p_init[5, opt_site[5]]]
