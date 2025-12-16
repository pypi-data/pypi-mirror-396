from taurus.qt.qtgui.input import TaurusValueComboBox


class TangoValueComboBox(TaurusValueComboBox):
    def __init__(self, parent=None, designMode=False):
        super().__init__(parent, designMode)
        self.initComboBoxHandled = False

    def handleEvent(self, src, evt_type, evt_value):
        if not self.initComboBoxHandled and evt_value is not None:
            self.initComboBoxHandled = True
            self.setCurrentIndex(evt_value.wvalue)
        super().handleEvent(src, evt_type, evt_value)

    def setModel(self, model, **kwargs):
        if model is None or model == "":
            return
        super().setModel(model, **kwargs)
        modelObj = self.taurusValueBuddy().getModelObj()
        self.setValueNames((name, i) for i, name in enumerate(modelObj.enum_labels))
