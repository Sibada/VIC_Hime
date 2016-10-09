#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np

########################################################################################################################
#
# Create site of the next cell.
#
########################################################################################################################


def next_cell(direc, dir_code="DEF"):
    # Direction code.
    if dir_code == "ARC":
        dx = {1: 0,
              2: 1,
              3: 1,
              4: 1,
              5: 0,
              6: -1,
              7: -1,
              8: -1}
        dy = {1: -1,
              2: -1,
              3: 0,
              4: 1,
              5: 1,
              6: 1,
              7: 0,
              8: -1}
    else:
        dx = {64: 0,
              128: 1,
              1: 1,
              2: 1,
              4: 0,
              8: -1,
              16: -1,
              32: -1}
        dy = {64: -1,
              128: -1,
              1: 0,
              2: 1,
              4: 1,
              8: 1,
              16: 0,
              32: -1}

    next_x = direc.value.copy()
    next_y = direc.value.copy()

    # Find x y site of next cell.
    for x in range(direc.ncol):
        for y in range(direc.nrow):
            if np.isnan(direc.value[y, x]):
                continue
            direc_v = direc.value[y, x]
            next_x[y, x] = x + dx[direc_v]
            next_y[y, x] = y + dy[direc_v]

    return next_x, next_y