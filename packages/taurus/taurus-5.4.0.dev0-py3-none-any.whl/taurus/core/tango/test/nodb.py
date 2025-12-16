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

"""Module containing base classes for database-less tango tests"""

import pytest
from tango.test_context import DeviceTestContext

from taurus.core.tango.tangovalidator import TangoDeviceNameValidator

from .res.TangoSchemeTest import TangoSchemeTest

__docformat__ = "restructuredtext"


class NamedDeviceTestContext(DeviceTestContext):
    """
    Reimplementation of :class:`tango.test_context.DeviceTestContext that
    returns the taurus full name of the Deviceinstead of a
    :class:`tango.DeviceProxy`
    """

    def __enter__(self):
        if not self.thread.is_alive():
            self.start()
        v = TangoDeviceNameValidator()
        fullname, _, _ = v.getNames(self.get_device_access())
        return fullname


@pytest.fixture(scope="module")
def nodb_dev():
    """
    A pytest fixture that launches TangoSchemeTest for the test
    It provides the device name as the fixture value.

    Usage::
        from taurus.core.tango.test import nodb_dev

        def test_foo(nodb_dev):
            import taurus
            d = taurus.Device(nodb_dev)
            assert d["string_scalar"].rvalue == "hello world"
    """
    with NamedDeviceTestContext(TangoSchemeTest, process=True, timeout=15) as full_name:
        yield full_name
