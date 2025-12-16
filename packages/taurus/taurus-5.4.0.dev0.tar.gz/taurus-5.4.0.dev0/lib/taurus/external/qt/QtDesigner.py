# -*- coding: utf-8 -*-
#
# Copyright © 2014-2015 Colin Duquesnoy
#
# Licensed under the terms of the MIT License
# (see LICENSE.txt for details)

"""
Provides QtDesigner classes and functions.
"""

from . import PYQT5, PYQT6, PYSIDE2, PYSIDE6, PythonQtError

if PYQT5:
    from PyQt5.QtDesigner import *  # noqa: F403,F401
elif PYQT6:
    from PyQt6.QtDesigner import *  # noqa: F403,F401
elif PYSIDE2:
    from PySide2.QtDesigner import *  # noqa: F403,F401
elif PYSIDE6:
    from PySide6.QtDesigner import *  # noqa: F403,F401

else:
    raise PythonQtError("No compatible Qt bindings could be found")


def get_qt_designer_binary():
    """Determines the binary path and name of the designer application

    Return:
        str path to the binary of the designer application
    """
    import os
    import subprocess
    import sys

    from taurus.external.qt import Qt

    from . import PYQT5, PYQT6, PYSIDE2, PYSIDE6

    designer_bin_dir = str(Qt.QLibraryInfo.location(Qt.QLibraryInfo.BinariesPath))

    plat = sys.platform
    # If QT_DESIGNER_PATH is set, force its use
    custom_designer_path = os.environ.get("QT_DESIGNER_PATH", None)
    if custom_designer_path is not None:
        return custom_designer_path

    if plat == "darwin":
        designer_bin = os.path.join(
            designer_bin_dir, "Designer.app", "Contents", "MacOS", "designer"
        )
    elif plat in ("win32", "nt"):
        designer_bin = os.path.join(designer_bin_dir, "designer.exe")
        if not os.path.exists(designer_bin):
            # some installations don't properly install designer
            # in QLibraryInfo.BinariesPath. We do a best effort to find it
            try:
                designer_bin_query = subprocess.check_output("where designer")
            except subprocess.CalledProcessError:
                raise FileNotFoundError("Unable to locate qt designer in system PATH.")
            # Return the first qt designer that where finds.
            designer_bin = designer_bin_query.decode().split("\r\n")[0].strip()
    else:
        designer_bin = os.path.join(designer_bin_dir, "designer")
        if not os.path.exists(designer_bin):
            if PYQT5 or PYSIDE2:
                designer_bin = os.path.join(designer_bin_dir, "designer-qt5")
            elif PYQT6:
                designer_bin = os.path.join(designer_bin_dir, "designer-qt6")
        # PySide6 implemented support for native-python widgets using
        # a new binary.
        if PYSIDE6:
            from PySide6.QtCore import QStandardPaths

            designer_bin = str(QStandardPaths.findExecutable("pyside6-designer"))
    if not os.path.exists(designer_bin):
        raise FileNotFoundError(
            f"Unable to locate qt designer in system PATH: looking for {designer_bin}"
        )
    return designer_bin


del PYQT5, PYQT6, PYSIDE2, PYSIDE6, PythonQtError
