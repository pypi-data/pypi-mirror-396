import pytest

import taurus
from taurus.core.units import UR
from taurus.external.qt import PYSIDE2
from taurus.qt.qtgui.input import TaurusValueComboBox

try:
    # The following are Tango-centric imports.
    from taurus.core.tango.test import nodb_dev  # noqa: F401

    _TANGO_MISSING = False
except Exception:
    _TANGO_MISSING = True


@pytest.mark.parametrize(
    "model,names,value,expected",
    [
        # test with quantities
        (
            "eval:@taurus.core.evaluation.test.res.mymod.MyClass()/self.foo",
            [("A", 1234), ("B", "123"), ("C", 123 * UR.mm), ("E", -123)],
            123 * UR.mm,
            "C",
        ),
        # test with a boolean
        (
            "/boolean_scalar",
            [("N", None), ("F", False), ("T", True)],
            False,
            "F",
        ),
        # test with a boolean spectrum
        (
            "/boolean_spectrum",
            [
                ("A", False),
                ("B", [False, False, False]),
                ("C", [False, True, False]),
            ],
            [False, True, False],
            "C",
        ),
        # test with a string
        (
            "/string_scalar",
            [("A", "foobarbaz"), ("B", "FOOBAR"), ("C", "foobar")],
            "foobar",
            "C",
        ),
        # test non  -match
        (
            "/string_scalar",
            [("A", "foobarbaz"), ("B", "FOOBAR"), ("C", "foobar")],
            "foo",
            "",
        ),
    ],
)
@pytest.mark.forked
def test_TaurusValueCombobox(
    qtbot,
    nodb_dev,  # noqa: F811
    model,
    names,
    value,
    expected,
):
    """Check that the TaurusValueComboBox is started with the right display
    See https://gitlab.com/taurus-org/taurus/-/merge_requests/1032
    """
    if model.startswith("/"):
        model = nodb_dev + model
    a = taurus.Attribute(model)
    a.write(value)
    w = TaurusValueComboBox()
    qtbot.addWidget(w)
    # ----------------------------------
    # workaround: avoid PySide2 segfaults when adding quantity to combobox
    # https://bugreports.qt.io/browse/PYSIDE-683
    if isinstance(value, UR.Quantity) and PYSIDE2:
        pytest.skip("avoid segfault due to PYSIDE-683 bug")
    # ----------------------------------
    w.addValueNames(names)
    qtbot.wait_until(lambda: w.count() == len(names), timeout=3200)
    try:
        with qtbot.waitSignal(w.valueChangedSignal, timeout=3200):
            w.setModel(model)
        assert w.currentText() == expected
    finally:
        del a
        # set model to None as an attempt to avoid problems in atexit()
        with qtbot.waitSignal(w.valueChangedSignal, timeout=3200):
            w.setModel(None)
