"""
A 3dequalizer4 engine for Tank.

"""

import tank
import sys
import traceback
import re
import time
import os
import logging
import shutil
import tempfile

from tank.platform import Engine

class TDE4Engine(Engine):
    @property
    def context_change_allowed(self):
        return True

    @property
    def host_info(self):
        host_info = {"name": "3DEqualizer4", "version": "unknown"}
        try:
            import tde4
            host_info['name'], host_info['version'] = re.match("^([^\s]+)\s+(.*)$", tde4.get3DEVersion()).groups()
        except:
            # Fallback to initialized above
            pass

        return host_info

    def create_shotgun_menu(self):
        if self.has_ui:
            self.logger.info("Creating Shotgun menu...")

            # create temp dir
            self.custom_scripts_dir_path = tempfile.mkdtemp()

            for i, (name, command) in enumerate(self.commands.iteritems()):
                script_path = os.path.join(self.custom_scripts_dir_path, "{:04d}.py".format(i))
                f = open(script_path, "w")
                f.write("\n".join((
                    "# 3DE4.script.name: {}".format(name),
                    "# 3DE4.script.gui:	Main Window::Shotgun",
                    "if __name__ == '__main__':",
                    "   import tank",
                    "   tank.platform.current_engine().commands[{}]['callback']()".format(repr(name)),
                )))
                f.close()

            toks = os.getenv('PYTHON_CUSTOM_SCRIPTS_3DE4', "").split(':')
            toks.append(self.custom_scripts_dir_path)
            os.environ['PYTHON_CUSTOM_SCRIPTS_3DE4'] = ":".join(toks)

            import tde4
            tde4.rescanPythonDirs()

            return True
        return False

    def post_app_init(self):
        self.create_shotgun_menu()

    def post_qt_init(self):
        self._initialize_dark_look_and_feel()

    def post_context_change(self, old_context, new_context):
        self.create_shotgun_menu()

    def destroy_engine(self):
        self.logger.debug("%s: Destroying...", self)

        toks = os.getenv('PYTHON_CUSTOM_SCRIPTS_3DE4', "").split(':')
        toks.remove(self.custom_scripts_dir_path)
        os.environ['PYTHON_CUSTOM_SCRIPTS_3DE4'] = ":".join(toks)

        shutil.rmtree(self.custom_scripts_dir_path)

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

        # Display the message in Maya script editor in a thread safe manner.
        print msg

    def _create_dialog(self, title, bundle, widget, parent):
        from tank.platform.qt import QtCore
        dialog = super(TDE4Engine, self)._create_dialog(title, bundle, widget, parent)
        dialog.setWindowFlags(dialog.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)
        dialog.raise_()
        dialog.activateWindow()
        return dialog

    #############
    # custom api
    
    def iter_all_cameras(self):
        return self.import_module('tk_3de4').api.TDE4Camera.iter_all()

    def iter_selected_cameras(self):
        return self.import_module('tk_3de4').api.TDE4Camera.iter_selected()

