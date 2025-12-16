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

"""This package contains a collection of taurus Qt widgets that typically
interact with the user. Examples are line edits, comboboxes and checkboxes"""

from .choicedlg import GraphicalChoiceDlg, GraphicalChoiceWidget
from .qwheel import QWheelEdit
from .tauruscheckbox import TaurusValueCheckBox
from .tauruscombobox import TaurusAttrListComboBox, TaurusValueComboBox
from .tauruslineedit import TaurusValueLineEdit
from .taurusspinbox import TaurusValueSpinBox, TaurusValueSpinBoxEx
from .tauruswheel import TaurusWheelEdit

__all__ = [
    "QWheelEdit",
    "TaurusValueCheckBox",
    "TaurusAttrListComboBox",
    "TaurusValueComboBox",
    "TaurusValueLineEdit",
    "TaurusValueSpinBox",
    "TaurusValueSpinBoxEx",
    "TaurusWheelEdit",
    "GraphicalChoiceDlg",
    "GraphicalChoiceWidget",
]
__docformat__ = "restructuredtext"
