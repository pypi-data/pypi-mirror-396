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

"""Unit tests for taurusbase"""

import pytest

from taurus.qt.qtgui.base.taurusbase import defaultFormatter
from taurus.qt.qtgui.container import TaurusWidget
from taurus.test.pytest import check_taurus_deprecations

try:
    # The following are Tango-centric imports.
    from taurus.core.tango.test import nodb_dev  # noqa: F401

    _TANGO_MISSING = False
except Exception:
    _TANGO_MISSING = True


@pytest.mark.skipif(_TANGO_MISSING, reason="tango-dependent test")
@pytest.mark.parametrize(
    "model, expected, formatter",
    [
        ("/boolean_scalar", "True", defaultFormatter),
        ("/short_scalar", "123 mm", defaultFormatter),
        ("/double_scalar", "1.23 mm", defaultFormatter),
        ("/state", "ON", defaultFormatter),
        ("/state", "ON", "taurus.core.tango.util.tangoFormatter"),
        ("/float_scalar#", "-----", defaultFormatter),
        ("/float_scalar#label", "float_scalar", defaultFormatter),
        ("/double_scalar#rvalue.magnitude", "1.23", defaultFormatter),
        ("eval:1+2", "3", defaultFormatter),
        ("eval:1+2#label", "1+2", defaultFormatter),
        ("eval:1+2#", "-----", defaultFormatter),
    ],
)
@pytest.mark.forked
def test_display_value(qtbot, caplog, nodb_dev, model, expected, formatter):  # noqa: F811
    """Check the getDisplayValue method"""
    with check_taurus_deprecations(caplog):
        w = TaurusWidget()
        qtbot.addWidget(w)
        w.setFormat(formatter)
        if model.startswith("/"):
            model = "{}{}".format(nodb_dev, model)
        with qtbot.waitSignal(w.modelChanged, timeout=3200):
            w.setModel(model)

        def _ok():
            """Check text"""
            assert w.getDisplayValue() == expected

        qtbot.waitUntil(_ok, timeout=3200)
