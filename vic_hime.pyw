#!/usr/bin/env python
#  -*- coding: utf-8 -*-


from Hime import version as __version__
from os.path import dirname, join

import platform
import os
import sys
import logging

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from interfaces import GlobalConfig, VicRun, Routing, Calibrater, ForcingCreater, ParamsCreater

from Hime import log
from Hime.vic_proj import VicProj

img_src = join(dirname(__file__), "img_src")

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        self.proj = None

        new_proj_action = self.createAction("&New project", self.create_proj,
                                            QKeySequence.New, None, "Create an new project")

        open_proj_action = self.createAction("&Open project", self.open_proj,
                                             QKeySequence.Open, None, "Open a project")

        save_proj_action = self.createAction("&Save project", self.save_proj,
                                             QKeySequence.Save, None, "Save current project")

        about_action = self.createAction("&About...", self.about)

        quit_action = self.createAction("&Quit", self.close,
                                        "Ctrl+Q", "filequit", "Close the application")

        file_menu = self.menuBar().addMenu("&File")
        self.addActions(file_menu, (new_proj_action, open_proj_action, save_proj_action, quit_action))

        help_manu = self.menuBar().addMenu("&Help")
        self.addActions(help_manu, (about_action, ))

        #######################################################################
        # Tabs.
        #######################################################################
        self.global_config_panel = GlobalConfig(self)
        self.vic_run_panel = VicRun(self)
        self.routing_panel = Routing(self)
        self.calibrate_panel = Calibrater(self)
        self.forcing_create_panel = ForcingCreater(self)
        self.params_create_panel = ParamsCreater(self)

        #######################################################################
        # Set main interface.
        #######################################################################
        tabs = QTabWidget()
        tabs.setMinimumSize(600, 680)
        tabs.setMaximumSize(1000, 720)
        tabs.addTab(self.global_config_panel, "Global setting")
        tabs.addTab(self.vic_run_panel, "Run VIC")
        tabs.addTab(self.routing_panel, "Routing")
        tabs.addTab(self.calibrate_panel, "Calibrate")
        tabs.addTab(self.forcing_create_panel, "Forcing file create")
        tabs.addTab(self.params_create_panel, "Params file create")

        self.log_console = QTextBrowser()
        self.log_console.setMinimumWidth(300)

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
        main_widget = QWidget(self)
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        settings = QSettings()
        size = settings.value("MainWindow/Size", QVariant(QSize(1080, 680))).toSize()
        self.resize(size)
        position = settings.value("MainWindow/Position", QVariant(QPoint(0, 0))).toPoint()
        self.move(position)
        self.restoreState(settings.value("MainWindow/State").toByteArray())

        self.base_window_title = "VIC Hime " + __version__
        self.setWindowTitle(self.base_window_title)
        self.show()
        #######################################################################
        # Business configs.
        #######################################################################

        self.dirty = False

        QTextCodec.setCodecForCStrings(QTextCodec.codecForName("utf-8"))

        box_log = logging.StreamHandler(StreamEmitter(text_written=self.output_writen))
        box_log.setLevel(logging.INFO)
        box_log.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s',
                                               datefmt='%Y-%m-%d %H:%M:%S'))
        log.addHandler(box_log)

        self.current_proj_path = None

        current_proj_path = unicode(settings.value("current_project").toString())
        if current_proj_path != "":
            try:
                self.load_proj(current_proj_path)
                self.current_proj_path = current_proj_path
            except Exception:
                pass

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

    def addActions(self, target, actions):
        for action in actions:
            if action is None:
                target.addSeparator()
            else:
                target.addAction(action)

    def make_tab(self, layout):
        tab = QWidget()
        tab.setLayout(layout)
        return tab

    def output_writen(self, text):
        cursor = self.log_console.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.insertText(text)
        self.log_console.setTextCursor(cursor)
        self.log_console.ensureCursorVisible()

    ####################################################################################################################
    #
    # Business functions
    #
    ####################################################################################################################
    def create_proj(self):
        dialog = CreateProjDialog(self)
        if dialog.exec_():
            proj_name = unicode(dialog.proj_name_le.text())
            proj_dir = unicode(dialog.proj_dir_le.text())
            if len(proj_name) == 0 or len(proj_dir) == 0:
                log.error("Project name or directory should not be empty.")
                return
            if proj_dir[-1] != "/":
                proj_dir += "/"
            proj_path = proj_dir + proj_name

            if not os.path.exists(proj_path) or \
                            QMessageBox.question(self, 'Directory exist', 'Directory exist, Overwrite it?',
                                                 QMessageBox.Yes | QMessageBox.No, QMessageBox.No) == QMessageBox.Yes:

                log.info("Create VIC project %s" % proj_name)
                self.proj = VicProj(proj_name, proj_path, True)
                self.current_proj_path = proj_path
                self.load_configs()

    def load_proj(self, proj_file):
        log.debug("Read proj: %s" % proj_file)
        if proj_file == "":
            return
        self.proj = VicProj()
        self.proj = self.proj.read_proj_file(proj_file)
        self.load_configs()

        self.setWindowTitle(self.base_window_title + " - " + self.proj.proj_params["proj_name"])

    def open_proj(self):
        proj_file = QFileDialog.getOpenFileName(self, "Select project file.",
                                                "VIC project files (*.vic_proj);All Files (*)")
        self.load_proj(proj_file)

    def save_proj(self):
        if self.proj is None:
            log.error("Have not open any project.")
            return

        self.proj.write_proj_file()
        self.dirty = False
        log.info("Changes have saved.")

    def load_configs(self):
        self.current_proj_path = self.proj.proj_params["proj_file"]

        self.global_config_panel.load_configs()
        self.vic_run_panel.load_configs()
        self.calibrate_panel.load_configs()
        self.routing_panel.load_configs()
        self.forcing_create_panel.load_configs()
        self.params_create_panel.load_configs()

    def ok_to_exist(self):
        if self.dirty:
            reply = QMessageBox.question(self, "VIC Hime: Unsaved Changes","Save unsaved changes?",
                            QMessageBox.Yes|QMessageBox.No|QMessageBox.Cancel)
            if reply == QMessageBox.Cancel:
                return False
            elif reply == QMessageBox.Yes:
                self.save_proj()
        return True

    def about(self):
        QMessageBox.about(self, "About VIC Hime",
                          """
                          <b>VIC Hime</b> Ver. %s
                          <p>Licence GPL3.0<p>
                          <p>By Sibada, zrd2017@163.com, SCUT hydro, Guangzhou, China<p>
                          <p>VIC project manager<p>
                          <p>Python %s - Qt %s - PyQt %s on %s
                          """ % (__version__, platform.python_version(),
                                 QT_VERSION_STR, PYQT_VERSION_STR, platform.system()))

    def closeEvent(self, QCloseEvent):
        if self.ok_to_exist():
            settings = QSettings()
            settings.setValue("MainWindow/Size", QVariant(self.size()))
            settings.setValue("MainWindow/Position", QVariant(self.pos()))
            settings.setValue("MainWindow/State", QVariant(self.saveState()))

            settings.setValue("current_project", self.current_proj_path)
        else:
            QCloseEvent.ignore()


class CreateProjDialog(QDialog):
    def __init__(self, parent=None):
        super(CreateProjDialog, self).__init__(parent)

        proj_name_lb = QLabel("&Project name:")
        self.proj_name_le = QLineEdit()
        proj_name_lb.setBuddy(self.proj_name_le)

        proj_dir_lb = QLabel("&Project path:")
        self.proj_dir_le = QLineEdit()
        proj_dir_lb.setBuddy(self.proj_dir_le)

        proj_dir_btn = QPushButton("...")
        proj_dir_btn.setFixedWidth(36)

        btn_box = QDialogButtonBox(QDialogButtonBox.Ok |
                                        QDialogButtonBox.Cancel)
        # btn_box(QDialogButtonBox.Ok).setDefault(True)

        layout = QGridLayout()
        layout.addWidget(proj_name_lb, 0, 0)
        layout.addWidget(self.proj_name_le, 0, 1)
        layout.addWidget(proj_dir_lb, 1, 0)
        layout.addWidget(self.proj_dir_le, 1, 1, 1, 3)
        layout.addWidget(proj_dir_btn, 1, 4)
        layout.addWidget(btn_box, 3, 0, 1, 3)
        self.setLayout(layout)
        self.setWindowTitle("Create new Project")

        self.connect(proj_dir_btn, SIGNAL("clicked()"), self.select_file)

        self.connect(btn_box, SIGNAL("accepted()"), self, SLOT("accept()"))
        self.connect(btn_box, SIGNAL("rejected()"), self, SLOT("reject()"))

    def select_file(self):
        self.proj_dir_le.setText(QFileDialog.getExistingDirectory(self, "Select dir"))


class StreamEmitter(QObject):
    text_written = pyqtSignal(str)
    def write(self, text):
        self.text_written.emit(str(text))

def main():
    app = QApplication(sys.argv)
    app.setOrganizationName("SCUT Hydro")
    app.setOrganizationDomain("None yet")
    app.setApplicationName("VIC Hime")
    app.setApplicationVersion(__version__)
    app.setWindowIcon(QIcon(join(img_src, "icon.png")))
    form = MainWindow()
    form.show()
    app.exec_()

if __name__ == "__main__":
    main()
