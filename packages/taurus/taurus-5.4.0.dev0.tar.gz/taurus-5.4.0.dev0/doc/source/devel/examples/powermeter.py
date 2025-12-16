from taurus.external.qt import Qt
from taurus.qt.qtgui.application import TaurusApplication
from taurus.qt.qtgui.base import TaurusBaseComponent


class PowerMeter(Qt.QProgressBar, TaurusBaseComponent):
    """A Taurus-ified QProgressBar"""

    # setFormat() defined by both TaurusBaseComponent and QProgressBar. Rename.
    setFormat = TaurusBaseComponent.setFormat
    setBarFormat = Qt.QProgressBar.setFormat

    def __init__(self, parent=None, value_range=(0, 100)):
        super(PowerMeter, self).__init__(parent=parent)
        self.setOrientation(Qt.Qt.Vertical)
        self.setRange(*value_range)
        self.setTextVisible(False)

    def handleEvent(self, evt_src, evt_type, evt_value):
        """reimplemented from TaurusBaseComponent"""
        try:
            self.setValue(int(evt_value.rvalue.m))
        except Exception as e:
            self.info("Skipping event. Reason: %s", e)


if __name__ == "__main__":
    import sys

    app = TaurusApplication()
    w = PowerMeter()
    w.setModel("eval:Q(60+20*rand())")
    w.show()
    sys.exit(app.exec_())
