#!/usr/bin/env python
# -*- coding: utf-8 -*-

from Hime.statistic import nmse, bias
from Hime.model_execer.vic_execer import vic_exec_mpi, vic_exec
from Hime.routing.confluence import load_rout_data, confluence, gather_to_month
from Hime.utils import set_value_nc, set_soil_depth
from . import log
import numpy as np
import pandas as pd


########################################################################################################################
#
# Run vic and routing and return a accuracy index of the simulation.
#
########################################################################################################################
def try_run_vic(proj, rout_data):
    time_scale = proj.proj_params["calib_param"]["time_scale"]

    global_file = proj.proj_params["calib_param"]["global_file"]
    domain_file = proj.proj_params["calib_param"]["domain_file"]
    out_file = proj.proj_params["calib_param"]["out_file"]

    obs_data_file = proj.proj_params["calib_param"]["obs_data_file"]
    obs_start_date = proj.proj_params["calib_param"]["obs_start_date"]

    start_date = proj.proj_params["calib_param"]["start_date"]
    rout_date = proj.proj_params["calib_param"]["rout_date"]
    end_date = proj.proj_params["calib_param"]["end_date"]

    mpi = proj.proj_params["calib_param"]["mpi"]

    BPC = proj.proj_params["calib_param"]["BPC"]
    only_bias = proj.proj_params["calib_param"]["only_bias"]

    driver = proj.get_image_driver()

    # Execute VIC
    if mpi:
        ncores = proj.get_ncores()
        vic_exec_mpi(driver, global_file, n_proc=ncores)
    else:
        vic_exec(driver, global_file)

    # Confluence.
    sim = confluence(out_file, rout_data, domain_file, rout_date, end_date)
    if time_scale == "M":
        sim = gather_to_month(sim)

    # Load observation runoff data
    obs = np.loadtxt(obs_data_file)
    if len(obs.shape) > 1:
        obs = obs[:, 1]
    ts_obs = pd.date_range(obs_start_date, periods=len(obs), freq=time_scale)
    obs = pd.Series(obs, ts_obs)
    obs = obs[rout_date: end_date]

    # Calculate statistic indexes.
    NMSE = nmse(obs, sim)
    BIAS = bias(obs, sim)

    if only_bias:
        e = BIAS
    else:
        e = np.abs(BIAS) * BPC + NMSE

    return e, NMSE, BIAS


def set_nc_calib_params(params_file, calib_mask, calib_var, value):
    if calib_var == "infilt":
        set_value_nc(params_file, "infilt", value, col_row=calib_mask)

    if calib_var == "Ds":
        set_value_nc(params_file, "Ds", value, col_row=calib_mask)

    if calib_var == "Dsmax":
        set_value_nc(params_file, "Dsmax", value, col_row=calib_mask)

    if calib_var == "Ws":
        set_value_nc(params_file, "Ws", value, col_row=calib_mask)

    if calib_var == "d2":
        set_soil_depth(params_file, 2, value, col_row=calib_mask)

    if calib_var == "d3":
        set_soil_depth(params_file, 3, value, col_row=calib_mask)


def run_adjust(proj, calib_mask, rout_data, calib_var, value):

    params_file = proj.proj_params["calib_param"]["params_file"]
    set_nc_calib_params(params_file, calib_mask, calib_var, value)

    e, NMSE, BIAS = try_run_vic(proj, rout_data)
    return e, NMSE, BIAS


def calibrate(proj):
    params_file = proj.proj_params["calib_param"]["params_file"]
    rout_data_file = proj.proj_params["calib_param"]["rout_data_file"]

    start_date = proj.proj_params["calib_param"]["start_date"]
    rout_date = proj.proj_params["calib_param"]["rout_date"]
    end_date = proj.proj_params["calib_param"]["end_date"]

    p_init = proj.proj_params["calib_param"]["p_init"]

    rout_data = load_rout_data(rout_data_file)
    calib_mask = rout_data["basin"]

    calib_params = ["infilt", "Ds", "Dsmax", "Ws", "d2", "d3"]
    lob = [0, 0, 0, 0, -1, -1]
    rob = [1, 1, -1, 1, -1, -1]
    lcb = [-1, -1, -1, -1, 0.1, 0.1]
    rcb = [-1, -1, -1, -1, -1, -1]

    opt_site = [1, 1, 1, 1, 1, 1]

    p_init = np.array(p_init)
    set_value_nc(params_file, "infilt", p_init[0, 1], col_row=calib_mask)
    set_value_nc(params_file, "Ds", p_init[1, 1], col_row=calib_mask)
    set_value_nc(params_file, "Dsmax", p_init[2, 1], col_row=calib_mask)
    set_value_nc(params_file, "Ws", p_init[3, 1], col_row=calib_mask)
    set_soil_depth(params_file, 2, p_init[4, 1], col_row=calib_mask)
    set_soil_depth(params_file, 3, p_init[5, 1], col_row=calib_mask)

    turns = 2
    max_itr = 10
    toler = 0.01

    step_val = None

    for turn in range(turns):
        for calib_param in calib_params:
            pid = calib_params.index(calib_param)

            left_x = p_init[pid, 0]
            median_x = p_init[pid, 1]
            right_x = p_init[pid, 2]

            if step_val is not None and opt_site[pid] == 0:
                left_y = step_val
            else:
                left_y, NMSE, BIAS = run_adjust(proj, calib_mask, rout_data, calib_param, median_x)

            if step_val is not None and opt_site[pid] == 1:
                median_y = step_val
            else:
                median_y, NMSE, BIAS = run_adjust(proj, calib_mask, rout_data, calib_param, median_x)

            if step_val is not None and opt_site[pid] == 2:
                right_y = step_val
            else:
                right_y, NMSE, BIAS = run_adjust(proj, calib_mask, rout_data, calib_param, median_x)

            sorted_y = sorted([left_y, median_y, right_y])
            dy = sorted_y[1] - sorted_y[0]

            itr = 0
            while dy > toler and itr < max_itr:
                if median_y < left_y and median_y < right_y:
                    left_x = (left_x + median_x) / 2
                    right_x = (right_x + median_x) / 2

                    left_y, NMSE, BIAS = run_adjust(proj, calib_mask, rout_data, calib_param, left_x)
                    right_y, NMSE, BIAS = run_adjust(proj, calib_mask, rout_data, calib_param, right_x)

                elif left_y < median_y < right_y:
                    left_x_o = left_x
                    left_x -= (right_x - left_x) / 2
                    if lcb[pid] != -1 and left_x_o == lcb[pid]:
                        step_val = left_y
                        opt_site[pid] = 0
                        break

                    elif lcb[pid] != -1 and left_x < lcb[pid]:
                        right_x = median_x
                        median_x = left_x
                        left_x = lcb[pid]

                        right_y = median_y
                        median_y = left_y
                        left_y, NMSE, BIAS = run_adjust(proj, calib_mask, rout_data, calib_param, left_x)

                    elif lob[pid] != -1 and left_x <= lob[pid]:
                        left_x = (lob[pid] + left_x_o) / 2
                        right_x = median_x
                        median_x = left_x_o

                        right_y = median_y
                        median_y = left_y
                        left_y, NMSE, BIAS = run_adjust(proj, calib_mask, rout_data, calib_param, left_x)

                elif left_y > median_y > right_y:
                    right_x_o = right_x
                    right_x += (right_x - left_x) / 2
                    if rcb[pid] != -1 and right_x_o == rcb[pid]:
                        step_val = right_y
                        opt_site[pid] = 2
                        break

                    elif rcb[pid] != -1 and right_x > rcb[pid]:
                        left_x = median_x
                        median_x = right_x
                        right_x = rcb[pid]

                        left_y = median_y
                        median_y = right_y
                        right_y, NMSE, BIAS = run_adjust(proj, calib_mask, rout_data, calib_param, right_x)

                    elif rob[pid] != -1 and right_x >= rob[pid]:
                        right_x = (rob[pid] + right_x_o) / 2
                        left_x = median_x
                        median_x = right_x_o

                        left_y = median_y
                        median_y = right_y
                        right_y, NMSE, BIAS = run_adjust(proj, calib_mask, rout_data, calib_param, right_x)

                p_init[pid, :] = [left_x, median_x, right_x]

                if median_y < left_y and median_y < right_y:
                    step_val = median_y
                    opt_site[pid] = 1
                elif left_y < median_y < right_y:
                    step_val = left_y
                    opt_site[pid] = 0
                elif left_y > median_y > right_y:
                    step_val = right_y
                    opt_site[pid] = 2

                sorted_y = sorted([left_y, median_y, right_y])
                dy = sorted_y[1] - sorted_y[0]

                log.info("Calibrate %s: value = %.3f, Nsc = %.3f, Bias = %.3f, E = %.3f" %
                         (calib_param, 1-NMSE, BIAS, step_val))




