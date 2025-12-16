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
tauruswidgetfactory.py:
"""

__docformat__ = "restructuredtext"

import importlib
import os.path

import pkg_resources

import taurus.qt.qtgui.base
from taurus.core.util.log import Logger, deprecation_decorator
from taurus.core.util.singleton import Singleton
from taurus.external.qt import Qt


def _getWidgetsOfType(widget, widgets, class_or_type_or_tuple):
    if isinstance(widget, class_or_type_or_tuple):
        widgets.append(widget)
    for w in widget.children():
        if isinstance(w, Qt.QWidget):
            _getWidgetsOfType(w, widgets, class_or_type_or_tuple)


def getWidgetsOfType(widget, class_or_type_or_tuple):
    """Returns all widgets in a hierarchy of a certain type

    :param widget: the widget to be inspected
    :type widget: Qt.QWidget
    :param class-or-type-or-tuple: type to be checked
    :type class-or-type-or-tuple: type class or a tuple of type classes
    :return: a sequence containning all widgets in the hierarchy that match the
        given type
    :rtype: seq<Qt.QWidget>
    """
    widgets = []
    _getWidgetsOfType(widget, widgets, class_or_type_or_tuple)
    return widgets


class TaurusWidgetFactory(Singleton, Logger):
    """The TaurusWidgetFactory is a utility class that provides information
    about all Qt widgets (Taurus and non Taurus) that are found in the
    current taurus distribution.
    TaurusWidgetFactory is a singleton class so you can freely create new
    instances since they will all reference the same object.
    Usage::

        from taurus.qt.qtgui.util import TaurusWidgetFactory

        wf = TaurusWidgetFactory()
        print(wf.getTaurusWidgetClassNames())
    """

    skip_modules = (
        "widget",
        "util",
        "qtdesigner",
        "uic",
        "resource",
        "console",
        "style",
        "plot",
    )

    def __init__(self):
        """Initialization. Nothing to be done here for now."""

    def init(self, *args):
        """Singleton instance initialization."""
        name = self.__class__.__name__
        self.call__init__(Logger, name)

        self.deprecated(rel="5.0.0", dep="TaurusWidgetFactory", alt="importlib")

        path = os.path.dirname(os.path.abspath(__file__))
        path, tail = os.path.split(path)
        self._taurus_widgets, self._qt_widgets = self._buildWidgets(
            "taurus.qt.qtgui", path
        )

        # Also explore modules registered via the `taurus.qt.qtgui` entry-point
        for ep in pkg_resources.iter_entry_points("taurus.qt.qtgui"):
            try:
                _module = ep.load()
                _name = _module.__name__
                _path = os.path.dirname(os.path.abspath(_module.__file__))
            except Exception as e:
                self.warning("Cannot explore %s. Reason: %r", ep, e)
                continue
            taurus_widgets, qt_widgets = self._buildWidgets(_name, _path)
            self._taurus_widgets.update(taurus_widgets)
            self._qt_widgets.update(qt_widgets)

        self._addExtraTaurusWidgets(self._taurus_widgets, self._qt_widgets)

    def _buildWidgets(self, module_name, path, recursive=True):
        import taurus.qt.qtgui.base

        if Qt.QApplication.instance() is None:
            # keep a reference
            app = Qt.QApplication([])  # noqa: F841

        elems = os.listdir(path)
        taurus_ret, qt_ret = {}, {}
        if "__init__.py" not in elems:
            return taurus_ret, qt_ret

        try:
            m = __import__(module_name, fromlist=["*"], level=0)
            dir_names = dir(m)
            for dir_name in dir_names:
                if dir_name.startswith("_"):
                    continue
                try:
                    attr = getattr(m, dir_name)
                    if issubclass(attr, Qt.QWidget):
                        package = m.__package__
                        qt_ret[dir_name] = package, attr
                        if issubclass(attr, taurus.qt.qtgui.base.TaurusBaseWidget):
                            taurus_ret[dir_name] = package, attr
                except Exception:
                    pass
        except Exception:
            return taurus_ret, qt_ret

        if not recursive:
            return taurus_ret, qt_ret

        for elem in elems:
            abs_elem = os.path.join(path, elem)
            if (
                (not elem.startswith("."))
                and os.path.isdir(abs_elem)
                and (elem not in self.skip_modules)
            ):
                m_name = os.path.splitext(elem)[0]
                new_module_name = "%s.%s" % (module_name, m_name)
                new_taurus_ret, new_qt_ret = self._buildWidgets(
                    new_module_name, abs_elem, True
                )
                taurus_ret.update(new_taurus_ret)
                qt_ret.update(new_qt_ret)
        return taurus_ret, qt_ret

    def _addExtraTaurusWidgets(self, taurus_ret, qt_widgets):
        designer_path = os.environ.get("TAURUSQTDESIGNERPATH")
        if designer_path is None:
            return taurus_ret
        designer_path = designer_path.split(os.path.pathsep)
        for path in designer_path:
            self._addExtraTaurusWidgetsPath(taurus_ret, qt_widgets, path)

    def _addExtraTaurusWidgetsPath(self, taurus_ret, qt_widgets, path):
        self.debug("Trying extra taurus widgets in %s", path)
        path = os.path.abspath(path)
        if not os.path.isdir(path):
            return
        elems = os.listdir(path)
        for elem in elems:
            m_name, ext = os.path.splitext(elem)
            if ext != ".py":
                continue
            try:
                spec = importlib.util.spec_from_file_location(m_name, elem)
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
            except ImportError as ie:
                self.debug("Could not load extra module %s:%s", m_name, ie)
                continue
            dir_names = dir(mod)
            for dir_name in dir_names:
                if dir_name.startswith("_"):
                    continue
                if dir_name in taurus_ret:
                    continue
                try:
                    attr = getattr(mod, dir_name)
                    if issubclass(attr, Qt.QWidget):
                        if issubclass(attr, taurus.qt.qtgui.base.TaurusBaseWidget):
                            qt_info = attr.getQtDesignerPluginInfo()
                            taurus_ret[dir_name] = qt_info["module"], attr
                            qt_widgets[dir_name] = qt_info["module"], attr
                            self.debug("registered taurus widget %s", dir_name)
                except Exception:
                    pass

    @deprecation_decorator(rel="5.0.0")
    def getWidgets(self):
        return self._qt_widgets

    @deprecation_decorator(rel="5.0.0")
    def getTaurusWidgets(self):
        return self._taurus_widgets

    @deprecation_decorator(rel="5.0.0")
    def getWidgetClassNames(self):
        return list(self._qt_widgets.keys())

    @deprecation_decorator(rel="5.0.0")
    def getWidgetClasses(self):
        return [klass for mod_name, klass in self._qt_widgets.values()]

    @deprecation_decorator(rel="5.0.0", alt="importlib")
    def getWidgetClass(self, name):
        return self._qt_widgets[name][1]

    @deprecation_decorator(rel="5.0.0")
    def getTaurusWidgetClassNames(self):
        return list(self._taurus_widgets.keys())

    @deprecation_decorator(rel="5.0.0")
    def getTaurusWidgetClasses(self):
        return [klass for mod_name, klass in self._taurus_widgets.values()]

    @deprecation_decorator(rel="5.0.0", alt="importlib")
    def getTaurusWidgetClass(self, name):
        return self._taurus_widgets.get(name)[1]
