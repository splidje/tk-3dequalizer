import os
import sys
import subprocess

import sgtk
from sgtk.platform import SoftwareLauncher, SoftwareVersion, LaunchInformation


class TDE4Launcher(SoftwareLauncher):
    """
    Handles launching 3DEqualizer4 executables. Automatically starts up
    a tk-3de4 engine with the current context in the new session
    of 3DEqualizer4.
    """

    def prepare_launch(self, exec_path, args, file_to_open=None):
        """
        Prepares an environment to launch 3DEqualizer4 in that will automatically
        load Toolkit and the tk-3de4 engine when 3DEqualizer starts.

        :param str exec_path: Path to 3DEqualizer4 executable to launch.
        :param str args: Command line arguments as strings.
        :param str file_to_open: (optional) Full path name of a file to open on launch.
        :returns: :class:`LaunchInformation` instance
        """
        required_env = {}

        # Run the engine's startup/*.py files when 3DEqualizer starts up
        # by appending it to the env PYTHON_CUSTOM_SCRIPTS_3DE4.
        startup_path = os.path.join(self.disk_location, "startup")
        #sgtk.util.append_path_to_env_var("PYTHON_CUSTOM_SCRIPTS_3DE4", startup_path)
        os.environ["PYTHON_CUSTOM_SCRIPTS_3DE4"] = startup_path
        required_env["PYTHON_CUSTOM_SCRIPTS_3DE4"] = os.environ["PYTHON_CUSTOM_SCRIPTS_3DE4"]

        # Add context information info to the env.
        required_env["TANK_CONTEXT"] = sgtk.Context.serialize(self.context)

        # open a file
        if file_to_open:
            args += " {}".format(subprocess.list2cmdline(("-open", file_to_open)))

        return LaunchInformation(exec_path, args, required_env)
