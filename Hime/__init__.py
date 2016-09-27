from .version import version as __version__

import os, sys

templates_path = os.path.split(os.path.realpath(__file__)) [0] + "/templates"