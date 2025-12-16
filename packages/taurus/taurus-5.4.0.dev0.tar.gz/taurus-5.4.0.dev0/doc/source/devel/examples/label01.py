import sys

from taurus.external.qt import Qt
from taurus.qt.qtgui.application import TaurusApplication
from taurus.qt.qtgui.display import TaurusLabel

app = TaurusApplication(sys.argv, cmd_line_parser=None)
panel = Qt.QWidget()
layout = Qt.QHBoxLayout()
panel.setLayout(layout)


w = TaurusLabel()
layout.addWidget(w)
w.model = "sys/tg_test/1/double_scalar#rvalue.magnitude"

panel.show()
sys.exit(app.exec_())
