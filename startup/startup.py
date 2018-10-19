# 3DE4.script.hide: 			true
# 3DE4.script.startup: 			true

import os
import sys
import tde4
from PySide import QtGui, QtCore

sys.path.append(
    os.path.join(os.getenv('TANK_CURRENT_PC'), 'install', 'core', 'python')
)
import tank

def _timer():
    QtCore.QCoreApplication.processEvents()
    # check for open file change
    global g_current_file
    cur_file = tde4.getProjectPath()
    if g_current_file != cur_file:
        if cur_file:
            engine = tank.platform.current_engine()
            context = engine.context
            new_context = engine.tank.context_from_path(cur_file, context)
            if new_context != context:
                tank.platform.change_context(new_context)
        g_current_file = cur_file

if __name__ == '__main__':
    engine = tank.platform.current_engine()
    if not engine:
        from tank_vendor.shotgun_authentication import ShotgunAuthenticator
        user = ShotgunAuthenticator(tank.util.CoreDefaultsManager()).get_user()
        tank.set_authenticated_user(user)
        context = tank.context.deserialize(os.environ.get("TANK_CONTEXT"))
        engine = tank.platform.start_engine('tk-3dequalizer', context.tank, context)

    # Qt
    if not QtCore.QCoreApplication.instance():
        QtGui.QApplication([])
        global g_current_file
        g_current_file = tde4.getProjectPath()
        tde4.setTimerCallbackFunction("_timer", 10)
        engine.post_qt_init()

