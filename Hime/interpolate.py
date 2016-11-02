#!/usr/bin/env python
#  -*- coding: utf-8 -*-

import numpy as np


########################################################################################################################
#
# Inverse distance weight itp_c.
#
########################################################################################################################
def idw(stn_data, stn_coords, grid_coords, idp=2, maxd=np.inf, maxp=None):

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