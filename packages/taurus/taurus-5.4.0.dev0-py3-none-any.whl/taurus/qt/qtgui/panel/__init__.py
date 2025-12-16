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

"""This package contains a collection of taurus Qt widgets representing various
panels like forms or panels to be inserted in dialogs
"""

from .qdataexportdialog import QDataExportDialog  # noqa: I001 - taurusmodelchooser must be imported before devicepanel
from .qdoublelist import QDoubleListDlg
from .qrawdatachooser import QRawDataWidget
from .taurusconfigeditor import QConfigEditor
from .taurusconfigurationpanel import (
    TangoConfigLineEdit,
    TaurusConfigLineEdit,
    TaurusConfigurationPanel,
)
from .taurusmodelchooser import (
    TaurusModelChooser,
    TaurusModelSelector,
    TaurusModelSelectorItem,
    TaurusModelSelectorTree,
)
from .taurusdevicepanel import TaurusDevicePanel, TaurusDevPanel
from .taurusform import TaurusAttrForm, TaurusCommandsForm, TaurusForm
from .taurusinputpanel import TaurusInputPanel
from .taurusmessagepanel import (
    MacroServerMessageErrorHandler,
    TangoMessageErrorHandler,
    TaurusMessageErrorHandler,
    TaurusMessagePanel,
)
from .taurusmodellist import TaurusModelItem, TaurusModelList, TaurusModelModel
from .taurusvalue import (
    DefaultLabelWidget,
    DefaultReadWidgetLabel,
    DefaultTaurusValueCheckBox,
    DefaultUnitsWidget,
    TaurusArrayEditorButton,
    TaurusDevButton,
    TaurusImageButton,
    TaurusPlotButton,
    TaurusValue,
    TaurusValuesFrame,
    TaurusValuesTableButton,
    TaurusValuesTableButton_W,
)

__all__ = [
    "QRawDataWidget",
    "QDataExportDialog",
    "TaurusMessagePanel",
    "TaurusMessageErrorHandler",
    "TangoMessageErrorHandler",
    "MacroServerMessageErrorHandler",
    "TaurusInputPanel",
    "TaurusModelSelectorTree",
    "TaurusModelChooser",
    "TaurusModelSelector",
    "TaurusModelSelectorItem",
    "TaurusValue",
    "TaurusValuesFrame",
    "DefaultTaurusValueCheckBox",
    "DefaultUnitsWidget",
    "TaurusPlotButton",
    "TaurusArrayEditorButton",
    "TaurusValuesTableButton",
    "TaurusValuesTableButton_W",
    "DefaultLabelWidget",
    "DefaultReadWidgetLabel",
    "TaurusDevButton",
    "TaurusImageButton",
    "TaurusAttrForm",
    "TaurusCommandsForm",
    "TaurusForm",
    "TaurusModelModel",
    "TaurusModelItem",
    "TaurusModelList",
    "QConfigEditor",
    "QDoubleListDlg",
    "TaurusDevicePanel",
    "TaurusDevPanel",
    "TaurusConfigurationPanel",
    "TangoConfigLineEdit",
    "TaurusConfigLineEdit",
]
__docformat__ = "restructuredtext"
