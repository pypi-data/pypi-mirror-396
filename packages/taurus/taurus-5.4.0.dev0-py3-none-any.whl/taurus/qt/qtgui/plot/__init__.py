#!/usr/bin/env python

# ###########################################################################
#
# This file is part of Taurus
#
# http://taurus-scada.org
#
# Copyright 2011 CELLS / ALBA Synchrotron, Bellaterra, Spain
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

"""
Taurus Plot module (old)
========================

This module is now deprecated.

It tries to provide a minimal API to help with the transition from PyQwt5-based
implementations of TaurusPlot and TaurusTren to pyqtgraph-based widgets.

Prior to taurus 5, taurus.qt.qtgui.qwt5 provided a full implementation
of plot and trend widgets based on Qwt5, but this is no longer available
since the `PyQwt5 module <http://pyqwt.sourceforge.net/>`_
only works with Python2 and PyQt4 and is no longer supported,
so taurus moved to other modules for plotting (pyqtgraph, silx, ...)
"""

import taurus.core.util.log as __log

__log.deprecated(dep="taurus.qt.qtgui.plot", rel="4.5", alt="taurus_pyqtgraph")


try:
    from taurus_pyqtgraph import TaurusPlot, TaurusTrend  # noqa: F401

    __log.info(
        "plot: Using taurus_pyqtgraph to provide a minimal API "
        + "to facilitate the transition"
    )
except Exception:
    __log.info(
        "plot: Cannot import taurus_pyqtgraph to provide a "
        + "minimal API for transition"
    )
