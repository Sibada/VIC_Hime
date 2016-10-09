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

