#!/usr/bin/env python
#  -*- coding: utf-8 -*-

from Hime.version import version

from os.path import dirname, join
import logging

templates_path = join(dirname(__file__), "templates")

########################################################################################################################
# Logger config.
########################################################################################################################
logging.basicConfig(level=logging.DEBUG)
console_log = logging.StreamHandler()
console_log.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s',
                                           datefmt='%Y-%m-%d %H:%M:%S'))

log = logging.getLogger("Hime")
log.addHandler(console_log)

########################################################################################################################