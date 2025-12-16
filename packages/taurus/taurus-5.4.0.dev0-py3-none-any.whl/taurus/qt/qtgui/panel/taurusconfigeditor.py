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
taurusconfigeditor.py:
"""

import os
import pickle
import shutil
import tempfile

import click

from taurus.external.qt import Qt, compat
from taurus.qt.qtcore.configuration import BaseConfigurableClass
from taurus.qt.qtgui.container import TaurusWidget

__docformat__ = "restructuredtext"


class QConfigEditorModel(Qt.QStandardItemModel):
    """A custom Model for QConfigEditor"""

    showError = Qt.pyqtSignal("QString", "QString")

    def __init__(self, parent=None, designMode=False):
        super(QConfigEditorModel, self).__init__(parent)
        self._temporaryFile = None
        self._settings = None
        self._configurationDictionaries = None
        self._modifiedPerspectives = []
        self.originalFile = None
        self.markedItems = []

    def setData(self, index, value, role=Qt.Qt.DisplayRole):
        """see :meth:`Qt.QAbstractTableModel.setData`"""

        idx_data_str = index.data()
        if idx_data_str == value:
            return False
        # self.itemFromIndex(index).setData(value, role)
        try:
            self.valueChanged(value, index)
        except Exception:
            self.showError.emit(
                "Wrong value! The value you entered is wrong. "
                + "The old value will be restored.",
            )
            return Qt.QStandardItemModel.setData(self, index, index.data(), role)
        return Qt.QStandardItemModel.setData(self, index, value, role)

    def loadFile(self, iniFileName):
        """
        Loads file with setting, creates temporary settings file, where changes
        made to configuration are saved.

        :param iniFileName:
        :type iniFileName: str
        """
        self.originalFile = iniFileName
        self._temporaryFile = tempfile.NamedTemporaryFile(delete=False).name
        shutil.copyfile(self.originalFile, self._temporaryFile)

        self._settings = Qt.QSettings(self._temporaryFile, Qt.QSettings.IniFormat)
        self.clear()
        self.setHorizontalHeaderLabels(["Configuration key", "type", "value"])
        self._configurationDictionaries = self.fillTopLevel()
        self.markedItems = []

    def deleteBranch(self):
        """
        Deletes selected branch from the settings tree. Also updates the
        temporary configuration file.
        """
        tmpindex = self._toDeleteIndex
        item = self.itemFromIndex(tmpindex)
        path = item.data(Qt.Qt.UserRole)
        self._delete = False
        self._configurationDictionaries = self.removeBranch(
            self._configurationDictionaries, path
        )

        try:
            group = eval(str(path).split(";", 1)[0])
        except Exception:
            group = str(path).split(";", 1)[0]
        itemToMark = self.itemFromIndex(tmpindex.parent())
        while itemToMark is not None:
            itemToMark.setData(Qt.QFont("Arial", 10, Qt.QFont.Bold), Qt.Qt.FontRole)
            itemToMark = self.itemFromIndex(itemToMark.index().parent())

        self.markedItems.append(self._toDeleteIndex.parent())
        self.removeRow(tmpindex.row(), tmpindex.parent())
        self.saveSettings(group)

    def removeBranch(self, dict, path):
        """
        Method called recursively by self.deleteBranch. In each step it takes
        next key (from the path) until reaches element to be deleted. After the
        element is deleted, returns updated dictionary.

        :param dict: a taurus configuration dictionary. See
            :class:`BaseConfigurableClass`
        :type dict: dict
        :param path: a semicolon-separated string containing the path of the
            branch in the tree
        :type path: str
        :return: the modified config dict
        :rtype: dict
        """
        val = str(path).split(";", 1)
        if len(val) == 2:
            path = val[1]
            try:
                key = eval(val[0])
            except Exception:
                key = val[0]
            dict[key] = self.removeBranch(dict[key], path)
            if self._delete is True:
                if "__orderedConfigNames__" not in dict:
                    return dict
                dict["__orderedConfigNames__"] = self.removeBranch(
                    dict["__orderedConfigNames__"], path
                )
                self._delete = False
            return dict
        else:
            if self._delete is True:
                if dict.count(val[0]) == 0:
                    return dict
                dict.remove(val[0])
                return dict
            if "__orderedConfigNames__" not in dict:
                self._delete = True
            dict.pop(val[0])
            return dict

    def valueChanged(self, value, index):
        """Modifies value in the temporary settings file and the model
        internal dictionary. Invoked by :meth:`Qt.QAbstractTableModel.setData`,
        when user make changes to the value in the settings tree.

        :param value: the new value (a string that will be python-evaluated)
        :type value: str
        :param index: index of the model
        :type index: QModelIndex
        """
        changedItem = self.itemFromIndex(index)
        path = changedItem.data(Qt.Qt.UserRole)
        self._configurationDictionaries = self.changeTreeValue(
            self._configurationDictionaries, path, value
        )
        try:
            group = eval(str(path).split(";", 1)[0])
        except Exception:
            group = str(path).split(";", 1)[0]
        itemToMark = self.itemFromIndex(index.sibling(index.row(), 0))
        self.markedItems.append(itemToMark.index())

        self.itemFromIndex(index.sibling(index.row(), 1)).setText(
            str(type(eval(value)))
        )
        changedItem.setData(
            "Value has been changed. Old value: " + str(changedItem.text()),
            Qt.Qt.ToolTipRole,
        )
        itemToMark.setData(Qt.QIcon.fromTheme("emblem-important"), Qt.Qt.DecorationRole)
        while itemToMark is not None:
            itemToMark.setData(Qt.QFont("Arial", 10, Qt.QFont.Bold), Qt.Qt.FontRole)
            itemToMark = self.itemFromIndex(itemToMark.index().parent())
        self.saveSettings(group)

    def changeTreeValue(self, cdict, path, value):
        """
        Method called recursively by valueChanged. In each step it takes next
        key (from the path) until reaches element to be modified. After the
        element is modified, returns updated dictionary.

        :param cdict: a configuration dictionary.  See
            :class:`BaseConfigurableClass`
        :param path: a semicolon-separated string containing the path of the
            branch in the tree
        :type path: str
        :param value: the new value (a string that will be python-evaluated)
        :type value: str
        :return: the modified config dict
        :rtype: dict
        """
        val = str(path).split(";", 1)
        if len(val) == 2:
            path = val[1]
            try:
                key = eval(val[0])
            except Exception:
                key = val[0]
            cdict[key] = self.changeTreeValue(cdict[key], path, value)
            return cdict
        else:
            cdict[val[0]] = eval(value)
            return cdict

    def fillTopLevel(self):
        """
        Creates a dictionary containing Main Window and Perspectives settings.
        This metod creates top nodes only (names of the perspectives, main
        window) and invokes fillTaurusConfig. Returns complete dictionary.

        :return: a configuration dictionary.  See
            :class:`BaseConfigurableClass`
        :rtype: dict
        """
        # self.tree.clear()
        root = self.invisibleRootItem()
        item = Qt.QStandardItem("LAST")
        item.setEditable(False)
        # item.setSelectable(False)
        root.appendRow(item)
        mainConfig = {}
        configdict = self.getTaurusConfigFromSettings()
        if configdict is not None:
            mainConfig[None] = configdict
            item.setData("None", Qt.Qt.UserRole)
            self.fillTaurusConfig(item, configdict)
        self._settings.beginGroup("Perspectives")
        self.perspectives = self._settings.childGroups()
        for name in self.perspectives:
            item = Qt.QStandardItem(name)
            item.setEditable(False)
            # item.setSelectable(False)
            path = "Perspectives/" + name
            item.setData(path, Qt.Qt.UserRole)
            root.appendRow(item)
            self._settings.beginGroup(name)
            configdict = self.getTaurusConfigFromSettings()
            if configdict is not None:
                mainConfig["Perspectives/" + str(name)] = configdict
                self.fillTaurusConfig(item, configdict)
            self._settings.endGroup()
        self._settings.endGroup()

        return mainConfig

    def fillTaurusConfig(self, item, configdict):
        """
        Fills the non-top nodes of the dictionary recursively.

        :param item: parent item
        :type item: Qt.QStandardItem
        :param configdict: a configuration dictionary.  See
            :class:`BaseConfigurableClass`
        :type configdict: dict
        """
        if not BaseConfigurableClass.isTaurusConfig(configdict):
            return
        # fill the registered keys
        registeredkeys = configdict.get("__orderedConfigNames__", [])
        valuesdict = configdict.get("__itemConfigurations__", {})
        for k in registeredkeys:
            value = valuesdict[k]
            child = Qt.QStandardItem(k)
            if BaseConfigurableClass.isTaurusConfig(value):
                child.setEditable(False)
                item.appendRow(child)

                txt = item.data(Qt.Qt.UserRole)
                path = txt + ";__itemConfigurations__;" + k
                child.setData(path, Qt.Qt.UserRole)
                # recursive call to fill all nodes
                self.fillTaurusConfig(child, value)
            else:
                typeV = Qt.QStandardItem(repr(type(value)))
                valueV = Qt.QStandardItem(repr(value))

                typeV.setForeground(Qt.QBrush(Qt.QColor("gray")))
                child.setForeground(Qt.QBrush(Qt.QColor("gray")))

                item.appendRow([child, typeV, valueV])

                txt = item.data(Qt.Qt.UserRole)
                path = txt + ";__itemConfigurations__;" + k
                child.setEditable(False)
                typeV.setEditable(False)

                child.setData(path, Qt.Qt.UserRole)
                typeV.setData(path, Qt.Qt.UserRole)
                valueV.setData(path, Qt.Qt.UserRole)

        customkeys = [
            k
            for k in configdict
            if k
            not in (
                "__orderedConfigNames__",
                "__itemConfigurations__",
                "__pickable__",
            )
        ]
        if len(customkeys) > 0:
            custom = Qt.QStandardItem("[custom]")
            item.appendRow(custom)
            custom.setEditable(False)
            # custom.setSelectable(False)
            custom.setBackground(Qt.QBrush(Qt.QColor("gray")))
            for k in customkeys:
                value = configdict[k]
                child = Qt.QStandardItem(str(k))
                # item.appendRow(child)

                if BaseConfigurableClass.isTaurusConfig(value):
                    child.setEditable(False)
                    item.appendRow(child)
                    txt = item.data(Qt.Qt.UserRole)
                    path = txt + ";" + k
                    child.setData(path, Qt.Qt.UserRole)
                    # recursive call to fill all nodes
                    self.fillTaurusConfig(child, value)
                else:
                    typeV = Qt.QStandardItem(repr(type(value)))
                    valueV = Qt.QStandardItem(repr(value))
                    typeV.setForeground(Qt.QBrush(Qt.QColor("gray")))
                    child.setForeground(Qt.QBrush(Qt.QColor("gray")))
                    item.appendRow([child, typeV, valueV])
                    txt = item.data(Qt.Qt.UserRole)
                    path = txt + ";" + k

                    child.setData(path, Qt.Qt.UserRole)
                    child.setEditable(False)
                    typeV.setEditable(False)
                    typeV.setData(path, Qt.Qt.UserRole)
                    valueV.setData(path, Qt.Qt.UserRole)

    def getTaurusConfigFromSettings(self, key="TaurusConfig"):
        """
        Loads and returns the configuration dictionary from the settings file
        using pickle module.

        :param key:
        :type key: str
        :returns (dict)
        """
        result = None
        qstate = self._settings.value(key)
        if qstate is not None:
            try:
                result = pickle.loads(qstate.data())
            except Exception as e:
                msg = "problems loading TaurusConfig: \n%s" % repr(e)
                Qt.QMessageBox.critical(None, "Error loading settings", msg)
        return result

    def reloadFile(self):
        """
        Reloads the file. Configuration tree is build again.
        """
        self.loadFile(self.originalFile)

    def saveFile(self):
        """
        Replaces original file with temporary file (where changes were being
        saved).
        """
        if self.markedItems == []:
            return
        self._settings.sync()

        shutil.copyfile(self._temporaryFile, self.originalFile)
        self.clearChanges()
        # self.reloadFile()

    def saveSettings(self, group=None):
        """Saves the current state to the temporary file

        :param group: a prefix that will be added to the keys to be saved (no
            prefix by default)
        :type group: str
        """
        if group is not None:
            self._settings.beginGroup(group)

        # store the config dict
        self._settings.setValue(
            "TaurusConfig",
            Qt.QByteArray(pickle.dumps(self._configurationDictionaries[group])),
        )
        if group is not None:
            self._settings.endGroup()

    def restoreOriginal(self):
        """
        Replaces temporary file with the original file and builds again the
        configuration tree.
        """
        if self.markedItems == []:
            return

        self.reloadFile()

    def clearChanges(self):
        """
        Clears all changes in style of the modified elements in tree view.
        """
        for index in self.markedItems:
            itemToMark = self.itemFromIndex(index)
            while itemToMark is not None:
                itemToMark.setData(
                    Qt.QFont("Arial", 10, Qt.QFont.Normal), Qt.Qt.FontRole
                )
                itemToMark.setData(None, Qt.Qt.DecorationRole)
                itemToMark = self.itemFromIndex(itemToMark.index().parent())


class QConfigEditor(TaurusWidget):
    """A widget that shows a tree view of the contents of Taurus
    configuration files saved by TaurusMainWindow and lets the user edit
    the values of the configuration keys
    """

    def __init__(self, parent=None, designMode=False):
        TaurusWidget.__init__(self, parent=parent, designMode=designMode)
        self.setLayout(Qt.QVBoxLayout())
        self.tree = QConfigEditorModel()
        self.treeview = Qt.QTreeView()
        self.tree.setHorizontalHeaderLabels(["Configuration key", "type", "value"])
        self.layout().addWidget(self.treeview)
        self._toolbar = Qt.QToolBar("QConfigViewer Main toolBar")
        self._toolbar.addAction(
            Qt.QIcon.fromTheme("document-open"), "Open File", self.loadFile
        )
        self._toolbar.addAction(
            Qt.QIcon.fromTheme("document-save"), "Save File", self.saveFile
        )
        self._toolbar.addAction(
            Qt.QIcon.fromTheme("edit-undo"),
            "Reload from file",
            self.restoreOriginal,
        )
        self.layout().setMenuBar(self._toolbar)
        self.setWindowTitle("TaurusConfigEditor")
        self.tree.showError.connect(self._showError)

    def contextMenuEvent(self, event):
        """Reimplemented from :meth:`QWidget.contextMenuEvent`"""

        self.tree._toDeleteIndex = self.treeview.selectedIndexes()[0]
        text = self.tree._toDeleteIndex.data()
        if (
            self.tree._toDeleteIndex.column() in [1, 2]
            or text in ["LAST", "[custom]"]
            or text in self.tree.perspectives
        ):
            return
        menu = Qt.QMenu()
        menu.addAction(
            Qt.QIcon.fromTheme("process-stop"),
            "Delete branch: " + text,
            self.tree.deleteBranch,
        )
        menu.addSeparator()
        menu.addAction(Qt.QIcon.fromTheme("help-browser"), "Help")
        menu.exec_(event.globalPos())
        event.accept()

    def _showError(self, title, body):
        """
        Opens a warning dialog with a given title and body.

        :title: (str) title
        :body: (str) body
        """
        Qt.QMessageBox.warning(self, title, body, Qt.QMessageBox.Ok)

    def loadFile(self, iniFileName=None):
        """
        Loads a configuration stored in a file and creates the tree.

        :param iniFileName: Name of the file. If None is given the user is
            prompted for a file.
        :type iniFileName: str
        """
        if iniFileName is None:
            if self.tree.originalFile is None:
                path = Qt.QDir.homePath()
            else:
                path = self.tree.originalFile
            iniFileName, _ = compat.getOpenFileName(
                self, "Select a settings file", path, "Ini Files (*.ini)"
            )
            if not iniFileName:
                return
        self.tree.loadFile(iniFileName)
        self.treeview.setModel(self.tree)
        self.setWindowTitle(
            "TaurusConfigEditor - %s" % os.path.basename(self.tree.originalFile)
        )

    def saveFile(self):
        """Replaces original file with temporary file (where changes were
        being saved).
        """
        self.tree.saveFile()

    def restoreOriginal(self):
        """
        Replaces temporary file with the original file and builds again the
        configuration tree.
        """
        self.tree.restoreOriginal()


@click.command("config")
@click.argument("config_file", type=click.Path(exists=True), required=False)
def config_cmd(config_file):
    """Open the taurus configuration editor"""
    import sys

    from taurus.qt.qtgui.application import TaurusApplication

    app = TaurusApplication(cmd_line_parser=None)

    w = QConfigEditor()
    w.setMinimumSize(500, 500)
    w.show()
    if config_file:
        w.loadFile(config_file)

    sys.exit(app.exec_())


if __name__ == "__main__":
    config_cmd()
