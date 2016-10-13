#!/usr/bin/env python
# -*- coding: utf-8 -*-

from Hime.statistic import nmse, bias
from Hime.model_execer.vic_execer import vic_exec_mpi, vic_exec
from Hime.routing.confluence import load_rout_data, confluence, gather_to_month
import numpy as np
import pandas as pd

def try_run_vic(proj):
    rout_data_file = proj.proj_params["calib_param"]["rout_data_file"]
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
    rout_data = load_rout_data(rout_data_file)
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

    print "NSC: %.3f; BIAS: %.3f" % (1-NMSE, BIAS)

    return e