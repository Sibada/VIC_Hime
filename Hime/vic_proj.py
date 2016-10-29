#!/usr/bin/env python
# -*- coding: utf-8 -*-

from Hime import log
from .version import version as __version__
from collections import OrderedDict
import datetime
import json
import os


########################################################################################################################
#
# A class to storage parameters of a VIC project.
#
########################################################################################################################
class VicProj(object):
    def __init__(self, proj_name="", proj_path="", create_proj=False):
        self.global_params = OrderedDict()
        self.proj_params = OrderedDict()

        glo_prm = self.global_params
        prj_prm = self.proj_params
        #######################################################################
        # Project parameters.
        #######################################################################
        prj_prm["proj_path"] = proj_path
        prj_prm["proj_name"] = proj_name
        prj_prm["proj_file"] = proj_path + "/" + proj_name + ".vic_proj"
        prj_prm["global_file"] = proj_path + "/" + proj_name + "_image.global.txt"

        prj_prm["vic_image_driver"] = None
        prj_prm["n_cores"] = 4

        #######################################################################
        # VIC auto-calibration parameters.
        #######################################################################
        calib_param = OrderedDict()

        calib_param["rout_data_file"] = None
        calib_param["time_scale"] = "M"

        calib_param["global_file"] = None
        calib_param["params_file"] = None
        calib_param["domain_file"] = None
        calib_param["out_file"] = None

        calib_param["obs_data_file"] = None
        calib_param["obs_start_date"] = None

        calib_param["start_date"] = None
        calib_param["rout_date"] = None
        calib_param["end_date"] = None

        calib_param["BPC"] = 0.25
        calib_param["only_bias"] = False

        calib_param["mpi"] = False

        calib_param["p_init"] = [[0.1, 0.25, 0.5],
                               [0.01, 0.1, 0.3],
                               [10.0, 40.0, 80.0],
                               [0.75, 0.8, 0.85],
                               [0.1, 0.3, 0.5],
                               [0.1, 0.4, 0.7]]

        self.proj_params["calib_param"] = calib_param

        #######################################################################
        # VIC global parameters.
        #######################################################################

        # Basic run parameters.
        glo_prm["model_steps_per_day"] = 1
        glo_prm["snow_steps_per_day"] = 1
        glo_prm["runoff_steps_per_day"] = 1
        glo_prm["start_time"] = datetime.datetime(1960, 1, 1)
        glo_prm["end_time"] = datetime.datetime(1970, 12, 31)
        glo_prm["calendar"] = "proleptic_gregorian"

        glo_prm["full_energy"] = "FALSE"
        glo_prm["frozen_soil"] = "FALSE"

        glo_prm["compute_treeline"] = "FALSE"
        glo_prm["veglib_vegcover"] = "FALSE"
        # Domain file.
        glo_prm["domain_path"] = None
        domain_type = OrderedDict({
            "LAT": "lat",
            "LON": "lon",
            "MASK": "mask",
            "AREA": "area",
            "FRAC": "frac",
            "YDIM": "lat",
            "XDIM": "lon"
        })
        glo_prm["domain_type"] = domain_type

        # Forcing files.
        forcing1 = OrderedDict()
        forcing1["file_path"] = None
        forcing1["force_type"] = OrderedDict({
            "AIR_TEMP": "tas",
            "PREC": "prcp",
            "PRESSURE": "pres",
            "SWDOWN": "dswrf",
            "LWDOWN": "dlwrf",
            "VP": "vp",
            "WIND": "wind"
        })
        forcing1["wind_h"] = None
        glo_prm["forcing1"] = forcing1
        glo_prm["forcing2"] = None

        # Parameters file.
        glo_prm["param_file"] = None
        glo_prm["snow_band"] = "FALSE"
        glo_prm["july_tavg"] = "FALSE"
        glo_prm["organic"] = "FALSE"
        glo_prm["organic_fract"] = "FALSE"
        glo_prm["baseflow"] = "ARNO"
        glo_prm["LAI_src"] = "FROM_VEGPARAM"
        glo_prm["nlayer"] = 3
        glo_prm["nodes"] = 3

        # Output files.
        glo_prm["out_path"] = None
        out_file1 = OrderedDict({
            "out_file": "runoff",
            "out_format": "NETCDF4",
            "compress": "FALSE",
            "aggfreq": "NDAYS 1",
            "out_var": ["OUT_RUNOFF",
                        "OUT_BASEFLOW"]
        })
        glo_prm["out_file"] = [out_file1]

        #######################################################################
        # Create new project.
        #######################################################################
        if create_proj:
            if not os.path.exists(proj_path):
                os.makedirs(proj_path)
            self.write_proj_file()

    ####################################################################################################################
    """
    Write global parameters file for VIC Image Driver.
    """
    def write_global_file(self, out_global_file=None):
        if out_global_file is None:
            out_global_file = self.proj_params["global_file"]

        out_lines = []
        glo_prm = self.global_params

        out_lines.append("#######################################################################")
        out_lines.append("# VIC Model Parameters for Stehekin Basin Sample Image Driver Setup")
        out_lines.append("#")
        out_lines.append("# This file is create by VIC Hime %s at %s" % (__version__, datetime.datetime.now().
                                                                         strftime('%Y-%m-%d, %H:%M:%S')))
        out_lines.append("#######################################################################")
        out_lines.append("")
        out_lines.append("#######################################################################")
        out_lines.append("# Simulation Parameters")
        out_lines.append("#######################################################################")

        out_lines.append("MODEL_STEPS_PER_DAY %d" % glo_prm["model_steps_per_day"])
        out_lines.append("SNOW_STEPS_PER_DAY %d" % glo_prm["snow_steps_per_day"])
        out_lines.append("RUNOFF_STEPS_PER_DAY %d" % glo_prm["runoff_steps_per_day"])
        out_lines.append("")
        out_lines.append("STARTYEAR %d" % glo_prm["start_time"].year)
        out_lines.append("STARTMONTH %d" % glo_prm["start_time"].month)
        out_lines.append("STARTDAY %d" % glo_prm["start_time"].day)
        out_lines.append("ENDYEAR %d" % glo_prm["end_time"].year)
        out_lines.append("ENDMONTH %d" % glo_prm["end_time"].month)
        out_lines.append("ENDDAY %d" % glo_prm["end_time"].day)
        out_lines.append("CALENDAR %s" % glo_prm["calendar"])
        out_lines.append("")
        out_lines.append("FULL_ENERGY %s" % glo_prm["full_energy"])
        out_lines.append("FROZEN_SOIL %s" % glo_prm["frozen_soil"])
        out_lines.append("")
        out_lines.append("COMPUTE_TREELINE %s" % glo_prm["compute_treeline"])

        out_lines.append("#######################################################################")
        out_lines.append("# DOMAIN INFO")
        out_lines.append("#######################################################################")
        out_lines.append("DOMAIN %s" % glo_prm["domain_path"])
        for tp in glo_prm["domain_type"].items():
            out_lines.append("DOMAIN_TYPE %s %s" % (tp[0], tp[1]))
        out_lines.append("")

        out_lines.append("#######################################################################")
        out_lines.append("# Forcing Files and Parameters")
        out_lines.append("# netcdf forcing files will be of the form: <FORCING1>YYYY.nc")
        out_lines.append("#######################################################################")

        forcing1 = glo_prm["forcing1"]
        out_lines.append("FORCING1 %s" % forcing1["file_path"])
        for type in forcing1["force_type"].items():
            out_lines.append("FORCE_TYPE %s %s" % (type[0], type[1]))
        if forcing1["wind_h"] is not None:
            out_lines.append("WIND_H %.2f" % forcing1["wind_h"])
        out_lines.append("")

        if glo_prm["forcing2"] is not None:
            forcing2 = glo_prm["forcing2"]
            out_lines.append("FORCING2 %s" % forcing2["file_path"])
            for tp in forcing2["force_type"].items():
                out_lines.append("FORCE_TYPE %s %s" % (tp[0], tp[1]))
            if forcing2["wind_h"] is not None:
                out_lines.append("WIND_H %.2f" % forcing1["wind_h"])
            out_lines.append("")

        out_lines.append("#######################################################################")
        out_lines.append("# Land Surface Files and Parameters")
        out_lines.append("#######################################################################")

        out_lines.append("PARAMETERS %s" % glo_prm["param_file"])
        out_lines.append("SNOW_BAND %s" % glo_prm["snow_band"])
        out_lines.append("BASEFLOW %s" % glo_prm["baseflow"])
        out_lines.append("JULY_TAVG_SUPPLIED %s" % glo_prm["july_tavg"])
        out_lines.append("ORGANIC_FRACT %s" % glo_prm["organic_fract"])
        out_lines.append("LAI_SRC %s" % glo_prm["LAI_src"])
        out_lines.append("NLAYER %d" % glo_prm["nlayer"])
        out_lines.append("NODES %d" % glo_prm["nodes"])
        out_lines.append("")

        out_lines.append("#######################################################################")
        out_lines.append("# Output Files and Parameters")
        out_lines.append("#######################################################################")

        out_lines.append("RESULT_DIR %s"% glo_prm["out_path"])
        for out_file in glo_prm["out_file"]:
            out_lines.append("OUTFILE %s" % out_file["out_file"])
            out_lines.append("OUT_FORMAT %s" % out_file["out_format"])
            out_lines.append("COMPRESS %s" % out_file["compress"] )
            out_lines.append("AGGFREQ %s" %  out_file["aggfreq"])
            for var in out_file["out_var"]:
                out_lines.append("OUTVAR %s" % var)
            out_lines.append("")

        out_lines = [line+"\n" for line in out_lines]

        of = open(out_global_file, "w")
        of.writelines(out_lines)
        of.close()
        log.info("File \"%s\" have been write."% out_global_file)

    ####################################################################################################################
    '''
    Write out project parameters file.
    '''
    def write_proj_file(self, out_proj_file=None):
        glo_prm_cp = self.global_params.copy()
        prj_prm_cp = self.proj_params.copy()
        glo_prm_cp["start_time"] = glo_prm_cp["start_time"].strftime('%Y-%m-%d %H:%M:%S')
        glo_prm_cp["end_time"] = glo_prm_cp["end_time"].strftime('%Y-%m-%d %H:%M:%S')

        proj = OrderedDict({
            "proj_params": prj_prm_cp,
            "global_params": glo_prm_cp
        })

        proj_json = json.dumps(proj, indent=4)

        if out_proj_file is None:
            out_proj_file = self.proj_params["proj_file"]

        pf = open(out_proj_file, "w")
        pf.write(proj_json)
        pf.close()

    ####################################################################################################################
    '''
    Read in project parameters file.
    '''
    def read_proj_file(self, proj_file):

        pf = open(proj_file, "r")
        proj_str = pf.readlines()
        pf.close()

        proj_str = "".join(proj_str)
        proj = json.loads(proj_str, object_pairs_hook=OrderedDict)

        self.proj_params = proj["proj_params"]
        self.global_params = proj["global_params"]
        self.global_params["start_time"] = datetime.datetime.strptime(self.global_params["start_time"],
                                                                      '%Y-%m-%d %H:%M:%S')
        self.global_params["end_time"] = datetime.datetime.strptime(self.global_params["end_time"],
                                                                    '%Y-%m-%d %H:%M:%S')

        return self

    ####################################################################################################################
    #
    # Create and delete forcing2 files.
    #
    ####################################################################################################################
    def create_forcing2(self):
        forcing2 = OrderedDict()
        forcing2["file_path"] = None
        forcing2["force_type"] = OrderedDict({
            "AIR_TEMP": "tas",
            "PREC": "prcp",
            "PRESSURE": "pres",
            "SWDOWN": "dwsrf",
            "LWDOWN": "dlwrf",
            "VP": "vp",
            "WIND": "wind"
        })
        forcing2["wind_h"] = None
        self.global_params["forcing2"] = forcing2

    def delete_forcing2(self):
        self.global_params["forcing2"] = None

    ####################################################################################################################
    #
    # Getter & Setters.
    #
    ####################################################################################################################

    ###########################################################################
    # Set input file paths of global parameters.
    ###########################################################################
    def set_parameters_file(self, file_path):
        self.global_params["param_file"] = file_path

    def get_parameters_file(self):
        return self.global_params["param_file"]

    def set_domain_file(self, file_path):
        self.global_params["domain"]["file_path"] = file_path

    def get_domain_file(self):
        return self.global_params["domain"]["file_path"]

    def set_result_path(self, result_path):
        self.global_params["out_path"] = result_path

    def set_start_time(self, y, m, d):
        self.global_params["start_time"] = datetime.datetime(y, m, d)

    def set_end_time(self, y, m, d):
        self.global_params["end_time"] = datetime.datetime(y, m, d)

    ###########################################################################
    # forcing must be a dict like that:
    #     forcing = {
    #         "file_path": ".../filepath.",
    #         "force_type": {
    #             "AIR_TEMP": "tas",
    #             "PREC": "prcp",
    #             "PRESSURE": "pres",
    #             "SWDOWN": "dswrf",
    #             "LWDOWN": "dlwrf",
    #             "VP": "vp",
    #             "WIND": "wind"
    #         },
    #         "wind_h": None
    #     }
    ###########################################################################
    def set_forcing1(self, forcing):
        self.global_params["forcing1"] = forcing

    def set_forcing2(self, forcing):
        self.global_params["forcing2"] = forcing

    ###########################################################################
    # Set and get driver path.
    ###########################################################################

    def set_image_driver(self, driver_path):
        self.proj_params["vic_image_driver"] = driver_path

    def get_image_driver(self):
        return self.proj_params["vic_image_driver"]

    def set_proj_path(self, driver_path):
        self.proj_params["proj_path"] = driver_path

    def get_proj_path(self):
        return self.proj_params["proj_path"]

    def set_ncores(self, ncores):
        self.proj_params["n_cores"] = ncores

    def get_ncores(self):
        return self.proj_params["n_cores"]