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

"""Unit tests for Taurus Led"""

import pytest

from taurus.qt.qtgui.display import TaurusLed
from taurus.test.pytest import check_taurus_deprecations

try:
    # The following are Tango-centric imports.
    from taurus.core.tango.test import nodb_dev  # noqa: F401

    _TANGO_MISSING = False
except Exception:
    _TANGO_MISSING = True


def _check_taurusled(
    qtbot,
    caplog,
    model,
    modelIndex=None,
    colorOn=None,
    colorOff=None,
    inverted=False,
    depr=0,
    expected_color=TaurusLed.DefaultOnColor,
    expected_state=True,
    expected_bg=False,
):
    with check_taurus_deprecations(caplog, expected=depr):
        w = TaurusLed()
        qtbot.addWidget(w)
        with qtbot.waitSignal(w.modelChanged, timeout=3200):
            w.setModel(model)
        if modelIndex is not None:
            w.setModelIndex(modelIndex)
        if colorOn is not None:
            w.setOnColor(colorOn)
        if colorOff is not None:
            w.setOffColor(colorOff)
        w.setLedInverted(inverted=inverted)

        def _ok():
            """Check led"""
            assert w.ledColor == expected_color
            if w.ledInverted:
                assert w.ledStatus is not expected_state
            else:
                assert w.ledStatus is expected_state
            assert w.autoFillBackground() == expected_bg

        qtbot.waitUntil(_ok, timeout=3200)


def _check_taurusled_with_tango(
    qtbot,
    caplog,
    nodb_dev,  # noqa: F811
    model,
    modelIndex=None,
    colorOn=None,
    colorOff=None,
    inverted=False,
    depr=0,
    expected_color=TaurusLed.DefaultOnColor,
    expected_state=True,
    expected_bg=False,
):
    with check_taurus_deprecations(caplog, expected=depr):
        w = TaurusLed()
        qtbot.addWidget(w)
        if model.startswith("/"):
            model = "{}{}".format(nodb_dev, model)
        with qtbot.waitSignal(w.modelChanged, timeout=3200):
            w.setModel(model)
        if modelIndex is not None:
            w.setModelIndex(modelIndex)
        if colorOn is not None:
            w.setOnColor(colorOn)
        if colorOff is not None:
            w.setOffColor(colorOff)
        w.setLedInverted(inverted=inverted)

        def _ok():
            """Check led"""
            assert w.ledColor == expected_color
            if w.ledInverted:
                assert w.ledStatus is not expected_state
            else:
                assert w.ledStatus is expected_state
            assert w.autoFillBackground() == expected_bg

        qtbot.waitUntil(_ok, timeout=3200)


LED_ON_DATA = [
    # model, modelIndex
    ("eval:True", None),
    ("eval:[True, False]", 0),
    # integers
    ("eval:1", None),
    ("eval:123", None),
    # strings
    ("eval:'0'", None),
    ("eval:'1'", None),
    ("eval:'123'", None),
    ("eval:'False'", None),
    ("eval:'foo'", None),
]


@pytest.mark.parametrize(
    "model, modelIndex",
    LED_ON_DATA,
)
@pytest.mark.forked
def test_taurusled_led_on(qtbot, caplog, model, modelIndex):
    _check_taurusled(
        qtbot,
        caplog,
        model,
        modelIndex=modelIndex,
        expected_state=True,
    )


@pytest.mark.parametrize(
    "model, modelIndex",
    LED_ON_DATA,
)
@pytest.mark.forked
def test_taurusled_led_on_inverted(qtbot, caplog, model, modelIndex):
    _check_taurusled(
        qtbot,
        caplog,
        model,
        modelIndex=modelIndex,
        inverted=True,
        expected_state=False,
    )


LED_OFF_DATA = [
    # model, modelIndex
    ("eval:False", None),
    ("eval:[True, False]", 1),
    # integers
    ("eval:0", None),
    # strings
    ("eval:''", None),
]


@pytest.mark.parametrize(
    "model, modelIndex",
    LED_OFF_DATA,
)
@pytest.mark.forked
def test_taurusled_led_off(qtbot, caplog, model, modelIndex):
    _check_taurusled(
        qtbot,
        caplog,
        model,
        modelIndex=modelIndex,
        expected_state=False,
    )


@pytest.mark.parametrize(
    "model, modelIndex",
    LED_OFF_DATA,
)
@pytest.mark.forked
def test_taurusled_led_off_inverted(qtbot, caplog, model, modelIndex):
    _check_taurusled(
        qtbot,
        caplog,
        model,
        modelIndex=modelIndex,
        inverted=True,
        expected_state=True,
    )


@pytest.mark.parametrize(
    "model, inverted, expected_color, expected_state",
    [
        ("eval:True", False, "red", True),
        ("eval:False", False, "blue", False),
        ("eval:True", True, "red", False),
        ("eval:False", True, "blue", True),
    ],
)
@pytest.mark.forked
def test_taurusled_red_on_blue_off(
    qtbot, caplog, model, inverted, expected_color, expected_state
):
    _check_taurusled(
        qtbot,
        caplog,
        model,
        inverted=inverted,
        colorOn="red",
        colorOff="blue",
        expected_color=expected_color,
        expected_state=expected_state,
    )


FAILURE_COLOR = "black"
FAILURE_BG = True
FAILURE_DATA = [
    # model, modelIndex
    ("eval:None", None),
    # index out of range
    ("eval:[True, False]", 2),
]


@pytest.mark.parametrize(
    "model, modelIndex",
    FAILURE_DATA,
)
@pytest.mark.forked
def test_taurusled_failure(qtbot, caplog, model, modelIndex):
    _check_taurusled(
        qtbot,
        caplog,
        model,
        modelIndex=modelIndex,
        expected_color=FAILURE_COLOR,
        expected_state=False,
        expected_bg=FAILURE_BG,
    )


@pytest.mark.parametrize(
    "model, modelIndex",
    FAILURE_DATA,
)
@pytest.mark.forked
def test_taurusled_failure_inverted(qtbot, caplog, model, modelIndex):
    _check_taurusled(
        qtbot,
        caplog,
        model,
        modelIndex=modelIndex,
        inverted=True,
        expected_color=FAILURE_COLOR,
        expected_state=True,
        expected_bg=FAILURE_BG,
    )


FAILURE_TANGO_DATA = [
    # tango model
    "/invalid_tango_attr",
    "tango://not/existing/device/anyAttrName",
]


@pytest.mark.skipif(_TANGO_MISSING, reason="tango-dependent test")
@pytest.mark.parametrize(
    "model",
    FAILURE_TANGO_DATA,
)
@pytest.mark.forked
def test_taurusled_tango_failure(qtbot, caplog, nodb_dev, model):  # noqa: F811
    _check_taurusled_with_tango(
        qtbot,
        caplog,
        nodb_dev,
        model,
        expected_color=FAILURE_COLOR,
        expected_state=False,
        expected_bg=FAILURE_BG,
    )


@pytest.mark.skipif(_TANGO_MISSING, reason="tango-dependent test")
@pytest.mark.parametrize(
    "model",
    FAILURE_TANGO_DATA,
)
@pytest.mark.forked
def test_taurusled_tango_failinv(qtbot, caplog, nodb_dev, model):  # noqa: F811
    _check_taurusled_with_tango(
        qtbot,
        caplog,
        nodb_dev,
        model,
        inverted=True,
        expected_color=FAILURE_COLOR,
        expected_state=True,
        expected_bg=FAILURE_BG,
    )


def test_value_changed_signal(qtbot):
    """Tests if the valueChangedSignal is emitted after a new value has been
    handled by the widget/controller"""
    w = TaurusLed()

    with qtbot.waitSignals([w.valueChangedSignal, w.modelChanged], timeout=3200):
        w.setModel("eval:True")
