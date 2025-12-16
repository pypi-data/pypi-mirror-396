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

"""This package provides a set of taurus wiget utilities like color management,
configuration, actions.
"""

__docformat__ = "restructuredtext"

from .qdraganddropdebug import DropDebugger
from .taurusaction import (
    AttributeAllConfigAction,
    AttributeHistoryAction,
    AttributeImageDisplayAction,
    AttributeMenu,
    AttributeMonitorDeviceAction,
    ConfigurationMenu,
    ExternalAppAction,
    SeparatorAction,
    TaurusAction,
    TaurusMenu,
)
from .taurusactionfactory import ActionFactory
from .tauruscolor import (
    QT_ATTRIBUTE_QUALITY_PALETTE,
    QT_DEVICE_STATE_PALETTE,
    QtColorPalette,
)
from .taurusscreenshot import Grabber, grabWidget
from .tauruswidgetfactory import TaurusWidgetFactory, getWidgetsOfType
from .ui import UILoadable, loadUi
from .validator import PintValidator

__all__ = [
    "ActionFactory",
    "ExternalAppAction",
    "TaurusMenu",
    "TaurusAction",
    "SeparatorAction",
    "AttributeHistoryAction",
    "AttributeAllConfigAction",
    "AttributeMonitorDeviceAction",
    "AttributeImageDisplayAction",
    "AttributeMenu",
    "ConfigurationMenu",
    "QtColorPalette",
    "QT_DEVICE_STATE_PALETTE",
    "QT_ATTRIBUTE_QUALITY_PALETTE",
    "TaurusWidgetFactory",
    "getWidgetsOfType",
    "Grabber",
    "grabWidget",
    "DropDebugger",
    "loadUi",
    "UILoadable",
    "PintValidator",
]
