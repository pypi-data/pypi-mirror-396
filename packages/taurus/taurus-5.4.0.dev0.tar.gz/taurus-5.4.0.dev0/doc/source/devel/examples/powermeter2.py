from taurus.external.qt import Qt
from taurus.qt.qtgui.application import TaurusApplication
from taurus.qt.qtgui.base import TaurusBaseComponent


class PowerMeter2(Qt.QProgressBar, TaurusBaseComponent):
    """A Taurus-ified QProgressBar with separate models for value and color"""

    # setFormat() defined by both TaurusBaseComponent and QProgressBar. Rename.
    setFormat = TaurusBaseComponent.setFormat
    setBarFormat = Qt.QProgressBar.setFormat

    modelKeys = ["power", "color"]  # support 2 models (default key is "power")
    _template = "QProgressBar::chunk {background: %s}"  # stylesheet template

    def __init__(self, parent=None, value_range=(0, 100)):
        super(PowerMeter2, self).__init__(parent=parent)
        self.setOrientation(Qt.Qt.Vertical)
        self.setRange(*value_range)
        self.setTextVisible(False)

    def handleEvent(self, evt_src, evt_type, evt_value):
        """reimplemented from TaurusBaseComponent"""
        try:
            if evt_src is self.getModelObj(key="power"):
                self.setValue(int(evt_value.rvalue.m))
            elif evt_src is self.getModelObj(key="color"):
                self.setStyleSheet(self._template % evt_value.rvalue)
        except Exception as e:
            self.info("Skipping event. Reason: %s", e)


if __name__ == "__main__":
    import sys

    app = TaurusApplication()
    w = PowerMeter2()
    w.setModel("eval:Q(60+20*rand())")  # implicit use of  key="power"
    w.setModel("eval:['green','red','blue'][randint(3)]", key="color")
    w.show()
    sys.exit(app.exec_())
