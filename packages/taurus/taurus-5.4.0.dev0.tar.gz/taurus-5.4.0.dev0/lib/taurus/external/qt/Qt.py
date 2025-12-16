# -*- coding: utf-8 -*-

# ###########################################################################
#
# This file is part of Taurus
#
# http://taurus-scada.org
#
# Copyright 2025 CELLS / ALBA Synchrotron, Bellaterra, Spain
#
# Taurus is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Taurus is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with Taurus.  If not, see <http://www.gnu.org/licenses/>.
#
# ###########################################################################

"""This module exposes the Qt module"""

from taurus import Logger

from .QtCore import *  # noqa: F403,F401
from .QtGui import *  # noqa: F403,F401

# Fixes for PyQt6 for QtWidgets module needs to be loaded
# here, since enums from QtWidgets are to be propagate to Qt
# namespace.
from .QtWidgets import *  # noqa: F403,F401


class _QAppCompat(object):
    _log = Logger(__name__)
    _msg = "No Qt application instance available yet (create a QApplication first)."

    def _get(self):
        self._deprecate()
        return QApplication.instance()  # noqa: F405

    def _deprecate(self):
        self._log.deprecated(
            dep="Qt.qApp",
            alt="QtWidgets.QApplication.instance()",
            rel="5.3",
        )

    def __getattr__(self, name):
        app = self._get()
        if app is None:
            raise RuntimeError(self._msg)
        return getattr(app, name)

    def __setattr__(self, name, value):
        if name.startswith("_"):
            object.__setattr__(self, name, value)
            return
        app = self._get()
        if app is None:
            raise RuntimeError(self._msg)
        setattr(app, name, value)

    def __call__(self):
        return self._get()

    def __bool__(self):
        return self._get() is not None


qApp = _QAppCompat()
