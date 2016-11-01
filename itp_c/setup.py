#!/usr/bin/env python
#  -*- coding: utf-8 -*-

from distutils.core import setup
from distutils.extension import Extension
from Cython.Build import cythonize
import numpy as np

setup(
    name='itp_c',
    version='0.0.1',
    description='Assistant module for VIC Hime.',

    ext_modules=cythonize([
        Extension("itp_c", ["itp_c.pyx"], include_dirs=[np.get_include()]),
    ]),
)