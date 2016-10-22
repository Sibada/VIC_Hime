#!/usr/bin/env python
#  -*- coding: utf-8 -*-


from Hime import version as __version__
from Hime import templates_path

import os
import sys

from PyQt4.QtCore import *
from PyQt4.QtGui import *


group_ss = "QGroupBox{border-radius: 5px; border: 2px groove lightgrey; margin-top: 1.2ex;font-family:serif}" \
           "QGroupBox::title {subcontrol-origin: margin;subcontrol-position: top left; left:15px;}"


class GlobalConfig(QWidget):
    def __init__(self, parent=None):
        super(GlobalConfig, self).__init__(parent)

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

        self.calendar_co = QComboBox()
        self.calendar_co.addItems(["standard", "gregorian", "proleptic_gregorian", 
                                   "noleap", "365_day", "360_day", "julian", "all_leap", "366_day"])

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
        self.output_table.setColumnCount(3)
        output_header = self.output_table.horizontalHeader()
        output_header.setResizeMode(0, QHeaderView.ResizeToContents)
        output_header.setResizeMode(1, QHeaderView.ResizeToContents)
        output_header.setResizeMode(2, QHeaderView.Stretch)
        self.output_table.setHorizontalHeaderLabels(["Out file", "Out variable", "Out format"])

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
        self.save_btn = QPushButton("&Save settings")
        self.create_global_btn = QPushButton("&Create global file")

        button_layout = QHBoxLayout()
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
        # Parameters
        #######################################################################
        self.proj = None






