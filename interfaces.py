#!/usr/bin/env python
#  -*- coding: utf-8 -*-


from Hime import version as __version__
from Hime import templates_path
from Hime import log
from Hime.model_execer.vic_execer import vic_exec

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from collections import OrderedDict
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

    def set_params(self):
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

    def get_params(self):
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
        self.get_params()
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

        self.global_path_le = QLineEdit()
        self.global_path_btn = QPushButton("...")
        self.global_path_btn.setFixedWidth(36)

        self.rout_cb = QCheckBox("With routing")
        self.rout_data_path_le = QLineEdit()
        self.rout_data_path_btn = QPushButton("...")
        self.rout_data_path_btn.setFixedWidth(36)

        self.rout_out_path_le = QLineEdit()
        self.rout_out_path_btn = QPushButton("...")
        self.rout_out_path_btn.setFixedWidth(36)

        self.vic_output_path_le = QLineEdit()
        self.vic_output_path_btn = QPushButton("...")
        self.vic_output_path_btn.setFixedWidth(36)
        self.mpi_cb = QCheckBox("Run with MPI")
        self.run_btn = QPushButton("Run VIC")

        control_layout = QGridLayout()
        control_layout.addWidget(QLabel("Global file path:"), 0, 0)
        control_layout.addWidget(self.global_path_le, 0, 1, 1, 3)
        control_layout.addWidget(self.global_path_btn, 0, 4, 1, 1)
        control_layout.addWidget(self.rout_cb)
        control_layout.addWidget(QLabel("VIC output file path:"), 2, 0)
        control_layout.addWidget(self.vic_output_path_le, 2, 1, 1, 3)
        control_layout.addWidget(self.vic_output_path_btn, 2, 4, 1, 1)
        control_layout.addWidget(QLabel("Routing data file path:"), 2, 0)
        control_layout.addWidget(self.rout_data_path_le, 3, 1, 1, 3)
        control_layout.addWidget(self.rout_data_path_btn, 3, 4, 1, 1)
        control_layout.addWidget(QLabel("Routing output file path:"), 3, 0)
        control_layout.addWidget(self.rout_out_path_le, 4, 1, 1, 3)
        control_layout.addWidget(self.rout_out_path_btn, 4, 4, 1, 1)
        control_layout.addWidget(self.mpi_cb, 5, 5, 1, 2)
        control_layout.addWidget(self.run_btn, 5, 7, 1, 1)

        main_layout = QVBoxLayout()
        main_layout.addLayout(control_layout)
        main_layout.addStretch(1)

        self.setLayout(main_layout)

        self.connect(self.global_path_btn, SIGNAL("clicked()"),
                     lambda: self.set_file_by_dialog(line_edit=self.global_path_le, disc="Set global file path"))
        self.connect(self.vic_output_path_btn, SIGNAL("clicked()"),
                     lambda: self.set_file_by_dialog(line_edit=self.vic_output_path_le, disc="Set VIC output file path."))
        self.connect(self.rout_data_path_btn, SIGNAL("clicked()"),
                     lambda: self.set_file_by_dialog(line_edit=self.rout_data_path_le, disc="Set routing data path."))
        self.connect(self.rout_out_path_btn, SIGNAL("clicked()"),
                     lambda: self.set_dir_by_dialog(line_edit=self.rout_out_path_le, disc="Set routing output path."))

        #######################################################################
        # Business part
        #######################################################################
        self.vic_running = False

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
        # TODO Add an thread to run VIC, and set the status to "RUNNING"
        pass