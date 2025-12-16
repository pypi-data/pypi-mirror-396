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

"""Tests for taurus.core.tango.tangofactory"""

import gc
import time

import pytest

import taurus

from .nodb import nodb_dev  # noqa


# TODO: remove xfail mark when PyTango !412 is fixed
@pytest.mark.xfail(msg="it fails with pytango 9.3.3")
def test_factory_forgets_devices(nodb_dev):  # noqa: F811
    """The tango factory should not remember unreferenced devices"""

    factory = taurus.Factory("tango")
    old = sorted(factory.tango_devs)
    assert nodb_dev not in old

    def create():
        _ = taurus.Device(nodb_dev)
        assert nodb_dev in sorted(factory.tango_devs)

    # create the taurus Device but do not maintain a reference to it
    create()
    assert sorted(factory.tango_devs) == old


# TODO: remove xfail mark when PyTango !412 is fixed
@pytest.mark.xfail(msg="it fails with pytango 9.3.3")
def test_factory_forgets_attributes(nodb_dev):  # noqa: F811
    """The tango factory should not remember unreferenced attributes"""
    factory = taurus.Factory("tango")
    attrname = nodb_dev + "/float_scalar"
    old = sorted(factory.tango_attrs)
    assert attrname not in old

    def create():
        _ = taurus.Attribute(attrname)
        assert attrname in sorted(factory.tango_attrs)

    # create the taurus Attribute but do not maintain a reference to it
    create()
    assert sorted(factory.tango_attrs) == old


# TODO: remove this test when PyTango !412 is fixed
def test_factory_forgets_devices_with_gc_workaround(nodb_dev):  # noqa: F811
    """The tango factory should not remember unreferenced devices
    But avoiding  https://gitlab.com/tango-controls/pytango/-/issues/412
    """

    factory = taurus.Factory("tango")
    old = sorted(factory.tango_devs)
    assert nodb_dev not in old

    def create():
        _ = taurus.Device(nodb_dev)
        assert nodb_dev in sorted(factory.tango_devs)

    # create the taurus Device but do not maintain a reference to it
    create()
    gc.collect()  # avoid PyTango bug 412
    assert sorted(factory.tango_devs) == old


# TODO: remove this test when PyTango !412 is fixed
def test_factory_forgets_attributes_with_gc_workaround(nodb_dev):  # noqa: F811
    """The tango factory should not remember unreferenced attributes
    But avoiding  https://gitlab.com/tango-controls/pytango/-/issues/412
    """
    factory = taurus.Factory("tango")
    attrname = nodb_dev + "/float_scalar"
    old = sorted(factory.tango_attrs)
    assert attrname not in old

    def create():
        _ = taurus.Attribute(attrname)
        assert attrname in sorted(factory.tango_attrs)

    # create the taurus Attribute but do not maintain a reference to it
    create()
    gc.collect()  # avoid PyTango bug 412
    assert sorted(factory.tango_attrs) == old


@pytest.mark.parametrize("attrname", ["/FLOAT_scalar", "/sTaTe"])
def test_cleanup_after_polling(nodb_dev, attrname):  # noqa: F811
    """
    Ensure that polling a Tango attribute does not keep device alive
    See Bug #999
    (Also check case insensitivity)
    """
    f = taurus.Factory("tango")
    old_attrs = sorted(f.tango_attrs)
    old_devs = sorted(f.tango_devs)
    assert nodb_dev + attrname not in old_attrs
    assert nodb_dev not in old_devs
    polling_period = 0.1  # seconds
    a = taurus.Attribute(nodb_dev + attrname)
    a.activatePolling(int(polling_period * 1000), force=True)
    assert nodb_dev + attrname in f.tango_attrs
    assert nodb_dev in f.tango_devs
    a = None
    # TODO: remove the gc.collect() when PyTango !412 is fixed
    gc.collect()  # avoid PyTango bug 412
    time.sleep(polling_period * 2)
    assert sorted(f.tango_attrs) == old_attrs
    assert sorted(f.tango_devs) == old_devs
