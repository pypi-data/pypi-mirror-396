import os

import pytest

from taurus.external.qt import PYSIDE2
from taurus.qt.qtgui.taurusgui import TaurusGui


@pytest.mark.xfail(PYSIDE2, reason="This test is known to fail with PySide2")
@pytest.mark.forked
def test_paneldescription(qtbot):
    conf = os.path.join(os.path.dirname(__file__), "res", "conf.py")
    with open(conf) as conf_file:
        gui = TaurusGui(confname=conf_file.name, configRecursionDepth=0)

    gui.SAVE_SETTINGS_ON_CLOSE = False  # avoid interactive prompt during test
    w1 = gui.getPanel("testpanel1").widget()
    qtbot.addWidget(gui)
    qtbot.addWidget(w1)
    assert w1.withButtons is False
    assert w1.isWithButtons() is False
    assert not hasattr(w1, "foobar")
    assert w1.toolTip() == "test tooltip"
    assert not hasattr(w1, "qt_foobar")
    assert w1.modifiableByUser is False
