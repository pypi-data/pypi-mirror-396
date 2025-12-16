# -*- coding: utf-8 -*-
#
# Copyright © 2018- CELLS / ALBA Synchrotron, Bellaterra, Spain
# Copyright © 2014-2015 Colin Duquesnoy
# Copyright © 2009-2018 The Spyder Development Team
#
# Licensed under the terms of the MIT License
# (see LICENSE.txt for details)

"""
Provides QtGui classes and functions.
.. warning:: Contrary to qtpy.QtGui, this module exposes the namespace
    available in ``PyQt4.QtGui``.
"""

from . import PYQT5, PYQT6, PYSIDE2, PYSIDE6, PythonQtError

if PYQT5:
    from PyQt5.QtGui import *  # noqa: F403,F401
    from PyQt5.QtGui import QFontMetrics
    from PyQt5.QtPrintSupport import *  # noqa: F403,F401

    # import * from QtWidgets and QtPrintSupport for PyQt4 style compat
    from PyQt5.QtWidgets import *  # noqa: F403,F401

    if not hasattr(QFontMetrics, "horizontalAdvance"):
        QFontMetrics.horizontalAdvance = lambda self, *args, **kwargs: self.width(
            *args,
            **kwargs,
        )

elif PYQT6:
    import PyQt6.QtGui
    from PyQt6.QtGui import *  # noqa: F403,F401
    from PyQt6.QtGui import QAction, QFontMetrics, QFontMetricsF
    from PyQt6.QtPrintSupport import *  # noqa: F403,F401
    from PyQt6.QtWidgets import *  # noqa: F403,F401

    # Adds older naming schema for enumerations.
    # See https://gitlab.com/taurus-org/taurus/-/issues/1299
    from .compat_qt6 import promote_enums

    promote_enums(PyQt6.QtGui)
    QFontMetrics.width = lambda self, *args, **kwargs: self.horizontalAdvance(
        *args,
        **kwargs,
    )
    QFontMetricsF.width = lambda self, *args, **kwargs: self.horizontalAdvance(
        *args,
        **kwargs,
    )
    if not hasattr(QAction, "parentWidget"):
        QAction.parentWidget = lambda self: self.parent()


elif PYSIDE2:
    from PySide2.QtGui import *  # noqa: F403,F401
    from PySide2.QtGui import QFontMetrics
    from PySide2.QtPrintSupport import *  # noqa: F403,F401

    # import * from QtWidgets and QtPrintSupport for PyQt4 style compat
    from PySide2.QtWidgets import *  # noqa: F403,F401

    if not hasattr(QFontMetrics, "horizontalAdvance"):
        QFontMetrics.horizontalAdvance = lambda self, *args, **kwargs: self.width(
            *args,
            **kwargs,
        )

elif PYSIDE6:
    from PySide6.QtGui import *  # noqa: F403,F401
    from PySide6.QtGui import QAction, QFontMetrics, QFontMetricsF
    from PySide6.QtPrintSupport import *  # noqa: F403,F401
    from PySide6.QtWidgets import *  # noqa: F403,F401

    QFontMetrics.width = lambda self, *args, **kwargs: self.horizontalAdvance(
        *args,
        **kwargs,
    )
    QFontMetricsF.width = lambda self, *args, **kwargs: self.horizontalAdvance(
        *args,
        **kwargs,
    )
    if not hasattr(QAction, "parentWidget"):
        QAction.parentWidget = lambda self: self.parent()


else:
    raise PythonQtError("No Qt bindings could be found")
