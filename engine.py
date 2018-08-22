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
        """
        Whether the engine allows a context change without the need for a restart.
        """
        return True

    @property
    def host_info(self):
        """
        :returns: A dictionary with information about the application hosting this engine.

        The returned dictionary is of the following form on success:

            {
                "name": "Maya",
                "version": "2017 Update 4",
            }

        The returned dictionary is of following form on an error preventing
        the version identification.

            {
                "name": "Maya",
                "version: "unknown"
            }
        """

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
        """
        Called when all apps have initialized
        """
        self.create_shotgun_menu()

        # Run a series of app instance commands at startup.
        #self._run_app_instance_commands()

    def post_context_change(self, old_context, new_context):
        """
        Runs after a context change. The Maya event watching will be stopped
        and new callbacks registered containing the new context information.

        :param old_context: The context being changed away from.
        :param new_context: The new context being changed to.
        """
        self.create_shotgun_menu()

    def _run_app_instance_commands(self):
        """
        Runs the series of app instance commands listed in the 'run_at_startup' setting
        of the environment configuration yaml file.
        """

        # Build a dictionary mapping app instance names to dictionaries of commands they registered with the engine.
        app_instance_commands = {}
        for (command_name, value) in self.commands.iteritems():
            app_instance = value["properties"].get("app")
            if app_instance:
                # Add entry 'command name: command function' to the command dictionary of this app instance.
                command_dict = app_instance_commands.setdefault(app_instance.instance_name, {})
                command_dict[command_name] = value["callback"]

        # Run the series of app instance commands listed in the 'run_at_startup' setting.
        for app_setting_dict in self.get_setting("run_at_startup", []):

            app_instance_name = app_setting_dict["app_instance"]
            # Menu name of the command to run or '' to run all commands of the given app instance.
            setting_command_name = app_setting_dict["name"]

            # Retrieve the command dictionary of the given app instance.
            command_dict = app_instance_commands.get(app_instance_name)

            if command_dict is None:
                self.logger.warning(
                    "%s configuration setting 'run_at_startup' requests app '%s' that is not installed.",
                    self.name, app_instance_name)
            else:
                if not setting_command_name:
                    # Run all commands of the given app instance.
                    # Run these commands once Maya will have completed its UI update and be idle
                    # in order to run them after the ones that restore the persisted Shotgun app panels.
                    for (command_name, command_function) in command_dict.iteritems():
                        self.logger.debug("%s startup running app '%s' command '%s'.",
                                       self.name, app_instance_name, command_name)
                        maya.utils.executeDeferred(command_function)
                else:
                    # Run the command whose name is listed in the 'run_at_startup' setting.
                    # Run this command once Maya will have completed its UI update and be idle
                    # in order to run it after the ones that restore the persisted Shotgun app panels.
                    command_function = command_dict.get(setting_command_name)
                    if command_function:
                        self.logger.debug("%s startup running app '%s' command '%s'.",
                                       self.name, app_instance_name, setting_command_name)
                        maya.utils.executeDeferred(command_function)
                    else:
                        known_commands = ', '.join("'%s'" % name for name in command_dict)
                        self.logger.warning(
                            "%s configuration setting 'run_at_startup' requests app '%s' unknown command '%s'. "
                            "Known commands: %s",
                            self.name, app_instance_name, setting_command_name, known_commands)


    def destroy_engine(self):
        """
        Stops watching scene events and tears down menu.
        """
        self.logger.debug("%s: Destroying...", self)

        toks = os.getenv('PYTHON_CUSTOM_SCRIPTS_3DE4', "").split(':')
        toks.remove(self.custom_scripts_dir_path)
        os.environ['PYTHON_CUSTOM_SCRIPTS_3DE4'] = ":".join(toks)

        shutil.rmtree(self.custom_scripts_dir_path)

    @property
    def has_ui(self):
        """
        Detect and return if maya is running in batch mode
        """
        return True
        #if cmds.about(batch=True):
        #    # batch mode or prompt mode
        #    return False
        #else:
        #    return True

    ##########################################################################################
    # logging

    def _emit_log_message(self, handler, record):
        """
        Called by the engine to log messages in Maya script editor.
        All log messages from the toolkit logging namespace will be passed to this method.

        :param handler: Log handler that this message was dispatched from.
                        Its default format is "[levelname basename] message".
        :type handler: :class:`~python.logging.LogHandler`
        :param record: Standard python logging record.
        :type record: :class:`~python.logging.LogRecord`
        """
        # Give a standard format to the message:
        #     Shotgun <basename>: <message>
        # where "basename" is the leaf part of the logging record name,
        # for example "tk-multi-shotgunpanel" or "qt_importer".
        if record.levelno < logging.INFO:
            formatter = logging.Formatter("Debug: Shotgun %(basename)s: %(message)s")
        else:
            formatter = logging.Formatter("Shotgun %(basename)s: %(message)s")

        msg = formatter.format(record)

        # Display the message in Maya script editor in a thread safe manner.
        print msg

    def _create_dialog(self, title, bundle, widget, parent):
        """
        Overriden from the base Engine class - create a TankQDialog with the specified widget 
        embedded.
        
        :param title: The title of the window
        :param bundle: The app, engine or framework object that is associated with this window
        :param widget: A QWidget instance to be embedded in the newly created dialog.
        :param parent: The parent QWidget for the dialog
        """
        from tank.platform.qt import QtCore
        dialog = super(TDE4Engine, self)._create_dialog(title, bundle, widget, parent)
        self._apply_external_stylesheet(self, dialog)
        dialog.setWindowFlags(dialog.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)
        dialog.raise_()
        dialog.activateWindow()
        return dialog

