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

"""Utility functions to convert between tango and Taurus types"""

import tango
from pint import UndefinedUnitError

from taurus.core.taurusbasetypes import (
    AttrQuality,
    DataFormat,
    DataType,
    DisplayLevel,
)
from taurus.core.units import UR, Quantity

__NO_STR_VALUE = (
    tango.constants.AlrmValueNotSpec,
    tango.constants.StatusNotSet,
)

FROM_TANGO_TO_TAURUS_DFORMAT = {
    tango.AttrDataFormat.SCALAR: DataFormat._0D,
    tango.AttrDataFormat.SPECTRUM: DataFormat._1D,
    tango.AttrDataFormat.IMAGE: DataFormat._2D,
}

FROM_TANGO_TO_TAURUS_TYPE = {
    tango.CmdArgType.DevVoid: None,
    tango.CmdArgType.DevBoolean: DataType.Boolean,
    tango.CmdArgType.DevShort: DataType.Integer,
    tango.CmdArgType.DevLong: DataType.Integer,
    tango.CmdArgType.DevFloat: DataType.Float,
    tango.CmdArgType.DevDouble: DataType.Float,
    tango.CmdArgType.DevUShort: DataType.Integer,
    tango.CmdArgType.DevULong: DataType.Integer,
    tango.CmdArgType.DevString: DataType.String,
    tango.CmdArgType.DevVarCharArray: DataType.Bytes,
    tango.CmdArgType.DevVarShortArray: DataType.Integer,
    tango.CmdArgType.DevVarLongArray: DataType.Integer,
    tango.CmdArgType.DevVarFloatArray: DataType.Float,
    tango.CmdArgType.DevVarDoubleArray: DataType.Float,
    tango.CmdArgType.DevVarUShortArray: DataType.Integer,
    tango.CmdArgType.DevVarULongArray: DataType.Integer,
    tango.CmdArgType.DevVarStringArray: DataType.String,
    tango.CmdArgType.DevVarLongStringArray: DataType.Object,
    tango.CmdArgType.DevVarDoubleStringArray: DataType.Object,
    tango.CmdArgType.DevState: DataType.DevState,
    tango.CmdArgType.ConstDevString: DataType.String,
    tango.CmdArgType.DevVarBooleanArray: DataType.Boolean,
    tango.CmdArgType.DevUChar: DataType.Bytes,
    tango.CmdArgType.DevLong64: DataType.Integer,
    tango.CmdArgType.DevULong64: DataType.Integer,
    tango.CmdArgType.DevVarLong64Array: DataType.Integer,
    tango.CmdArgType.DevVarULong64Array: DataType.Integer,
    tango.CmdArgType.DevEncoded: DataType.DevEncoded,
    tango.CmdArgType.DevEnum: DataType.DevEnum,
}
# DevInt removed in cpptango/pytango 9.5.0
try:
    FROM_TANGO_TO_TAURUS_TYPE[tango.CmdArgType.DevInt] = DataType.Integer
except AttributeError:
    pass
if hasattr(tango, "str_2_obj"):
    str_2_obj = tango.str_2_obj
else:
    # Old PyTango
    import tango.utils

    def bool_(value_str):
        return value_str.lower() == "true"

    def str_2_obj(obj_str, tg_type=None):
        f = str
        if tango.utils.is_scalar_type(tg_type):
            if tango.utils.is_numerical_type(tg_type):
                if obj_str in __NO_STR_VALUE:
                    return None

            if tango.utils.is_int_type(tg_type):
                f = int
            elif tango.utils.is_float_type(tg_type):
                f = float
            elif tango.utils.is_bool_type(tg_type):
                f = bool_
        return f(obj_str)


def get_quantity(value, units=None, fmt=None):
    if value is None:
        return None
    res = Quantity(value, units=units)
    if fmt is not None:
        res.default_format = fmt + res.default_format
    return res


def quantity_from_tango_str(
    value_str, dtype=None, units=None, fmt=None, ignore_exception=True
):
    try:
        return get_quantity(str_2_obj(value_str, dtype), units=units, fmt=fmt)
    except ValueError:
        if not ignore_exception:
            raise
        return None


def unit_from_tango(unit):
    from taurus import deprecated

    deprecated(dep="unit_from_tango", rel="4.0.4", alt="pint's parse_units")

    if unit == tango.constants.UnitNotSpec or unit == "No unit" or unit is None:
        unit = ""
    try:
        return UR.parse_units(unit)
    except (UndefinedUnitError, UnicodeDecodeError):
        # TODO: Maybe we could dynamically register the unit in the UR
        from taurus import warning

        warning('Unknown unit "%s" (will be treated as unitless)', unit)
        return UR.parse_units("")


def ndim_from_tango(data_format):
    return int(data_format)


def data_format_from_tango(data_format):
    return FROM_TANGO_TO_TAURUS_DFORMAT[data_format]


def data_type_from_tango(data_type):
    return FROM_TANGO_TO_TAURUS_TYPE[data_type]


def display_level_from_tango(disp_level):
    return DisplayLevel(disp_level)


def quality_from_tango(quality):
    return AttrQuality(int(quality))


__NULL_DESC = tango.constants.NotSet, tango.constants.DescNotSpec


def description_from_tango(desc):
    if desc in __NULL_DESC:
        desc = ""
    return desc


__S_TYPES = (
    tango.CmdArgType.DevString,
    tango.CmdArgType.DevVarStringArray,
    tango.CmdArgType.DevEncoded,
)


def standard_display_format_from_tango(dtype, fmt):
    if fmt == "Not specified":
        return "!s"

    # %6.2f is the default value that Tango sets when the format is
    # unassigned in tango < 8. This is only good for float types! So for other
    # types I am changing this value.
    if fmt == "%6.2f":
        if tango.is_float_type(dtype, inc_array=True):
            pass
        elif tango.is_int_type(dtype, inc_array=True):
            fmt = "%d"
        elif dtype in __S_TYPES:
            fmt = "%s"
    return fmt


def display_format_from_tango(dtype, fmt):
    fmt = standard_display_format_from_tango(dtype, fmt)
    return fmt.replace("%s", "!s").replace("%r", "!r").replace("%", "")
