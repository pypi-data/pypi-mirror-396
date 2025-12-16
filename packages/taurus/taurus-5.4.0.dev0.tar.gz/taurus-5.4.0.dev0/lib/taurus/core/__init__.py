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

"""The core module"""

import taurus.tauruscustomsettings

from .taurusbasetypes import (  # noqa: F401
    AttrAccess,
    AttrQuality,
    DataFormat,
    DataType,
    DisplayLevel,
    LockStatus,
    ManagerState,
    MatchLevel,
    OperationMode,
    SubscriptionState,
    TaurusAttrValue,
    TaurusConfigValue,
    TaurusDevState,
    TaurusElementType,
    TaurusEventType,
    TaurusLockInfo,
    TaurusModelValue,
    TaurusSerializationMode,
    TaurusSWDevHealth,
    TaurusSWDevState,
    TaurusTimeVal,
)

__docformat__ = "restructuredtext"

__all__ = [
    "OperationMode",
    "TaurusSerializationMode",
    "SubscriptionState",
    "TaurusEventType",
    "MatchLevel",
    "TaurusElementType",
    "LockStatus",
    "DataFormat",
    "AttrQuality",
    "AttrAccess",
    "DisplayLevel",
    "ManagerState",
    "TaurusTimeVal",
    "TaurusAttrValue",
    "TaurusConfigValue",
    "DataType",
    "TaurusLockInfo",
    "TaurusDevState",
    "TaurusModelValue",
]

# import more stuff here for backwards-compatibility if required
if not getattr(taurus.tauruscustomsettings, "LIGHTWEIGHT_IMPORTS", False):
    from .. import _release as Release  # noqa: F401
    from .taurusattribute import *  # noqa: F403,F401
    from .taurusauthority import *  # noqa: F403,F401
    from .taurusconfiguration import *  # noqa: F403,F401
    from .taurusdevice import *  # noqa: F403,F401
    from .taurusexception import *  # noqa: F403,F401
    from .taurusfactory import *  # noqa: F403,F401
    from .tauruslistener import *  # noqa: F403,F401
    from .taurusmanager import *  # noqa: F403,F401
    from .taurusmodel import *  # noqa: F403,F401
    from .taurusoperation import *  # noqa: F403,F401
    from .tauruspollingtimer import *  # noqa: F403,F401
    from .taurusvalidator import *  # noqa: F403,F401
    from .units import *  # noqa: F403,F401
