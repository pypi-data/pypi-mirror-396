# -*- coding: utf-8 -*-

# ###########################################################################
#
# This file is part of Taurus, a Tango User Interface Library
#
# http://www.tango-controls.org/static/taurus/latest/doc/html/index.html
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


from taurus.core.tango.enums import DevState
from taurus.core.units import Quantity


def tangoFormatter(dtype=None, **kwargs):
    """
    The tango formatter callable. Returns a format string based on
    the `format` Tango Attribute configuration (Display.Format in Tango DB)

    :param dtype: type of the value object
    :type dtype: type
    :param kwargs: other keyword arguments (ignored)
    :return: the string formatting
    """
    if dtype is Quantity:
        fmt = "{:~{bc.modelObj.format_spec}}"
    elif dtype is DevState:
        fmt = "{0.name}"
    else:
        fmt = "{:{bc.modelObj.format_spec}}"
    return fmt
