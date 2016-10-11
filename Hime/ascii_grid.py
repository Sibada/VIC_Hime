#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
import re

########################################################################################################################
#
# Read in and storage grid data from ASCII grid file.
#
########################################################################################################################


class Grid(object):
    def __init__(self, file_path=None, shape=None, value=0, xcor=0, ycor=0, csize=1):

        # Read grid from ASCII grid file.
        if file_path is not None:
            ascii_grid = open(file_path)
            disc_lines = []
            for i in range(6):
                disc_lines.append(ascii_grid.readline())
            ascii_grid.close()

            self.xcor = float(re.split("\s+", disc_lines[2])[1])
            self.ycor = float(re.split("\s+", disc_lines[3])[1])
            self.csize = float(re.split("\s+", disc_lines[4])[1])
            ndvalue = float(re.split("\s+", disc_lines[5])[1])

            self.value = np.loadtxt(file_path, skiprows=6)[::-1, ]
            self.value[self.value == ndvalue] = np.nan

            self.shape = self.value.shape
            self.nrow = self.value.shape[0]
            self.ncol = self.value.shape[1]

        # Create an empty or single value grid.
        else:
            if shape is None or not (type(shape) == tuple or type(shape) == list):
                raise ValueError("dim was not provided or is not tuple nor list.")
            if len(shape) < 2:
                raise ValueError("Length of dim should not less than 2.")
            self.value = np.ones(shape) * value
            self.xcor = xcor
            self.ycor = ycor
            self.csize=csize

            self.shape = shape
            self.nrow = shape[0]
            self.ncol = shape[1]

