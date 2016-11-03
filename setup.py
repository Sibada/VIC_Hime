#!/usr/bin/env python
#  -*- coding: utf-8 -*-

from os.path import join, dirname
from setuptools import setup, find_packages, Extension
from Cython.Build import cythonize
import numpy as np

from Hime.version import version

setup(
    name='VIC_Hime',
    version=version,
    description='VIC hydrological model project manager',
    url='https://github.com/Sibada/VIC_Hime',
    long_description="An program with input file creating, routing, auto-calibrate and GUI to make VIC used easier.",
    author='Sibada',
    maintainer='Zhong Ruida',
    maintainer_email='zrd2017@163.com',
    license='GPL3.0',

    packages=find_packages(),
    package_data={
        'Hime': [join('templates', '*.template')]
    },
    install_requires=[
        'numpy', 'pandas'
    ],

    ext_modules=[
        Extension("Hime.lib.idw", ["Hime/lib/idw.pyx"]),
    ],
    include_dirs=[np.get_include()]
)
