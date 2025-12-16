# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright © 2009- The Spyder Development Team
#
# Licensed under the terms of the MIT License
# (see LICENSE.txt for details)
# -----------------------------------------------------------------------------
"""Provides QtSvg classes and functions."""

# Local imports
from . import PYQT5, PYQT6, PYSIDE2, PYSIDE6, PythonQtError

if PYQT6:
    from PyQt6.QtSvg import *  # noqa: F403,F401
elif PYQT5:
    from PyQt5.QtSvg import *  # noqa: F403,F401
elif PYSIDE6:
    from PySide6.QtSvg import *  # noqa: F403,F401
elif PYSIDE2:
    from PySide2.QtSvg import *  # noqa: F403,F401
else:
    raise PythonQtError("No Qt bindings could be found")

del PYQT5, PYQT6, PYSIDE2, PYSIDE6
