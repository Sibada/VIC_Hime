#!/usr/bin/env python
#  -*- coding: utf-8 -*-


from Hime import version as __version__

import os
import sys

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from interfaces import GlobalConfig


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        self.proj = None

        new_proj_action = self.createAction("&New...", self.create_proj,
                                          QKeySequence.New, None, "Create an new project")
        # fileOpenAction = self.createAction("&Open...",None,
        #                                    QKeySequence.Open, "fileopen", "Open an existing image file")
        # fileSaveAction = self.createAction("&Save", None,
        #         QKeySequence.Save, "filesave", "Save the image")
        # fileSaveAsAction = self.createAction("Save &As...",
        #         None, icon="filesaveas",
        #         tip="Save the image using a new name")
        #
        # fileQuitAction = self.createAction("&Quit", None,
        #         "Ctrl+Q", "filequit", "Close the application")

        self.fileMenu = self.menuBar().addMenu("&File")
        self.fileMenuActions = (new_proj_action, )
        self.connect(self.fileMenu, SIGNAL("aboutToShow()"), self.updateFileMenu)

        self.help_manu = self.menuBar().addMenu("&Help")

        #######################################################################
        # Tabs.
        #######################################################################
        self.global_config = GlobalConfig()

        self.run_layout = QVBoxLayout()
        self.calib_layout = QVBoxLayout()
        self.rout_layout = QVBoxLayout()
        self.file_layout = QVBoxLayout()
        self.forcing_layout = QVBoxLayout()

        #######################################################################
        # Set main interface.
        #######################################################################
        tabs = QTabWidget()
        tabs.setMinimumSize(600, 640)
        tabs.addTab(self.global_config, "Global setting")
        tabs.addTab(self.make_tab(self.run_layout), "Run VIC")
        tabs.addTab(self.make_tab(self.calib_layout), "Calibrate")
        tabs.addTab(self.make_tab(self.rout_layout), "Routing")
        tabs.addTab(self.make_tab(self.file_layout), "Input file create")

        self.log_console = QTextBrowser()
        self.log_console.setMinimumWidth(256)
        log_cons_lb = QLabel("Log console")

        log_layout = QVBoxLayout()
        log_layout.addWidget(log_cons_lb)
        log_layout.addWidget(self.log_console)

        # Set main layout
        main_layout = QHBoxLayout()
        main_layout.addWidget(tabs)
        main_layout.addLayout(log_layout)

        #######################################################################
        # Main window configs
        #######################################################################
        self.resize(1000, 680)
        self.setWindowTitle("VIC Hime - VIC project manager Ver." + __version__)
        main_widget = QWidget(self)
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        self.show()

        QTextCodec.setCodecForCStrings(QTextCodec.codecForName("utf-8"))

    ####################################################################################################################
    #
    # Assistant functions
    #
    ####################################################################################################################
    def createAction(self, text, slot=None, shortcut=None, icon=None,
                     tip=None, checkable=False, signal="triggered()"):
        action = QAction(text, self)
        if icon is not None:
            action.setIcon(QIcon(":/%s.png" % icon))
        if shortcut is not None:
            action.setShortcut(shortcut)
        if tip is not None:
            action.setToolTip(tip)
            action.setStatusTip(tip)
        if slot is not None:
            self.connect(action, SIGNAL(signal), slot)
        if checkable:
            action.setCheckable(True)
        return action

    def updateFileMenu(self):
        self.fileMenu.clear()
        self.addActions(self.fileMenu, self.fileMenuActions[:-1])
        current = QString(self.filename) \
                if self.filename is not None else None
        recentFiles = []
        for fname in self.recentFiles:
            if fname != current and QFile.exists(fname):
                recentFiles.append(fname)
        if recentFiles:
            self.fileMenu.addSeparator()
            for i, fname in enumerate(recentFiles):
                action = QAction(QIcon(":/icon.png"), "&%d %s" % (
                        i + 1, QFileInfo(fname).fileName()), self)
                action.setData(QVariant(fname))
                self.connect(action, SIGNAL("triggered()"),
                             self.loadFile)
                self.fileMenu.addAction(action)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.fileMenuActions[-1])

    def make_tab(self, layout):
        tab = QWidget()
        tab.setLayout(layout)
        return tab

    ####################################################################################################################
    #
    # Service functions
    #
    ####################################################################################################################
    def create_proj(self):
        dialog = CreateProjDialog(self)
        if dialog.exec_():
            proj_name = unicode(dialog.proj_name_le.text())
            proj_dir = unicode(dialog.proj_dir_le.text())
            if proj_dir[-1] != "/":
                proj_dir += "/"
            proj_path = proj_dir + proj_name
            print proj_path
        return


class CreateProjDialog(QDialog):

    def __init__(self, parent=None):
        super(CreateProjDialog, self).__init__(parent)

        proj_name_lb = QLabel("&Project name:")
        self.proj_name_le = QLineEdit()
        proj_name_lb.setBuddy(self.proj_name_le)

        proj_dir_lb = QLabel("&Project path:")
        self.proj_dir_le = QLineEdit()
        proj_dir_lb.setBuddy(self.proj_dir_le)

        self.proj_dir_btn = QPushButton("...")
        self.proj_dir_btn.setFixedWidth(36)

        btn_box = QDialogButtonBox(QDialogButtonBox.Ok |
                                        QDialogButtonBox.Cancel)
        btn_box(QDialogButtonBox.Ok).setDefault(True)

        layout = QGridLayout()
        layout.addWidget(proj_name_lb, 0, 0)
        layout.addWidget(self.proj_name_le, 0, 1)
        layout.addWidget(proj_dir_lb, 1, 0)
        layout.addWidget(self.proj_dir_le, 1, 1, 1, 3)
        layout.addWidget(self.proj_dir_btn, 1, 4)
        layout.addWidget(btn_box, 3, 0, 1, 3)
        self.setLayout(layout)
        self.setWindowTitle("Create new Project")

        self.connect(self.proj_dir_btn, SIGNAL("clicked()"), self.select_file())

        self.connect(btn_box, SIGNAL("accepted()"), self, SLOT("accept()"))
        self.connect(btn_box, SIGNAL("rejected()"), self, SLOT("reject()"))

    def select_file(self):
        self.proj_dir_le.setText(QFileDialog.getExistingDirectory(self, "Select dir"))


def main():
    app = QApplication(sys.argv)
    app.setOrganizationName("SCUT Hydro")
    app.setOrganizationDomain("None yet")
    app.setApplicationName("VIC Hime")
    app.setApplicationVersion(__version__)
    # app.setWindowIcon(QIcon(":/icon.png"))
    form = MainWindow()
    form.show()
    app.exec_()

if __name__ == "__main__":
    main()

