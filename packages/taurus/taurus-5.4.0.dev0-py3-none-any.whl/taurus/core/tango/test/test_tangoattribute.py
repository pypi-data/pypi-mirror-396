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

"""Test for taurus.core.tango.test.test_tangovalidator..."""

# __all__ = []

__docformat__ = "restructuredtext"

import numpy
import pytest
import tango
from pint import UndefinedUnitError

import taurus
from taurus.core import DataFormat, DataType
from taurus.core.tango.tangoattribute import TangoAttrValue
from taurus.core.taurusbasetypes import AttrQuality
from taurus.core.units import UR, Quantity

from .nodb import nodb_dev  # noqa

_INT_IMG = numpy.arange(2 * 3, dtype="int16").reshape((2, 3))
_INT_SPE = _INT_IMG[1, :]
_FLOAT_IMG = numpy.linspace(0.1, 0.6, 6, dtype=numpy.float32).reshape((2, 3))
_FLOAT_SPE = _FLOAT_IMG[1, :]
_FLOAT32_SCALAR_RO = numpy.float32(1.23)
_BOOL_IMG = numpy.array([[True, False], [False, True]])
_BOOL_SPE = [True, False]
_STR = "foo BAR |-+#@!?_[]{}"
_UINT8_IMG = numpy.array([[1, 2], [3, 4]], dtype="uint8")
_UINT8_SPE = _UINT8_IMG[1, :]
_ENUM_IMG_W = numpy.array([[0, 1], [1, 2]])
_ENUM_IMG_R = numpy.array([["ZERO", "ONE"], ["ONE", "TWO"]])
_ENUM_SPE_W = _ENUM_IMG_W[1, :]
_ENUM_SPE_R = _ENUM_IMG_R[1, :]


def _npfloat32(val):
    return numpy.float32(val)


def _npfloat64(val):
    return numpy.float64(val)


def _assertValidValue(exp, got, msg):
    # if we are dealing with quantities, use the magnitude for comparing
    if isinstance(got, Quantity):
        got = got.to(Quantity(exp).units).magnitude
    if isinstance(exp, Quantity):
        exp = exp.magnitude
    try:
        # first try the most generic equality
        chk = bool(got == exp)
    except Exception:
        chk = False
    if not chk:
        # some cases may fail the simple equality but still be True
        try:
            # for those values that can be handled by numpy.allclose()
            chk = numpy.allclose(got, exp, rtol=1e-15)
        except Exception:
            if isinstance(got, numpy.ndarray):
                # uchars were not handled with allclose
                # UGLY!! but numpy.all does not work
                chk = got.tolist() == exp.tolist()
    assert chk, msg


def _getDecodePyTangoAttr(dev_name, attr_name, cfg):
    """Helper for decode the tango attribute infoex"""
    if dev_name.startswith("tango-nodb:"):
        tg_dev_name = "tango" + dev_name[10:] + "#dbase=no"
    dev = tango.DeviceProxy(tg_dev_name)
    infoex = dev.get_attribute_config_ex(attr_name)[0]
    unit = infoex.unit
    if unit is None:
        unit = ""
    try:
        unit = UR.parse_units(unit)
    except (UndefinedUnitError, UnicodeDecodeError):
        unit = UR.parse_units("")
    if cfg in ["range", "alarms", "warnings"]:
        if cfg == "range":
            low = infoex.min_value
            high = infoex.max_value
        elif cfg == "alarms":
            low = infoex.alarms.min_alarm
            high = infoex.alarms.max_alarm
        elif cfg == "warnings":
            low = infoex.alarms.min_warning
            high = infoex.alarms.max_warning
        if low == "Not specified":
            low = "-inf"
        if high == "Not specified":
            high = "inf"
        return [Quantity(float(low), unit), Quantity(float(high), unit)]
    elif cfg == "label":
        return infoex.label
    else:
        return None


@pytest.mark.parametrize(
    "attr_name, setvalue, expected, expected_attrv, expectedshape",
    [
        (
            "short_spectrum",
            Quantity(numpy.empty(0, dtype="int16"), "km"),
            dict(rvalue=Quantity([], "mm"), type=DataType.Integer, unit="mm"),
            dict(rvalue=Quantity([], "mm"), type=DataType.Integer, unit="mm"),
            (0,),
        ),
        (
            "short_image",
            Quantity(numpy.empty((0, 0), dtype="int16"), "mm"),
            dict(rvalue=Quantity([], "mm"), type=DataType.Integer),
            None,
            (0, 0),
        ),
        (
            "boolean_spectrum",
            numpy.empty(0, dtype="bool"),
            dict(type=DataType.Boolean),
            None,
            (0,),
        ),
        (
            "boolean_image",
            numpy.empty((0, 0), dtype="bool"),
            dict(type=DataType.Boolean),
            None,
            (0, 0),
        ),
        # Test encode-decode of strings, booleans and uchars
        (
            "uchar_image",
            _UINT8_IMG,
            dict(
                rvalue=_UINT8_IMG,
                wvalue=_UINT8_IMG,
                type=DataType.Bytes,
                label="uchar_image",
                writable=True,
            ),
            dict(
                rvalue=_UINT8_IMG,
                value=_UINT8_IMG,
                wvalue=_UINT8_IMG,
                w_value=_UINT8_IMG,
                quality=AttrQuality.ATTR_VALID,
            ),
            None,
        ),
        (
            "uchar_spectrum",
            _UINT8_SPE,
            dict(
                rvalue=_UINT8_SPE,
                wvalue=_UINT8_SPE,
                type=DataType.Bytes,
                writable=True,
            ),
            dict(
                rvalue=_UINT8_SPE,
                value=_UINT8_SPE,
                wvalue=_UINT8_SPE,
                w_value=_UINT8_SPE,
                quality=AttrQuality.ATTR_VALID,
            ),
            None,
        ),
        (
            "uchar_scalar",
            12,
            dict(
                rvalue=12,
                wvalue=12,
                type=DataType.Bytes,
                writable=True,
                range=[None, None],
                alarms=[None, None],
                warnings=[None, None],
            ),
            dict(
                rvalue=12,
                value=12,
                wvalue=12,
                w_value=12,
                quality=AttrQuality.ATTR_VALID,
            ),
            None,
        ),
        (
            "uchar_image",
            _UINT8_IMG,
            dict(
                rvalue=_UINT8_IMG,
                wvalue=_UINT8_IMG,
                type=DataType.Bytes,
                label="uchar_image",
                writable=True,
            ),
            dict(
                rvalue=_UINT8_IMG,
                value=_UINT8_IMG,
                wvalue=_UINT8_IMG,
                w_value=_UINT8_IMG,
                quality=AttrQuality.ATTR_VALID,
            ),
            None,
        ),
        (
            "uchar_spectrum",
            _UINT8_SPE,
            dict(
                rvalue=_UINT8_SPE,
                wvalue=_UINT8_SPE,
                type=DataType.Bytes,
                writable=True,
            ),
            dict(
                rvalue=_UINT8_SPE,
                value=_UINT8_SPE,
                wvalue=_UINT8_SPE,
                w_value=_UINT8_SPE,
                quality=AttrQuality.ATTR_VALID,
            ),
            None,
        ),
        (
            "uchar_scalar",
            12,
            dict(
                rvalue=12,
                wvalue=12,
                type=DataType.Bytes,
                writable=True,
                range=[None, None],
                alarms=[None, None],
                warnings=[None, None],
            ),
            dict(
                rvalue=Quantity(12, "mm"),
                value=12,
                wvalue=Quantity(12, "mm"),
                w_value=12,
                quality=AttrQuality.ATTR_VALID,
            ),
            None,
        ),
        (
            "string_image",
            ((_STR,) * 3,) * 2,
            dict(
                rvalue=((_STR,) * 3,) * 2,
                wvalue=((_STR,) * 3,) * 2,
                type=DataType.String,
                label="string_image",
                writable=True,
            ),
            dict(
                value=((_STR,) * 3,) * 2,
                w_value=((_STR,) * 3,) * 2,
                rvalue=((_STR,) * 3,) * 2,
                wvalue=((_STR,) * 3,) * 2,
                quality=AttrQuality.ATTR_VALID,
            ),
            None,
        ),
        (
            "string_spectrum",
            (_STR,) * 3,
            dict(
                rvalue=(_STR,) * 3,
                wvalue=(_STR,) * 3,
                type=DataType.String,
                label="string_spectrum",
                writable=True,
            ),
            dict(
                value=(_STR,) * 3,
                w_value=(_STR,) * 3,
                rvalue=(_STR,) * 3,
                wvalue=(_STR,) * 3,
                quality=AttrQuality.ATTR_VALID,
            ),
            None,
        ),
        (
            "string_scalar",
            _STR,
            dict(
                rvalue=_STR,
                wvalue=_STR,
                type=DataType.String,
                label="string_scalar",
                writable=True,
            ),
            dict(
                value=_STR,
                w_value=_STR,
                rvalue=_STR,
                wvalue=_STR,
                quality=AttrQuality.ATTR_VALID,
            ),
            None,
        ),
        (
            "boolean_image",
            _BOOL_IMG,
            dict(
                rvalue=_BOOL_IMG,
                wvalue=_BOOL_IMG,
                type=DataType.Boolean,
                label="boolean_image",
                writable=True,
            ),
            dict(
                rvalue=_BOOL_IMG,
                value=_BOOL_IMG,
                wvalue=_BOOL_IMG,
                w_value=_BOOL_IMG,
                quality=AttrQuality.ATTR_VALID,
            ),
            None,
        ),
        (
            "boolean_spectrum",
            _BOOL_SPE,
            dict(
                rvalue=_BOOL_SPE,
                wvalue=_BOOL_SPE,
                type=DataType.Boolean,
                writable=True,
            ),
            dict(
                rvalue=_BOOL_SPE,
                value=_BOOL_SPE,
                wvalue=_BOOL_SPE,
                w_value=_BOOL_SPE,
                quality=AttrQuality.ATTR_VALID,
            ),
            None,
        ),
        (
            "boolean_scalar",
            False,
            dict(
                rvalue=False,
                wvalue=False,
                type=DataType.Boolean,
                writable=True,
                range=[None, None],
                alarms=[None, None],
                warnings=[None, None],
            ),
            dict(
                rvalue=False,
                value=False,
                wvalue=False,
                w_value=False,
                quality=AttrQuality.ATTR_VALID,
            ),
            None,
        ),
        (
            "enum_scalar",
            1,
            dict(
                rvalue="ONE",
                wvalue=1,
                type=DataType.DevEnum,
                writable=True,
            ),
            dict(
                rvalue="ONE",
                value="ONE",
                wvalue=1,
                w_value=1,
                quality=AttrQuality.ATTR_VALID,
            ),
            None,
        ),
        (
            "enum_spectrum",
            _ENUM_SPE_W,
            dict(
                rvalue=_ENUM_SPE_R,
                wvalue=_ENUM_SPE_W,
                type=DataType.DevEnum,
                writable=True,
            ),
            dict(
                rvalue=_ENUM_SPE_R,
                value=_ENUM_SPE_R,
                wvalue=_ENUM_SPE_W,
                w_value=_ENUM_SPE_W,
                quality=AttrQuality.ATTR_VALID,
            ),
            None,
        ),
        (
            "enum_image",
            _ENUM_IMG_W,
            dict(
                rvalue=_ENUM_IMG_R,
                wvalue=_ENUM_IMG_W,
                type=DataType.DevEnum,
                label="enum_image",
                writable=True,
            ),
            dict(
                rvalue=_ENUM_IMG_R,
                value=_ENUM_IMG_R,
                wvalue=_ENUM_IMG_W,
                w_value=_ENUM_IMG_W,
                quality=AttrQuality.ATTR_VALID,
            ),
            None,
        ),
        # ==================================================================
        # Test encode-decode with quantitiy conversions
        (
            "float_image",
            Quantity(_FLOAT_IMG, "m"),
            dict(
                rvalue=Quantity(_FLOAT_IMG, "m"),
                wvalue=Quantity(_FLOAT_IMG, "m"),
                type=DataType.Float,
                writable=True,
                quality=AttrQuality.ATTR_VALID,
                label="float_image",
                range=[
                    Quantity(float("-inf"), "mm"),
                    Quantity(float("inf"), "mm"),
                ],
                alarms=[
                    Quantity(float("-inf"), "mm"),
                    Quantity(float("inf"), "mm"),
                ],
                warnings=[
                    Quantity(float("-inf"), "mm"),
                    Quantity(float("inf"), "mm"),
                ],
            ),
            dict(
                rvalue=Quantity(_FLOAT_IMG, "m"),
                value=1000 * _FLOAT_IMG,
                wvalue=Quantity(_FLOAT_IMG, "m"),
                w_value=1000 * _FLOAT_IMG,
                quality=AttrQuality.ATTR_VALID,
            ),
            numpy.shape(_FLOAT_IMG),
        ),
        (
            "float_spectrum",
            Quantity(_FLOAT_SPE, "m"),
            dict(
                rvalue=Quantity(_FLOAT_SPE, "m"),
                wvalue=Quantity(_FLOAT_SPE, "m"),
                type=DataType.Float,
                quality=AttrQuality.ATTR_VALID,
            ),
            dict(
                rvalue=Quantity(_FLOAT_SPE, "m"),
                value=1000 * _FLOAT_SPE,
                wvalue=Quantity(_FLOAT_SPE, "m"),
                w_value=1000 * _FLOAT_SPE,
                quality=AttrQuality.ATTR_VALID,
            ),
            numpy.shape(_FLOAT_SPE),
        ),
        (
            "float_scalar",
            Quantity(_npfloat32(0.01), "m"),
            dict(
                rvalue=Quantity(_npfloat32(0.01), "m"),
                wvalue=Quantity(_npfloat32(10), "mm"),
                type=DataType.Float,
                name="float_scalar",
                range=[
                    Quantity(_npfloat32(-12.30), "mm"),
                    Quantity(_npfloat32(12.30), "mm"),
                ],
                alarms=[
                    Quantity(_npfloat32(-6.15), "mm"),
                    Quantity(_npfloat32(6.15), "mm"),
                ],
                warnings=[
                    Quantity(_npfloat32(-3.69), "mm"),
                    Quantity(_npfloat32(3.69), "mm"),
                ],
            ),
            dict(
                value=_npfloat32(10),
                rvalue=Quantity(_npfloat32(0.01), "m"),
                w_value=_npfloat32(10),
                wvalue=Quantity(_npfloat32(10), "mm"),
                quality=AttrQuality.ATTR_ALARM,
            ),
            None,
        ),
        (
            "float_scalar",
            Quantity(_npfloat32(0.004), "m"),
            dict(
                rvalue=Quantity(_npfloat32(4), "mm"),
                wvalue=Quantity(_npfloat32(4), "mm"),
            ),
            dict(
                rvalue=Quantity(_npfloat32(4), "mm"),
                wvalue=Quantity(_npfloat32(0.004), "m"),
                quality=AttrQuality.ATTR_WARNING,
            ),
            None,
        ),
        (
            "float_scalar",
            Quantity(_npfloat32(3), "mm"),
            dict(
                rvalue=Quantity(_npfloat32(3), "mm"),
                wvalue=Quantity(_npfloat32(3), "mm"),
                type=DataType.Float,
            ),
            dict(
                value=_npfloat32(3),
                w_value=_npfloat32(3),
                quality=AttrQuality.ATTR_VALID,
            ),
            None,
        ),
        (
            "double_scalar",
            Quantity(_npfloat64(0.01), "m"),
            dict(
                rvalue=Quantity(_npfloat64(0.01), "m"),
                wvalue=Quantity(_npfloat64(10), "mm"),
                type=DataType.Float,
                name="double_scalar",
                range=[
                    Quantity(_npfloat64(-12.30), "mm"),
                    Quantity(_npfloat64(12.30), "mm"),
                ],
                alarms=[
                    Quantity(_npfloat64(-6.15), "mm"),
                    Quantity(_npfloat64(6.15), "mm"),
                ],
                warnings=[
                    Quantity(_npfloat64(-3.69), "mm"),
                    Quantity(_npfloat64(3.69), "mm"),
                ],
            ),
            dict(
                value=_npfloat64(10),
                rvalue=Quantity(_npfloat64(0.01), "m"),
                w_value=_npfloat64(10),
                wvalue=Quantity(_npfloat64(10), "mm"),
                quality=AttrQuality.ATTR_ALARM,
            ),
            None,
        ),
        (
            "double_scalar",
            Quantity(_npfloat64(0.004), "m"),
            dict(
                rvalue=Quantity(_npfloat64(4), "mm"),
                wvalue=Quantity(_npfloat64(4), "mm"),
            ),
            dict(
                rvalue=Quantity(_npfloat64(4), "mm"),
                wvalue=Quantity(_npfloat64(0.004), "m"),
                quality=AttrQuality.ATTR_WARNING,
            ),
            None,
        ),
        (
            "double_scalar",
            Quantity(_npfloat64(3), "mm"),
            dict(
                rvalue=Quantity(_npfloat64(3), "mm"),
                wvalue=Quantity(_npfloat64(3), "mm"),
                type=DataType.Float,
            ),
            dict(
                value=_npfloat64(3),
                w_value=_npfloat64(3),
                quality=AttrQuality.ATTR_VALID,
            ),
            None,
        ),
        (
            "short_image",
            Quantity(_INT_IMG, "m"),
            dict(
                rvalue=Quantity(_INT_IMG, "m"),
                wvalue=Quantity(_INT_IMG, "m"),
                type=DataType.Integer,
            ),
            dict(
                value=1000 * _INT_IMG,
                rvalue=Quantity(_INT_IMG, "m"),
                wvalue=Quantity(_INT_IMG, "m"),
                w_value=1000 * _INT_IMG,
                quality=AttrQuality.ATTR_VALID,
            ),
            numpy.shape(_INT_IMG),
        ),
        (
            "short_spectrum",
            Quantity(_INT_SPE, "m"),
            dict(
                rvalue=Quantity(_INT_SPE, "m"),
                wvalue=Quantity(_INT_SPE, "m"),
                type=DataType.Integer,
            ),
            dict(value=1000 * _INT_SPE, w_value=1000 * _INT_SPE),
            numpy.shape(_INT_SPE),
        ),
        (
            "short_scalar",
            Quantity(1, "m"),
            dict(
                rvalue=Quantity(1000, "mm"),
                wvalue=Quantity(1000, "mm"),
                type=DataType.Integer,
                label="short_scalar",
                data_format=DataFormat._0D,
                writable=True,
                range=[Quantity(-1230, "mm"), Quantity(1230, "mm")],
                alarms=[Quantity(-615, "mm"), Quantity(615, "mm")],
                warnings=[Quantity(-369, "mm"), Quantity(369, "mm")],
            ),
            dict(value=1000, w_value=1000, quality=AttrQuality.ATTR_ALARM),
            None,
        ),
        # ===================================================================
        # Test read of tango attributes
        (
            "uchar_image_ro",
            None,
            dict(
                rvalue=Quantity([[1] * 3] * 3, "mm"),
                wvalue=[[]] if tango.Release.version_number >= 940 else None,
                type=DataType.Bytes,
            ),
            dict(
                value=[[1] * 3] * 3,
                w_value=[[]] if tango.Release.version_number >= 940 else None,
                quality=AttrQuality.ATTR_VALID,
            ),
            (3, 3),
        ),
        (
            "uchar_scalar_ro",
            None,
            dict(
                rvalue=1,
                wvalue=None,
                type=DataType.Bytes,
                data_format=DataFormat._0D,
                writable=False,
                range=[None, None],
                alarms=[None, None],
                warnings=[None, None],
            ),
            dict(
                rvalue=Quantity(1, "mm"),
                value=1,
                quality=AttrQuality.ATTR_VALID,
                wvalue=None,
                w_value=None,
            ),
            None,
        ),
        # ------------------------------------------------------------------
        # Disable these 2tests because of known (Py)Tango bug for empty
        # string arrays
        #
        # (
        #     "string_image_ro",
        #     None,
        #     dict(
        #         rvalue=(("hello world",) * 3,) * 3,
        #         wvalue=None,
        #         type=DataType.String,
        #     ),
        #     dict(
        #         value=(("hello world",) * 3,) * 3,
        #         w_value=None,
        #         quality=AttrQuality.ATTR_VALID,
        #     ),
        #     (3, 3),
        # ),
        # (
        #     "string_spectrum_ro",
        #     None,
        #     dict(
        #         rvalue=("hello world",) * 3,
        #         wvalue=None,
        #         type=DataType.String
        #     ),
        #     dict(
        #         value=("hello world",) * 3,
        #         w_value=None,
        #         quality=AttrQuality.ATTR_VALID,
        #     ),
        #     (3,),
        # ),
        # ------------------------------------------------------------------
        (
            "string_scalar_ro",
            None,
            dict(rvalue="hello world", wvalue=None, type=DataType.String),
            dict(
                value="hello world",
                w_value=None,
                quality=AttrQuality.ATTR_VALID,
            ),
            None,
        ),
        (
            "boolean_image_ro",
            None,
            dict(
                rvalue=numpy.ones((3, 3), dtype="b"),
                wvalue=[[]] if tango.Release.version_number >= 940 else None,
                type=DataType.Boolean,
            ),
            dict(
                value=numpy.ones((3, 3), dtype="b"),
                w_value=[[]] if tango.Release.version_number >= 940 else None,
                quality=AttrQuality.ATTR_VALID,
            ),
            (3, 3),
        ),
        (
            "boolean_spectrum_ro",
            None,
            dict(
                rvalue=numpy.array([True] * 3),
                wvalue=[] if tango.Release.version_number >= 940 else None,
                type=DataType.Boolean,
                label="boolean_spectrum_ro",
            ),
            dict(
                value=numpy.array([True] * 3),
                w_value=[] if tango.Release.version_number >= 940 else None,
                quality=AttrQuality.ATTR_VALID,
            ),
            (3,),
        ),
        (
            "boolean_scalar_ro",
            None,
            dict(
                rvalue=True,
                wvalue=None,
                type=DataType.Boolean,
                range=[None, None],
                alarms=[None, None],
                warnings=[None, None],
                data_format=DataFormat._0D,
                writable=False,
            ),
            dict(value=True, w_value=None, quality=AttrQuality.ATTR_VALID),
            None,
        ),
        (
            "enum_image_ro",
            None,
            dict(
                rvalue=numpy.full((3, 3), "ZERO"),
                wvalue=[[]] if tango.Release.version_number >= 940 else None,
                type=DataType.DevEnum,
            ),
            dict(
                value=numpy.full((3, 3), "ZERO"),
                w_value=[[]] if tango.Release.version_number >= 940 else None,
                quality=AttrQuality.ATTR_VALID,
            ),
            (3, 3),
        ),
        (
            "enum_spectrum_ro",
            None,
            dict(
                rvalue=numpy.array(["ZERO"] * 3),
                wvalue=[] if tango.Release.version_number >= 940 else None,
                type=DataType.DevEnum,
                label="enum_spectrum_ro",
            ),
            dict(
                value=numpy.array(["ZERO"] * 3),
                w_value=[] if tango.Release.version_number >= 940 else None,
                quality=AttrQuality.ATTR_VALID,
            ),
            (3,),
        ),
        (
            "enum_scalar_ro",
            None,
            dict(
                rvalue="ZERO",
                wvalue=None,
                type=DataType.DevEnum,
                range=[None, None],
                alarms=[None, None],
                warnings=[None, None],
                data_format=DataFormat._0D,
                writable=False,
            ),
            dict(value="ZERO", w_value=None, quality=AttrQuality.ATTR_VALID),
            None,
        ),
        (
            "float_image_ro",
            None,
            dict(
                rvalue=Quantity([[_FLOAT32_SCALAR_RO] * 3] * 3, "mm"),
                wvalue=(
                    Quantity([[]], "mm")
                    if tango.Release.version_number >= 940
                    else None
                ),
                type=DataType.Float,
            ),
            dict(
                value=[[_FLOAT32_SCALAR_RO] * 3] * 3,
                w_value=(
                    Quantity([[]], "mm")
                    if tango.Release.version_number >= 940
                    else None
                ),
                quality=AttrQuality.ATTR_VALID,
                wvalue=(
                    Quantity([[]], "mm")
                    if tango.Release.version_number >= 940
                    else None
                ),
            ),
            (3, 3),
        ),
        (
            "float_spectrum_ro",
            None,
            dict(
                rvalue=Quantity([_FLOAT32_SCALAR_RO] * 3, "mm"),
                wvalue=(
                    Quantity([], "mm") if tango.Release.version_number >= 940 else None
                ),
                type=DataType.Float,
            ),
            dict(
                value=[_FLOAT32_SCALAR_RO] * 3,
                w_value=(
                    Quantity([], "mm") if tango.Release.version_number >= 940 else None
                ),
                quality=AttrQuality.ATTR_VALID,
            ),
            (3,),
        ),
        (
            "float_scalar_ro",
            None,
            dict(
                rvalue=Quantity(_FLOAT32_SCALAR_RO, "mm"),
                wvalue=None,
                type=DataType.Float,
                writable=False,
                range=[
                    Quantity(float("-inf"), "mm"),
                    Quantity(float("inf"), "mm"),
                ],
                alarms=[
                    Quantity(float("-inf"), "mm"),
                    Quantity(float("inf"), "mm"),
                ],
                warnings=[
                    Quantity(float("-inf"), "mm"),
                    Quantity(float("inf"), "mm"),
                ],
            ),
            dict(
                value=_FLOAT32_SCALAR_RO,
                w_value=None,
                quality=AttrQuality.ATTR_VALID,
            ),
            None,
        ),
        (
            "short_image_ro",
            None,
            dict(
                rvalue=Quantity([[123] * 3] * 3, "mm"),
                wvalue=(
                    Quantity([[]], "mm")
                    if tango.Release.version_number >= 940
                    else None
                ),
                type=DataType.Integer,
            ),
            dict(
                rvalue=Quantity([[123] * 3] * 3, "mm"),
                value=[[123] * 3] * 3,
                quality=AttrQuality.ATTR_VALID,
                wvalue=(
                    Quantity([[]], "mm")
                    if tango.Release.version_number >= 940
                    else None
                ),
                w_value=(
                    Quantity([[]], "mm")
                    if tango.Release.version_number >= 940
                    else None
                ),
            ),
            (3, 3),
        ),
        (
            "short_spectrum_ro",
            None,
            dict(
                rvalue=Quantity([123] * 3, "mm"),
                wvalue=(
                    Quantity([], "mm") if tango.Release.version_number >= 940 else None
                ),
                type=DataType.Integer,
                data_format=DataFormat._1D,
                writable=False,
            ),
            dict(
                rvalue=Quantity([123] * 3, "mm"),
                value=[123] * 3,
                quality=AttrQuality.ATTR_VALID,
                wvalue=(
                    Quantity([], "mm") if tango.Release.version_number >= 940 else None
                ),
                w_value=(
                    Quantity([], "mm") if tango.Release.version_number >= 940 else None
                ),
            ),
            (3,),
        ),
        (
            "short_scalar_ro",
            None,
            dict(
                rvalue=Quantity(123, "mm"),
                wvalue=None,
                type=DataType.Integer,
                data_format=DataFormat._0D,
                writable=False,
                range=[
                    Quantity(float("-inf"), "mm"),
                    Quantity(float("inf"), "mm"),
                ],
                alarms=[
                    Quantity(float("-inf"), "mm"),
                    Quantity(float("inf"), "mm"),
                ],
                warnings=[
                    Quantity(float("-inf"), "mm"),
                    Quantity(float("inf"), "mm"),
                ],
            ),
            dict(
                rvalue=Quantity(123, "mm"),
                value=123,
                quality=AttrQuality.ATTR_VALID,
                wvalue=None,
                w_value=None,
            ),
            None,
        ),
    ],
)
def test_write_read_attr(
    nodb_dev,  # noqa: F811
    attr_name,
    setvalue,
    expected,
    expected_attrv,
    expectedshape,
):
    """check creation and correct write-and-read of an attribute"""

    if expected is None:
        expected = {}
    if expected_attrv is None:
        expected_attrv = {}

    attr_fullname = "{}/{}".format(nodb_dev, attr_name)
    a = taurus.Attribute(attr_fullname)

    if setvalue is None:
        read_value = a.read()
    else:
        a.write(setvalue)
        read_value = a.read(cache=False)

    msg = 'read() for "%s" did not return a TangoAttrValue (got a %s)' % (
        attr_name,
        read_value.__class__.__name__,
    )
    assert isinstance(read_value, TangoAttrValue), msg

    # Test attribute
    for k, exp in expected.items():
        try:
            got = getattr(a, k)
        except AttributeError:
            msg = 'The attribute, "%s" does not provide info on %s' % (
                attr_name,
                k,
            )
            pytest.fail(msg)
        msg = '%s for "%s" should be %r (got %r)' % (k, attr_name, exp, got)
        _assertValidValue(exp, got, msg)

    # Test attribute value
    for k, exp in expected_attrv.items():
        try:
            got = getattr(read_value, k)
        except AttributeError:
            msg = 'The read value for "%s" does not provide info on %s' % (
                attr_name,
                k,
            )
            pytest.fail(msg)
        msg = "%s for the value of %s should be %r (got %r)" % (
            k,
            attr_name,
            exp,
            got,
        )
        _assertValidValue(exp, got, msg)

    if expectedshape is not None:
        msg = "rvalue.shape for %s should be %r (got %r)" % (
            attr_name,
            expectedshape,
            read_value.rvalue.shape,
        )
        assert read_value.rvalue.shape == expectedshape, msg


@pytest.mark.parametrize(
    "attr_name, cfg, value, expected",
    [
        (
            "short_scalar_nu",
            "range",
            [float("-inf"), float("inf")],
            [Quantity(float("-inf")), Quantity(float("inf"))],
        ),
        (
            "short_scalar_nu",
            "range",
            [Quantity(float("-inf")), Quantity(float("inf"))],
            [Quantity(float("-inf")), Quantity(float("inf"))],
        ),
        (
            "short_scalar_nu",
            "range",
            [100, 300],
            [Quantity(100), Quantity(300)],
        ),
        (
            "short_scalar_nu",
            "range",
            [Quantity(100), Quantity(300)],
            [Quantity(100), Quantity(300)],
        ),
        (
            "float_scalar",
            "range",
            [Quantity(_npfloat32(-5), "mm"), Quantity(_npfloat32(5), "mm")],
            [Quantity(_npfloat32(-0.005), "m"), Quantity(_npfloat32(5), "mm")],
        ),
        ("short_spectrum", "label", "Just a Test", "Just a Test"),
        ("boolean_spectrum", "label", "Just_a_Test", "Just_a_Test"),
        (
            "short_scalar",
            "warnings",
            [Quantity(-2, "mm"), Quantity(2, "mm")],
            [Quantity(-2, "mm"), Quantity(0.002, "m")],
        ),
        (
            "short_image",
            "warnings",
            [Quantity(-2, "mm"), Quantity(2, "mm")],
            [Quantity(-0.002, "m"), Quantity(2, "mm")],
        ),
        (
            "float_image",
            "warnings",
            [
                Quantity(_npfloat32(-0.75), "mm"),
                Quantity(_npfloat32(0.75), "mm"),
            ],
            [
                Quantity(_npfloat32(-0.00075), "m"),
                Quantity(_npfloat32(0.75), "mm"),
            ],
        ),
        (
            "short_scalar_nu",
            "warnings",
            [100, 300],
            [Quantity(100), Quantity(300)],
        ),
        (
            "short_scalar",
            "alarms",
            [Quantity(-50, "mm"), Quantity(50, "mm")],
            [Quantity(-50, "mm"), Quantity(50, "mm")],
        ),
        (
            "short_image",
            "alarms",
            [Quantity(-2, "mm"), Quantity(2, "mm")],
            [Quantity(-0.002, "m"), Quantity(2, "mm")],
        ),
        (
            "float_image",
            "alarms",
            [
                Quantity(_npfloat32(-0.75), "mm"),
                Quantity(_npfloat32(0.75), "mm"),
            ],
            [
                Quantity(_npfloat32(-0.00075), "m"),
                Quantity(_npfloat32(0.75), "mm"),
            ],
        ),
        (
            "short_scalar_nu",
            "alarms",
            [100, 300],
            [Quantity(100), Quantity(300)],
        ),
    ],
)
def test_write_read_conf(
    nodb_dev,  # noqa: F811
    attr_name,
    cfg,
    value,
    expected,
):
    """Check the write-and-read of the TangoAttribute configuration"""
    attr_fullname = "{}/{}".format(nodb_dev, attr_name)
    attr = taurus.Attribute(attr_fullname)
    # write the property
    setattr(attr, cfg, value)
    # read the property
    got = getattr(attr, cfg)
    msg = "%s.%s from Taurus do not mach, expected %s read %s" % (
        attr_name,
        cfg,
        expected,
        got,
    )
    map(_assertValidValue, got, expected, msg)

    msg = "%s.%s from Tango do not mach, expected %s read %s" % (
        attr_name,
        cfg,
        expected,
        got,
    )
    tangovalue = _getDecodePyTangoAttr(nodb_dev, attr_name, cfg)
    map(_assertValidValue, got, tangovalue, msg)
