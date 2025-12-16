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
QLogTable tests
"""


def test_qloggingwidget_instantiation(qtbot):
    from taurus.qt.qtgui.table.qlogtable import QLoggingWidget

    w = QLoggingWidget()
    qtbot.addWidget(w)


def test_qloggingwidget_setfiltertext(qtbot):
    from taurus.qt.qtgui.table.qlogtable import QLoggingWidget

    w = QLoggingWidget()
    qtbot.addWidget(w)
    tb = w._toolBars[0]
    tb.setFilterText("taurus")
