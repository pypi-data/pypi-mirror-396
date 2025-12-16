# -*- coding: utf-8 -*-
#
# Copyright © 2018- CELLS / ALBA Synchrotron, Bellaterra, Spain
# Copyright © 2014-2015 Colin Duquesnoy
# Copyright © 2009-2018 The Spyder Development Team
#
# Licensed under the terms of the MIT License
# (see LICENSE.txt for details)

"""
Provides QtCore classes and functions.
"""

from taurus.core.util.log import deprecation_decorator as __deprecation

from . import PYQT5, PYQT6, PYSIDE2, PYSIDE6, PythonQtError


# --------------------------------------------------------------------------
# QString, from_qvariant and to_qvariant are kept for now to
# facilitate transition of existing code but using them
# should be avoided (they only make sense with API 1, which is not supported)
@__deprecation(rel="4.0.1", alt="str")
class QString(str):
    pass


@__deprecation(rel="4.0.1", alt="python objects directly")
def from_qvariant(qobj=None, convfunc=None):
    return qobj


@__deprecation(rel="4.0.1", alt="python objects directly")
def to_qvariant(pyobj=None):
    return pyobj


# --------------------------------------------------------------------------

if PYQT5:
    from PyQt5.QtCore import *  # noqa: F403,F401
    from PyQt5.QtCore import QT_VERSION_STR as __version__  # noqa: F401

    # For issue #153 of qtpy
    from PyQt5.QtCore import QDateTime
    from PyQt5.QtCore import pyqtProperty as Property
    from PyQt5.QtCore import pyqtSignal as Signal  # noqa: F401
    from PyQt5.QtCore import pyqtSlot as Slot  # noqa: F401

    QDateTime.toPython = QDateTime.toPyDateTime

elif PYQT6:
    from PyQt6.QtCore import *  # noqa: F403,F401
    from PyQt6.QtCore import QT_VERSION_STR as __version__  # noqa: F401

    # For issue #153 of qtpy
    from PyQt6.QtCore import (
        QCoreApplication,
        QDateTime,
        QEventLoop,
        QLibraryInfo,
        QThread,
    )
    from PyQt6.QtCore import pyqtProperty as Property
    from PyQt6.QtCore import pyqtSignal as Signal  # noqa: F401
    from PyQt6.QtCore import pyqtSlot as Slot  # noqa: F401

    QDateTime.toPython = QDateTime.toPyDateTime

    # Adds older naming schema for enumerations.
    # See https://gitlab.com/taurus-org/taurus/-/issues/1299
    import PyQt6.QtCore

    from .compat_qt6 import promote_enums

    promote_enums(PyQt6.QtCore)
    QCoreApplication.exec_ = QCoreApplication.exec
    # Qt6 did not introduce deprecation for this change (path -> location)
    QLibraryInfo.location = QLibraryInfo.path
    QThread.exec_ = lambda self, *args, **kwargs: self.exec(*args, **kwargs)
    QEventLoop.exec_ = lambda self, *args, **kwargs: self.exec(*args, **kwargs)

elif PYSIDE2:
    from PySide2.QtCore import *  # noqa: F403,F401
    from PySide2.QtCore import Signal as pyqtSignal  # noqa: F401
    from PySide2.QtCore import Slot as pyqtSlot  # noqa: F401

    # ------------------------------------------------
    # Calling Property with doc="" produces segfaults in the tests.
    # As a workaround, just remove the doc kwarg. Note this is an ad-hoc
    # workaround: I could not find the API definition for
    # PySide.QtCore.Property in order to do a more complete mock
    def pyqtProperty(*args, **kwargs):
        kwargs.pop("doc", None)
        return Property(*args, **kwargs)

    # -------------------------------------------------

    try:  # may be limited to PySide-5.11a1 only
        from PySide2.QtGui import QStringListModel  # noqa: F401
    except Exception:
        pass

elif PYSIDE6:
    from PySide6.QtCore import *  # noqa: F403,F401
    from PySide6.QtCore import QLibraryInfo
    from PySide6.QtCore import Signal as pyqtSignal  # noqa: F401
    from PySide6.QtCore import Slot as pyqtSlot  # noqa: F401

    # ------------------------------------------------
    # Calling Property with doc="" produces segfaults in the tests.
    # As a workaround, just remove the doc kwarg. Note this is an ad-hoc
    # workaround: I could not find the API definition for
    # PySide.QtCore.Property in order to do a more complete mock

    # Qt6 did not introduce deprecation for this change (path -> location)
    QLibraryInfo.path = QLibraryInfo.location

    def pyqtProperty(*args, **kwargs):
        kwargs.pop("doc", None)
        return Property(*args, **kwargs)

    # -------------------------------------------------

    try:  # may be limited to PySide-5.11a1 only
        from PySide6.QtGui import QStringListModel  # noqa: F401
    except Exception:
        pass

else:
    raise PythonQtError("No Qt bindings could be found")
