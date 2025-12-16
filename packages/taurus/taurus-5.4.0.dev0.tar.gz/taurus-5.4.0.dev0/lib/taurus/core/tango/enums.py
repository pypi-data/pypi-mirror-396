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

"""This module contains all basic tango enumerations"""

__docformat__ = "restructuredtext"

from enum import IntEnum

import numpy
import tango

from taurus.core.util.enumeration import Enumeration

TangoObjectType = Enumeration(
    "TangoObjectType",
    [
        "Authority",
        "Server",
        "Class",
        "Device",
        "Attribute",
        "Property",
        "Configuration",
        "Object",
    ],
)
TangoObjectType.Database = TangoObjectType.Authority  # backwards compatibility


# The exception reasons that will force switching from events to polling
# API_AttributePollingNotStarted - the attribute does not support events.
#     Don't try to resubscribe.
# API_DSFailedRegisteringEvent - same exception then the one above but higher
#     in the stack
# API_NotificationServiceFailed - Problems in notifd, it was not able to
#     register the event.
# API_EventChannelNotExported - the notifd is not running
# API_EventTimeout - after a successfull register the the device server
#     and/or notifd shuts down/crashes
# API_CommandNotFound - Added on request from ESRF (Matias Guijarro). They have
#     a DS in java (doesn't have events) and the only way they
#     found to fix the event problem was to add this exception
#     type here. Maybe in future this will be solved in a better way
# API_BadConfigurationProperty - the device server is not running
EVENT_TO_POLLING_EXCEPTIONS = (
    "API_AttributePollingNotStarted",
    "API_DSFailedRegisteringEvent",
    "API_NotificationServiceFailed",
    "API_EventChannelNotExported",
    "API_EventTimeout",
    "API_EventPropertiesNotSet",
    "API_CommandNotFound",
    "API_PollObjNotFound",
)
#                                   'API_BadConfigurationProperty')

TIMEOUT_EXCEPTION = "API_DeviceTimedOut"

FROM_TANGO_TO_NUMPY_TYPE = {
    tango.DevVoid: None,
    tango.DevBoolean: numpy.bool_,
    tango.DevUChar: numpy.uint8,
    tango.DevShort: numpy.short,
    tango.DevUShort: numpy.ushort,
    tango.DevLong: numpy.int32,
    tango.DevULong: numpy.uint32,
    tango.DevLong64: numpy.int64,
    tango.DevULong64: numpy.uint64,
    tango.DevString: str,
    tango.DevDouble: numpy.float64,
    tango.DevFloat: numpy.float32,
    tango.DevEnum: numpy.ushort,
}

FROM_TANGO_TO_STR_TYPE = {
    tango.DevVoid: None,
    tango.DevBoolean: "bool",
    tango.DevUChar: "uint8",
    tango.DevShort: "short",
    tango.DevUShort: "ushort",
    tango.DevLong: "int32",
    tango.DevULong: "uint32",
    tango.DevLong64: "int64",
    tango.DevULong64: "uint64",
    tango.DevString: "str",
    tango.DevDouble: "float64",
    tango.DevFloat: "float32",
    tango.DevEnum: "str",
}


class DevState(IntEnum):
    """This is the taurus.core.tango equivalent to tango.DevState.
    It defines the same members and uses the same numerical values internally,
    allowing equality comparisons with :class:`tango.DevState` (but not
    identity checks!)::

        from taurus.core.tango import DevState as D1
        from tango import DevState as D2

        D1.OPEN == D2.OPEN          # --> True
        D1.OPEN in (D2.ON, D2.OPEN) # --> True
        D1.OPEN == 3                # --> True
        D1.OPEN is 3                # --> False
        D1.OPEN is D2.OPEN          # --> False
    """

    ON = 0
    OFF = 1
    CLOSE = 2
    OPEN = 3
    INSERT = 4
    EXTRACT = 5
    MOVING = 6
    STANDBY = 7
    FAULT = 8
    INIT = 9
    RUNNING = 10
    ALARM = 11
    DISABLE = 12
    UNKNOWN = 13

    def __str__(self):
        return "{}.{}".format(self.__class__.__name__, self.name)
