from datetime import datetime

from taurus.core import TaurusEventType
from taurus.external.qt import Qt
from taurus.qt.qtgui.application import TaurusApplication
from taurus.qt.qtgui.base import TaurusBaseComponent


class EventLogger(Qt.QTextEdit, TaurusBaseComponent):
    """A taurus-ified QTextEdit widget that logs events received
    from an arbitrary list of taurus attributes
    """

    modelKeys = [TaurusBaseComponent.MLIST]

    def __init__(self, parent=None):
        super(EventLogger, self).__init__(parent=parent)
        self.setMinimumWidth(800)

    def handleEvent(self, evt_src, evt_type, evt_value):
        """reimplemented from TaurusBaseComponent"""
        line = "{}\t[{}]\t{}".format(
            datetime.now(),
            TaurusEventType.whatis(evt_type),
            evt_src.getFullName(),
        )
        self.append(line)


if __name__ == "__main__":
    import sys

    app = TaurusApplication()
    w = EventLogger()
    w.setModel(["eval:123", "tango:sys/tg_test/1/short_scalar", "eval:rand()"])
    w.show()
    sys.exit(app.exec_())
