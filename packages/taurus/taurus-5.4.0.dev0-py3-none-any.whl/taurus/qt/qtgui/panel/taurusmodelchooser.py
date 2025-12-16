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

"""
AttributeChooser.py: widget for choosing (a list of) attributes from a tango DB
"""

import sys

import pkg_resources

import taurus
import taurus.core
from taurus.core.util.containers import CaselessList
from taurus.external.qt import Qt, QtCore
from taurus.external.qt.compat import PY_OBJECT
from taurus.qt.qtgui.container import TaurusWidget
from taurus.qt.qtgui.panel.taurusmodellist import TaurusModelList
from taurus.qt.qtgui.tree import TaurusDbTreeWidget


class TaurusModelSelector(Qt.QTabWidget):
    """TaurusModelSelector is a QTabWidget container for
    TaurusModelSelectorItem.
    """

    # TODO add action to add new TaurusModelSelectorItem
    # TODO add mechanism to allow manual plugin activation
    #      (instead of relying on installation)
    modelsAdded = Qt.pyqtSignal(PY_OBJECT)

    def __init__(self, parent=None):
        Qt.QTabWidget.__init__(self, parent=parent)

        self.currentChanged.connect(self.__setTabItemModel)
        # ---------------------------------------------------------------------
        # Note: this is an experimental feature
        # It may be removed or changed in future releases
        # Discover the taurus.modelselector plugins
        ep_group_name = "taurus.model_selector.items"
        for ep in pkg_resources.iter_entry_points(ep_group_name):
            try:
                ms_class = ep.load()
                ms_item = ms_class(parent=self)
                self.__addItem(ms_item, ep.name)

            except Exception as e:
                err = "Invalid TaurusModelSelectorItem plugin: {}\n{}".format(
                    ep.module_name, e
                )
                taurus.warning(err)
        # ---------------------------------------------------------------------

    def __setTabItemModel(self):
        w = self.currentWidget()
        c = self.cursor()
        try:
            if not w.model:
                self.setCursor(QtCore.Qt.WaitCursor)
                w.setModel(w.default_model)
        except Exception as e:
            taurus.warning("Problem setting up selector: %r", e)
        finally:
            self.setCursor(c)

    def __addItem(self, widget, name, model=None):
        if model is not None:
            widget.default_model = model

        widget.modelsAdded.connect(self.modelsAdded)
        self.addTab(widget, name)


class TaurusModelSelectorItem(TaurusWidget):
    """Base class for ModelSelectorItem.
    It defines the minimal API to be defined in the specialization
    """

    modelsAdded = Qt.pyqtSignal(PY_OBJECT)
    _dragEnabled = True
    # TODO add action for setModel

    def __init__(self, parent=None, **kwargs):
        TaurusWidget.__init__(self, parent)
        self._default_model = None

    def getSelectedModels(self):
        raise NotImplementedError(
            (
                "getSelectedModels must be implemented"
                + " in TaurusModelSelectorItem subclass"
            )
        )

    def getModelMimeData(self):
        """Reimplemented from TaurusBaseComponent"""
        models = self.getSelectedModels()
        md = Qt.QMimeData()
        # md.setText(", ".join(models))
        md.setText(" ".join(models))
        models_bytes = [bytes(m, encoding="utf-8") for m in models]
        md.setData(
            taurus.qt.qtcore.mimetypes.TAURUS_MODEL_LIST_MIME_TYPE,
            b"\r\n".join(models_bytes),
        )
        return md

    def _get_default_model(self):
        """
        Reimplement to return a default model to initialize the widget
        """
        raise NotImplementedError(
            (
                "default_model must be implemented"
                + " in TaurusModelSelectorItem subclass"
            )
        )

    def _set_default_model(self, model):
        """
        Set default model to initialize the widget
        """
        self._default_model = model

    # Reimplement this property
    default_model = property(fget=_get_default_model, fset=_set_default_model)


class TaurusModelSelectorTree(TaurusModelSelectorItem):
    addModels = Qt.pyqtSignal("QStringList")
    UpdateAttrs = Qt.pyqtSignal((list))

    def __init__(self, parent=None, selectables=None, buttonsPos=None, designMode=None):
        TaurusModelSelectorItem.__init__(self, parent)
        if selectables is None:
            selectables = [
                taurus.core.taurusbasetypes.TaurusElementType.Attribute,
                taurus.core.taurusbasetypes.TaurusElementType.Member,
                taurus.core.taurusbasetypes.TaurusElementType.Device,
            ]
        self._selectables = selectables
        self._allowDuplicates = False

        # tree
        self._deviceTree = TaurusDbTreeWidget(
            perspective=taurus.core.taurusbasetypes.TaurusElementType.Device
        )
        self._deviceTree.getQModel().setSelectables(self._selectables)

        self.setSingleModelMode(False)

        self._list = TaurusModelList()
        self._list.setSelectionMode(Qt.QAbstractItemView.ExtendedSelection)
        applyBT = Qt.QToolButton()
        applyBT.setToolButtonStyle(Qt.Qt.ToolButtonTextBesideIcon)
        applyBT.setText("Apply")
        applyBT.setIcon(Qt.QIcon("status:available.svg"))

        # toolbar
        self._toolbar = Qt.QToolBar("TangoSelector toolbar")
        self._toolbar.setIconSize(Qt.QSize(16, 16))
        self._toolbar.setFloatable(False)
        self._addSelectedAction = self._toolbar.addAction(
            Qt.QIcon.fromTheme("list-add"), "Add selected", self.onAddSelected
        )
        self._toolbar.addAction(self._list.removeSelectedAction)
        self._toolbar.addAction(self._list.removeAllAction)
        self._toolbar.addAction(self._list.moveUpAction)
        self._toolbar.addAction(self._list.moveDownAction)
        self._toolbar.addSeparator()
        self._toolbar.addWidget(applyBT)

        # defines the layout
        self.setButtonsPos(buttonsPos)

        self.modelChanged.connect(self._deviceTree.setModel)
        applyBT.clicked.connect(self._onUpdateModels)

    def setButtonsPos(self, buttonsPos):
        # we must delete the previous layout before we can set a new one
        currlayout = self.layout()
        if currlayout is not None:
            currlayout.deleteLater()
            Qt.QCoreApplication.sendPostedEvents(currlayout, Qt.QEvent.DeferredDelete)
        # add to layout
        if buttonsPos is None:
            self.setLayout(Qt.QVBoxLayout())
            self.layout().addWidget(self._deviceTree)
        elif buttonsPos == Qt.Qt.BottomToolBarArea:
            self._toolbar.setOrientation(Qt.Qt.Horizontal)
            self.setLayout(Qt.QVBoxLayout())
            self.layout().addWidget(self._deviceTree)
            self.layout().addWidget(self._toolbar)
            self.layout().addWidget(self._list)
        elif buttonsPos == Qt.Qt.TopToolBarArea:
            self._toolbar.setOrientation(Qt.Qt.Horizontal)
            self.setLayout(Qt.QVBoxLayout())
            self.layout().addWidget(self._toolbar)
            self.layout().addWidget(self._deviceTree)
            self.layout().addWidget(self._list)
            self.layout().addWidget(self._deviceTree)
        elif buttonsPos == Qt.Qt.LeftToolBarArea:
            self._toolbar.setOrientation(Qt.Qt.Vertical)
            self.setLayout(Qt.QHBoxLayout())
            self.layout().addWidget(self._list)
            self.layout().addWidget(self._toolbar)
            self.layout().addWidget(self._deviceTree)

        elif buttonsPos == Qt.Qt.RightToolBarArea:
            self._toolbar.setOrientation(Qt.Qt.Vertical)
            self.setLayout(Qt.QHBoxLayout())
            self.layout().addWidget(self._deviceTree)
            self.layout().addWidget(self._toolbar)
            self.layout().addWidget(self._list)
        else:
            raise ValueError("Invalid buttons position")

    def getSelectedModels(self):
        selected = []
        try:
            from taurus.core.tango.tangodatabase import (
                TangoAttrInfo,
                TangoDevInfo,
            )
        except Exception:
            return selected
        for item in self._deviceTree.selectedItems():
            nfo = item.itemData()
            if isinstance(nfo, TangoDevInfo):
                selected.append(nfo.fullName())
            elif isinstance(nfo, TangoAttrInfo):
                selected.append("%s/%s" % (nfo.device().fullName(), nfo.name()))
            else:
                self.info("Unknown item '%s' in selection" % repr(nfo))
        return selected

    def onAddSelected(self):
        self.addModelsToList(self.getSelectedModels())

    def treeView(self):
        return self._deviceTree.treeView()

    def getListedModels(self):
        """returns the list of models that have been added

        :param asMimeData: If False (default), the return value will be a list
            of models. If True, the return value is a `QMimeData` containing at
            least `TAURUS_MODEL_LIST_MIME_TYPE` and `text/plain` MIME types. If
            only one model was selected, the mime data also contains a
            TAURUS_MODEL_MIME_TYPE.
        :type asMimeData: bool
        :return: the type of return depends on the value of `asMimeData`
        :rtype: list<str> or QMimeData
        """
        models = self._list.getModelList()
        if self.isSingleModelMode():
            models = models[:1]
        return models

    def setListedModels(self, models):
        """Adds the given list of models to the widget list"""
        self._list.model().clearAll()
        self._list.addModels(models)

    def resetListedModels(self):
        """Equivalent to setListedModels([])"""
        self._list.model().clearAll()

    def addModelsToList(self, models):
        """Add given models to the selected models list"""
        if len(models) == 0:
            models = [""]
        if self.isSingleModelMode():
            self.resetListedModels()
        if self._allowDuplicates:
            self._list.addModels(models)
        else:
            listedmodels = CaselessList(self.getListedModels())
            for m in models:
                if m not in listedmodels:
                    listedmodels.append(m)
                    self._list.addModels([m])

    def _onUpdateModels(self):
        models = self.getListedModels()
        self.modelsAdded.emit(models)
        if taurus.core.taurusbasetypes.TaurusElementType.Attribute in self._selectables:
            self.UpdateAttrs.emit(models)

    def setSingleModelMode(self, single):
        """sets whether the selection should be limited to just one model
        (single=True) or not (single=False)
        """
        if single:
            self.treeView().setSelectionMode(Qt.QAbstractItemView.SingleSelection)
        else:
            self.treeView().setSelectionMode(Qt.QAbstractItemView.ExtendedSelection)
        self._singleModelMode = single

    def isSingleModelMode(self):
        """Returns True if the selection is limited to just one model. Returns
        False otherwise.

        :return:
        :rtype: bool
        """
        return self._singleModelMode

    def resetSingleModelMode(self):
        """Equivalent to setSingleModelMode(False)"""
        self.setSingleModelMode(self, False)

    @classmethod
    def getQtDesignerPluginInfo(cls):
        ret = TaurusWidget.getQtDesignerPluginInfo()
        ret["module"] = "taurus.qt.qtgui.panel"
        ret["icon"] = "designer:listview.png"
        ret["container"] = False
        ret["group"] = "Taurus Views"
        return ret


class TangoModelSelectorItem(TaurusModelSelectorTree):
    """A taurus model selector item for Tango models"""

    # TODO: Tango-centric (move to Taurus-Tango plugin)
    def __init__(
        self,
        parent=None,
        selectables=None,
        buttonsPos=Qt.Qt.BottomToolBarArea,
        designMode=None,
    ):
        TaurusModelSelectorTree.__init__(
            self,
            parent=parent,
            selectables=selectables,
            buttonsPos=buttonsPos,
            designMode=designMode,
        )

    def _get_default_model(self):
        """Reimplemented from TaurusModelSelectorItem"""
        if self._default_model is None:
            f = taurus.Factory("tango")
            self._default_model = f.getAuthority().getFullName()
        return self._default_model

    default_model = property(
        fget=_get_default_model,
        fset=TaurusModelSelectorTree._set_default_model,
    )


class TaurusModelChooser(TaurusWidget):
    """A widget that allows the user to select a list of models from a tree
    representing devices and attributes from a Tango server.

    The user selects models and adds them to a list. Then the user should click
    on the update button to notify that the selection is ready.

    signals::
      - "updateModels"  emitted when the user clicks on the update button. It
        passes a list<str> of models that have been selected.
    """

    updateModels = Qt.pyqtSignal("QStringList")
    UpdateAttrs = Qt.pyqtSignal(["QStringList"], ["QMimeData"])

    def __init__(
        self,
        parent=None,
        selectables=None,
        host=None,
        designMode=None,
        singleModel=False,
    ):
        """Creator of TaurusModelChooser

        :param parent: parent for the dialog
        :type parent: QObject
        :param selectables: if passed, only elements of the tree whose type is
            in the list will be selectable.
        :type selectables: list<TaurusElementType>
        :param host: Tango host to be explored by the chooser
        :type host: QObject
        :param designMode: needed for taurusdesigner but ignored here
        :type designMode: bool
        :param singleModel: If True, the selection will be of just one model.
            Otherwise (default) a list of models can be selected
        :type singleModel: bool
        """
        TaurusWidget.__init__(self, parent)

        if host is None:
            try:  # TODO: Tango-centric!
                host = taurus.Factory("tango").getAuthority().getFullName()
            except Exception as e:
                taurus.info("Cannot populate Tango Tree: %r", e)

        self._selectedModels = []
        self.setLayout(Qt.QVBoxLayout())

        self.tree = TaurusModelSelectorTree(
            selectables=selectables, buttonsPos=Qt.Qt.BottomToolBarArea
        )
        self.tree.setModel(host)
        self.tree.setSingleModelMode(singleModel)

        self.layout().addWidget(self.tree)

        # Workaround for UseSetParentModel issues
        self.modelChanged.connect(self.tree.setModel)

        # connections:
        self.tree.modelsAdded.connect(self._onUpdateModels)

    def setListedModels(self, models):
        """Adds the given list of models to the widget list"""
        self.tree.setListedModels(models)

    def resetListedModels(self):
        """equivalent to setListedModels([])"""
        self.tree.resetListedModels()

    def updateList(self, attrList):
        """for backwards compatibility with AttributeChooser only. Use
        :meth:`setListedModels` instead
        """
        self.info(
            "ModelChooser.updateList() is provided for "
            + "backwards compatibility only. Use setListedModels() instead"
        )
        self.setListedModels(attrList)

    def getSelectedModels(self):
        """
        Returns selected models that are in TaurusModelLIst in TaurusModelSelectorTree
        """
        return self._selectedModels

    def _onUpdateModels(self, models):
        """
        Function necessary for standalone execution.
        It stores selected models and emits a signal notifying
        about the end of selecting
        """
        self._selectedModels = models
        self.updateModels.emit(self._selectedModels)

    def setSingleModelMode(self, single):
        """Sets whether the selection should be limited to just one model
        (single=True) or not (single=False)
        """
        self.tree.setSingleModelMode(single)

    def isSingleModelMode(self):
        """Returns True if the selection is limited to just one model. Returns
        False otherwise.

        :return:
        :rtype: bool
        """
        return self.tree.isSingleModelMode()

    def resetSingleModelMode(self):
        """Equivalent to setSingleModelMode(False)"""
        self.tree.resetSingleModelMode()

    @staticmethod
    def modelChooserDlg(
        parent=None,
        selectables=None,
        host=None,
        asMimeData=False,
        singleModel=False,
        windowTitle="Model Chooser",
        listedModels=None,
    ):
        """Static method that launches a modal dialog containing a
        TaurusModelChooser

        :param parent: parent for the dialog
        :type parent: QObject
        :param selectables: if passed, only elements of the tree whose type is
            in the list will be selectable.
        :type selectables: list<TaurusElementType>
        :param host: Tango host to be explored by the chooser
        :type host: QObject
        :param asMimeData: If False (default),  a list of models will be.
            returned. If True, a `QMimeData` object will be returned instead.
            See :meth:`getListedModels` for a detailed description of this
            QMimeData object.
        :type asMimeData: bool
        :param singleModel: If True, the selection will be of just one model.
            Otherwise (default) a list of models can be selected
        :type singleModel: bool
        :param windowTitle: Title of the dialog (default="Model Chooser")
        :type windowTitle: str
        :param listedModels: List of model names for initializing the model
            list
        :type listedModels: list<str>
        :return: Returns a models,ok tuple. models can be either a list of
            models or a QMimeData object, depending on `asMimeData`. ok is True
            if the dialog was accepted (by clicking on the "update" button) and
            False otherwise
        :rtype: list,bool or QMimeData,bool
        """
        dlg = Qt.QDialog(parent)
        dlg.setWindowTitle(windowTitle)
        dlg.setWindowIcon(Qt.QIcon("logos:taurus.png"))
        layout = Qt.QVBoxLayout()
        w = TaurusModelChooser(
            parent=parent,
            selectables=selectables,
            host=host,
            singleModel=singleModel,
        )
        if listedModels is not None:
            w.setListedModels(listedModels)
        layout.addWidget(w)
        dlg.setLayout(layout)
        w.updateModels.connect(dlg.accept)
        dlg.exec_()

        models = w.getSelectedModels()
        return w._asMimeData(models) if asMimeData else models, (
            dlg.result() == dlg.Accepted
        )

    def _asMimeData(self, models):
        md = Qt.QMimeData()
        md.setData(
            taurus.qt.qtcore.mimetypes.TAURUS_MODEL_LIST_MIME_TYPE,
            bytes("\r\n".join(models), encoding="utf8"),
        )
        md.setText(", ".join(models))
        if len(models) == 1:
            md.setData(
                taurus.qt.qtcore.mimetypes.TAURUS_MODEL_MIME_TYPE,
                bytes(models[0], encoding="utf8"),
            )
        return md

    @classmethod
    def getQtDesignerPluginInfo(cls):
        ret = TaurusWidget.getQtDesignerPluginInfo()
        ret["module"] = "taurus.qt.qtgui.panel"
        ret["icon"] = "designer:listview.png"
        ret["container"] = False
        ret["group"] = "Taurus Views"
        return ret

    singleModelMode = Qt.pyqtProperty(
        "bool", isSingleModelMode, setSingleModelMode, resetSingleModelMode
    )


def main(args):
    if len(sys.argv) > 1:
        host = sys.argv[1]
    else:
        host = None

    _ = Qt.QApplication(args)
    print(TaurusModelChooser.modelChooserDlg(host=host))
    sys.exit()


if __name__ == "__main__":
    main(sys.argv)
