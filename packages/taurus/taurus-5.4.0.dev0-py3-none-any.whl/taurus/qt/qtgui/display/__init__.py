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

"""This package contains a collection of taurus widgets designed to display
taurus information, typically in a read-only fashion (no user interaction is
possible). Examples of widgets that suite this rule are labels, leds and LCDs
"""

from .qfallback import (
    QFallBackWidget,
    TaurusFallBackWidget,
    create_fallback,
    create_taurus_fallback,
)
from .qled import LedColor, LedSize, LedStatus, QLed
from .qlogo import QLogo
from .qpixmapwidget import QPixmapWidget
from .qsevensegment import Q7SegDigit
from .tauruslabel import TaurusLabel
from .tauruslcd import TaurusLCD
from .taurusled import TaurusLed

__all__ = [
    "create_fallback",
    "create_taurus_fallback",
    "QFallBackWidget",
    "TaurusFallBackWidget",
    "QPixmapWidget",
    "LedColor",
    "LedStatus",
    "LedSize",
    "QLed",
    "QLogo",
    "Q7SegDigit",
    "TaurusLabel",
    "TaurusLed",
    "TaurusLCD",
]

__docformat__ = "restructuredtext"
