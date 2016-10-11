#!/usr/bin/env python
# -*- coding: utf-8 -*-

from collections import OrderedDict
import json


########################################################################################################################
#
# Read output information template file.
#
########################################################################################################################
def read_template(template_file):
    tf = open(template_file)
    tem_lines = tf.readlines()
    tf.close()
    try:
        tem_str = "".join(tem_lines)
        tem = json.loads(tem_str, object_pairs_hook=OrderedDict)
    except Exception:
        raise ValueError("Format of parameter template file uncorrect.")
    return tem


########################################################################################################################
#
# Row and column to series number.
#
########################################################################################################################
def xy_to_sn(x, y, nx=None, ny=None):
    if nx is None or ny is None:
        nx, ny = x.max() + 1, y.max() + 1

    sn = (y - 1) * nx + x - 1
    return sn


