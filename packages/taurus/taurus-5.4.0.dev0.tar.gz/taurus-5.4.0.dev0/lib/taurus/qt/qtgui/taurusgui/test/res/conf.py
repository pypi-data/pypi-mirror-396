"""TaurusGui configuration file for tests"""

from taurus.qt.qtgui.taurusgui import utils

p1 = utils.PanelDescription(
    "testpanel1",
    classname="taurus.qt.qtgui.panel:TaurusForm",
    model=["eval:1"],
    widget_properties={"withButtons": False, "foobar": 34},
    widget_qt_properties={"toolTip": "test tooltip", "qt_foobar": 34},
)
