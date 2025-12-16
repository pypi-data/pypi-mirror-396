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

from importlib import import_module

from taurus import Logger
from taurus.external.qt import PYSIDE6
from taurus.qt.qtdesigner.tauruswidgetmap import _DEFAULT_TAURUS_WIDGET_CATALOG

_PYSIDE6_FILTER_OUT_WIDGETS = [
    "TaurusBoolRW",
    "TaurusLabelEditRW",
    "AboutDialog",  # It does loadUIC
    "HelpPanel",
    "QWheelEdit",
    "TaurusWheelEdit",
    "TaurusGrid",
    "TaurusImageDialog",  # In qt6 qwt is no longer supported
    "TaurusTrend2DDialog",  # In qt6 qwt is no longer supported
]

if PYSIDE6:
    _log = Logger(__name__)
    _log.setLogLevel(Logger.Debug)

    from taurus.external.qt.QtDesigner import (
        QPyDesignerCustomWidgetCollection,
    )

    ok = 0
    skipped = 0

    # use explicit list of specs instead of original approach of instrospecting
    # with TaurusWidgetFactory().getWidgetClasses()
    # TODO: complement specs with an entry-point
    specs = _DEFAULT_TAURUS_WIDGET_CATALOG
    for spec in specs:
        spec = spec.strip()
        msg = spec + " : "
        try:
            assert ":" in spec, "expected 'modname:classname'"
            _mod_name, _cls_name = spec.rsplit(":", maxsplit=1)
            if _cls_name in _PYSIDE6_FILTER_OUT_WIDGETS:
                skipped += 1
                continue
            widget_class = getattr(import_module(_mod_name), _cls_name)
        except Exception as e:
            _log.warning(msg + "error importing: %s", e)
            # _log.debug(traceback.format_exc())
            continue

        try:
            qt_info = widget_class.getQtDesignerPluginInfo()
            assert qt_info is not None, "getQtDesignerPluginInfo() -> None"
            assert "module" in qt_info, "'module' key not available"
        except Exception as e:
            _log.warning(msg + "error getting plugin info: %s", e)
            # _log.debug(traceback.format_exc())
            continue

        instance_name = _cls_name[:1].lower() + _cls_name[1:]
        xml = (
            f"<ui language='c++'><widget class='{_cls_name}' "
            f"name='{instance_name}'></widget></ui>"
        )
        try:
            # dynamically register taurus widgets classes
            _log.trace(str(qt_info))
            QPyDesignerCustomWidgetCollection.registerCustomWidget(
                widget_class,
                xml=qt_info.get("xml", xml),
                tool_tip=qt_info.get("tool_tip", _cls_name),
                icon=qt_info.get("icon", None),
                group=qt_info.get("group", "Taurus"),
                module=_mod_name,
                container=qt_info.get("container", False),
            )
        except Exception as e:
            _log.warning(msg + "error creating plugin: %s", e)
            # _log.debug(traceback.format_exc())
            continue

        # if we got here, everything went fine for this
        _log.info(msg + "ok")
        ok += 1

    _log.info(
        "Designer plugins: %d created, %d skipped, %d failed",
        ok,
        skipped,
        len(specs) - ok - skipped,
    )
