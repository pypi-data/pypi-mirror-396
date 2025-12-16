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
Plugin module for QtDesigner that auto generates a the collections of plugins
to be added to the Qt designer catalog
"""

from importlib import import_module

from taurus.external.qt import QtDesigner
from taurus.qt.qtdesigner.tauruswidgetmap import _DEFAULT_TAURUS_WIDGET_CATALOG

_plugins = {}

_PYQT6_FILTER_OUT_WIDGETS = [
    "TaurusImageDialog",  # In qt6 qwt is no longer supported
    "TaurusTrend2DDialog",
    "CurveWidget",
    "ImageWidget",
    "TaurusCurveDialog",
    "TaurusTrendDialog",
]


def build_qtdesigner_widget_plugin(klass):
    from taurus.qt.qtdesigner.taurusplugin import taurusplugin

    class Plugin(taurusplugin.TaurusWidgetPlugin):
        WidgetClass = klass

    Plugin.__name__ = klass.__name__ + "QtDesignerPlugin"
    return Plugin


def _create_plugins():
    from taurus import Logger

    Logger.setLogLevel(Logger.Debug)
    _log = Logger(__name__)

    ok = 0

    # use explicit list of specs instead of original approach of instrospecting
    # with TaurusWidgetFactory().getWidgetClasses()
    # TODO: complement specs with an entry-point
    specs = _DEFAULT_TAURUS_WIDGET_CATALOG
    from taurus.external.qt import PYQT6

    for spec in specs:
        spec = spec.strip()
        msg = spec + " : "
        try:
            assert ":" in spec, "expected 'modname:classname'"
            _mod_name, _cls_name = spec.rsplit(":", maxsplit=1)
            if PYQT6 and _cls_name in _PYQT6_FILTER_OUT_WIDGETS:
                continue
            widget_class = getattr(import_module(_mod_name), _cls_name)
        except Exception as e:
            _log.warning(msg + "error importing: %s", e)
            continue

        try:
            qt_info = widget_class.getQtDesignerPluginInfo()
            assert qt_info is not None, "getQtDesignerPluginInfo() -> None"
            assert "module" in qt_info, "'module' key not available"
        except Exception as e:
            _log.warning(msg + "error getting plugin info: %s", e)
            continue

        try:
            # dynamically create taurus plugin classes and expose them
            plugin_class = build_qtdesigner_widget_plugin(widget_class)
            plugin_class_name = plugin_class.__name__
            globals()[plugin_class_name] = plugin_class
            _plugins[plugin_class_name] = plugin_class
        except Exception as e:
            _log.warning(msg + "error creating plugin: %s", e)
            continue

        # if we got here, everything went fine for this
        _log.info(msg + "ok")
        ok += 1

    del PYQT6
    _log.info("Designer plugins: %d created, %d failed", ok, len(specs) - ok)


def main():
    try:
        _create_plugins()
    except Exception:
        import traceback

        traceback.print_exc()


class TaurusWidgets(QtDesigner.QPyDesignerCustomWidgetCollectionPlugin):
    def __init__(self, parent=None):
        QtDesigner.QPyDesignerCustomWidgetCollectionPlugin.__init__(parent)
        self._widgets = None

    def customWidgets(self):
        if self._widgets is None:
            self._widgets = [w(self) for w in _plugins.values()]
        return self._widgets


if __name__ != "__main__":
    main()
