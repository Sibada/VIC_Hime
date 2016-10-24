#!/usr/bin/env python
#  -*- coding: utf-8 -*-


from Hime import version as __version__
from Hime import templates_path
from Hime import log
from Hime.model_execer.vic_execer import vic_exec
from Hime.routing.uh_creater import create_rout
from Hime.routing.confluence import write_rout_data, load_rout_data, confluence

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
        for i in range(4):
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
        self.domain_path_le.setText(unicode(global_params["domain_path"]))

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

        global_params["model_steps_per_day"] = unicode(self.model_steps_le.text())
        global_params["snow_steps_per_day"] = unicode(self.model_steps_le.text())
        global_params["runoff_steps_per_day"] = unicode(self.model_steps_le.text())
        global_params["nodes"] = unicode(self.model_steps_le.text())
        global_params["nlayer"] = unicode(self.model_steps_le.text())
        global_params["param_file"] = unicode(self.model_steps_le.text())
        global_params["domain_file"] = unicode(self.model_steps_le.text())

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
        self.parent.proj.write_proj_file()
        log.info("Changes have saved.")

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
        file = QFileDialog.getOpenFileName(self, "Set forcing files")
        log.debug("Get file: %s" % file)
        if file == "":
            return
        file = re.sub(r"\d\d\d\d\.nc", "", unicode(file))
        self.forcing_path_le.setText(file)

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
        input_file_layout.addWidget(self.run_btn, 5, 7, 1, 1)

        input_file_group.setLayout(input_file_layout)

        main_layout = QVBoxLayout()
        main_layout.addWidget(driver_group)
        main_layout.addWidget(input_file_group)
        # main_layout.addStretch(1)
        main_layout.addWidget(self.vic_run_console)
        self.setLayout(main_layout)

        self.connect(self.global_file_btn, SIGNAL("clicked()"),
                     lambda: self.set_file_by_dialog(line_edit=self.global_file_le, disc="Set global file path"))
        self.connect(self.vic_output_btn, SIGNAL("clicked()"),
                     lambda: self.set_file_by_dialog(line_edit=self.vic_output_le, disc="Set VIC output file path."))
        self.connect(self.rout_data_btn, SIGNAL("clicked()"),
                     lambda: self.set_file_by_dialog(line_edit=self.rout_data_le, disc="Set routing data path."))
        self.connect(self.rout_out_path_btn, SIGNAL("clicked()"),
                     lambda: self.set_dir_by_dialog(line_edit=self.rout_out_path_le, disc="Set routing output path."))

        self.connect(self.run_btn, SIGNAL("clicked()"), self.start_vic)

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

    def run_vic(self):
        if self.rout_cb.isChecked() and self.parent.proj.proj_params.get("routing_config") is None:
            log.error("Routing configs was not set. Can not run with routing.")
            return

        vic_path = unicode(self.vic_driver_le.text())
        n_cores = unicode(self.cores_le.text())
        use_mpi = True if self.mpi_cb.isChecked() else False
        status = vic_exec(vic_path, unicode(self.global_file_le.text()), mpi=use_mpi, n_cores=int(n_cores))
        if status != 0:
            log.error("Error in VIC running.")
            return

        log.info("VIC running complete.")
        if self.rout_cb.isChecked():
            pass
        log.info("Routing complete.")

    def start_vic(self):
        self.vic_run_thread.start()

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


########################################################################################################################
#
# The second panel of main interface of VIC Hime.
# Mainly to run VIC model.
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
            self.configs["start_date"] = [1970, 12, 31]

        else:
            self.configs = self.parent.proj.proj_params["routing_config"]

        self.direc_file_le.setText(self.configs["direc_file"])
        self.veloc_file_le.setText(self.configs["veloc_file"])
        self.diffu_file_le.setText(self.configs["diffu_file"])
        self.uh_slope_data_le.setText(self.configs["uh_slope"])
        self.stn_name_le.setText(self.configs["station_name"])
        self.stn_x_le.setText(self.configs["station_row"])
        self.stn_y_le.setText(self.configs["station_col"])
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
                "x": unicode(self.stn_x_le.text()),
                "y": unicode(self.stn_y_le.text())
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
        rout_data = load_rout_data(unicode(self.rout_data_file_le.text()))
        confluence(unicode(self.vic_out_file_le.text()), rout_data, unicode(self.domain_file_le.text()),
                   self.start_date_de.dateTime().toPyDateTime(), self.start_date_de.dateTime().toPyDateTime())


class VICRunThread(QThread):
    def __init__(self, parent=None):
        super(VICRunThread, self).__init__(parent)
        self.parent = parent

    def run(self):
        log.info("VIC start to run...")

        self.parent.vic_running = True
        sys.stdout = StreamEmitter(text_written=self.output_writen)
        sys.stderr = StreamEmitter(text_written=self.output_writen)

        self.parent.run_vic()

        self.parent.vic_running = False
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__

    def output_writen(self, text):
        cursor = self.parent.vic_run_console.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.insertText(text)
        self.parent.vic_run_console.setTextCursor(cursor)
        self.parent.vic_run_console.ensureCursorVisible()


class StreamEmitter(QObject):
        text_written = pyqtSignal(str)

        def write(self, text):
            self.text_written.emit(str(text))