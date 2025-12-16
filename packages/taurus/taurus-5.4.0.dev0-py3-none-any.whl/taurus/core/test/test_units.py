#!/usr/bin/env python
# -*- coding: utf-8 -*-

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

from taurus.core.units import Q_

# from pint import UnitRegistry
# UR = UnitRegistry()
# Q_= UR.Quantity
# UR.define(u'degreeC = kelvin; offset: 273.15  = °C = ºC = degC = celsius')


def test_celsius():
    """
    Check that the definition of degreeC works
    Note: see https://github.com/hgrecco/pint/issues/546
    """
    a = Q_(3, "°C")
    b = Q_(3, "ºC")  # "°C" is not "°C"  !
    c = Q_(3, "degC")
    d = Q_(3, "celsius")
    e = Q_(276.15, "kelvin")
    assert a == b
    assert a == c
    assert a == d
    assert a == e
    assert a.to("kelvin") == e
    assert a == e.to("°C")
    assert a == e.to("ºC")
    assert a == b.to("degC")
    assert a.to("ºC") == b
    assert a == e.to("celsius")
    assert "{}".format(a) == "3 °C"
    assert "{}".format(b) == "3 ºC"  # note that "°C" is not "°C"
    assert "{}".format(c) == "3 °C"
    assert "{}".format(d) == "3 °C"

    # # I would have expected the following to be formatted as "3 celsius"...
    # a.default_format = u""
    # b.default_format = u""
    # c.default_format = u""
    # d.default_format = u""
    # assert(u"{}".format(a) == u"3 celsius")
    # assert(u"{}".format(b) == u"3 celsius")
    # assert(u"{}".format(c) == u"3 celsius")
    # assert(u"{}".format(d) == u"3 celsius")
