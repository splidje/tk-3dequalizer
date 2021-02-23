"""
A 3dequalizer engine for Tank.

"""

import sys
import traceback
import re
import time
import os
import logging
import shutil
import tempfile

import tde4

import sgtk
from sgtk.platform import Engine


class TDEqualizerEngine(Engine):
    def __init__(self, *args, **kwargs):
        self._current_file = tde4.getProjectPath()
        self._custom_scripts_dir_path = None
        Engine.__init__(self, *args, **kwargs)

    def _tde_timer(self):
        from sgtk.platform.qt import QtCore, QtGui
        # Keep Qt alive
        QtCore.QCoreApplication.processEvents()
        # check for open file change
        cur_file = tde4.getProjectPath()
        if self._current_file != cur_file:
            if cur_file:
                new_context = self.sgtk.context_from_path(
                    cur_file, self.context
                )
                if new_context != self.context:
                    sgtk.platform.change_context(new_context)
            self._current_file = cur_file

    def pre_app_init(self):
        from sgtk.platform.qt import QtCore, QtGui
        if not QtCore.QCoreApplication.instance():
            # WARNING: need to keep a python reference to
            # the qt app, or python will destroy it and
            # ruin everything
            self._qt_app = QtGui.QApplication([])
            self._initialize_dark_look_and_feel()
            tde4.setTimerCallbackFunction(
                "sgtk.platform.current_engine()._tde_timer", 50
            )

    def post_app_init(self):
        self.create_shotgun_menu()

    def post_context_change(self, old_context, new_context):
        self.create_shotgun_menu()

    def destroy_engine(self):
        self.logger.debug("%s: Destroying...", self)
        if not self._custom_scripts_dir_path:
            return
        toks = os.getenv("PYTHON_CUSTOM_SCRIPTS_3DE4", "").split(":")
        toks.remove(self._custom_scripts_dir_path)
        os.environ["PYTHON_CUSTOM_SCRIPTS_3DE4"] = ":".join(toks)
        self._cleanup_custom_scripts_dir_path()

    @property
    def context_change_allowed(self):
        return True

    @property
    def host_info(self):
        host_info = dict(name="3DEqualizer", version="unknown")
        try:
            import tde4
            host_info["name"], host_info["version"] = re.match(
                r"^([^\s]+)\s+(.*)$", tde4.get3DEVersion()
            ).groups()
        except:
            # Fallback to initialized above
            pass

        return host_info

    def create_shotgun_menu(self):
        if self.has_ui:
            from sgtk.platform.qt import QtCore, QtGui

            self.logger.info("Creating Shotgun menu...")

            self._cleanup_custom_scripts_dir_path()

            # create temp dir
            self._custom_scripts_dir_path = tempfile.mkdtemp()

            for i, (name, _) in enumerate(self.commands.iteritems()):
                script_path = os.path.join(
                    self._custom_scripts_dir_path, "{:04d}.py".format(i)
                )
                f = open(script_path, "w")
                f.write("\n".join((
                    "# 3DE4.script.name: {}".format(name),
                    "# 3DE4.script.gui:	Main Window::Shotgun",
                    "if __name__ == '__main__':",
                    "   import sgtk",
                    "   sgtk.platform.current_engine().commands[{}]['callback']()".format(
                        repr(name)
                    ),
                )))
                f.close()

            toks = os.getenv("PYTHON_CUSTOM_SCRIPTS_3DE4", "").split(":")
            toks.append(self._custom_scripts_dir_path)
            os.environ["PYTHON_CUSTOM_SCRIPTS_3DE4"] = ":".join(toks)

            QtCore.QTimer.singleShot(0, tde4.rescanPythonDirs)

            self.logger.info("Shotgun menu created.")

            return True
        return False

    def _cleanup_custom_scripts_dir_path(self):
        if self._custom_scripts_dir_path and os.path.exists(self._custom_scripts_dir_path):
            shutil.rmtree(self._custom_scripts_dir_path)

    @property
    def has_ui(self):
        return True

    ##########################################################################################
    # logging

    def _emit_log_message(self, handler, record):
        if record.levelno < logging.INFO:
            formatter = logging.Formatter("Debug: Shotgun %(basename)s: %(message)s")
        else:
            formatter = logging.Formatter("Shotgun %(basename)s: %(message)s")
        msg = formatter.format(record)
        print msg

    def _create_dialog(self, title, bundle, widget, parent):
        from sgtk.platform.qt import QtCore
        dialog = super(TDEqualizerEngine, self)._create_dialog(title, bundle, widget, parent)
        dialog.raise_()
        dialog.activateWindow()
        return dialog

    #############
    # custom api
    
    @property
    def api(self):
        return self.import_module("tk_3dequalizer").api

    def iter_all_cameras(self):
        return self.api.TDECamera.iter_all()

    def iter_selected_cameras(self):
        return self.api.TDECamera.iter_selected()

    def iter_all_point_groups(self):
        return self.api.TDEPointGroup.iter_all()
