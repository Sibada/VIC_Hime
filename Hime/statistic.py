#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division

# Caculate statistic params such as NMSE ,BIAS and BABS.


def nmse(obs, sim):
    mse = ((obs - sim) ** 2).mean()
    nmse = mse / obs.var()
    return nmse


def bias(obs, sim):
    return sim.sum() / obs.sum() - 1
