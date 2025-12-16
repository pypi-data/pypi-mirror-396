from taurus.external.qt import Qt
from taurus.qt.qtgui.application import TaurusApplication
from taurus.qt.qtgui.base import MLIST, TaurusBaseComponent
from taurus.qt.qtgui.display import TaurusLabel


class SimpleForm(Qt.QWidget, TaurusBaseComponent):
    """A simple taurus form using the model list support from
    TaurusBaseComponent.
    """

    modelKeys = [MLIST]

    def __init__(self, parent=None):
        super(SimpleForm, self).__init__(parent=parent)
        self.setLayout(Qt.QFormLayout(self))

    def setModel(self, model, *, key=MLIST):
        """reimplemented from TaurusBaseComponent"""
        TaurusBaseComponent.setModel(self, model, key=key)
        _ly = self.layout()

        if key is MLIST:  # (re)create all rows
            # remove existing rows
            while _ly.rowCount():
                _ly.removeRow(0)
            # create new rows
            for i, name in enumerate(model):
                simple_name = self.getModelObj(key=(MLIST, i)).getSimpleName()
                value_label = TaurusLabel()
                value_label.setModel(name)
                _ly.addRow(simple_name, value_label)
        else:  # update a single existing row
            _, row = key  # key must be of the form (MLIST, <i>)
            name_label = _ly.itemAt(row, _ly.ItemRole.LabelRole).widget()
            value_label = _ly.itemAt(row, _ly.ItemRole.FieldRole).widget()
            name_label.setText(self.getModelObj(key=key).getSimpleName())
            value_label.setModel(self.getModelName(key=key))


if __name__ == "__main__":
    import sys

    app = TaurusApplication()
    w = SimpleForm()
    w.setModel(
        [
            "eval:foo=123;foo",
            "eval:randint(99)",
            "sys/tg_test/1/short_scalar",
            "eval:randint(99)",
        ]
    )
    w.show()
    sys.exit(app.exec_())
