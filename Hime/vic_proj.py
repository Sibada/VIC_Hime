#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .version import version as __version__
from collections import OrderedDict
import datetime
import json

class VicProj(object):
    def __init__(self, proj_name, proj_path):
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

        #################################################### Creater parameters
        creater_params = OrderedDict()
        creater_params["n_layers"] = 3
        creater_params["n_rootzones"] = 3
        creater_params["snow_band"] = 5
        creater_params["veg_class"] = 12
        creater_params["soil_file"] = None
        creater_params["veg_file"] = None
        creater_params["veg_lib_file"] = None
        creater_params["params_file"] = None
        creater_params["domain_file"] = None

        creater_params["decimal"] = 4

        # Forcings.
        creater_params["forcing_date"] = datetime.datetime(1949, 1, 1)
        creater_params["temp_file"] = None
        creater_params["prec_file"] = None
        creater_params["press_file"] = None
        creater_params["swdown_file"] = None
        creater_params["lwdown_file"] = None
        creater_params["vp_file"] = None
        creater_params["wind_file"] = None
        creater_params["sh_file"] = None
        creater_params["stn_coords_file"] = None

        creater_params["use_sh"] = False
        creater_params["forcing_file"] = None

        creater_params["itp_method"] = "idw"
        creater_params["idw_params"] = OrderedDict({"idp": 2, "maxd": None})

        prj_prm["creater_params"] = creater_params

        ##################################################### Routing parameters
        rout_params = OrderedDict()
        rout_params["uh_file"] = None
        rout_params["sim_file"] = None
        rout_params["obs_file"] = None
        prj_prm["rout_params"] = rout_params

        #######################################################################
        # VIC global parameters.
        #######################################################################

        # Basic run parameters.
        glo_prm["model_steps_per_day"] = 1
        glo_prm["snow_steps_per_day"] = 4
        glo_prm["runoff_steps_per_day"] = 4
        glo_prm["start_time"] = datetime.datetime(1949, 1, 1)
        glo_prm["end_time"] = datetime.datetime(1980, 12, 31)
        glo_prm["calendar"] = "PROLEPTIC_GREGORIAN"

        glo_prm["full_energy"] = "FALSE"
        glo_prm["frozen_soil"] = "FALSE"

        glo_prm["compute_treeline"] = "FALSE"
        glo_prm["veglib_vegcover"] = "FALSE"
        # Domain file.
        domain = OrderedDict({
            "file_path": None,
            "domain_type": {
                "LAT": "lat",
                "LON": "lon",
                "MASK": "mask",
                "AREA": "area",
                "FRAC": "frac",
                "YDIM": "lat",
                "XDIM": "lon"
            }
        })
        glo_prm["domain"] = domain

        # Forcing files.
        forcing1 = OrderedDict()
        forcing1["file_path"] = None
        forcing1["force_type"] = OrderedDict({
            "AIR_TEMP": "tas",
            "PREC": "prcp",
            "PRESSURE": "pres",
            "SWDOWN": "dwsrf",
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
        glo_prm["baseflow"] = "ARNO"
        glo_prm["LAI_src"] = "FROM_VEGPARAM"
        glo_prm["nodes"] = 3

        # Output files.
        glo_prm["out_path"] = None
        out_file1 = OrderedDict({
            "out_file": "runoff",
            "out_format": "NETCDF4",
            "compress": "FALSE",
            "aggfreq": ["NDAYS", "1"],
            "out_var": ["OUT_RUNOFF",
                        "OUT_BASEFLOW"]
        })
        glo_prm["out_file"] = [out_file1]

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
        domain = glo_prm["domain"]
        out_lines.append("DOMAIN %s" % domain["file_path"])
        for type in domain["domain_type"].items():
            out_lines.append("DOMAIN_TYPE %s %s" % (type[0], type[1]))
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
            out_lines.append("FORCING2 %s" % forcing1["file_path"])
            for type in forcing2["force_type"].items():
                out_lines.append("FORCE_TYPE %s %s" % (type[0], type[1]))
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
        out_lines.append("ORGANIC_FRACT %s" % glo_prm["organic"])
        out_lines.append("LAI_SRC %s" % glo_prm["LAI_src"])
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
            out_lines.append("AGGFREQ %s %s" %  tuple(out_file["aggfreq"]))
            for var in out_file["out_var"]:
                out_lines.append("OUTVAR %s" % var)
            out_lines.append("")

        out_lines = [line+"\n" for line in out_lines]

        of = open(out_global_file, "w")
        of.writelines(out_lines)
        of.close()
        print "File %s have been write."% out_global_file

    ####################################################################################################################
    '''
    Write out project parameters file.
    '''
    def write_proj_file(self, out_proj_file = None):
        glo_prm_cp = self.global_params.copy()
        prj_prm_cp = self.proj_params.copy()
        glo_prm_cp["start_time"] = glo_prm_cp["start_time"].strftime('%Y-%m-%d %H:%M:%S')
        glo_prm_cp["end_time"] = glo_prm_cp["end_time"].strftime('%Y-%m-%d %H:%M:%S')
        prj_prm_cp["creater_params"]["forcing_date"] = \
            prj_prm_cp["creater_params"]["forcing_date"].strftime('%Y-%m-%d %H:%M:%S')

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
        self.proj_params["creater_params"]["forcing_date"] = \
            datetime.datetime.strptime(self.proj_params["creater_params"]["forcing_date"],'%Y-%m-%d %H:%M:%S')

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
    def get_rout_param(self):
        return self.proj_params["rout_params"]

    def set_soil_file(self,soil_file):
        self.proj_params["creater_params"]["soil_file"] = soil_file

    def set_veg_file(self,veg_file):
        self.proj_params["creater_params"]["veg_file"] = veg_file

    def set_veg_lib_file(self, veg_lib_file):
        self.proj_params["creater_params"]["veg_lib_file"] = veg_lib_file

    def set_out_params_file(self, params_file):
        self.proj_params["creater_params"]["params_file"] = params_file

    def set_out_domain_file(self, domain_file):
        self.proj_params["creater_params"]["domain_file"] = domain_file

    def get_out_domain_file(self):
        return self.proj_params["creater_params"]["domain_file"]

    def set_out_forcing_file(self, domain_file):
        self.proj_params["creater_params"]["forcing_file"] = domain_file

    def get_parameters_file(self):
        return self.global_params["param_file"]

    def set_parameters_file(self, file_path):
        self.global_params["param_file"] = file_path

    def set_domain_file(self, file_path):
        self.global_params["domain"]["file_path"] = file_path

    def get_domain_file(self):
        return self.global_params["domain"]["file_path"]

    def set_result_path(self, result_path):
        self.global_params["out_path"] = result_path

    def set_use_sh(self, on):
        self.proj_params["creater_params"]["use_sh"] = on

    def set_atmospheric_file(self, temp, prec, press, vp, wind, swdown=None, lwdown=None, sh=None):
        self.proj_params["creater_params"]["temp_file"] = temp
        self.proj_params["creater_params"]["prec_file"] = prec
        self.proj_params["creater_params"]["press_file"] = press
        self.proj_params["creater_params"]["swdown_file"] = swdown
        self.proj_params["creater_params"]["lwdown_file"] = lwdown
        self.proj_params["creater_params"]["vp_file"] = vp
        self.proj_params["creater_params"]["wind_file"] = wind
        self.proj_params["creater_params"]["sh_file"] = sh

    def set_station_coords_file(self, stn_coords):
        self.proj_params["creater_params"]["stn_coords_file"] = stn_coords

    def set_itp_method(self, method):
        self.proj_params["creater_params"]["itp_method"] = method

    def set_idw_params(self, idp=None, maxd=None):
        if idp is not None: self.proj_params["creater_params"]["idw_params"]["idp"] = idp
        if maxd is not None: self.proj_params["creater_params"]["idw_params"]["maxd"] = maxd

    def set_forcing1_path(self, forcing_path):
        self.global_params["forcing1"]["file_path"] = forcing_path