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

            # Get temp folder path and create it if needed.
            self.custom_scripts_dir_path = os.environ['TK_3DE4_MENU_DIR']
            try:
                os.makedirs(self.custom_scripts_dir_path)
            except OSError as error:
                if error.errno != 17: # Don't error if folder already exists.
                    raise

            # Clear it.
            for item in os.listdir(self.custom_scripts_dir_path):
                os.remove(os.path.join(self.custom_scripts_dir_path, item))

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

        try:
            shutil.rmtree(self.custom_scripts_dir_path)
        except OSError as error:
            if error.errno != 2: # Don't error if folder not found.
                raise

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
        from tank.platform.qt import QtCore
        dialog = super(TDE4Engine, self)._create_dialog(title, bundle, widget, parent)
        dialog.setWindowFlags(dialog.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)
        dialog.raise_()
        dialog.activateWindow()
        return dialog
