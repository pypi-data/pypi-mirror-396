#!/usr/bin/env python
# -*- coding: utf-8 -*-

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

"""This module provides a taurus QPushButton based widgets"""

import importlib

from taurus.core.taurusbasetypes import LockStatus, TaurusLockInfo
from taurus.core.taurusdevice import TaurusDevice
from taurus.core.util import eventfilters
from taurus.external.qt import Qt, compat
from taurus.qt.qtgui.base import TaurusBaseWidget
from taurus.qt.qtgui.dialog import ProtectTaurusMessageBox
from taurus.taurusstatecontroller import application

__docformat__ = "restructuredtext"


class _ButtonDialog(Qt.QDialog):
    _widget = None
    deleteWidgetOnClose = False

    def __init__(self, parent=None):
        Qt.QDialog.__init__(self, parent, Qt.Qt.WindowTitleHint)
        lyt = Qt.QVBoxLayout()
        self.setLayout(lyt)
        self.previousWidgetConfig = None

    def setWidget(self, widget):
        oldWidget = self.widget()
        if oldWidget is not None:
            try:
                self._widget.setModel(None)
            except Exception:
                pass
            oldWidget.hide()
            oldWidget.setParent(None)
            oldWidget.deleteLater()
        if widget is not None:
            self.layout().addWidget(widget)
        self._widget = widget

    def widget(self):
        return self._widget

    def closeEvent(self, event):
        if self.deleteWidgetOnClose:
            try:
                self.previousWidgetConfig = self.widget().createConfig()
            except Exception:
                self.previousWidgetConfig = None
            self.setWidget(None)
        Qt.QDialog.closeEvent(self, event)


class TaurusLauncherButton(Qt.QPushButton, TaurusBaseWidget):
    """This class provides a button that launches a modeless dialog containing
    a specified Taurus widget which gets the same model as the button.
    The button does not use the model directly. Instead it passes it to the
    associated widget.

    Code examples::

        # a button that launches a TaurusAttrForm when clicked
        b = TaurusLauncherButton(widget = TaurusAttrForm())
        # set dev name, which will be set at the TaurusAttrForm when clicking
        b.setModel("a/b/c")

        # a button that launches a taurusLabel
        b = TaurusLauncherButton(widget="taurus.qt.qtgui.display:TaurusLabel")
        b.setModel("a/b/c/d")

        # a button that launches a TaurusPlot
        b = TaurusLauncherButton(widget="taurus_pyqtgraph:TaurusPlot")
        b.setModel("eval:rand(50)")
    """

    _widgetClassName = ""
    _args = []
    _kwargs = {}
    _deleteWidgetOnClose = True
    _icon = None
    _text = None

    def __init__(
        self, parent=None, designMode=False, widget=None, icon=None, text=None
    ):
        """Constructor

        :param parent: parent of this widget
        :type parent: Qt.QWidget or None
        :param designMode: flag for Qt designer
        :type designMode: bool
        :param widget: a QWidget (or its "module:class" specification) that
            will be shown when clicking in the button
        :type widget: Qt.QWidget or str
        :param icon: icon for the button
        :type icon: Qt.QIcon
        :param text: the button text (if None passed, the widget's class name
            is used)
        :type text: str
        """

        name = self.__class__.__name__
        self.call__init__wo_kw(Qt.QPushButton, parent)
        self.call__init__(TaurusBaseWidget, name, designMode=designMode)
        self._dialog = _ButtonDialog(self)
        if icon is None and self._icon is not None:
            icon = Qt.QIcon(self._icon)
        if icon is not None:
            self.setIcon(Qt.QIcon(icon))
        if text is not None:
            self._text = text
        if isinstance(widget, Qt.QWidget):
            # we cannot be sure on recreating the same widget again
            self._deleteWidgetOnClose = False
            self.setWidget(widget)
        elif widget is not None:
            self._widgetClassName = widget
        self.clicked.connect(self.onClicked)
        self.setDefault(False)
        self.setAutoDefault(False)
        # no need to listen to change events!
        self.insertEventFilter(eventfilters.IGNORE_CHANGE_AND_PERIODIC)
        self._updateText()

    def getModelClass(self, **kwargs):
        """see :meth:`TaurusBaseComponent.getModelClass`. Note that in the case
        of :class:`TaurusLauncherButton`, the class is completely dependent on
        the widget's class
        """
        try:
            return self.widget().getModelClass(**kwargs)
        except Exception:
            # return None  #@TODO: Uncommenting this avoids the exception when
            # TaurusBaseWidget.getModelClass chokes with relative classes. But
            # the thing should be solved at TaurusBaseWidget.getModelClass
            # level
            return TaurusBaseWidget.getModelClass(self, **kwargs)

    def setText(self, text):
        """Sets the text of the button. see :meth:`Qt.QPushButton.setText`"""
        self._text = text
        Qt.QPushButton.setText(self, text)

    def getWidgetClassName(self):
        return self._widgetClassName

    def setWidgetClassName(self, className, args=None, kwargs=None):
        self._widgetClassName = str(className)
        if args is not None:
            self._args = args
        if kwargs is not None:
            self._kwargs = kwargs
        self._updateText()

    def resetWidgetClassName(self, className, args=None, kwargs=None):
        self.setWidgetClassName(self.__class__._widgetClassName)

    def createWidget(self):
        if ":" in self._widgetClassName:
            # assuming pkg_resources-style spec:  modname:object[.attr]
            mod_name, class_name = self._widgetClassName.split(":")
            klass = getattr(importlib.import_module(mod_name), class_name)
        else:
            # using TaurusWidgetFactory, deprecated
            from taurus.qt.qtgui.util import TaurusWidgetFactory

            _qt_widgets = TaurusWidgetFactory()._qt_widgets
            _modname, klass = _qt_widgets[self._widgetClassName]
            self.deprecated(
                dep="specifying the classname ('{}') without module".format(
                    self._widgetClassName
                ),
                alt="'{}:{}'".format(_modname, self._widgetClassName),
                rel="5.0.0",
            )

        widget = klass(*self._args, **self._kwargs)
        self.setWidget(widget)
        if self._dialog.previousWidgetConfig is not None:
            try:
                widget.applyConfig(self._dialog.previousWidgetConfig)
            except Exception as e:
                self.warning(
                    "Cannot apply previous configuration to widget. " + "Reason: %s",
                    repr(e),
                )

    def widget(self):
        return self._dialog.widget()

    def setWidget(self, widget):
        """sets the widget that will be shown when clicking the button

        :param widget:
        :type widget: Qt.QWidget
        """
        self._dialog.setWidget(widget)
        self._updateText()

    def displayValue(self, v):
        """see :meth:`TaurusBaseComponent.displayValue`"""
        if self._text is not None:
            return self._text  # make sure the text is not changed once set
        TaurusBaseWidget.displayValue(self, v)

    def getDisplayValue(self, **kwargs):
        """see :meth:`TaurusBaseComponent.getDisplayValue`"""
        if self._text is not None:
            return self._text
        if self.widget() is not None:
            return self.widget().__class__.__name__
        return self._widgetClassName or "---"

    def _updateText(self):
        Qt.QPushButton.setText(self, self.getDisplayValue())

    def onClicked(self):
        """
        Slot called when the button is clicked.
        Note that the dialog will only be created once. Subsequent clicks on
        the button will only raise the existing dialog
        """
        application.application_starting()
        if self.widget() is None:
            self.createWidget()
        self.widget().setModel(self.getModelName())
        self._dialog.deleteWidgetOnClose = self._deleteWidgetOnClose
        # dialog.resize(400,300)

        # It's always necessary to set the title since the model could have
        # changed
        self._dialog.setWindowTitle(str(self.getModelName()))

        self._dialog.show()
        self._dialog.raise_()
        application.application_started()

    @classmethod
    def getQtDesignerPluginInfo(cls):
        return {
            "group": "Taurus Buttons",
            "icon": "designer:pushbutton.png",
            "module": "taurus.qt.qtgui.button",
            "container": False,
        }

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #                      Qt Properties
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    Model = Qt.pyqtProperty(
        "QString",
        TaurusBaseWidget.getModel,
        TaurusBaseWidget.setModel,
        TaurusBaseWidget.resetModel,
    )
    #: (deprecated))
    UseParentModel = Qt.pyqtProperty(
        "bool",
        TaurusBaseWidget.getUseParentModel,
        TaurusBaseWidget.setUseParentModel,
        TaurusBaseWidget.resetUseParentModel,
    )
    widgetClassName = Qt.pyqtProperty(
        "QString", getWidgetClassName, setWidgetClassName, resetWidgetClassName
    )


class TaurusCommandButton(Qt.QPushButton, TaurusBaseWidget):
    """This class provides a button that executes a tango command on its
    device.

    Code examples::

        # a button that executes the "status" command for
        # the 'a/b/c' device server
        button =  TaurusCommandButton(
            command = 'Status', icon='logos:taurus.png'
            )
        button.setModel('a/b/c')

        #  a button that executes the "exec" command for
        # the 'a/b/c' device server with one parameter
        button =  TaurusCommandButton(
            command = 'Status', parameters=['2+2'],icon='logos:taurus.png'
            )
        button.setModel('a/b/c')

    .. seealso:: :class:`TaurusCommandsForm` provides a good example of use of
                 TaurusCommandButton (including managing the return value)
    """

    # TODO: tango-centric
    commandExecuted = Qt.pyqtSignal(compat.PY_OBJECT)

    def __init__(
        self,
        parent=None,
        designMode=False,
        command=None,
        parameters=None,
        icon=None,
        text=None,
        timeout=None,
    ):
        """Constructor

        :param parent: parent of this widget
        :type parent: Qt.QWidget or None
        :param designMode: flag for Qt designer
        :type designMode: bool
        :param command: the name of the command to be executed
        :type command: str
        :param parameters: the list of parameteres. Default value is None
            meaning no parameters
        :type parameters: sequence<str>
        :param icon: icon for the button
        :type icon: Qt.QIcon
        :param text: the button text (if None passed, `command` is used)
        :type text: str
        :param timeout: the command timeout (in seconds)
        :type timeout: float
        """
        name = self.__class__.__name__
        if command is None:
            command = ""
        if parameters is None:
            parameters = []
        self._command = command
        self._parameters = parameters
        self._timeout = timeout
        self._customText = text
        self.call__init__wo_kw(Qt.QPushButton, parent)
        self.call__init__(TaurusBaseWidget, name, designMode=designMode)
        if icon is not None:
            self.setIcon(Qt.QIcon(icon))
        self.setCustomText(text)
        self.setDefault(False)
        self.setAutoDefault(False)
        self.clicked.connect(self.onClicked)

    def getDisplayValue(self, **kwargs):
        """see :meth:`TaurusBaseComponent.displayValue`"""
        if self._customText is not None:
            return self._customText
        if len(self._command) == 0:
            return "---"
        modelobj = self.getModelObj()
        if modelobj is None or not hasattr(modelobj, self._command):
            return "---"
        return self._command

    @ProtectTaurusMessageBox(title="Unexpected error when executing command")
    def onClicked(self, value=0):
        return self._onClicked()

    def _onClicked(self):
        """Slot called when the button is clicked. It executes the command with
        parameters. It may issue a warning if the command is flagged as
        dangerous. On successful execution, it returns the command result and
        it emits a "commandExecuted" signal with the result as well.

        :return: The result of the command. The type depends on the command. It
            may be None.


        .. seealso:: :meth:`setCommand`, :meth:`setParameters`,
            :meth:`TaurusBaseComponent.isDangerous`
        """

        self.debug("launch command %s" % str(self._command))
        if len(self._command) == 0:
            return
        modelobj = self.getModelObj()
        if modelobj is None or not hasattr(modelobj, self._command):
            self.warning(
                "Device %s does not implement command %s" % (modelobj, self._command)
            )
            return

        if self.isDangerous() and not self.getForceDangerousOperations():
            result = Qt.QMessageBox.question(
                self,
                "Potentially dangerous action",
                "%s\nProceed?" % self.getDangerMessage(),
                Qt.QMessageBox.Ok | Qt.QMessageBox.Cancel,
                Qt.QMessageBox.Ok,
            )
            if result != Qt.QMessageBox.Ok:
                return
        # After all the checks, we can finally do the action
        orig_timeout = modelobj.get_timeout_millis()
        try:
            if self._timeout is not None:
                modelobj.set_timeout_millis(int(self._timeout * 1000))
            result = modelobj.command_inout(
                self._command,
                self._castParameters(self._parameters, self._command, modelobj),
            )
        except Exception as e:
            self.error(
                "Unexpected error when executing command %s of %s: %s"
                % (self._command, modelobj.getNormalName(), str(e))
            )
            raise
        finally:
            modelobj.set_timeout_millis(orig_timeout)

        self.commandExecuted.emit(result)
        return result

    def _castParameters(self, parameters=None, command=None, dev=None):
        """Internal method used to cast the command paramters to the
        appropriate type required for the given command

        :param parameters: a sequence of parameters. If None is passed, the
            currently set parameters are used.
        :type parameters: sequence
        :param command: the command name. If None is passed, the currently set
            command is used.
        :type command: str
        :param dev: the device on which the command is executed. If None is
            passed, the current model is used.
        :type dev: taurus.core.taurusdevice.TaurusDevice
        :return: a sequence of parameters (or a scalar if only one parameter)
        :rtype: sequence or scalar
        """
        import tango

        if parameters is None:
            parameters = self._parameters
        if command is None:
            command = self._command
        if dev is None:
            dev = self.getModelObj()

        try:
            param_type = dev.command_query(command).in_type
        except Exception as e:
            self.warning(
                "Cannot get parameters info for command %s:%s" % (command, str(e))
            )
            return parameters
        if param_type == tango.CmdArgType.DevVoid:
            return None
        if tango.is_int_type(param_type, True):
            cast_type = int
        elif tango.is_float_type(param_type, True):
            cast_type = float
        elif (
            param_type == tango.CmdArgType.DevVarStringArray
            or param_type == tango.CmdArgType.DevString
        ):
            cast_type = str
        elif (
            param_type == tango.CmdArgType.DevVarBooleanArray
            or param_type == tango.CmdArgType.DevBoolean
        ):
            cast_type = bool
        else:
            self.info(
                'Unsupported parameters type (%s). Casting to "str"' % str(param_type)
            )
            cast_type = str
        if tango.is_scalar_type(param_type):
            if parameters:
                return cast_type(parameters[0])
            else:
                return parameters
        else:
            return list(map(cast_type, parameters))

    def setCommand(self, commandName):
        """sets the command to be executed when the button is clicked

        :param commandName: the command name
        :type commandName: str or None
        """
        if commandName is None:
            self._command = ""
        else:
            self._command = str(commandName)
        self._setText(self.getDisplayValue())

    def getCommand(self):
        """returns the command name to be executed when the button is clicked

        :return: the command name
        :rtype: str or None
        """
        return self._command

    def resetCommand(self):
        """equivalent to self.setCommand(None)"""
        self.setCommand("")

    def setParameters(self, parameters):
        """
        Sets the parameters to be used on command execution.

        :param parameters: a sequence of parameters. If the elements of the
            sequence are not of the right type required for the parameter, an
            automatic conversion will be attempted on execution time. As a
            special case, if parameters is a string not starting and ending in
            quote characters, it will be splitted on whitespace to obtain a
            sequence of parameters. If it is a string starting and ending with
            quotes, the quotes will be removed and the quoted text will not be
            splitted.
        :type parameters: sequence
        """
        if isinstance(parameters, str):
            parameters = str(parameters).strip()
            if parameters[0] in ('"', "'") and parameters[0] == parameters[-1]:
                parameters = [parameters[1:-1]]
            else:
                parameters = parameters.split()
        self._parameters = parameters

    def getParameters(self):
        """returns the parameters to be used on command execution

        :param parameters:
        :type parameters: sequence
        """
        return self._parameters

    def resetParameters(self):
        """Equivalent to setParameters([])"""
        self.setParameters([])

    def setCustomText(self, customText=None):
        """Sets a custom text for the button (by default it is the command
        name)

        :param customText: the custom text. If None passed, it will use the
            command name
        :type customText: str or None
        """
        self._customText = customText
        self._setText(self.getDisplayValue())

    def getCustomText(self):
        """Returns the custom text of the buttom, or None if no custom text is
        used
        """
        return self._customText

    def resetCustomText(self):
        """Equivalent to setCustomText(None)"""
        self.setCustomText(None)

    @Qt.pyqtSlot(float)
    @Qt.pyqtSlot(int)
    def setTimeout(self, timeout):
        """Sets the number of seconds to wait for the result of the command.

        .. seealso:: :meth:`tango.DeviceProxy.command_inout`

        :param timeout: the command timeout in seconds (timeout <0 or
            timeout=None disables the timeout)
        :type timeout: float
        """
        if timeout < 0:
            timeout = None
        self._timeout = timeout

    def getTimeout(self):
        """
        Returns the number of seconds to wait for the result of the command
        (or -1 if timeout is disabled)
        """
        ret = self._timeout
        if ret is None or ret < 0:
            ret = -1
        return ret

    def resetTimeout(self):
        """Equivalent to setTimeout(None)"""
        self.setTimeout(None)

    @classmethod
    def getQtDesignerPluginInfo(cls):
        return {
            "group": "Taurus Buttons",
            "icon": "designer:pushbutton.png",
            "module": "taurus.qt.qtgui.button",
            "container": False,
        }

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #                      Qt Properties
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Model = Qt.pyqtProperty(
        "QString",
        TaurusBaseWidget.getModel,
        TaurusBaseWidget.setModel,
        TaurusBaseWidget.resetModel,
    )

    #: (deprecated))
    UseParentModel = Qt.pyqtProperty(
        "bool",
        TaurusBaseWidget.getUseParentModel,
        TaurusBaseWidget.setUseParentModel,
        TaurusBaseWidget.resetUseParentModel,
    )

    Command = Qt.pyqtProperty("QString", getCommand, setCommand, resetCommand)

    Parameters = Qt.pyqtProperty(
        "QStringList", getParameters, setParameters, resetParameters
    )

    DangerMessage = Qt.pyqtProperty(
        "QString",
        TaurusBaseWidget.getDangerMessage,
        TaurusBaseWidget.setDangerMessage,
        TaurusBaseWidget.resetDangerMessage,
    )

    CustomText = Qt.pyqtProperty(
        "QString", getCustomText, setCustomText, resetCustomText
    )

    Timeout = Qt.pyqtProperty("double", getTimeout, setTimeout, resetTimeout)


class TaurusLockButton(Qt.QPushButton, TaurusBaseWidget):
    _LOCK_MAP = {
        LockStatus.Unlocked: "extra_icons:lock_unlocked.svg",
        LockStatus.Locked: "extra_icons:lock_locked_unpreviledged.svg",
        LockStatus.LockedMaster: "extra_icons:lock_locked.svg",
        LockStatus.Unknown: "extra_icons:lock_unknown.svg",
    }

    def __init__(self, parent=None, designMode=False):
        self._lock_info = TaurusLockInfo()
        name = self.__class__.__name__
        self.call__init__wo_kw(Qt.QPushButton, parent)
        self.call__init__(TaurusBaseWidget, name, designMode=designMode)
        self.toggled.connect(self.on_toggle)
        self.setCheckable(True)
        self.setAutoTooltip(False)
        self.insertEventFilter(eventfilters.IGNORE_ALL)
        self.update_button()

    @classmethod
    def getQtDesignerPluginInfo(cls):
        return {
            "group": "Taurus Buttons",
            "icon": "designer:pushbutton.png",
            "module": "taurus.qt.qtgui.button",
            "container": False,
        }

    def getModelClass(self, **kwargs):
        return TaurusDevice

    def setModel(self, model, **kwargs):
        TaurusBaseWidget.setModel(self, model, **kwargs)
        self.update_button()

    def get_lock_info(self, cache=False):
        dev = self.getModelObj()
        if dev is not None:
            self._lock_info = dev.getLockInfo(cache=cache)
        return self._lock_info

    def update_button(self, lock_info=None):
        if lock_info is None:
            lock_info = self.get_lock_info()
        status = lock_info.status
        self.setIcon(Qt.QIcon(self._LOCK_MAP[status]))
        self.setDown(status in (LockStatus.Locked, LockStatus.LockedMaster))
        self.setToolTip(lock_info.status_msg)
        self.update()
        return lock_info

    def _on_toggle(self, down):
        dev = self.getModelObj()
        if down:
            dev.lock()
        else:
            dev.unlock()
        self.update_button()

    def on_toggle(self, down):
        try:
            self._on_toggle(down)
        except Exception:
            import sys

            from taurus.qt.qtgui.dialog import TaurusMessageBox

            msgbox = TaurusMessageBox(*sys.exc_info())
            msgbox.setWindowTitle("Error locking device")
            if self.update_button().status == LockStatus.Locked:
                msgbox.setText(self._lock_info.status_msg)
            msgbox.exec_()

    model = Qt.pyqtProperty(
        "QString",
        TaurusBaseWidget.getModel,
        setModel,
        TaurusBaseWidget.resetModel,
    )


def lockButtonMain():
    import sys

    import taurus.qt.qtgui.application

    Application = taurus.qt.qtgui.application.TaurusApplication

    app = Application.instance()
    owns_app = app is None

    if owns_app:
        import taurus.core.util.argparse

        parser = taurus.core.util.argparse.get_taurus_parser()
        parser.usage = "%prog [options] <full_attribute_name(s)>"
        app = Application(
            sys.argv,
            cmd_line_parser=parser,
            app_name="Taurus lock button demo",
            app_version="1.0",
            org_domain="Taurus",
            org_name="Tango community",
        )

    args = app.get_command_line_args()

    if len(args) == 0:
        w = demo()
    else:
        models = list(map(str.lower, args))

        w = Qt.QWidget()
        layout = Qt.QGridLayout()
        w.setLayout(layout)
        for model in models:
            lock_button = TaurusLockButton()
            lock_button.model = model
            layout.addWidget(lock_button)
    w.show()

    if owns_app:
        sys.exit(app.exec_())
    else:
        return w


def commandButtonMain():
    import sys

    from taurus.qt.qtgui.application import TaurusApplication

    app = TaurusApplication(cmd_line_parser=None)
    form = TaurusCommandButton(
        parent=None,
        designMode=False,
        command="DevBoolean",
        parameters=[123],
        icon="logos:taurus.png",
        text="launch: DevBoolean 123",
    )
    form.setModel("sys/tg_test/1")
    form.setDangerMessage("Booo scary command!!\n Maybe you should think twice!")

    def f(*a):
        print(a)

    form.commandExecuted.connect(f)
    form.show()
    sys.exit(app.exec_())


def launcherButtonMain():
    import sys

    from taurus.qt.qtgui.application import TaurusApplication

    app = TaurusApplication(cmd_line_parser=None)

    # Creating button giving the widget
    # from taurus.qt.qtgui.plot import TaurusPlot
    # w = TaurusPlot()
    # form = TaurusLauncherButton(parent=None, designMode=False, widget=w,
    #                             icon='logos:taurus.png'), text='show')

    # Creating button giving the widget class name
    # form = TaurusLauncherButton(parent=None, designMode=False,
    #                             widget='TaurusPlot', icon='logos:taurus.png',
    #                             text='show')

    # Creating button using a derived class with the name widget class
    # hardcoded
    class MyButton(TaurusLauncherButton):
        _widgetClassName = "taurus_pyqtgraph:TaurusPlot"
        _icon = "logos:taurus.png"
        _text = "show"

    form = MyButton()

    form.setModel("sys/tg_test/1/wave")
    form.show()
    sys.exit(app.exec_())


def main():
    lockButtonMain()


def demo():
    """Lock button"""
    lock_button = TaurusLockButton()
    lock_button.model = "sys/tg_test/1"
    return lock_button


if __name__ == "__main__":
    # lockButtonMain()
    launcherButtonMain()
    # commandButtonMain()
