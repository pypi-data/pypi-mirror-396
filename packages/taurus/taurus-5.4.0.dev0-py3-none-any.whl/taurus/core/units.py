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

"""
This module provides a pint unit registry instance (`UR`) to be used by all
taurus objects. It also provides the `Quantity` factory from that registry
(also aliased as `Q_`).
"""

__all__ = ["UR", "Quantity", "Q_"]

from pint import UnitRegistry, __version__
from pkg_resources import parse_version as __parse_version

# Ininitialize the unit registry for taurus
UR = UnitRegistry()
UR.default_format = "~"  # use abbreviated units
Q_ = Quantity = UR.Quantity

if __parse_version(__version__) < __parse_version("0.10"):
    UR.define("degreeC = kelvin; offset: 273.15 = °C = degC = celsius")

# define this for bck-compat because we used to define it in taurus, but
# pint (even newer version does not define it (note that °C is different
# from ºC )
UR.define("ºC = kelvin; offset: 273.15")
