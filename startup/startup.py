# 3DE4.script.hide: 			true
# 3DE4.script.startup: 			true

import os
import sys


if __name__ == '__main__':
    sys.path.append(
        os.path.join(
            os.getenv("TANK_CURRENT_PC"),
            "install", "core", "python",
        )
    )
    import sgtk

    if not sgtk.platform.current_engine():
        from tank_vendor.shotgun_authentication import ShotgunAuthenticator
        user = ShotgunAuthenticator(sgtk.util.CoreDefaultsManager()).get_user()
        sgtk.set_authenticated_user(user)
        context = sgtk.context.deserialize(os.environ.get("TANK_CONTEXT"))
        sgtk.platform.start_engine("tk-3dequalizer", context.sgtk, context)

    toks = os.getenv("PYTHON_CUSTOM_SCRIPTS_3DE4", "").split(":")
    toks.remove(os.path.dirname(__file__))
    os.environ["PYTHON_CUSTOM_SCRIPTS_3DE4"] = ":".join(toks)
