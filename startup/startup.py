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

if __name__ == '__main__':
    if not tank.platform.current_engine():
        from tank_vendor.shotgun_authentication import ShotgunAuthenticator
        user = ShotgunAuthenticator(tank.util.CoreDefaultsManager()).get_user()
        tank.set_authenticated_user(user)
        context = tank.context.deserialize(os.environ.get("TANK_CONTEXT"))
        engine = tank.platform.start_engine('tk-3de4', context.tank, context)

    # Qt
    if not QtCore.QCoreApplication.instance():
        QtGui.QApplication([])
        tde4.setTimerCallbackFunction("_timer", 100)

