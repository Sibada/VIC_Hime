#!/usr/bin/env python
# -*- coding: utf-8 -*-

from Hime.statistic import nmse, bias
from Hime.model_execer.vic_execer import vic_exec
from Hime.routing.confluence import load_rout_data, confluence, gather_to_month, write_runoff_data
from Hime.utils import set_value_nc, set_soil_depth
from Hime import log

from datetime import datetime
from collections import OrderedDict
import numpy as np
import pandas as pd
import copy


########################################################################################################################
# calibrate configures should look like this.
# calib_configs = {
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
def vic_try(calib_params):
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


def set_params(params_file, calib_range, var_id, value):
    if var_id == 0:
        set_value_nc(params_file, "infilt", value, col_row=calib_range)
    if var_id == 1:
        set_value_nc(params_file, "Ds", value, col_row=calib_range)
    if var_id == 2:
        set_value_nc(params_file, "Dsmax", value, col_row=calib_range)
    if var_id == 3:
        set_value_nc(params_file, "Ws", value, col_row=calib_range)
    if var_id == 4:
        set_soil_depth(params_file, 2, value, col_row=calib_range)
    if var_id == 5:
        set_soil_depth(params_file, 3, value, col_row=calib_range)


def vic_try_with_param(calib_configs, var_id, value):
    params_file = calib_configs["params_file"]
    calib_range = calib_configs["calib_range"]
    set_params(params_file, calib_range, var_id, value)

    e, NMSE, BIAS = vic_try(calib_configs)
    return [e, NMSE, BIAS]


########################################################################################################################
#
# Auto-calibrate VIC model
#
########################################################################################################################
def calibrate(proj, calib_configs):
    params_file = calib_configs["params_file"]

    start_date = calib_configs["start_date"]
    end_date = calib_configs["end_date"]

    p_rngs = np.array(calib_configs["p_init"])

    calib_configs["obs_data"] = np.loadtxt(calib_configs["obs_data_file"])
    calib_configs["rout_data"] = load_rout_data(calib_configs["rout_data_file"])

    calib_range = calib_configs["rout_data"]["basin"]\
        if calib_configs.get("calib_range_file") is None \
        else np.loadtxt(calib_configs.get["calib_range_file"], dtype=int, delimiter=r"[/s,]")
    calib_configs["calib_range"] = calib_range

    turns = calib_configs["turns"]
    max_itr = calib_configs["max_itr"]
    toler = calib_configs["toler"]
    BPC = calib_configs["BPC"]

    # Set run area.
    set_value_nc(params_file, "run_cell", 0, all=True)
    set_value_nc(params_file, "run_cell", 1, col_row=calib_range)

    ###########################################################################
    # Create a single global file for calibration.
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
    # Presets of auto-calibration.
    ###########################################################################
    param_names = ["infilt", "Ds", "Dsmax", "Ws", "d2", "d3"]

    lob = [0, 0, 0, 0, -1, -1]  # Left open boundary, -1 means not boundary.
    rob = [1, 1, -1, 1, -1, -1]  # Right open boundary.
    lcb = [-1, -1, -1, -1, 0.1, 0.1]  # Left close boundary. Params can get this value.
    rcb = [-1, -1, -1, -1, 10, 10]  # Right close boundary.

    step_r = None
    rs = [None, None, None]
    step_params = p_rngs[:, 1]

    log.info("###### Automatical calibration start... ######")
    log.info("\nTurns:\t%d\nmax itr:\t%d\ntoler:\t%.5f\nBPC:\t%.2f" % (turns, max_itr, toler, BPC))

    for t in range(turns):
        turn = t + 1
        log.info("Turns %d:" % turn)
        for p in range(6):
            param_name = param_names[p]
            log.info("Calibrate %s:" % param_name)

            [set_params(params_file, calib_range, i, step_params[i]) for i in range(6)]

            x = list(p_rngs[p, :])
            rs[0] = vic_try_with_param(calib_configs, p, x[0])
            rs[2] = vic_try_with_param(calib_configs, p, x[2])

            if step_r is not None:
                rs[1] = step_r
            else:
                rs[1] = vic_try_with_param(calib_configs, p, x[1])

            od = order(rs)  # Order of the results sorted by optimise level. The od[0]'s is the optimized.
            es, NMSEs, BIASs = [r[0] for r in rs], [r[1] for r in rs], [r[2] for r in rs]
            opt_E = es[od[0]]
            opt_val = x[od[0]]
            NMSE = NMSEs[od[0]]
            BIAS = BIASs[od[0]]

            step_params[p] = opt_val

            step_r = rs[od[0]]
            de = es[od[2]] - es[od[0]]

            itr = 0  # Iteration times of single parameter.
            while de >= toler:
                if itr > max_itr:
                    break

                if es[1] < es[0] and es[1] < es[2]:
                    x[0] = (x[0] + x[1])/2
                    x[2] = (x[1] + x[2])/2
                    rs[0] = vic_try_with_param(calib_configs, p, x[0])
                    rs[2] = vic_try_with_param(calib_configs, p, x[2])

                elif es[0] < es[1] < es[2]:
                    if lcb[p] < 0 and x[0] == lcb[p]:
                        break

                    x[2], x[1], x[0] = x[1], x[0], x[0]-(x[2]-x[0])/2
                    rs[2], rs[1] = rs[1], rs[0]

                    if lcb[p] > 0 and x[0] < lcb[p]:
                        x[0] = lcb[p]
                    elif lob[p] > 0 and x[0] <= lob[p]:
                        x[0] = x[1] - 0.618 * (x[1]-lob)

                    rs[0] = vic_try_with_param(calib_configs, p, x[0])

                elif es[0] > es[1] > es[2]:
                    if rcb[p] > 0 and x[2] == rcb[p]:
                        break

                    x[0], x[1], x[2] = x[1], x[2], x[2]+(x[2]-x[0])/2
                    rs[0], rs[1] = rs[1], rs[2]

                    if x[2] > rcb[p] > 0:
                        x[2] = lcb[p]
                    elif x[2] >= rob[p] > 0:
                        x[2] = x[1] + 0.618 * (rob[p]-x[1])

                    rs[2] = vic_try_with_param(calib_configs, p, x[2])

                es, NMSEs, BIASs = [r[0] for r in rs], [r[1] for r in rs], [r[2] for r in rs]

                od = order(rs)
                opt_E = es[od[0]]
                opt_val = x[od[0]]
                NMSE = NMSEs[od[0]]
                BIAS = BIASs[od[0]]

                step_params[p] = opt_val
                step_r = rs[od[0]]
                de = es[od[2]] - es[od[0]]
                itr += 1

                log.info("Iteration %d: param value=%.3f, E=%.3f, NSCE=%.3f, BIAS=%.3f" %
                         (itr, opt_val, opt_E, 1-NMSE, BIAS))
                log.debug("[%.3f, %.3f, %.3f, %.3f, %.3f, %.3f] => VIC => E:%.3f, NMSE:%.3f, BIAS:%.3f"
                          % (step_params[0], step_params[1], step_params[2], step_params[3],
                             step_params[4], step_params[5], opt_E, NMSE, BIAS))

            log.info("Parameter %s calibrated. Optimized value: %.3f, E: %.3f, NSCE: %.3f, BIAS: %.3f" %
                     (param_name, opt_val, opt_E, 1-NMSE, BIAS))

        # Reset range.
        n_rngs = (p_rngs[:, 2] - p_rngs[:, 0]) / 2 * 0.618
        p_rngs[:, 1] = step_params
        p_rngs[:, 0], p_rngs[:, 2] = step_params - n_rngs, step_params + n_rngs
        for i in range(6):
            if lob[i] > 0 and p_rngs[i, 0] <= lob[i]:
                p_rngs[i, 0] = step_params[i] - (step_params[i] - lob[i]) * 0.618
            if not rob[i] <= 0 and p_rngs[i, 2] >= rob[i]:
                p_rngs[i, 2] = step_params[i] + (rob[i] - step_params[i]) * 0.618
            if lcb[i] > 0 and p_rngs[i, 0] < lcb[i]:
                p_rngs[i, 0] = lcb[i]
            if not rcb[i] <= 0 and p_rngs[i, 2] > rcb[i]:
                p_rngs[i, 2] = rcb[i]

    log.info("######### calibration completed. #########")

    # Apply optimized parameters to file.
    [set_params(params_file, calib_range, i, step_params[i]) for i in range(6)]

    return step_params


########################################################################################################################
#
# Take the orders of an array like in R.
#
########################################################################################################################
def order(array):
    return list(pd.DataFrame(array).sort(0).index)

