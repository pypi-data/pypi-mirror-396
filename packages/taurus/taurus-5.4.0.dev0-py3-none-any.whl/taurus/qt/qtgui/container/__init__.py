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

"""This package provides generic taurus container widgets"""

from .qcontainer import QGroupWidget
from .taurusbasecontainer import TaurusBaseContainer
from .taurusframe import TaurusFrame
from .taurusgroupbox import TaurusGroupBox
from .taurusgroupwidget import TaurusGroupWidget
from .taurusmainwindow import TaurusMainWindow
from .taurusscrollarea import TaurusScrollArea
from .tauruswidget import TaurusWidget

__all__ = [
    "QGroupWidget",
    "TaurusBaseContainer",
    "TaurusFrame",
    "TaurusWidget",
    "TaurusGroupBox",
    "TaurusGroupWidget",
    "TaurusScrollArea",
    "TaurusMainWindow",
]
__docformat__ = "restructuredtext"
