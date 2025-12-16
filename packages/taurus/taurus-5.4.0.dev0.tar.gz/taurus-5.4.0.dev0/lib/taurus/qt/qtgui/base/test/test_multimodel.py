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

"""Unit tests for the multi-model API"""

from unittest.mock import DEFAULT, MagicMock, patch

import pytest

import taurus
from taurus.core import TaurusElementType
from taurus.external.qt import Qt
from taurus.qt.qtgui.base import MLIST, TaurusBaseComponent, TaurusBaseWidget
from taurus.test.pytest import check_taurus_deprecations


class _FooComposer(TaurusBaseComponent):
    modelKeys = ["", "foo"]


class _XYComposer(TaurusBaseComponent):
    modelKeys = ["x", "y"]


class _Container(TaurusBaseComponent):
    modelKeys = [MLIST]


class _FooWidget(Qt.QWidget, TaurusBaseWidget):
    def __init__(self):
        # explicit init call instead of super to workaround a bug in PySide MRO
        Qt.QWidget.__init__(self)
        TaurusBaseWidget.__init__(self)


@pytest.mark.forked
def test_single_model(caplog):
    """Check that the original single-model behaviour is preserved. All the
    model-related API is tested
    """

    with check_taurus_deprecations(caplog):
        # Check initialization state
        b = TaurusBaseComponent()
        _setModelName_mock = MagicMock(wraps=b._setModelName)

        assert b.modelKeys == [""]

        assert b.modelObj is None
        assert b.modelName == ""
        assert b.modelFragmentName is None

        assert b._findModelClass() is None
        assert b.getDisplayValue() is b.noneValue
        assert b.getFullModelName() is None
        assert b.getModel() == ""
        assert b.getModelClass() is None
        pytest.raises(AttributeError, b.getModelFragmentObj)  # is this ok?
        assert b.getModelInConfig() is False
        assert b.getModelIndexValue() is None
        assert b.getModelName() == ""
        assert b.getModelObj() is None
        assert b.getModelType() is TaurusElementType.Unknown
        assert b.getModelValueObj() is None
        assert b._getParentModelName() == ""
        assert b._getParentModelObj() is None
        pytest.raises(RuntimeError, b._getParentTaurusComponent)
        assert b._getUseParentModel() is False
        assert b.isAttached() is False

        # set model and check state
        n1 = "eval:1"
        a1 = taurus.Attribute(n1)
        fn1 = a1.getFullName()

        _setModelCheck_mock = MagicMock(wraps=b._setModelCheck)
        _setModelName_mock = MagicMock(wraps=b._setModelName)
        with patch.multiple(
            b,
            preAttach=DEFAULT,
            postAttach=DEFAULT,
            preDetach=DEFAULT,
            postDetach=DEFAULT,
            _setModelCheck=_setModelCheck_mock,
            _setModelName=_setModelName_mock,
        ) as _att:
            b.setModel(n1)
            _att["preAttach"].assert_called_once_with(key="")
            _att["postAttach"].assert_called_once_with(key="")
            _att["preDetach"].assert_called_once_with(key="")
            _att["postDetach"].assert_called_once_with(key="")
            _setModelCheck_mock.assert_called_once_with(n1, key="")
            _setModelName_mock.assert_called_once_with(n1, parent=None, key="")

        # check state after setting model
        assert b.modelObj is a1
        assert b.modelName is n1
        assert b.modelFragmentName is None

        assert b._findModelClass() is a1.__class__
        assert b.getDisplayValue() == "1"
        assert b.getFullModelName() is fn1
        assert b.getModel() is n1
        assert b.getModelClass() is a1.__class__
        assert b.getModelFragmentObj() is a1.rvalue
        assert b.getModelInConfig() is False
        assert b.getModelIndexValue() is None
        assert b.getModelName() is n1
        assert b.getModelObj() is a1
        assert b.getModelType() is TaurusElementType.Attribute
        assert b.getModelValueObj() is a1.read()
        assert b._getParentModelName() == ""
        assert b._getParentModelObj() is None
        pytest.raises(RuntimeError, b._getParentTaurusComponent)
        assert b._getUseParentModel() is False
        assert b.isAttached() is True

        # reset model
        _setModelCheck_mock = MagicMock(wraps=b._setModelCheck)
        _setModelName_mock = MagicMock(wraps=b._setModelName)
        with patch.multiple(
            b,
            preAttach=DEFAULT,
            postAttach=DEFAULT,
            preDetach=DEFAULT,
            postDetach=DEFAULT,
            _setModelCheck=_setModelCheck_mock,
            _setModelName=_setModelName_mock,
        ) as _att:
            b.resetModel()
            _att["preAttach"].assert_called_once_with(key="")
            _att["postAttach"].assert_called_once_with(key="")
            _att["preDetach"].assert_called_once_with(key="")
            _att["postDetach"].assert_called_once_with(key="")
            _setModelCheck_mock.assert_called_once_with("", key="")
            _setModelName_mock.assert_called_once_with("", parent=None, key="")

        # check state after resetting model
        assert b.modelObj is None
        assert b.modelName == ""
        assert b.modelFragmentName is None

        assert b._findModelClass() is None
        assert b.getDisplayValue() is b.noneValue
        assert b.getFullModelName() is None
        assert b.getModel() == ""
        assert b.getModelClass() is None
        pytest.raises(AttributeError, b.getModelFragmentObj)  # is this ok?
        assert b.getModelInConfig() is False
        assert b.getModelIndexValue() is None
        assert b.getModelName() == ""
        assert b.getModelObj() is None
        assert b.getModelType() is TaurusElementType.Unknown
        assert b.getModelValueObj() is None
        assert b._getParentModelName() == ""
        assert b._getParentModelObj() is None
        pytest.raises(RuntimeError, b._getParentTaurusComponent)
        assert b._getUseParentModel() is False
        assert b.isAttached() is False


@pytest.mark.forked
def test_deprecated_model_api(qtbot, caplog):
    """Check that the deprecated methods of the single-model api still work

    Each call to the following should emit a deprecation

        - `findModelClass`
        - `getParentModelName`
        - `getParentModelObj`
        - `getParentTaurusComponent`
        - `getUseParentModel`
        - `resetUseParentModel`
        - `setModelCheck`
        - `setModelName`
        - `setUseParentModel`

    """
    w = _FooWidget()
    qtbot.addWidget(w)

    with check_taurus_deprecations(caplog, expected=1):
        assert w.findModelClass() is None
    with check_taurus_deprecations(caplog, expected=1):
        assert w.getParentModelName() == ""
    with check_taurus_deprecations(caplog, expected=1):
        assert w.getParentModelObj() is None
    with check_taurus_deprecations(caplog, expected=1):
        assert w.getParentTaurusComponent() is None
    with check_taurus_deprecations(caplog, expected=1):
        assert w.getUseParentModel() is False
    with check_taurus_deprecations(caplog, expected=1):
        w.setUseParentModel(True)
    with check_taurus_deprecations(caplog, expected=1):
        assert w.getUseParentModel() is True
    with check_taurus_deprecations(caplog, expected=1):
        w.resetUseParentModel()
    with check_taurus_deprecations(caplog, expected=1):
        assert w.getUseParentModel() is False
    with check_taurus_deprecations(caplog, expected=1):
        w.setModelCheck("eval:1")
    with check_taurus_deprecations(caplog, expected=1):
        w.setModelName("eval:2")


@pytest.mark.forked
def test_single_model_reimplementation_support(caplog):
    """
    Check that the multi-model API works also for objects that reimplement some
    members according to the old single-model API
    """

    class _OldReimplementer(TaurusBaseComponent):
        modelKeys = ["", "other"]

        def __init__(self):
            TaurusBaseComponent.__init__(self)
            self._calls = []

        def lastcalls(self):
            ret = self._calls[:]
            self._calls = []
            return ret

        def getModelClass(self):
            self._calls.append("getModelClass")
            return taurus.Attribute("eval:1").__class__

        def getModelFragmentObj(self, fragmentName=None):
            self._calls.append("getModelFragmentObj")
            return "abcd"

        def getModelObj(self):
            self._calls.append("getModelObj")
            return TaurusBaseComponent.getModelObj(self, key="")

        def setModelCheck(self, model, check=True):
            self._calls.append("setModelCheck")
            return TaurusBaseComponent._setModelCheck(self, model, check=check, key="")

        def setModelName(self, name, parent=None):
            self._calls.append("setModelName")
            return TaurusBaseComponent._setModelName(self, name, parent=parent, key="")

        def preAttach(self):
            self._calls.append("preAttach")

        def postAttach(self):
            self._calls.append("postAttach")

        def preDetach(self):
            self._calls.append("preDetach")

        def postDetach(self):
            self._calls.append("postDetach")

    b = _OldReimplementer()

    with check_taurus_deprecations(caplog, expected=7):
        # trigger calls to deprecated reimplementations of:
        # - setModelCheck
        # - setModelName
        # - {pre,post}{At,De}tach
        # - getModelClass
        b.setModel("eval:1")
        assert b.lastcalls() == [
            "setModelCheck",
            "setModelName",
            "preDetach",
            "postDetach",
            "preAttach",
            "getModelClass",
            "postAttach",
        ]

    with check_taurus_deprecations(caplog, expected=1):
        # trigger call to getModelObj() which is reimplemented for single model
        b.getFullModelName()
        assert b.lastcalls() == ["getModelObj"]

    with check_taurus_deprecations(caplog, expected=0):
        # trigger getModelObj(key="other") which is reimplemented for single
        # model and therefore does not support the key kwarg
        pytest.raises(TypeError, b.getFullModelName, key="other")
        assert b.lastcalls() == []

    b.setModel("eval:123#label")
    assert b.lastcalls() == [
        "setModelCheck",
        "setModelName",
        "preDetach",
        "postDetach",
        "preAttach",
        "getModelClass",
        "postAttach",
    ]

    with check_taurus_deprecations(caplog, expected=1):
        # triggers getModelFragmentObj
        assert b.getDisplayValue() == "abcd"
        assert b.lastcalls() == ["getModelFragmentObj"]


@pytest.mark.forked
def test_foo_model_composer(caplog):
    with check_taurus_deprecations(caplog):
        b = _FooComposer()
        assert b.modelKeys == ["", "foo"]

        n1 = "eval:1"
        a1 = taurus.Attribute(n1)
        fn1 = a1.getFullName()
        n2 = "eval:2"
        a2 = taurus.Attribute(n2)
        fn2 = a2.getFullName()

        # check setModel
        _setModelCheck_mock = MagicMock(wraps=b._setModelCheck)
        _setModelName_mock = MagicMock(wraps=b._setModelName)
        with patch.multiple(
            b,
            preAttach=DEFAULT,
            postAttach=DEFAULT,
            preDetach=DEFAULT,
            postDetach=DEFAULT,
            _setModelCheck=_setModelCheck_mock,
            _setModelName=_setModelName_mock,
        ) as _att:
            b.setModel(n1)
            b.setModel(n2, key="foo")
            assert _setModelCheck_mock.call_args_list == [
                ((n1,), {"key": ""}),
                ((n2,), {"key": "foo"}),
            ]
            assert _setModelName_mock.call_args_list == [
                ((n1,), {"parent": None, "key": ""}),
                ((n2,), {"parent": None, "key": "foo"}),
            ]
            for m in "preAttach", "postAttach", "preDetach", "postDetach":
                _calls = _att[m].call_args_list
                assert _calls == [({"key": ""},), ({"key": "foo"},)]
            pytest.raises(TypeError, b.setModel, "eval:3", "foo")
            pytest.raises(KeyError, b.setModel, "eval:4", key="bar")

        # check model attributes
        assert b.modelObj is a1
        assert b.modelName == n1
        assert b.modelFragmentName is None

        assert b._modelObj == {"": a1, "foo": a2}

        # check methods
        assert b._findModelClass() is a1.__class__
        assert b._findModelClass(key="") is a1.__class__
        assert b._findModelClass(key="foo") is a2.__class__
        pytest.raises(TypeError, b._findModelClass, "foo")
        pytest.raises(KeyError, b._findModelClass, key="bar")

        assert b.getDisplayValue() == "1"
        assert b.getDisplayValue(key="") == "1"
        assert b.getDisplayValue(key="foo") == "2"
        # pytest.raises(TypeError, b.getDisplayValue, "foo")
        pytest.raises(KeyError, b.getDisplayValue, key="bar")

        assert b.getFullModelName() is fn1
        assert b.getFullModelName(key="") is fn1
        assert b.getFullModelName(key="foo") is fn2
        pytest.raises(TypeError, b.getFullModelName, "foo")
        pytest.raises(KeyError, b.getFullModelName, key="bar")

        assert b.getModel() is n1
        assert b.getModel(key="") is n1
        assert b.getModel(key="foo") is n2
        pytest.raises(TypeError, b.getModel, "foo")
        pytest.raises(KeyError, b.getModel, key="bar")

        assert b.getModelClass() is a1.__class__
        assert b.getModelClass(key="") is a1.__class__
        assert b.getModelClass(key="foo") is a2.__class__
        pytest.raises(TypeError, b.getModelClass, "foo")
        pytest.raises(KeyError, b.getModelClass, key="bar")

        assert b.getModelFragmentObj() is a1.rvalue
        assert b.getModelFragmentObj(key="") is a1.rvalue
        assert b.getModelFragmentObj(key="foo") is a2.rvalue
        # pytest.raises(TypeError, b.getModelFragmentObj, "foo")
        pytest.raises(KeyError, b.getModelFragmentObj, key="bar")

        assert b.getModelName() is n1
        assert b.getModelName(key="") is n1
        assert b.getModelName(key="foo") is n2
        pytest.raises(TypeError, b.getModelName, "foo")
        pytest.raises(KeyError, b.getModelName, key="bar")

        assert b.getModelObj() is a1
        assert b.getModelObj(key="") is a1
        assert b.getModelObj(key="foo") is a2
        pytest.raises(TypeError, b.getModelObj, "foo")
        pytest.raises(KeyError, b.getModelObj, key="bar")

        assert b.getModelType() is TaurusElementType.Attribute
        assert b.getModelType(key="") is TaurusElementType.Attribute
        assert b.getModelType(key="foo") is TaurusElementType.Attribute
        pytest.raises(TypeError, b.getModelType, "foo")
        pytest.raises(KeyError, b.getModelType, key="bar")

        assert b.getModelValueObj() is a1.read()
        assert b.getModelValueObj(key="") is a1.read()
        assert b.getModelValueObj(key="foo") is a2.read()
        # pytest.raises(TypeError, b.getModelValueObj, "foo")
        pytest.raises(KeyError, b.getModelValueObj, key="bar")

        assert b.isAttached() is True
        assert b.isAttached(key="") is True
        assert b.isAttached(key="foo") is True
        pytest.raises(TypeError, b.isAttached, "foo")
        pytest.raises(KeyError, b.isAttached, key="bar")


@pytest.mark.forked
def test_model_container(caplog):
    with check_taurus_deprecations(caplog):
        b = _Container()

        n0 = "eval:0"
        a0 = taurus.Attribute(n0)
        fn0 = a0.getFullName()
        n1 = "eval:1"
        a1 = taurus.Attribute(n1)
        fn1 = a1.getFullName()

        assert b.modelKeys == [MLIST]

        # check setModel
        _setModelCheck_mock = MagicMock(wraps=b._setModelCheck)
        _setModelName_mock = MagicMock(wraps=b._setModelName)
        with patch.multiple(
            b,
            preAttach=DEFAULT,
            postAttach=DEFAULT,
            preDetach=DEFAULT,
            postDetach=DEFAULT,
            _setModelCheck=_setModelCheck_mock,
            _setModelName=_setModelName_mock,
        ) as _att:
            b.setModel([n0, n1])
            assert _setModelCheck_mock.call_args_list == [
                (([n0, n1],), {"key": MLIST}),
                ((n0,), {"key": (MLIST, 0)}),
                ((n1,), {"key": (MLIST, 1)}),
            ]
            assert _setModelName_mock.call_args_list == [
                ((n0,), {"parent": None, "key": (MLIST, 0)}),
                ((n1,), {"parent": None, "key": (MLIST, 1)}),
            ]
            for m in "preAttach", "postAttach", "preDetach", "postDetach":
                _calls = _att[m].call_args_list
                assert _calls == [
                    ({"key": (MLIST, 0)},),
                    ({"key": (MLIST, 1)},),
                ]

        # check model attributes
        assert b.modelObj is None
        assert b.modelName == (n0, n1)
        assert b.modelFragmentName is None

        assert b._modelObj == {MLIST: None, (MLIST, 0): a0, (MLIST, 1): a1}
        assert b._modelName == {
            MLIST: (n0, n1),
            (MLIST, 0): n0,
            (MLIST, 1): n1,
        }
        assert b._attached == {
            MLIST: False,
            (MLIST, 0): True,
            (MLIST, 1): True,
        }

        # check methods
        assert b._findModelClass() is None
        assert b._findModelClass(key=MLIST) is None
        assert b._findModelClass(key=(MLIST, 0)) is a0.__class__
        assert b._findModelClass(key=(MLIST, 1)) is a1.__class__
        pytest.raises(KeyError, b._findModelClass, key="")
        pytest.raises(KeyError, b._findModelClass, key=(MLIST, 99))

        assert b.getDisplayValue() == b.noneValue
        assert b.getDisplayValue(key=MLIST) == b.noneValue
        assert b.getDisplayValue(key=(MLIST, 0)) == "0"
        assert b.getDisplayValue(key=(MLIST, 1)) == "1"
        pytest.raises(KeyError, b.getDisplayValue, key="")
        pytest.raises(KeyError, b.getDisplayValue, key=(MLIST, 99))

        assert b.getFullModelName() is None  # TODO: should be (fn0, fn1)?
        assert b.getFullModelName(key=MLIST) is None
        assert b.getFullModelName(key=(MLIST, 0)) is fn0
        assert b.getFullModelName(key=(MLIST, 1)) is fn1
        pytest.raises(TypeError, b.getFullModelName, "")
        pytest.raises(KeyError, b.getFullModelName, key=(MLIST, 99))

        assert b.getModel() == (n0, n1)
        assert b.getModel(key=MLIST) == (n0, n1)
        assert b.getModel(key=(MLIST, 0)) is n0
        assert b.getModel(key=(MLIST, 1)) is n1
        pytest.raises(TypeError, b.getModel, "")
        pytest.raises(KeyError, b.getModel, key=(MLIST, 99))

        assert b.getModelClass() is None
        assert b.getModelClass(key=MLIST) is None
        assert b.getModelClass(key=(MLIST, 0)) is a0.__class__
        assert b.getModelClass(key=(MLIST, 1)) is a1.__class__
        pytest.raises(TypeError, b.getModelClass, "")
        pytest.raises(KeyError, b.getModelClass, key=(MLIST, 99))

        assert b.getModelFragmentObj() is None
        assert b.getModelFragmentObj(key=MLIST) is None
        assert b.getModelFragmentObj(key=(MLIST, 0)) is a0.rvalue
        assert b.getModelFragmentObj(key=(MLIST, 1)) is a1.rvalue
        pytest.raises(KeyError, b.getModelFragmentObj, key=(MLIST, 99))

        assert b.getModelName() == (n0, n1)
        assert b.getModelName(key=MLIST) == (n0, n1)
        assert b.getModelName(key=(MLIST, 0)) is n0
        assert b.getModelName(key=(MLIST, 1)) is n1
        pytest.raises(TypeError, b.getModelName, "")
        pytest.raises(KeyError, b.getModelName, key=(MLIST, 99))

        assert b.getModelObj() is None
        assert b.getModelObj(key=MLIST) is None
        assert b.getModelObj(key=(MLIST, 0)) is a0
        assert b.getModelObj(key=(MLIST, 1)) is a1
        pytest.raises(TypeError, b.getModelObj, "")
        pytest.raises(KeyError, b.getModelObj, key=(MLIST, 99))

        assert b.getModelType() == TaurusElementType.Unknown
        assert b.getModelType(key=MLIST) == TaurusElementType.Unknown
        assert b.getModelType(key=(MLIST, 0)) is TaurusElementType.Attribute
        assert b.getModelType(key=(MLIST, 1)) is TaurusElementType.Attribute
        pytest.raises(TypeError, b.getModelType, "")
        pytest.raises(KeyError, b.getModelType, key=(MLIST, 99))

        assert b.getModelValueObj() is None
        assert b.getModelValueObj(key=MLIST) is None
        assert b.getModelValueObj(key=(MLIST, 0)) is a0.read()
        assert b.getModelValueObj(key=(MLIST, 1)) is a1.read()
        # pytest.raises(TypeError, b.getModelValueObj, "")
        pytest.raises(KeyError, b.getModelValueObj, key=(MLIST, 99))

        assert b.isAttached() is False
        assert b.isAttached(key=MLIST) is False
        assert b.isAttached(key=(MLIST, 0)) is True
        assert b.isAttached(key=(MLIST, 1)) is True
        pytest.raises(TypeError, b.isAttached, "")
        pytest.raises(KeyError, b.isAttached, key=(MLIST, 99))

        # check creation/replacement/deletion of keys
        b.setModel([n0])
        assert b.modelKeys == [MLIST, (MLIST, 0)]
        b.setModel([])
        assert b.modelKeys == [MLIST]
        b.setModel([n1])
        assert b.modelKeys == [MLIST, (MLIST, 0)]
        b.setModel([n1, n0, n1, n0, n1])
        assert b.modelKeys == [MLIST] + [(MLIST, i) for i in range(5)]
        b.setModel([n1, n0])
        assert b.modelKeys == [MLIST, (MLIST, 0), (MLIST, 1)]
        assert b.getModel() == (n1, n0)
