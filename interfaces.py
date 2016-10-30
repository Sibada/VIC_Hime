#!/usr/bin/env python
#  -*- coding: utf-8 -*-


from Hime import version as __version__
from Hime import templates_path
from Hime import log
from Hime.model_execer.vic_execer import vic_exec
from Hime.routing.uh_creater import create_rout
from Hime.routing.confluence import write_rout_data, load_rout_data, confluence, write_runoff_data, gather_to_month
from Hime.file_creater.forcing_creater import read_stn_data, create_forcing
from Hime.file_creater.param_creater import create_params_file
from Hime.calibrater.calibrater import calibrate

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from collections import OrderedDict
from datetime import datetime as dt
import os
import sys
import re

group_ss = "QGroupBox{border-radius: 5px; border: 2px groove lightgrey; margin-top: 1.2ex;font-family:serif}" \
           "QGroupBox::title {subcontrol-origin: margin;subcontrol-position: top left; left:15px;}"


########################################################################################################################
#
# The first panel of main interface of VIC Hime.
# Mainly for global setting of VIC model.
#
########################################################################################################################
class GlobalConfig(QWidget):
    def __init__(self, parent=None):
        super(GlobalConfig, self).__init__(parent)
        self.parent = parent
        #######################################################################
        # Sys config group
        #######################################################################
        self.vic_driver_le = QLineEdit()
        self.vic_driver_le.setMinimumWidth(128)

        self.cores_le = QLineEdit()
        self.cores_le.setFixedWidth(36)

        self.vic_driver_btn = QPushButton("...")
        self.vic_driver_btn.setFixedWidth(36)

        sys_group = QGroupBox()
        sys_group.setStyleSheet(group_ss)
        sys_group.setTitle("System")
        sys_group.setMinimumWidth(420)

        sys_layout = QHBoxLayout()
        sys_group.setLayout(sys_layout)

        sys_layout.addWidget(QLabel("VIC driver path:"))
        sys_layout.addWidget(self.vic_driver_le)
        sys_layout.addWidget(self.vic_driver_btn)
        sys_layout.addStretch(1)
        sys_layout.addWidget(QLabel("Cores:"))
        sys_layout.addWidget(self.cores_le)

        #######################################################################
        # Global config group
        #######################################################################
        self.start_time_de = QDateTimeEdit()
        self.start_time_de.setDateTime(QDateTime(1949, 1, 1, 0, 0, 0))
        self.start_time_de.setDisplayFormat("yyyy-MM-dd")
        self.end_time_de = QDateTimeEdit()
        self.end_time_de.setDateTime(QDateTime(1950, 12, 31, 0, 0, 0))
        self.end_time_de.setDisplayFormat("yyyy-MM-dd")

        self.calendars = ["standard", "gregorian", "proleptic_gregorian","noleap",
                          "365_day", "360_day", "julian", "all_leap", "366_day"]
        self.calendar_co = QComboBox()
        self.calendar_co.addItems(self.calendars)

        self.model_steps_le = QLineEdit()
        self.snow_steps_le = QLineEdit()
        self.runoff_steps_le = QLineEdit()

        self.model_steps_le.setText("1")
        self.snow_steps_le.setText("4")
        self.runoff_steps_le.setText("4")

        self.model_steps_le.setFixedWidth(36)
        self.snow_steps_le.setFixedWidth(36)
        self.runoff_steps_le.setFixedWidth(36)

        self.param_path_le = QLineEdit()
        self.param_path_btn = QPushButton("...")
        self.param_path_btn.setFixedWidth(36)
        self.domain_path_le = QLineEdit()
        self.domain_path_btn = QPushButton("...")
        self.domain_path_btn.setFixedWidth(36)

        self.nodes_le = QLineEdit()
        self.nodes_le.setFixedWidth(36)

        self.layers_le = QLineEdit()
        self.layers_le.setFixedWidth(36)

        self.full_energy_cb = QCheckBox("Full energy")
        self.close_energy_cb = QCheckBox("Close energy")
        self.frozen_soil_cb = QCheckBox("Frozen soil")
        self.quick_flux_cb = QCheckBox("Quick flux")
        self.snow_bands_cb = QCheckBox("Snow bands")
        self.organic_cb = QCheckBox("Organic")
        self.organic_fract_cb = QCheckBox("Organic fraction")
        self.july_tavg_supplied_cb = QCheckBox("JULY_TAVG supplied")
        self.compute_treeline_cb = QCheckBox("Compute treeline")

        global_group = QGroupBox()
        global_group.setStyleSheet(group_ss)
        global_group.setTitle("Global")

        global_layout = QVBoxLayout()
        global_group.setLayout(global_layout)

        sub_top_layout = QGridLayout()

        sub_top_layout.addWidget(QLabel("Start time:"), 0, 0, 1, 1)
        sub_top_layout.addWidget(self.start_time_de, 0, 1, 1, 1)
        sub_top_layout.addWidget(QLabel("End time:"), 1, 0, 1, 1)
        sub_top_layout.addWidget(self.end_time_de, 1, 1, 1, 1)
        sub_top_layout.addWidget(QLabel("Calendar:"), 2, 0, 1, 1)
        sub_top_layout.addWidget(self.calendar_co, 2, 1, 1, 1)

        sub_top_layout.addWidget(QLabel("Model steps"), 0, 2, 1, 1)
        sub_top_layout.addWidget(QLabel("Snow steps"), 1, 2, 1, 1)
        sub_top_layout.addWidget(QLabel("Runoff steps"), 2, 2, 1, 1)

        sub_top_layout.addWidget(self.model_steps_le, 0, 3, 1, 1)
        sub_top_layout.addWidget(self.snow_steps_le, 1, 3, 1, 1)
        sub_top_layout.addWidget(self.runoff_steps_le, 2, 3, 1, 1)

        sub_median_layout = QGridLayout()
        sub_median_layout.addWidget(QLabel("Parameters file:"), 1, 0, 1, 2)
        sub_median_layout.addWidget(self.param_path_le, 1, 2, 1, 4)
        sub_median_layout.addWidget(self.param_path_btn, 1, 6, 1, 1)
        sub_median_layout.addWidget(QLabel("Domain file:"), 2, 0, 1, 2)
        sub_median_layout.addWidget(self.domain_path_le, 2, 2, 1, 4)
        sub_median_layout.addWidget(self.domain_path_btn, 2, 6, 1, 1)

        sub_median_layout.addWidget(QLabel("Layers:"), 0, 0, 1, 1)
        sub_median_layout.addWidget(self.layers_le, 0, 1, 1, 1)

        sub_median_layout.addWidget(QLabel("Nodes:"), 0, 3, 1, 1)
        sub_median_layout.addWidget(self.nodes_le, 0, 4, 1, 1)

        sub_bottom_layout = QGridLayout()
        sub_bottom_layout.addWidget(self.full_energy_cb, 0, 0, 1, 2)
        sub_bottom_layout.addWidget(self.close_energy_cb, 0, 2, 1, 2)
        sub_bottom_layout.addWidget(self.frozen_soil_cb, 1, 0, 1, 2)
        sub_bottom_layout.addWidget(self.quick_flux_cb, 1, 2, 1, 2)
        sub_bottom_layout.addWidget(self.organic_cb, 2, 0, 1, 2)
        sub_bottom_layout.addWidget(self.organic_fract_cb, 2, 2, 1, 2)
        sub_bottom_layout.addWidget(self.snow_bands_cb, 3, 0, 1, 2)
        sub_bottom_layout.addWidget(self.july_tavg_supplied_cb, 3, 2, 1, 2)
        sub_bottom_layout.addWidget(self.compute_treeline_cb, 4, 2, 1, 2)

        global_layout.addLayout(sub_top_layout)
        global_layout.addLayout(sub_median_layout)
        global_layout.addLayout(sub_bottom_layout)

        #######################################################################
        # Forcings interface setting
        #######################################################################
        self.forcing_table = QTableWidget()
        self.forcing_table.setMinimumWidth(192)
        self.forcing_table.setColumnCount(2)
        forcing_header = self.forcing_table.horizontalHeader()
        forcing_header.setResizeMode(0, QHeaderView.ResizeToContents)
        forcing_header.setResizeMode(1, QHeaderView.Stretch)
        self.forcing_table.setHorizontalHeaderLabels(["Force type", "nc variable name"])

        self.add_forcing_btn = QPushButton("Add item")
        self.remove_forcing_btn = QPushButton("Remove item")

        self.forcing_path_le = QLineEdit()
        self.forcing_path_btn = QPushButton("...")
        self.forcing_path_btn.setFixedWidth(36)

        forcings_group = QGroupBox()
        forcings_group.setStyleSheet(group_ss)
        forcings_group.setTitle("Forcing files")
        forcings_layout = QGridLayout()
        forcings_group.setLayout(forcings_layout)

        forcings_layout.addWidget(self.forcing_table, 0, 0, 5, 6)
        forcings_layout.addWidget(self.add_forcing_btn, 5, 3, 1, 1)
        forcings_layout.addWidget(self.remove_forcing_btn, 5, 4, 1, 2)
        forcings_layout.addWidget(QLabel("Path:"), 6, 0, 1, 1)
        forcings_layout.addWidget(self.forcing_path_le, 6, 1, 1, 4)
        forcings_layout.addWidget(self.forcing_path_btn, 6, 5, 1, 1)

        #######################################################################
        # Outputs interface setting
        #######################################################################
        self.output_table = QTableWidget()
        self.output_table.setMinimumWidth(192)
        self.output_table.setColumnCount(4)
        output_header = self.output_table.horizontalHeader()
        for i in range(7):
            output_header.setResizeMode(i, QHeaderView.ResizeToContents)
        self.output_table.setHorizontalHeaderLabels(["Out file", "Out variable", "Out format", "Agg freq"])

        self.add_outputs_btn = QPushButton("Add item")
        self.remove_outputs_btn = QPushButton("Remove item")

        self.output_path_le = QLineEdit()
        self.output_path_btn = QPushButton("...")
        self.output_path_btn.setFixedWidth(36)

        outputs_group = QGroupBox()
        outputs_group.setStyleSheet(group_ss)
        outputs_group.setTitle("Output files")
        outputs_layout = QGridLayout()
        outputs_group.setLayout(outputs_layout)

        outputs_layout.addWidget(self.output_table, 0, 0, 5, 6)
        outputs_layout.addWidget(self.add_outputs_btn, 5, 3, 1, 1)
        outputs_layout.addWidget(self.remove_outputs_btn, 5, 4, 1, 2)
        outputs_layout.addWidget(QLabel("Path:"), 6, 0, 1, 1)
        outputs_layout.addWidget(self.output_path_le, 6, 1, 1, 4)
        outputs_layout.addWidget(self.output_path_btn, 6, 5, 1, 1)

        #######################################################################
        # Bottom buttons
        #######################################################################
        self.global_path_le = QLineEdit()
        self.global_path_le.setMinimumWidth(240)
        self.global_path_btn = QPushButton("...")
        self.global_path_btn.setFixedWidth(36)

        self.save_btn = QPushButton("&Save settings")
        self.create_global_btn = QPushButton("&Create global file")

        button_layout = QHBoxLayout()
        button_layout.addStretch(1)
        button_layout.addWidget(QLabel("Global file path:"))
        button_layout.addWidget(self.global_path_le)
        button_layout.addWidget(self.global_path_btn)
        button_layout.addStretch(1)
        button_layout.addWidget(self.save_btn)
        button_layout.addWidget(self.create_global_btn)

        #######################################################################
        # Main layout
        #######################################################################
        main_layout = QVBoxLayout()
        top_layout = QHBoxLayout()
        left_layout = QVBoxLayout()
        right_layout = QVBoxLayout()

        left_layout.addWidget(sys_group)
        left_layout.addWidget(global_group)
        left_layout.addStretch(1)
        right_layout.addWidget(forcings_group)
        right_layout.addWidget(outputs_group)
        top_layout.addLayout(left_layout)
        top_layout.addLayout(right_layout)
        main_layout.addLayout(top_layout)
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

        #######################################################################
        # Actions of file dialogs (Setting path).
        #######################################################################
        self.connect(self.vic_driver_btn, SIGNAL("clicked()"),
                     lambda: self.set_file_by_dialog(line_edit=self.vic_driver_le, disc="Set VIC driver path"))

        self.connect(self.param_path_btn, SIGNAL("clicked()"),
                     lambda: self.set_file_by_dialog(line_edit=self.param_path_le, disc="Set parameters file path"))

        self.connect(self.domain_path_btn, SIGNAL("clicked()"),
                     lambda: self.set_file_by_dialog(line_edit=self.domain_path_le, disc="Set domain file path"))

        self.connect(self.global_path_btn, SIGNAL("clicked()"),
                     lambda: self.set_file_by_dialog(line_edit=self.global_path_le, disc="Set global file path"))

        self.connect(self.output_path_btn, SIGNAL("clicked()"),
                     lambda: self.set_dir_by_dialog(line_edit=self.output_path_le, disc="Set VIC output path"))

        self.connect(self.forcing_path_btn, SIGNAL("clicked()"), self.set_forcing_path)

        #######################################################################
        # Saving, writing global file, and others.
        #######################################################################
        self.connect(self.save_btn, SIGNAL("clicked()"), self.save_setting)

        self.connect(self.create_global_btn, SIGNAL("clicked()"), self.write_global_file)

        self.connect(self.add_forcing_btn, SIGNAL("clicked()"), lambda: self.add_item(table=self.forcing_table))
        self.connect(self.remove_forcing_btn, SIGNAL("clicked()"), lambda: self.remove_item(table=self.forcing_table))

        self.connect(self.add_outputs_btn, SIGNAL("clicked()"), lambda: self.add_item(table=self.output_table))
        self.connect(self.remove_outputs_btn, SIGNAL("clicked()"), lambda: self.remove_item(table=self.output_table))

        #######################################################################
        # Parameters
        #######################################################################
        # TODO

    def load_configs(self):
        proj_params = self.parent.proj.proj_params
        global_params = self.parent.proj.global_params
        self.vic_driver_le.setText(unicode(proj_params["vic_image_driver"]))
        self.cores_le.setText(unicode(proj_params["n_cores"]))
        self.global_path_le.setText(unicode(proj_params["global_file"]))

        self.start_time_de.setDateTime(global_params["start_time"])
        self.end_time_de.setDateTime(global_params["end_time"])

        calendar = global_params["calendar"]
        for i in range(self.calendar_co.count()):
            if self.calendar_co.itemText(i) == calendar:
                self.calendar_co.setCurrentIndex(i)

        self.model_steps_le.setText(unicode(global_params["model_steps_per_day"]))
        self.snow_steps_le.setText(unicode(global_params["snow_steps_per_day"]))
        self.runoff_steps_le.setText(unicode(global_params["runoff_steps_per_day"]))

        self.nodes_le.setText(unicode(global_params["nodes"]))
        self.layers_le.setText(unicode(global_params["nlayer"]))

        self.param_path_le.setText(unicode(global_params["param_file"]))
        self.domain_path_le.setText(unicode(global_params["domain_file"]))

        if global_params.get("full_energy") == "TRUE":
            self.full_energy_cb.setCheckState(Qt.Checked)
        else:
            self.full_energy_cb.setCheckState(Qt.Unchecked)

        if global_params.get("close_energy") == "TRUE":
            self.close_energy_cb.setCheckState(Qt.Checked)
        else:
            self.close_energy_cb.setCheckState(Qt.Unchecked)

        if global_params.get("frozen_soil") == "TRUE":
            self.frozen_soil_cb.setCheckState(Qt.Checked)
        else:
            self.frozen_soil_cb.setCheckState(Qt.Unchecked)

        if global_params.get("quick_flux") == "TRUE":
            self.quick_flux_cb.setCheckState(Qt.Checked)
        else:
            self.quick_flux_cb.setCheckState(Qt.Unchecked)

        if global_params.get("organic") == "TRUE":
            self.organic_cb.setCheckState(Qt.Checked)
        else:
            self.organic_cb.setCheckState(Qt.Unchecked)

        if global_params.get("organic_fract") == "TRUE":
            self.organic_fract_cb.setCheckState(Qt.Checked)
        else:
            self.organic_fract_cb.setCheckState(Qt.Unchecked)

        if global_params.get("snow_band") == "TRUE":
            self.snow_bands_cb.setCheckState(Qt.Checked)
        else:
            self.snow_bands_cb.setCheckState(Qt.Unchecked)

        if global_params.get("july_tavg") == "TRUE":
            self.july_tavg_supplied_cb.setCheckState(Qt.Checked)
        else:
            self.july_tavg_supplied_cb.setCheckState(Qt.Unchecked)

        if global_params.get("compute_treeline") == "TRUE":
            self.compute_treeline_cb.setCheckState(Qt.Checked)
        else:
            self.compute_treeline_cb.setCheckState(Qt.Unchecked)

        # Forcings.
        self.forcing_path_le.setText(unicode(global_params["forcing1"]["file_path"]))
        forcing1_types = global_params["forcing1"]["force_type"]
        self.forcing_table.setRowCount(len(forcing1_types))
        for i in range(len(forcing1_types)):
            key = forcing1_types.keys()[i]
            self.forcing_table.setItem(i, 0, QTableWidgetItem(key))
            self.forcing_table.setItem(i, 1, QTableWidgetItem(forcing1_types[key]))

        # Outputs.
        self.output_path_le.setText(unicode(global_params["out_path"]))
        r = 0
        for f in global_params["out_file"]:
            for type in f["out_var"]:
                self.output_table.setRowCount(r + 1)
                self.output_table.setItem(r, 0, QTableWidgetItem(f["out_file"]))
                self.output_table.setItem(r, 1, QTableWidgetItem(type))
                self.output_table.setItem(r, 2, QTableWidgetItem(f["out_format"]))
                self.output_table.setItem(r, 3, QTableWidgetItem(f["aggfreq"]))
                r += 1

    def apply_configs(self):
        proj_params = self.parent.proj.proj_params
        global_params = self.parent.proj.global_params
        proj_params["vic_image_driver"] = unicode(self.vic_driver_le.text())
        proj_params["n_cores"] = unicode(self.cores_le.text())
        proj_params["global_file"] = unicode(self.global_path_le.text())

        global_params["start_time"] = self.start_time_de.dateTime().toPyDateTime()
        global_params["end_time"] = self.end_time_de.dateTime().toPyDateTime()

        global_params["calendar"] = unicode(self.calendar_co.currentText())

        global_params["model_steps_per_day"] = int(self.model_steps_le.text())
        global_params["snow_steps_per_day"] = int(self.model_steps_le.text())
        global_params["runoff_steps_per_day"] = int(self.model_steps_le.text())
        global_params["nodes"] = int(self.nodes_le.text())
        global_params["nlayer"] = int(self.layers_le.text())
        global_params["param_file"] = unicode(self.param_path_le.text())
        global_params["domain_file"] = unicode(self.domain_path_le.text())

        global_params["full_energy"] = "TRUE" if self.full_energy_cb.isChecked() else "False"
        global_params["close_energy"] = "TRUE" if self.close_energy_cb.isChecked() else "False"
        global_params["frozen_soil"] = "TRUE" if self.frozen_soil_cb.isChecked() else "False"
        global_params["quick_flux"] = "TRUE" if self.quick_flux_cb.isChecked() else "False"
        global_params["organic"] = "TRUE" if self.organic_cb.isChecked() else "False"
        global_params["organic_fract"] = "TRUE" if self.organic_fract_cb.isChecked() else "False"
        global_params["snow_band"] = "TRUE" if self.snow_bands_cb.isChecked() else "False"
        global_params["july_tavg"] = "TRUE" if self.july_tavg_supplied_cb.isChecked() else "False"
        global_params["compute_treeline"] = "TRUE" if self.compute_treeline_cb.isChecked() else "False"

        # Forcings.
        global_params["forcing1"]["file_path"] = unicode(self.forcing_path_le.text())
        global_params["forcing1"]["force_type"] = OrderedDict()
        forcing1_types = global_params["forcing1"]["force_type"]
        for i in range(self.forcing_table.rowCount()):
            key = unicode(self.forcing_table.item(i, 0).text())
            value = unicode(self.forcing_table.item(i, 1).text())
            forcing1_types[key] = value

        # Outputs.
        global_params["out_path"] = unicode(self.output_path_le.text())
        global_params["out_file"] = []
        current_file = None
        for i in range(self.output_table.rowCount()):
            out_file = unicode(self.output_table.item(i, 0).text())
            out_var = unicode(self.output_table.item(i, 1).text())
            out_format = unicode(self.output_table.item(i, 2).text())
            agg_freq = unicode(self.output_table.item(i, 3).text())

            if current_file != out_file:
                current_file = out_file

                current_info = OrderedDict()
                current_info["out_file"] = current_file
                current_info["out_format"] = out_format
                current_info["compress"] = "FALSE"
                current_info["aggfreq"] = agg_freq
                current_info["out_var"] = []
                global_params["out_file"].append(current_info)

            current_info["out_var"].append(out_var)

    def save_setting(self):
        self.apply_configs()
        self.parent.save_proj()

    def set_file_by_dialog(self, line_edit, disc):
        file = QFileDialog.getOpenFileName(self, disc)
        log.debug("Get file: %s" % file)
        if file == "":
            return
        line_edit.setText(file)

    def set_dir_by_dialog(self, line_edit, disc):
        dir = QFileDialog.getExistingDirectory(self, disc)
        log.debug("Get dir: %s" % dir)
        if dir == "":
            return
        line_edit.setText(dir)

    def set_forcing_path(self):
        forcing_file = QFileDialog.getOpenFileName(self, "Set forcing files")
        log.debug("Get file: %s" % forcing_file)
        if forcing_file == "":
            return
        forcing_file = re.sub(r"\d\d\d\d\.nc", "", unicode(forcing_file))
        self.forcing_path_le.setText(forcing_file)

    def add_item(self, table):
        nrow_o = table.rowCount()
        table.setRowCount(nrow_o + 1)
        if nrow_o < 1:
            return
        for i in range(table.columnCount()):
            table.setItem(nrow_o, i, QTableWidgetItem(table.item(nrow_o-1, i)))

    def remove_item(self, table):
        rs = [ind.row() for ind in table.selectedIndexes()]
        rs = list(set(rs))
        rs.sort(reverse=True)
        [table.removeRow(r) for r in rs]
        log.debug("Remove row %s" % rs)

    def write_global_file(self):
        self.parent.proj.write_global_file()


########################################################################################################################
#
# The second panel of main interface of VIC Hime.
# Mainly to run VIC model.
#
########################################################################################################################
class VicRun(QWidget):
    def __init__(self, parent=None):
        super(VicRun, self).__init__(parent)
        self.parent = parent
        #######################################################################
        # Driver config group
        #######################################################################
        self.vic_driver_le = QLineEdit()
        self.vic_driver_le.setMinimumWidth(128)

        self.cores_le = QLineEdit()
        self.cores_le.setFixedWidth(36)

        self.vic_driver_btn = QPushButton("...")
        self.vic_driver_btn.setFixedWidth(36)

        driver_group = QGroupBox()
        driver_group.setStyleSheet(group_ss)
        driver_group.setTitle("VIC driver")
        driver_group.setMinimumWidth(420)

        driver_layout = QHBoxLayout()
        driver_group.setLayout(driver_layout)

        driver_layout.addWidget(QLabel("VIC driver path:"))
        driver_layout.addWidget(self.vic_driver_le)
        driver_layout.addWidget(self.vic_driver_btn)
        driver_layout.addStretch(1)
        driver_layout.addWidget(QLabel("Cores:"))
        driver_layout.addWidget(self.cores_le)

        #######################################################################
        # Input file config group
        #######################################################################

        self.global_file_le = QLineEdit()
        self.global_file_btn = QPushButton("...")
        self.global_file_btn.setFixedWidth(36)

        self.rout_cb = QCheckBox("With routing")
        self.rout_data_le = QLineEdit()
        self.rout_data_btn = QPushButton("...")
        self.rout_data_btn.setFixedWidth(36)

        self.rout_out_path_le = QLineEdit()
        self.rout_out_path_btn = QPushButton("...")
        self.rout_out_path_btn.setFixedWidth(36)

        self.vic_output_le = QLineEdit()
        self.vic_output_btn = QPushButton("...")
        self.vic_output_btn.setFixedWidth(36)

        self.apply_configs_btn = QPushButton("&Apply configs")
        self.mpi_cb = QCheckBox("Run with MPI")

        self.apply_configs_btn = QPushButton("&Apply configs")
        self.run_btn = QPushButton("&Run VIC")

        self.vic_run_console = QTextBrowser()

        input_file_group = QGroupBox()
        input_file_group.setStyleSheet(group_ss)
        input_file_group.setTitle("Input file")
        input_file_group.setMinimumWidth(420)

        input_file_layout = QGridLayout()
        input_file_layout.addWidget(QLabel("Global file:"), 0, 0)
        input_file_layout.addWidget(self.global_file_le, 0, 1, 1, 3)
        input_file_layout.addWidget(self.global_file_btn, 0, 4, 1, 1)
        input_file_layout.addWidget(self.rout_cb, 1, 0, 1, 1)

        input_file_layout.addWidget(self.mpi_cb, 1, 2, 1, 1)
        input_file_layout.addWidget(self.apply_configs_btn, 5, 5, 1, 1)
        input_file_layout.addWidget(self.run_btn, 5, 7, 1, 1)

        input_file_group.setLayout(input_file_layout)

        main_layout = QVBoxLayout()
        main_layout.addWidget(driver_group)
        main_layout.addWidget(input_file_group)
        # main_layout.addStretch(1)
        main_layout.addWidget(self.vic_run_console)
        self.setLayout(main_layout)

        #######################################################################
        # Connections.
        #######################################################################
        self.connect(self.vic_driver_btn, SIGNAL("clicked()"),
                     lambda: self.set_file_by_dialog(line_edit=self.vic_driver_le, disc="Set VIC driver file path"))
        self.connect(self.global_file_btn, SIGNAL("clicked()"),
                     lambda: self.set_file_by_dialog(line_edit=self.global_file_le, disc="Set global file path"))
        self.connect(self.vic_output_btn, SIGNAL("clicked()"),
                     lambda: self.set_file_by_dialog(line_edit=self.vic_output_le, disc="Set VIC output file path."))
        self.connect(self.rout_data_btn, SIGNAL("clicked()"),
                     lambda: self.set_file_by_dialog(line_edit=self.rout_data_le, disc="Set routing data path."))
        self.connect(self.rout_out_path_btn, SIGNAL("clicked()"),
                     lambda: self.set_dir_by_dialog(line_edit=self.rout_out_path_le, disc="Set routing output path."))

        self.connect(self.run_btn, SIGNAL("clicked()"), self.start_vic)
        self.connect(self.apply_configs_btn, SIGNAL("clicked()"), self.apply_configs)

        #######################################################################
        # Business part
        #######################################################################
        self.configs = None
        self.vic_running = False
        self.vic_run_thread = VICRunThread(self)

    def set_file_by_dialog(self, line_edit, disc):
        file = QFileDialog.getOpenFileName(self, disc)
        log.debug("Open file: %s" % file)
        if file == "":
            return
        line_edit.setText(file)

    def set_dir_by_dialog(self, line_edit, disc):
        dir = QFileDialog.getExistingDirectory(self, disc)
        log.debug("Open directory: %s" % dir)
        if dir == "":
            return
        line_edit.setText(dir)

    def output_writen(self, text):
        cursor = self.parent.vic_run_console.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.insertText(text)
        self.parent.vic_run_console.setTextCursor(cursor)
        self.parent.vic_run_console.ensureCursorVisible()

    def run_vic(self):
        if self.rout_cb.isChecked() and self.parent.proj.proj_params.get("routing_config") is None:
            log.error("Routing configs was not set. Can not run with routing.")
            return

        vic_path = unicode(self.vic_driver_le.text())
        n_cores = unicode(self.cores_le.text())
        use_mpi = True if self.mpi_cb.isChecked() else False

        status, logs = vic_exec(vic_path, unicode(self.global_file_le.text()), mpi=use_mpi, n_cores=n_cores)
        for line in logs:
            self.vic_run_console.setText(unicode(line))

        if status != 0:
            log.error("Error in VIC running.")
            return

        log.info("VIC running complete.")
        if self.rout_cb.isChecked():
            pass
        log.info("Routing complete.")

    def start_vic(self):
        log.info("VIC start to run...")
        self.vic_running = True
        sys.stdout = StreamEmitter(text_written=self.output_writen)
        sys.stderr = StreamEmitter(text_written=self.output_writen)

        self.vic_run_thread.start()

        self.parent.vic_running = False
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__
        log.info("VIC run completed.")

    def apply_configs(self):
        self.configs["vic_driver_path"] = unicode(self.vic_driver_le.text())
        self.configs["n_cores"] = unicode(self.cores_le.text())
        self.configs["global_file"] = unicode(self.global_file_le.text())

        if self.mpi_cb.isChecked():
            self.configs["with_mpi"] = True
        else:
            self.configs["with_mpi"] = False

        if self.rout_cb.isChecked():
            self.configs["with_routing"] = True
        else:
            self.configs["with_routing"] = False

        self.parent.proj.proj_params["vic_run_config"] = self.configs
        self.parent.dirty = True
        log.info("Configs has been applied.")

    def load_configs(self):
        if self.parent.proj.proj_params.get("vic_run_config") is None:
            self.configs = OrderedDict()
            self.configs["vic_driver_path"] = "None"
            self.configs["n_cores"] = "4"
            self.configs["global_file"] = self.parent.proj.proj_params["global_file"]
            self.configs["with_mpi"] = False
            self.configs["with_routing"] = False
        else:
            self.configs = self.parent.proj.proj_params["vic_run_config"]

        self.vic_driver_le.setText(self.configs["vic_driver_path"])
        self.cores_le.setText(self.configs["n_cores"])
        self.global_file_le.setText(self.configs["global_file"])

        if self.configs["with_mpi"]:
            self.mpi_cb.setCheckState(Qt.Checked)
        else:
            self.mpi_cb.setCheckState(Qt.Unchecked)

        if self.configs["with_routing"]:
            self.rout_cb.setCheckState(Qt.Checked)
        else:
            self.rout_cb.setCheckState(Qt.Unchecked)


class VICRunThread(QThread):
    def __init__(self, parent=None):
        super(VICRunThread, self).__init__(parent)
        self.parent = parent

    def run(self):
        self.parent.run_vic()


class StreamEmitter(QObject):
    def __init__(self, parent=None, text_written=None):
        super(StreamEmitter, self).__init__(parent)
        self.parent = parent
        if text_written is None:
            self.text_written = pyqtSignal(str)

    def write(self, text):
        self.text_written.emit(str(text))


########################################################################################################################
#
# The third panel of main interface of VIC Hime.
# Mainly to run Routing model for VIC.
#
########################################################################################################################
class Routing(QWidget):
    def __init__(self, parent=None):
        super(Routing, self).__init__(parent)
        self.parent = parent
        #######################################################################
        # Rout data creating group
        #######################################################################
        self.direc_file_le = QLineEdit()
        self.direc_file_btn = QPushButton("...")
        self.direc_file_btn.setFixedWidth(36)

        self.veloc_file_le = QLineEdit()
        self.veloc_file_btn = QPushButton("...")
        self.veloc_file_btn.setFixedWidth(36)

        self.diffu_file_le = QLineEdit()
        self.diffu_file_btn = QPushButton("...")
        self.diffu_file_btn.setFixedWidth(36)

        self.uh_slope_data_le = QLineEdit()
        self.uh_slope_data_btn = QPushButton("...")
        self.uh_slope_data_btn.setFixedWidth(36)

        self.out_rout_data_le = QLineEdit()
        self.out_rout_data_btn = QPushButton("...")
        self.out_rout_data_btn.setFixedWidth(36)

        self.stn_name_le = QLineEdit()
        self.stn_name_le.setFixedWidth(128)

        self.stn_x_le = QLineEdit()
        self.stn_x_le.setFixedWidth(36)
        self.stn_y_le = QLineEdit()
        self.stn_y_le.setFixedWidth(36)

        self.create_rout_data_btn = QPushButton("&Create rout data")

        rout_data_group = QGroupBox()
        rout_data_group.setStyleSheet(group_ss)
        rout_data_layout = QGridLayout()
        rout_data_group.setLayout(rout_data_layout)
        rout_data_group.setTitle("Rout data create")
        rout_data_layout.addWidget(QLabel("Direction file:"), 0, 0)
        rout_data_layout.addWidget(self.direc_file_le, 0, 1, 1, 10)
        rout_data_layout.addWidget(self.direc_file_btn, 0, 11, 1, 1)
        rout_data_layout.addWidget(QLabel("Velocity file:"), 1, 0)
        rout_data_layout.addWidget(self.veloc_file_le, 1, 1, 1, 10)
        rout_data_layout.addWidget(self.veloc_file_btn, 1, 11, 1, 1)
        rout_data_layout.addWidget(QLabel("Diffusion file:"), 2, 0)
        rout_data_layout.addWidget(self.diffu_file_le, 2, 1, 1, 10)
        rout_data_layout.addWidget(self.diffu_file_btn, 2, 11, 1, 1)
        rout_data_layout.addWidget(QLabel("Slope UH file:"), 3, 0)
        rout_data_layout.addWidget(self.uh_slope_data_le, 3, 1, 1, 10)
        rout_data_layout.addWidget(self.uh_slope_data_btn, 3, 11, 1, 1)
        rout_data_layout.addWidget(QLabel("Station name:"), 4, 0)
        rout_data_layout.addWidget(self.stn_name_le, 4, 1, 1, 3)
        rout_data_layout.addWidget(QLabel("Station location  Column:"), 5, 0, 1, 2)
        rout_data_layout.addWidget(self.stn_x_le, 5, 2)
        rout_data_layout.addWidget(QLabel("Row:"), 5, 3)
        rout_data_layout.addWidget(self.stn_y_le, 5, 4)
        rout_data_layout.addWidget(QLabel("Rout data output path:"), 6, 0, 1, 2)
        rout_data_layout.addWidget(self.out_rout_data_le, 6, 2, 1, 9)
        rout_data_layout.addWidget(self.out_rout_data_btn, 6, 11, 1, 1)
        rout_data_layout.addWidget(self.create_rout_data_btn, 7, 10, 1, 2)

        #######################################################################
        # Routing group
        #######################################################################
        self.vic_out_file_le = QLineEdit()
        self.vic_out_file_btn = QPushButton("...")
        self.vic_out_file_btn.setFixedWidth(36)

        self.domain_file_le = QLineEdit()
        self.domain_file_btn = QPushButton("...")
        self.domain_file_btn.setFixedWidth(36)

        self.rout_data_file_le = QLineEdit()
        self.rout_data_file_btn = QPushButton("...")
        self.rout_data_file_btn.setFixedWidth(36)

        self.rout_out_dir_le = QLineEdit()
        self.rout_out_dir_btn = QPushButton("...")
        self.rout_out_dir_btn.setFixedWidth(36)

        self.start_date_de = QDateTimeEdit()
        self.start_date_de.setDisplayFormat("yyyy-MM-dd")
        self.end_date_de = QDateTimeEdit()
        self.end_date_de.setDisplayFormat("yyyy-MM-dd")

        self.apply_configs_btn = QPushButton("&Apply configs")
        self.routing_btn = QPushButton("&Routing")

        routing_group = QGroupBox()
        routing_group.setStyleSheet(group_ss)
        routing_group.setTitle("Routing")
        routing_layout = QGridLayout()
        routing_group.setLayout(routing_layout)
        routing_layout.addWidget(QLabel("VIC output file:"), 0, 0)
        routing_layout.addWidget(self.vic_out_file_le, 0, 1, 1, 8)
        routing_layout.addWidget(self.vic_out_file_btn, 0, 9)
        routing_layout.addWidget(QLabel("Domain file:"), 1, 0)
        routing_layout.addWidget(self.domain_file_le, 1, 1, 1, 8)
        routing_layout.addWidget(self.domain_file_btn, 1, 9)
        routing_layout.addWidget(QLabel("Rout data file:"), 2, 0)
        routing_layout.addWidget(self.rout_data_file_le, 2, 1, 1, 8)
        routing_layout.addWidget(self.rout_data_file_btn, 2, 9)
        routing_layout.addWidget(QLabel("Start date:"), 3, 0)
        routing_layout.addWidget(self.start_date_de, 3, 1, 1, 3)
        routing_layout.addWidget(QLabel("End date:"), 4, 0)
        routing_layout.addWidget(self.end_date_de, 4, 1, 1, 3)
        routing_layout.addWidget(QLabel("Routing output path:"), 5, 0, 1, 2)
        routing_layout.addWidget(self.rout_out_dir_le, 5, 2, 1, 7)
        routing_layout.addWidget(self.rout_out_dir_btn, 5, 9)

        routing_layout.addWidget(self.apply_configs_btn, 6, 6, 1, 2)
        routing_layout.addWidget(self.routing_btn, 6, 8, 1, 2)

        main_layout = QVBoxLayout()
        main_layout.addWidget(rout_data_group)
        main_layout.addWidget(routing_group)
        self.setLayout(main_layout)

        self.connect(self.direc_file_btn, SIGNAL("clicked()"),
                     lambda: self.set_file_by_dialog(line_edit=self.direc_file_le, disc="Set flow direction file path"))
        self.connect(self.veloc_file_btn, SIGNAL("clicked()"),
                     lambda: self.set_file_by_dialog(line_edit=self.veloc_file_le, disc="Set velocity file path"))
        self.connect(self.diffu_file_btn, SIGNAL("clicked()"),
                     lambda: self.set_file_by_dialog(line_edit=self.direc_file_le, disc="Set diffusion file path"))
        self.connect(self.uh_slope_data_btn, SIGNAL("clicked()"),
                     lambda: self.set_file_by_dialog(line_edit=self.uh_slope_data_le, disc="Set Slope UH file path"))
        self.connect(self.out_rout_data_btn, SIGNAL("clicked()"),
                     lambda: self.set_file_by_dialog(line_edit=self.out_rout_data_le, disc="Set Slope UH file path"))
        self.connect(self.vic_out_file_btn, SIGNAL("clicked()"),
                     lambda: self.set_file_by_dialog(line_edit=self.vic_out_file_le, disc="Set Slope UH file path"))
        self.connect(self.domain_file_btn, SIGNAL("clicked()"),
                     lambda: self.set_file_by_dialog(line_edit=self.domain_file_le, disc="Set Slope UH file path"))
        self.connect(self.rout_data_file_btn, SIGNAL("clicked()"),
                     lambda: self.set_file_by_dialog(line_edit=self.rout_data_file_le, disc="Set Slope UH file path"))
        self.connect(self.rout_out_dir_btn, SIGNAL("clicked()"),
                     lambda: self.set_dir_by_dialog(line_edit=self.rout_out_dir_le, disc="Set Slope UH file path"))

        self.connect(self.create_rout_data_btn, SIGNAL("clicked()"), self.create_rout_data)
        self.connect(self.apply_configs_btn, SIGNAL("clicked()"), self.apply_configs)
        self.connect(self.routing_btn, SIGNAL("clicked()"), self.routing)

        #######################################################################
        # Business part
        #######################################################################
        self.configs = None

    def set_file_by_dialog(self, line_edit, disc):
        file = QFileDialog.getOpenFileName(self, disc)
        log.debug("Open file: %s" % file)
        if file == "":
            return
        line_edit.setText(file)

    def set_dir_by_dialog(self, line_edit, disc):
        dir = QFileDialog.getExistingDirectory(self, disc)
        log.debug("Open directory: %s" % dir)
        if dir == "":
            return
        line_edit.setText(dir)

    def apply_configs(self):
        self.configs["direc_file"] = unicode(self.direc_file_le.text())
        self.configs["veloc_file"] = unicode(self.veloc_file_le.text())
        self.configs["diffu_file"] = unicode(self.diffu_file_le.text())
        self.configs["uh_slope"] = unicode(self.uh_slope_data_le.text())
        self.configs["station_name"] = unicode(self.stn_name_le.text())
        self.configs["station_row"] = unicode(self.stn_x_le.text())
        self.configs["station_col"] = unicode(self.stn_y_le.text())
        self.configs["out_rout_data"] = unicode(self.out_rout_data_le.text())
        self.configs["vic_out_file"] = unicode(self.vic_out_file_le.text())
        self.configs["domain_file"] = unicode(self.domain_file_le.text())
        self.configs["rout_data_file"] = unicode(self.rout_data_file_le.text())
        self.configs["rout_output_dir"] = unicode(self.rout_out_dir_le.text())

        self.configs["start_date"] = list(self.start_date_de.date().getDate())
        self.configs["end_date"] = list(self.end_date_de.date().getDate())

        self.parent.proj.proj_params["routing_config"] = self.configs
        self.parent.dirty = True
        log.info("Configs has been applied.")

    def load_configs(self):
        if self.parent.proj.proj_params.get("routing_config") is None:
            self.configs = OrderedDict()
            self.configs["direc_file"] = "None"
            self.configs["veloc_file"] = "1.5"
            self.configs["diffu_file"] = "800"
            self.configs["uh_slope"] = "from_template"
            self.configs["station_name"] = "NONE"
            self.configs["station_row"] = 0
            self.configs["station_col"] = 0
            self.configs["out_rout_data"] = "None"

            self.configs["vic_out_file"] = "None"
            self.configs["domain_file"] = "None"
            self.configs["rout_data_file"] = "None"
            self.configs["rout_output_dir"] = "None"
            self.configs["start_date"] = [1960, 1, 1]
            self.configs["end_date"] = [1970, 12, 31]

        else:
            self.configs = self.parent.proj.proj_params["routing_config"]

        self.direc_file_le.setText(self.configs["direc_file"])
        self.veloc_file_le.setText(self.configs["veloc_file"])
        self.diffu_file_le.setText(self.configs["diffu_file"])
        self.uh_slope_data_le.setText(self.configs["uh_slope"])
        self.stn_name_le.setText(self.configs["station_name"])
        self.stn_x_le.setText(unicode(self.configs["station_row"]))
        self.stn_y_le.setText(unicode(self.configs["station_col"]))
        self.out_rout_data_le.setText(self.configs["out_rout_data"])

        self.vic_out_file_le.setText(self.configs["vic_out_file"])
        self.domain_file_le.setText(self.configs["domain_file"])
        self.rout_data_file_le.setText(self.configs["rout_data_file"])
        self.rout_out_dir_le.setText(self.configs["rout_output_dir"])
        sdt = self.configs["start_date"]
        self.start_date_de.setDateTime(dt(sdt[0], sdt[1], sdt[2]))
        edt = self.configs["end_date"]
        self.end_date_de.setDateTime(dt(edt[0], edt[1], edt[2]))

    def create_rout_data(self):
        rout_info = {
            "arc_dir_code": True,
            "direc": unicode(self.direc_file_le.text()),
            "veloc": unicode(self.veloc_file_le.text()),
            "diffu": unicode(self.diffu_file_le.text()),
            "station": {
                "name": unicode(self.stn_name_le.text()),
                "x": int(self.stn_x_le.text()) - 1,
                "y": int(self.stn_y_le.text()) - 1
            },
            "uh_slope": unicode(self.uh_slope_data_le.text())
        }

        try:
            rout_info["veloc"] = float(rout_info["veloc"])
        except ValueError:
            pass
        try:
            rout_info["diffu"] = float(rout_info["diffu"])
        except ValueError:
            pass

        rout_data = create_rout(rout_info)
        write_rout_data(rout_data, unicode(self.out_rout_data_le.text()))

    def routing(self):
        log.info("Read rout data file.")
        rout_data = load_rout_data(unicode(self.rout_data_file_le.text()))
        log.info("Routing start...")
        runoffs = confluence(unicode(self.vic_out_file_le.text()), rout_data, unicode(self.domain_file_le.text()),
                   self.start_date_de.dateTime().toPyDateTime(), self.end_date_de.dateTime().toPyDateTime())
        log.info("Routing completed.")
        runoffs_m = gather_to_month(runoffs)

        out_dir = unicode(self.rout_out_dir_le.text())
        if out_dir[-1] != "/":
            out_dir += "/"
        write_runoff_data(runoffs, unicode(self.rout_out_dir_le.text()) +
                          unicode(self.stn_name_le.text()) + "_daily.txt")
        write_runoff_data(runoffs_m, unicode(self.rout_out_dir_le.text()) +
                          unicode(self.stn_name_le.text()) + "_monthly.txt")


########################################################################################################################
#
# The forth panel of main interface of VIC Hime.
# Mainly for auto calibrate of VIC.
#
########################################################################################################################
class Calibrater(QWidget):
    def __init__(self, parent=None):
        super(Calibrater, self).__init__(parent)
        self.parent = parent

        self.param_file_le = QLineEdit()
        self.param_file_btn = QPushButton("...")
        self.param_file_btn.setFixedWidth(36)
        self.obs_runoff_file_le = QLineEdit()
        self.obs_runoff_file_btn = QPushButton("...")
        self.obs_runoff_file_btn.setFixedWidth(36)

        self.obs_start_date_de = QDateTimeEdit()
        self.obs_start_date_de.setDisplayFormat("yyyy-MM-dd")
        self.time_scale_le = QLineEdit()

        self.calib_range_cb = QCheckBox("Use other calibrate range (default basin)")
        self.calib_range_le = QLineEdit()
        self.calib_range_btn = QPushButton("...")
        self.calib_range_btn.setFixedWidth(36)
        self.bpc_le = QLineEdit()
        self.bpc_le.setFixedWidth(56)
        self.only_bias_cb = QCheckBox("Objective function set only BIAS")

        self.turns_le = QLineEdit()
        self.turns_le.setFixedWidth(56)
        self.max_iterate_le = QLineEdit()
        self.max_iterate_le.setFixedWidth(56)
        self.toler_threshold_le = QLineEdit()
        self.toler_threshold_le.setFixedWidth(56)

        self.start_date_de = QDateTimeEdit()
        self.start_date_de.setDisplayFormat("yyyy-MM-dd")
        self.calib_start_date_de = QDateTimeEdit()
        self.calib_start_date_de.setDisplayFormat("yyyy-MM-dd")
        self.end_date_de = QDateTimeEdit()
        self.end_date_de.setDisplayFormat("yyyy-MM-dd")

        self.calib_params_table = QTableWidget()
        self.calib_result_table = QTableWidget()

        self.calib_params_table.setRowCount(6)
        self.calib_params_table.setColumnCount(3)
        self.calib_params_table.setHorizontalHeaderLabels(
            ["x1", "x2", "x3"])
        self.calib_params_table.setVerticalHeaderLabels(
            ["Infilt", "Ds", "Dsm", "Ws", "d2", "d3"])
        header = self.calib_params_table.horizontalHeader()
        for i in range(3):
            header.setResizeMode(i, QHeaderView.Stretch)

        self.calib_result_table.setColumnCount(1)
        self.calib_result_table.setRowCount(6)
        self.calib_result_table.setVerticalHeaderLabels(
            ["Infilt", "Ds", "Dsm", "Ws", "d2", "d3"])
        self.calib_result_table.setHorizontalHeaderLabels(["Value"])
        header = self.calib_result_table.horizontalHeader()
        header.setResizeMode(0, QHeaderView.Stretch)

        self.start_btn = QPushButton("&Calibrate start")
        self.apply_configs_btn = QPushButton("&Apply configs")

        self.run_console = QTextBrowser()

        setting_group = QGroupBox()
        setting_group.setStyleSheet(group_ss)
        setting_group.setTitle("Calibrate configs")
        setting_layout = QGridLayout()
        setting_group.setLayout(setting_layout)
        setting_layout.addWidget(QLabel("Parameters file:"), 0, 0, 1, 2)
        setting_layout.addWidget(self.param_file_le, 0, 2, 1, 6)
        setting_layout.addWidget(self.param_file_btn, 0, 8, 1, 1)

        setting_layout.addWidget(QLabel("Observation runoff file:"), 1, 0, 1, 2)
        setting_layout.addWidget(self.obs_runoff_file_le, 1, 2, 1, 6)
        setting_layout.addWidget(self.obs_runoff_file_btn, 1, 8, 1, 1)

        setting_layout.addWidget(QLabel("Obs runoff start time"), 2, 0, 1, 2)
        setting_layout.addWidget(self.obs_start_date_de, 2, 2, 1, 2)
        setting_layout.addWidget(QLabel("Time scale (M ro D):"), 2, 5, 1, 2)
        setting_layout.addWidget(self.time_scale_le, 2, 7, 1, 1)

        setting_layout.addWidget(QLabel("VIC start time:"), 3, 0, 1, 1)
        setting_layout.addWidget(self.start_date_de, 3, 1, 1, 1)
        setting_layout.addWidget(QLabel("Calibrate start time:"), 3, 2, 1, 2)
        setting_layout.addWidget(self.calib_start_date_de, 3, 4, 1, 1)
        setting_layout.addWidget(QLabel("Calibrate end time:"), 3, 5, 1, 2)
        setting_layout.addWidget(self.end_date_de, 3, 7, 1, 2)

        setting_layout.addWidget(self.calib_range_cb, 4, 0, 1, 5)
        setting_layout.addWidget(QLabel("Calibrate range:"), 5, 0, 1, 1)
        setting_layout.addWidget(self.calib_range_le, 5, 1, 1, 6)
        setting_layout.addWidget(self.calib_range_btn, 5, 7, 1, 1)
        setting_layout.addWidget(QLabel("Bias Propotion Coefficient:"), 6, 0, 1, 2)
        setting_layout.addWidget(self.bpc_le, 6, 2, 1, 1)
        setting_layout.addWidget(self.only_bias_cb, 6, 4, 1, 3)
        setting_layout.addWidget(QLabel("Turns:"), 7, 0, 1, 1)
        setting_layout.addWidget(self.turns_le, 7, 1, 1, 1)
        setting_layout.addWidget(QLabel("Max iterations:"), 7, 2, 1, 2)
        setting_layout.addWidget(self.max_iterate_le, 7, 4, 1, 1)
        setting_layout.addWidget(QLabel("Toler threshold:"), 7, 5, 1, 2)
        setting_layout.addWidget(self.toler_threshold_le, 7, 7, 1, 1)

        setting_layout.addWidget(self.apply_configs_btn, 8, 2, 1, 2)
        setting_layout.addWidget(self.start_btn, 8, 6, 1, 3)

        calib_params_group = QGroupBox()
        calib_params_group.setStyleSheet(group_ss)
        calib_params_group.setTitle("Calibrate parameters")
        calib_params_layout = QVBoxLayout()
        calib_params_group.setLayout(calib_params_layout)
        calib_params_layout.addWidget(QLabel("Initiate parameters:"))
        calib_params_layout.addWidget(self.calib_params_table)
        calib_params_layout.addStretch(1)
        calib_params_layout.addWidget(QLabel("Calibrate results:"))
        calib_params_layout.addWidget(self.calib_result_table)

        up_layout = QHBoxLayout()
        up_layout.addWidget(setting_group)
        up_layout.addWidget(calib_params_group)

        main_layout = QVBoxLayout()
        main_layout.addLayout(up_layout)
        main_layout.addWidget(self.run_console)
        self.setLayout(main_layout)

        #######################################################################
        # Connections.
        #######################################################################
        self.connect(self.param_file_btn, SIGNAL("clicked()"),
                     lambda: self.set_file_by_dialog(line_edit=self.param_file_le, disc="Set parameters file."))
        self.connect(self.calib_range_btn, SIGNAL("clicked()"),
                     lambda: self.set_file_by_dialog(line_edit=self.calib_range_le, disc="Set calibrate range file."))
        self.connect(self.obs_runoff_file_btn, SIGNAL("clicked()"),
                     lambda: self.set_file_by_dialog(line_edit=self.obs_runoff_file_le, disc="Set observation runoff file."))

        self.connect(self.apply_configs_btn, SIGNAL("clicked()"), self.apply_configs)
        self.connect(self.start_btn, SIGNAL("clicked()"), self.calibrate_start)

        self.calibrate_thread = CalibrateThread(self)

    def set_file_by_dialog(self, line_edit, disc):
        file = QFileDialog.getOpenFileName(self, disc)
        log.debug("Open file: %s" % file)
        if file == "":
            return
        line_edit.setText(file)

    def set_dir_by_dialog(self, line_edit, disc):
        dir = QFileDialog.getExistingDirectory(self, disc)
        log.debug("Open directory: %s" % dir)
        if dir == "":
            return
        line_edit.setText(dir)

    def apply_configs(self):
        self.configs["params_file"] = unicode(self.param_file_le.text())
        self.configs["runoff_obs"] = unicode(self.obs_runoff_file_le.text())
        self.configs["calib_range"] = unicode(self.calib_range_le.text())

        self.configs["time_scale"] = unicode(self.time_scale_le.text())

        self.configs["BPC"] = float(self.bpc_le.text())
        self.configs["turns"] = int(self.turns_le.text())
        self.configs["max_iterate"] = int(self.max_iterate_le.text())
        self.configs["toler_threshold"] = float(self.toler_threshold_le.text())

        self.configs["obs_start_date"] = list(self.obs_start_date_de.date().getDate())
        self.configs["start_date"] = list(self.start_date_de.date().getDate())
        self.configs["calib_start_date"] = list(self.calib_start_date_de.date().getDate())
        self.configs["end_date"] = list(self.end_date_de.date().getDate())

        self.configs["use_range"] = True if self.calib_range_cb.isChecked() else False
        self.configs["only_bias"] = True if self.only_bias_cb.isChecked() else False

        params = []
        for i in range(6):
            iparam = []
            for j in range(3):
                iparam.append(float(self.calib_params_table.item(i, j).text()))
            params.append(iparam)
        self.configs["init_params"] = params

        try:
            result_params = []
            for i in range(6):
                result_params. append(float(self.calib_result_table.item(i, 0)))
            self.configs["result_params"] = result_params
        except Exception:
            pass

        self.parent.proj.proj_params["calibrate_configs"] = self.configs
        self.parent.dirty = True
        log.info("Configs has been applied.")

    def load_configs(self):
        if self.parent.proj.proj_params.get("calibrate_configs") is None:

            proj_path = self.parent.proj.proj_params["proj_path"]
            if proj_path[-1] != "/":
                proj_path += "/"

            self.configs = OrderedDict()
            self.configs["params_file"] = proj_path + "params.nc"
            self.configs["runoff_obs"] = proj_path + "runoff_obs.txt"
            self.configs["time_scale"] = "M"
            self.configs["use_range"] = False
            self.configs["calib_range"] = "None"

            self.configs["BPC"] = 0.5
            self.configs["turns"] = 2
            self.configs["max_iterate"] = 20
            self.configs["toler_threshold"] = 0.005
            self.configs["only_bias"] = False

            self.configs["obs_start_date"] = [1961, 1, 1]
            self.configs["start_date"] = [1960, 1, 1]
            self.configs["calib_start_date"] = [1961, 1, 1]
            self.configs["end_date"] = [1970, 12, 31]

            self.configs["init_params"] = [[0.1, 0.25, 0.5],
                                           [0.05, 0.2, 0.35],
                                           [10, 30, 50],
                                           [0.75, 0.8, 0.85],
                                           [0.1, 0.3, 0.6],
                                           [0.1, 0.3, 0.6]]
        else:
            self.configs = self.parent.proj.proj_params["calibrate_configs"]

        self.param_file_le.setText(self.configs["params_file"])
        self.obs_runoff_file_le.setText(self.configs["runoff_obs"])
        self.calib_range_le.setText(self.configs["calib_range"])

        self.time_scale_le.setText(self.configs["time_scale"])

        self.bpc_le.setText(unicode(self.configs["BPC"]))
        self.turns_le.setText(unicode(self.configs["turns"]))
        self.max_iterate_le.setText(unicode(self.configs["max_iterate"]))
        self.toler_threshold_le.setText(unicode(self.configs["toler_threshold"]))

        if self.configs["use_range"]:
            self.calib_range_cb.setCheckState(Qt.Checked)
        else:
            self.calib_range_cb.setCheckState(Qt.Unchecked)

        if self.configs["only_bias"]:
            self.only_bias_cb.setCheckState(Qt.Checked)
        else:
            self.only_bias_cb.setCheckState(Qt.Unchecked)

        osdt = self.configs["obs_start_date"]
        self.obs_start_date_de.setDateTime(dt(osdt[0], osdt[1], osdt[2]))
        sdt = self.configs["start_date"]
        self.start_date_de.setDateTime(dt(sdt[0], sdt[1], sdt[2]))
        csdt = self.configs["calib_start_date"]
        self.calib_start_date_de.setDateTime(dt(csdt[0], csdt[1], csdt[2]))
        edt = self.configs["end_date"]
        self.end_date_de.setDateTime(dt(edt[0], edt[1], edt[2]))

        for i in range(6):
            for j in range(3):
                self.calib_params_table.setItem(i, j, QTableWidgetItem(unicode(self.configs["init_params"][i][j])))

        if self.configs.get("result_params") is not None:
            for i in range(6):
                self.calib_result_table.setItem(i, 0, QTableWidgetItem(unicode(self.configs["result_params"][i])))

    def create_calib_params(self):
        vic_run_configs = self.parent.proj.proj_params["vic_run_config"]
        routing_configs = self.parent.proj.proj_params["routing_config"]
        proj_path = self.parent.proj.proj_params["proj_path"]
        if proj_path[-1] != "/":
            proj_path += "/"

        calib_params = OrderedDict()
        calib_params["driver_path"] = vic_run_configs["vic_driver_path"]
        calib_params["global_file"] = proj_path + "global_calibrate.txt"
        calib_params["params_file"] = unicode(self.param_file_le.text())
        calib_params["mpi"] = vic_run_configs["with_mpi"]
        calib_params["ncores"] = vic_run_configs["n_cores"]

        calib_params["start_date"] = list(self.start_date_de.date().getDate())
        calib_params["end_date"] = list(self.end_date_de.date().getDate())
        calib_params["calib_start_date"] = list(self.start_date_de.date().getDate())

        calib_params["rout_data_file"] = routing_configs["rout_data_file"]
        calib_params["domain_file"] = routing_configs["domain_file"]
        calib_params["vic_out_file"] = ""
        calib_params["time_scale"] = unicode(self.time_scale_le.text())
        calib_params["obs_data_file"] = unicode(self.obs_runoff_file_le.text())
        calib_params["obs_start_date"] = list(self.start_date_de.date().getDate())

        if self.calib_range_cb.isChecked():
            calib_params["calib_range"] = unicode(self.calib_range_le.text())
        else:
            calib_params["calib_range"] = None

        calib_params["BPC"] = float(self.bpc_le.text())
        calib_params["only_bias"] = True if self.only_bias_cb.isChecked() else False
        calib_params["turns"] = int(self.turns_le.text())
        calib_params["max_itr"] = int(self.max_iterate_le.text())
        calib_params["toler"] = float(self.toler_threshold_le.text())

        p_init = []
        for i in range(6):
            iparam = []
            for j in range(3):
                iparam.append(float(self.calib_params_table.item(i, j).text()))
            p_init.append(iparam)
        calib_params["p_init"] = p_init

        return calib_params

    def run_calibrate(self):
        rc = self.parent.proj.proj_params.get("routing_config")
        vc = self.parent.proj.proj_params.get("vic_run_config")
        if rc is None or vc is None:
            log.error("VIC run or Routing not set.")
            return
        calib_params = self.create_calib_params()
        results = calibrate(self.parent.proj, calib_params)
        for i in range(6):
                self.calib_result_table.setItem(i, 0, QTableWidgetItem(unicode(results[i])))

    def calibrate_start(self):
        self.calibrate_thread.start()


class CalibrateThread(QThread):
    def __init__(self, parent=None):
        super(CalibrateThread, self).__init__(parent)
        self.parent = parent

    def run(self):
        self.parent.run_calibrate()


########################################################################################################################
#
# The fifth panel of main interface of VIC Hime.
# Mainly to create forcing files.
#
########################################################################################################################
class ForcingCreater(QWidget):
    def __init__(self, parent=None):
        super(ForcingCreater, self).__init__(parent)
        self.parent = parent

        #######################################################################
        # Forcing file create group
        #######################################################################
        self.forcing_var_table = QTableWidget()
        self.add_item_btn = QPushButton("Add item")
        self.remove_item_btn = QPushButton("Remove item")

        self.forc_prefix_le = QLineEdit()
        self.forc_out_path_le = QLineEdit()
        self.forc_out_path_btn = QPushButton("...")
        self.forc_out_path_btn.setFixedWidth(36)
        self.domain_file_le = QLineEdit()
        self.domain_file_btn = QPushButton("...")
        self.domain_file_btn.setFixedWidth(36)
        self.start_time_de = QDateTimeEdit()
        self.start_time_de.setDisplayFormat("yyyy-MM-dd")
        self.end_time_de = QDateTimeEdit()
        self.end_time_de.setDisplayFormat("yyyy-MM-dd")

        self.use_sh_cb = QCheckBox("Use sunshine hours data")
        self.sh_coords_le = QLineEdit()
        self.sh_coords_btn = QPushButton("...")
        self.sh_coords_btn.setFixedWidth(36)
        self.sh_data_le = QLineEdit()
        self.sh_data_btn = QPushButton("...")
        self.sh_data_btn.setFixedWidth(36)

        self.temp_data_le = QLineEdit()
        self.temp_data_btn = QPushButton("...")
        self.temp_data_btn.setFixedWidth(36)
        self.vp_data_le = QLineEdit()
        self.vp_data_btn = QPushButton("...")
        self.vp_data_btn.setFixedWidth(36)

        self.swdown_le = QLineEdit()
        self.swdown_le.setFixedWidth(72)
        self.lwdown_le = QLineEdit()
        self.lwdown_le.setFixedWidth(72)

        self.itp_p1_le = QLineEdit()
        self.itp_p1_le.setFixedWidth(48)
        self.itp_p2_le = QLineEdit()
        self.itp_p2_le.setFixedWidth(48)
        self.itp_p3_le = QLineEdit()
        self.itp_p3_le.setFixedWidth(48)

        self.forcing_start_btn = QPushButton("Start creating")
        self.apply_configs_btn = QPushButton("&Apply configs")

        self.forcing_var_table.setColumnCount(7)
        self.forcing_var_table.setMinimumHeight(96)
        self.forcing_var_table.setHorizontalHeaderLabels([
            "Data path", "Coordinates path", "Variable name", "Type", "ITP p1", "ITP p2", "ITP p3"])
        forcing_header = self.forcing_var_table.horizontalHeader()
        [forcing_header.setResizeMode(i, QHeaderView.ResizeToContents) for i in range(7)]
        [forcing_header.setResizeMode(i, QHeaderView.Stretch) for i in range(2)]

        forcing_group = QGroupBox()
        forcing_group.setStyleSheet(group_ss)
        forcing_group.setTitle("Create forcing file")
        forcing_layout = QGridLayout()
        forcing_group.setLayout(forcing_layout)

        forcing_layout.addWidget(self.forcing_var_table, 0, 0, 6, 9)
        forcing_layout.addWidget(self.add_item_btn, 6, 2, 1, 1)
        forcing_layout.addWidget(self.remove_item_btn, 6, 4, 1, 2)

        forcing_layout.addWidget(QLabel("Forcing file prefix:"), 7, 0, 1, 2)
        forcing_layout.addWidget(self.forc_prefix_le, 7, 2, 1, 1)

        forcing_layout.addWidget(QLabel("Forcing file output path:"), 8, 0, 1, 2)
        forcing_layout.addWidget(self.forc_out_path_le, 8, 2, 1, 4)
        forcing_layout.addWidget(self.forc_out_path_btn, 8, 6, 1, 1)

        forcing_layout.addWidget(QLabel("Domain file path:"), 9, 0, 1, 2)
        forcing_layout.addWidget(self.domain_file_le, 9, 2, 1, 4)
        forcing_layout.addWidget(self.domain_file_btn, 9, 6, 1, 1)

        forcing_layout.addWidget(QLabel("Start time:"), 7, 3, 1, 1)
        forcing_layout.addWidget(self.start_time_de, 7, 4, 1, 2)
        forcing_layout.addWidget(QLabel("End time:"), 7, 6, 1, 1)
        forcing_layout.addWidget(self.end_time_de, 7, 7, 1, 2)

        forcing_layout.addWidget(self.use_sh_cb, 10, 0, 1, 4)
        forcing_layout.addWidget(QLabel("Station coordinates file:"), 11, 0, 1, 2)
        forcing_layout.addWidget(self.sh_coords_le, 11, 2, 1, 3)
        forcing_layout.addWidget(self.sh_coords_btn, 11, 5, 1, 1)
        forcing_layout.addWidget(QLabel("Sunshine hours data file:"), 12, 0, 1, 2)
        forcing_layout.addWidget(self.sh_data_le, 12, 2, 1, 3)
        forcing_layout.addWidget(self.sh_data_btn, 12, 5, 1, 1)
        forcing_layout.addWidget(QLabel("Temperature data file:"), 13, 0, 1, 2)
        forcing_layout.addWidget(self.temp_data_le, 13, 2, 1, 3)
        forcing_layout.addWidget(self.temp_data_btn, 13, 5, 1, 1)
        forcing_layout.addWidget(QLabel("VP data file:"), 14, 0, 1, 2)
        forcing_layout.addWidget(self.vp_data_le, 14, 2, 1, 3)
        forcing_layout.addWidget(self.vp_data_btn, 14, 5, 1, 1)
        forcing_layout.addWidget(QLabel("Shortwave var name:"), 11, 6, 1, 2)
        forcing_layout.addWidget(self.swdown_le, 11, 8)
        forcing_layout.addWidget(QLabel("Longwave var name:"), 12, 6, 1, 2)
        forcing_layout.addWidget(self.lwdown_le, 12, 8)
        forcing_layout.addWidget(QLabel("Interpolation params:"), 13, 6, 1, 3)
        forcing_layout.addWidget(self.itp_p1_le, 14, 6)
        forcing_layout.addWidget(self.itp_p2_le, 14, 7)
        forcing_layout.addWidget(self.itp_p3_le, 14, 8)

        forcing_layout.addWidget(self.apply_configs_btn, 15, 3, 1, 2)
        forcing_layout.addWidget(self.forcing_start_btn, 15, 6, 1, 2)

        #######################################################################
        # Interpolation settings.
        #######################################################################
        self.idw_rb = QRadioButton("Use IDW")
        self.idw_rb.setChecked(True)

        self.krige_rb = QRadioButton("Use Krige (Still unavailable...)")
        # Todo Varivy krige.

        itp_group = QGroupBox()
        itp_group.setStyleSheet(group_ss)
        itp_group.setTitle("Interpolation configs")
        itp_layout = QGridLayout()
        itp_group.setLayout(itp_layout)

        itp_layout.addWidget(self.idw_rb, 0, 0)
        itp_layout.addWidget(self.krige_rb, 2, 0)

        main_layout = QVBoxLayout()
        main_layout.addWidget(forcing_group)
        main_layout.addStretch(1)
        main_layout.addWidget(itp_group)

        self.setLayout(main_layout)

        #######################################################################
        # Connections.
        #######################################################################
        self.connect(self.forc_out_path_btn, SIGNAL("clicked()"),
                     lambda: self.set_dir_by_dialog(line_edit=self.forc_out_path_le, disc="Set forcing file output path"))
        self.connect(self.domain_file_btn, SIGNAL("clicked()"),
                     lambda: self.set_file_by_dialog(line_edit=self.domain_file_le, disc="Set domain file"))
        self.connect(self.sh_coords_btn, SIGNAL("clicked()"),
                     lambda: self.set_file_by_dialog(line_edit=self.sh_coords_le, disc="Set station coordinates file"))
        self.connect(self.sh_data_btn, SIGNAL("clicked()"),
                     lambda: self.set_file_by_dialog(line_edit=self.sh_data_le, disc="Set sunshine hours data file"))
        self.connect(self.temp_data_btn, SIGNAL("clicked()"),
                     lambda: self.set_file_by_dialog(line_edit=self.temp_data_le, disc="Set temperature file"))
        self.connect(self.vp_data_btn, SIGNAL("clicked()"),
                     lambda: self.set_file_by_dialog(line_edit=self.vp_data_le, disc="Set vapor pressure file"))

        self.connect(self.apply_configs_btn, SIGNAL("clicked()"), self.apply_configs)

        self.connect(self.add_item_btn, SIGNAL("clicked()"), lambda: self.add_item(table=self.forcing_var_table))
        self.connect(self.remove_item_btn, SIGNAL("clicked()"), lambda: self.remove_item(table=self.forcing_var_table))

        self.connect(self.forcing_start_btn, SIGNAL("clicked()"), self.start_forcing_create)


        #######################################################################
        # Business part.
        #######################################################################
        self.configs = None
        self.file_create_thread = ForcingCreateThread(self)
        self.create_forcing = True

    def set_file_by_dialog(self, line_edit, disc):
        file = QFileDialog.getOpenFileName(self, disc)
        log.debug("Get file: %s" % file)
        if file == "":
            return
        line_edit.setText(file)

    def set_dir_by_dialog(self, line_edit, disc):
        dir = QFileDialog.getExistingDirectory(self, disc)
        log.debug("Get dir: %s" % dir)
        if dir == "":
            return
        line_edit.setText(dir)

    def load_configs(self):
        if self.parent.proj.proj_params.get("file_create_configs") is None:
            self.configs = OrderedDict()
            self.configs["forc_prefix"] = "forcing."

            proj_path = self.parent.proj.proj_params["proj_path"]
            if proj_path[-1] != "/":
                proj_path += "/"
            self.configs["forc_out_path"] = proj_path + "forcing"
            self.configs["domain_file"] = proj_path + "domain.nc"
            self.configs["start_time"] = [1960, 1, 1]
            self.configs["end_time"] = [1970, 12, 31]

            self.configs["use_sh"] = False

            self.configs["sh_coords"] = proj_path + "sh_coords.txt"
            self.configs["sh_data"] = proj_path + "sh_data.txt"
            self.configs["temp_data"] = proj_path + "temp_data.txt"
            self.configs["vp_data"] = proj_path + "vp_data.txt"
            self.configs["sw_varname"] = "swdown"
            self.configs["lw_varname"] = "lwdown"
            self.configs["wave_itp_params"] = [2.0, 6.0, 6]

            self.configs["forcing_vars"] = []

            self.configs["itp_method"] = 0
        else:
            self.configs = self.parent.proj.proj_params.get("file_create_configs")

        self.forc_prefix_le.setText(self.configs["forc_prefix"])

        self.forc_out_path_le.setText(self.configs["forc_out_path"])
        self.domain_file_le.setText(self.configs["domain_file"])
        sdt = self.configs["start_time"]
        self.start_time_de.setDateTime(dt(sdt[0], sdt[1], sdt[2]))
        edt = self.configs["end_time"]
        self.end_time_de.setDateTime(dt(edt[0], edt[1], edt[2]))

        if self.configs["use_sh"]:
            self.use_sh_cb.setCheckState(Qt.Checked)
        else:
            self.use_sh_cb.setCheckState(Qt.Unchecked)

        self.sh_coords_le.setText(self.configs["sh_coords"])
        self.sh_data_le.setText(self.configs["sh_data"])
        self.temp_data_le.setText(self.configs["temp_data"])
        self.vp_data_le.setText(self.configs["vp_data"])
        self.swdown_le.setText(self.configs["sw_varname"])
        self.lwdown_le.setText(self.configs["lw_varname"])
        self.itp_p1_le.setText(unicode(self.configs["wave_itp_params"][0]))
        self.itp_p2_le.setText(unicode(self.configs["wave_itp_params"][1]))
        self.itp_p3_le.setText(unicode(self.configs["wave_itp_params"][2]))

        forcing_vars = self.configs["forcing_vars"]
        self.forcing_var_table.setRowCount(len(forcing_vars))
        for i in range(len(forcing_vars)):
            for j in range(7):
                self.forcing_var_table.setItem(i, j, QTableWidgetItem(forcing_vars[i][j]))

        if self.configs["itp_method"] == 0:
            self.idw_rb.setChecked(True)
        else:
            self.krige_rb.setChecked(True)

    def apply_configs(self):
        self.configs["forc_prefix"] = unicode(self.forc_prefix_le.text())

        self.configs["forc_out_path"] = unicode(self.forc_out_path_le.text())
        self.configs["domain_file"] = unicode(self.domain_file_le.text())
        self.configs["start_time"] = list(self.start_time_de.date().getDate())
        self.configs["end_time"] = list(self.end_time_de.date().getDate())

        self.configs["use_sh"] = True if self.use_sh_cb.isChecked() else False
        self.configs["sh_coords"] = unicode(self.sh_coords_le.text())
        self.configs["sh_data"] = unicode(self.sh_data_le.text())
        self.configs["temp_data"] = unicode(self.temp_data_le.text())
        self.configs["vp_data"] = unicode(self.vp_data_le.text())

        self.configs["sw_varname"] = unicode(self.swdown_le.text())
        self.configs["lw_varname"] = unicode(self.lwdown_le.text())

        self.configs["wave_itp_params"] = [float(self.itp_p1_le.text()),
                                           float(self.itp_p2_le.text()),
                                           float(self.itp_p3_le.text()),]

        vars = []
        for i in range(self.forcing_var_table.rowCount()):
            var = []
            for j in range(7):
                var.append(unicode(self.forcing_var_table.item(i, j).text()))
            vars.append(var)
        self.configs["forcing_vars"] = vars

        if self.idw_rb.isChecked():
            self.configs["itp_method"] = 0
        else:
            self.configs["itp_method"] = 1

        self.parent.proj.proj_params["file_create_configs"] = self.configs
        self.parent.dirty = True
        log.info("Configs has been applied.")

    def add_item(self, table):
        nrow_o = table.rowCount()
        table.setRowCount(nrow_o + 1)
        if nrow_o < 1:
            table.setItem(nrow_o, 4, QTableWidgetItem(QString("2.0")))
            table.setItem(nrow_o, 5, QTableWidgetItem(QString("6.0")))
            table.setItem(nrow_o, 6, QTableWidgetItem(QString("6.0")))
        else:
            for i in range(table.columnCount()):
                table.setItem(nrow_o, i, QTableWidgetItem(table.item(nrow_o-1, i)))

    def remove_item(self, table):
        rs = [ind.row() for ind in table.selectedIndexes()]
        rs = list(set(rs))
        rs.sort(reverse=True)
        [table.removeRow(r) for r in rs]
        log.debug("Remove row %s" % rs)

    def create_forcing_params(self):
        forcing_params = OrderedDict()
        variables = []
        nvar = self.forcing_var_table.rowCount()
        for r in range(nvar):
            var = {
                "data_path": unicode(self.forcing_var_table.item(r, 0).text()),
                "coords_path": unicode(self.forcing_var_table.item(r, 1).text()),
                "var_name": unicode(self.forcing_var_table.item(r, 2).text()),
                "type": unicode(self.forcing_var_table.item(r, 3).text()),
                "itp_params": [float(unicode(self.forcing_var_table.item(r, 4).text())),
                               float(unicode(self.forcing_var_table.item(r, 5).text())),
                               float(unicode(self.forcing_var_table.item(r, 6).text()))]
            }
            variables.append(var)
        forcing_params["variables"] = variables

        forcing_params["start_time"] = list(self.start_time_de.date().getDate())
        forcing_params["end_time"] = list(self.end_time_de.date().getDate())
        forcing_params["freq"] = "D"

        if self.use_sh_cb.isChecked():
            forcing_params["use_sh"] = [unicode(self.sh_coords_le.text()),
                                        unicode(self.sh_data_le.text()),
                                        unicode(self.temp_data_le.text()),
                                        unicode(self.vp_data_le.text()),
                                        unicode(self.swdown_le.text()),
                                        unicode(self.lwdown_le.text()),
                                        float(self.itp_p1_le.text()),
                                        float(self.itp_p2_le.text()),
                                        float(self.itp_p3_le.text()),]
        else:
            forcing_params["use_sh"] = None

        return forcing_params

    def create_create_params(self):
        create_params = OrderedDict()
        forc_path = unicode(self.forc_out_path_le.text())
        if forc_path[-1] != "/":
            forc_path += "/"
        forc_path += unicode(self.forc_prefix_le.text())
        create_params["forcing_path"] = forc_path
        create_params["domain_file"] = unicode(self.domain_file_le.text())

        create_params["idw_params"] = [2, 6, 6]
        create_params["krige_params"] = ["exp"]

        return create_params

    def create_forcing_file(self):
        try:
            os.makedirs(unicode(self.forc_out_path_le.text()))
        except Exception:
            log.warn(unicode(self.forc_out_path_le.text()) + " exist.")
        forcing_params = self.create_forcing_params()
        forcing_data = read_stn_data(forcing_params)

        create_params = self.create_create_params()
        create_forcing(forcing_data, create_params)

    def start_forcing_create(self):
        self.create_forcing = True
        self.file_create_thread.start()


class ForcingCreateThread(QThread):
    def __init__(self, parent=None):
        super(ForcingCreateThread, self).__init__(parent)
        self.parent = parent

    def run(self):
        self.parent.create_forcing_file()


########################################################################################################################
#
# The sixth panel of main interface of VIC Hime.
# Mainly to create parameters file.
#
########################################################################################################################
class ParamsCreater(QWidget):
    def __init__(self, parent=None):
        super(ParamsCreater, self).__init__(parent)
        self.parent = parent

        #######################################################################
        # Parameters file create group
        #######################################################################
        self.soil_file_le = QLineEdit()
        self.soil_file_btn = QPushButton("...")
        self.soil_file_btn.setFixedWidth(36)

        self.veg_params_le = QLineEdit()
        self.veg_params_btn = QPushButton("...")
        self.veg_params_btn.setFixedWidth(36)

        self.veg_lib_le = QLineEdit()
        self.veg_lib_btn = QPushButton("...")
        self.veg_lib_btn.setFixedWidth(36)

        self.params_out_path_le = QLineEdit()
        self.params_out_path_btn = QPushButton("...")
        self.params_out_path_btn.setFixedWidth(36)

        self.fract_file_le = QLineEdit()
        self.fract_file_btn = QPushButton("...")
        self.fract_file_btn.setFixedWidth(36)

        self.snow_bands_le = QLineEdit()
        self.snow_bands_le.setFixedWidth(48)
        self.layers_le = QLineEdit()
        self.layers_le.setFixedWidth(48)
        self.rootzones_le = QLineEdit()
        self.rootzones_le.setFixedWidth(48)
        self.veg_class_le = QLineEdit()
        self.veg_class_le.setFixedWidth(48)
        self.dec_le = QLineEdit()
        self.dec_le.setFixedWidth(48)

        self.organic_cb = QCheckBox("Organic")
        self.treeline_cb = QCheckBox("Compute treeline")
        self.vegcover_cb = QCheckBox("Veg cover")

        self.apply_configs_btn = QPushButton("&Apply configs")
        self.params_create_btn = QPushButton("Create parameters file")

        params_group = QGroupBox()
        params_layout = QGridLayout()
        params_group.setLayout(params_layout)
        params_group.setStyleSheet(group_ss)
        params_group.setTitle("Create parameters file")

        params_layout.addWidget(QLabel("Soil parameters file:"), 0, 0, 1, 2)
        params_layout.addWidget(self.soil_file_le, 0, 2, 1, 4)
        params_layout.addWidget(self.soil_file_btn, 0, 6, 1, 1)

        params_layout.addWidget(QLabel("Veg parameters file:"), 1, 0, 1, 2)
        params_layout.addWidget(self.veg_params_le, 1, 2, 1, 4)
        params_layout.addWidget(self.veg_params_btn, 1, 6)

        params_layout.addWidget(QLabel("Veg lib file:"), 2, 0, 1, 2)
        params_layout.addWidget(self.veg_lib_le, 2, 2, 1, 4)
        params_layout.addWidget(self.veg_lib_btn, 2, 6, 1, 1)

        params_layout.addWidget(QLabel("Output path:"), 3, 0, 1, 2)
        params_layout.addWidget(self.params_out_path_le, 3, 2, 1, 4)
        params_layout.addWidget(self.params_out_path_btn, 3, 6)

        params_layout.addWidget(QLabel("Fraction file:"), 4, 0, 1, 2)
        params_layout.addWidget(self.fract_file_le, 4, 2, 1, 4)
        params_layout.addWidget(self.fract_file_btn, 4, 6)

        params_layout.addWidget(QLabel("Layers:"), 5, 0)
        params_layout.addWidget(self.layers_le, 5, 1)

        params_layout.addWidget(QLabel("Snow bands:"), 5, 2)
        params_layout.addWidget(self.snow_bands_le, 5, 3)

        params_layout.addWidget(QLabel("Rootzones:"), 6, 0)
        params_layout.addWidget(self.rootzones_le, 6, 1)

        params_layout.addWidget(QLabel("Veg class:"), 6, 2)
        params_layout.addWidget(self.veg_class_le, 6, 3)

        params_layout.addWidget(QLabel("Dec:"), 6, 4)
        params_layout.addWidget(self.dec_le, 6, 5)

        params_layout.addWidget(self.organic_cb, 7, 0)
        params_layout.addWidget(self.treeline_cb, 7, 1)
        params_layout.addWidget(self.vegcover_cb, 7, 2)
        params_layout.addWidget(self.apply_configs_btn, 8, 4, 1, 1)
        params_layout.addWidget(self.params_create_btn, 8, 5, 1, 2)

        main_layout = QVBoxLayout()
        main_layout.addWidget(params_group)
        main_layout.addStretch(1)

        self.setLayout(main_layout)

        self.connect(self.soil_file_btn, SIGNAL("clicked()"),
                     lambda: self.set_file_by_dialog(line_edit=self.soil_file_le, disc="Set soil file"))
        self.connect(self.veg_params_btn, SIGNAL("clicked()"),
                     lambda: self.set_file_by_dialog(line_edit=self.veg_params_le, disc="Set veg params file"))
        self.connect(self.veg_lib_btn, SIGNAL("clicked()"),
                     lambda: self.set_file_by_dialog(line_edit=self.veg_lib_le, disc="Set veg lib file"))
        self.connect(self.params_out_path_btn, SIGNAL("clicked()"),
                     lambda: self.set_dir_by_dialog(line_edit=self.params_out_path_le, disc="Set parameters files output path"))

        self.connect(self.apply_configs_btn, SIGNAL("clicked()"), self.apply_configs)
        self.connect(self.params_create_btn, SIGNAL("clicked()"), self.start_params_create)

        #######################################################################
        # Business part.
        #######################################################################
        self.create_thread = ParamsCreateThread(self)

    def set_file_by_dialog(self, line_edit, disc):
        file = QFileDialog.getOpenFileName(self, disc)
        log.debug("Get file: %s" % file)
        if file == "":
            return
        line_edit.setText(file)

    def set_dir_by_dialog(self, line_edit, disc):
        dir = QFileDialog.getExistingDirectory(self, disc)
        log.debug("Get dir: %s" % dir)
        if dir == "":
            return
        line_edit.setText(dir)

    def load_configs(self):
        if self.parent.proj.proj_params.get("params_configs") is None:
            self.configs = OrderedDict()

            proj_path = self.parent.proj.proj_params["proj_path"]
            if proj_path[-1] != "/":
                proj_path += "/"
            self.configs["soil"] = proj_path + "soil_params.txt"
            self.configs["veg"] = proj_path + "veg_params.txt"
            self.configs["veg_lib"] = proj_path + "veglib.LDAS"
            self.configs["fract"] = "None"
            self.configs["out_path"] = proj_path

            self.configs["layers"] = 3
            self.configs["snow_bands"] = 1
            self.configs["rootzones"] = 3
            self.configs["veg_class"] = 12
            self.configs["dev"] = 6

            self.configs["organic"] = False
            self.configs["treeline"] = False
            self.configs["vegcover"] = False
        else:
            self.configs = self.parent.proj.proj_params.get("params_configs")

        self.soil_file_le.setText(self.configs["soil"])
        self.veg_params_le.setText(self.configs["veg"])
        self.veg_lib_le.setText(self.configs["veg_lib"])
        self.params_out_path_le.setText(self.configs["out_path"])
        self.fract_file_le.setText(self.configs["fract"])

        self.layers_le.setText(unicode(self.configs["layers"]))
        self.snow_bands_le.setText(unicode(self.configs["snow_bands"]))
        self.rootzones_le.setText(unicode(self.configs["rootzones"]))
        self.veg_class_le.setText(unicode(self.configs["veg_class"]))
        self.dec_le.setText(unicode(self.configs["dev"]))

        if self.configs["organic"]:
            self.organic_cb.setChecked(Qt.Checked)
        else:
            self.organic_cb.setChecked(Qt.Unchecked)

        if self.configs["treeline"]:
            self.treeline_cb.setChecked(Qt.Checked)
        else:
            self.treeline_cb.setChecked(Qt.Unchecked)

        if self.configs["vegcover"]:
            self.vegcover_cb.setChecked(Qt.Checked)
        else:
            self.vegcover_cb.setChecked(Qt.Unchecked)

    def apply_configs(self):
        self.configs["soil"] = unicode(self.soil_file_le.text())
        self.configs["veg"] = unicode(self.veg_params_le.text())
        self.configs["veg_lib"] = unicode(self.veg_lib_le.text())
        self.configs["out_path"] = unicode(self.params_out_path_le.text())
        self.configs["fract"] = unicode(self.fract_file_le.text())

        self.configs["layers"] = unicode(self.layers_le.text())
        self.configs["snow_bands"] = unicode(self.snow_bands_le.text())
        self.configs["rootzones"] = unicode(self.rootzones_le.text())
        self.configs["veg_class"] = unicode(self.veg_class_le.text())
        self.configs["dev"] = unicode(self.dec_le.text())

        self.configs["organic"] = True if self.organic_cb.isChecked() else False
        self.configs["treeline"] = True if self.treeline_cb.isChecked() else False
        self.configs["vegcover"] = True if self.vegcover_cb.isChecked() else False

        self.parent.proj.proj_params["params_configs"] = self.configs
        self.parent.dirty = True
        log.info("Configs has been applied.")

    def create_parameters_file(self):
        creater_params = OrderedDict()
        creater_params["soil_file"] = unicode(self.soil_file_le.text())
        creater_params["fract_file"] = None
        creater_params["snow_band"] = int(unicode(self.snow_bands_le.text()))
        creater_params["n_layer"] = int(unicode(self.layers_le.text()))
        creater_params["organic"] = False
        creater_params["compute_treeline"] = False

        creater_params["veg_file"] = unicode(self.veg_params_le.text())
        creater_params["n_rootzones"] = int(unicode(self.rootzones_le.text()))

        creater_params["veg_lib_file"] = unicode(self.veg_lib_le.text())
        creater_params["veg_class"] = int(unicode(self.veg_class_le.text()))
        creater_params["veglib_vegcover"] = False

        creater_params["dec"] = int(unicode(self.dec_le.text()))

        out_path = unicode(self.params_out_path_le.text())
        if out_path[-1] != "/":
            out_path += "/"
        creater_params["params_file"] = out_path + "params.nc"
        creater_params["domain_file"] = out_path + "domain.nc"

        create_params_file(creater_params)

    def start_params_create(self):
        self.create_thread.start()


class ParamsCreateThread(QThread):
    def __init__(self, parent=None):
        super(ParamsCreateThread, self).__init__(parent)
        self.parent = parent

    def run(self):
        self.parent.create_parameters_file()