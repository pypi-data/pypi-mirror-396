# -*- coding: utf-8 -*-
#
# Copyright © 2014-2015 Colin Duquesnoy
# Copyright © 2009- The Spyder Developmet Team
#
# Licensed under the terms of the MIT License
# (see LICENSE.txt for details)

"""
Provides widget classes and functions.
.. warning:: Only PyQt4/PySide QtGui classes compatible with PyQt5.QtWidgets
    are exposed here. Therefore, you need to treat/use this package as if it
    were the ``PyQt5.QtWidgets`` module.
"""

import taurus.core.util.log as __log  # noqa: F401

from . import PYQT5, PYQT6, PYSIDE2, PYSIDE6, PythonQtError

if PYQT5:
    from PyQt5.QtWidgets import *  # noqa: F403,F401
elif PYQT6:
    # Adds older naming schema for enumerations.
    # See https://gitlab.com/taurus-org/taurus/-/issues/1299
    import PyQt6.QtWidgets
    from PyQt6.QtWidgets import *  # noqa: F403,F401

    from .compat_qt6 import promote_enums

    promote_enums(PyQt6.QtWidgets)
    PyQt6.QtWidgets.QMenu.exec_ = lambda self, *args, **kwargs: self.exec(
        *args, **kwargs
    )
    PyQt6.QtWidgets.QDialog.exec_ = lambda self, *args, **kwargs: self.exec(
        *args, **kwargs
    )
elif PYSIDE2:
    from PySide2.QtWidgets import *  # noqa: F403,F401
elif PYSIDE6:
    from PySide6.QtWidgets import *  # noqa: F403,F401
    from PySide6.QtWidgets import QApplication

    QApplication.exec_ = QApplication.exec
else:
    raise PythonQtError("No Qt bindings could be found")
