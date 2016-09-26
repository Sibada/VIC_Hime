#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
import numpy as np

# Caculate statistic params such as NMSE ,BIAS and BABS.

def nmse(obs, sim):
    mse = ((obs - sim) ** 2).mean()
    return mse / obs.var()

def bias(obs, sim):
    return sim.sum() / obs.sum() - 1

def babs(obs, sim):
    return abs(bias(obs, sim))