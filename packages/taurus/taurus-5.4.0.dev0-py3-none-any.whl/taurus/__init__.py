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

"""The main taurus module. It contains a reduced set of wrappers around the
real taurus model classes and information regarding the current release.
"""

__all__ = [
    "Release",
    "check_dependencies",
    "log_dependencies",
    "getSchemeFromName",
    "getValidTypesForName",
    "isValidName",
    "makeSchemeExplicit",
    "Manager",
    "Factory",
    "Device",
    "Attribute",
    "Configuration",
    "Database",
    "Authority",
    "Object",
    "Logger",
    "Critical",
    "Error",
    "Warning",
    "Info",
    "Debug",
    "Trace",
    "setLogLevel",
    "setLogFormat",
    "getLogLevel",
    "getLogFormat",
    "resetLogLevel",
    "resetLogFormat",
    "enableLogOutput",
    "disableLogOutput",
    "trace",
    "debug",
    "info",
    "warning",
    "error",
    "fatal",
    "critical",
    "deprecated",
    "changeDefaultPollingPeriod",
    "getValidatorFromName",
    "TRACE",
    "__version__",
]


from . import _release as Release
from ._taurushelper import (
    TRACE,
    Attribute,
    Authority,
    Configuration,
    Critical,
    Database,
    Debug,
    Device,
    Error,
    Factory,
    Info,
    Logger,
    Manager,
    Object,
    Trace,
    Warning,
    changeDefaultPollingPeriod,
    check_dependencies,
    critical,
    debug,
    deprecated,
    disableLogOutput,
    enableLogOutput,
    error,
    fatal,
    getLogFormat,
    getLogLevel,
    getSchemeFromName,
    getValidatorFromName,
    getValidTypesForName,
    info,
    isValidName,
    log_dependencies,
    makeSchemeExplicit,
    resetLogFormat,
    resetLogLevel,
    setLogFormat,
    setLogLevel,
    trace,
    warning,
)

__version__ = Release.version
