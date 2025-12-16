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

"""Unit tests for Taurus Lcd"""

import pytest

from taurus.external.qt import PYSIDE2
from taurus.qt.qtgui.display import TaurusLCD


@pytest.mark.skipif(
    PYSIDE2,
    reason="TaurusLCD is not working in PySide2. See #1236",
)
def test_value_changed_signal(qtbot):
    """Tests if the valueChangedSignal is emitted after a new value has been
    handled by the widget/controller"""
    w = TaurusLCD()

    with qtbot.waitSignals([w.valueChangedSignal, w.modelChanged], timeout=3200):
        w.setModel("eval:Q(12, 'm')")
