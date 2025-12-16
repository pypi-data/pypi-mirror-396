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
This module includes the current application state (the state will be NONE if there
is no TaurusApplication running)
"""

from enum import Enum

from taurus.core.util.event import EventGenerator

ApplicationStates = Enum("ApplicationStates", ["NONE", "STARTING", "STARTED"])


class ApplicationState:
    state = ApplicationStates.NONE
    application_ready_eg = EventGenerator("application_ready_event")

    def application_starting(self):
        self.state = ApplicationStates.STARTING

    def application_started(self):
        self.state = ApplicationStates.STARTED
        self.application_ready_eg.fireEvent()


application = ApplicationState()
