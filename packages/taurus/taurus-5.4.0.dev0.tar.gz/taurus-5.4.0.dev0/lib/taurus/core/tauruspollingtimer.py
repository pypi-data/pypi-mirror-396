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

"""This module contains the polling class"""

import threading
import time
import weakref

from taurus.taurusstatecontroller import ApplicationStates, application

from .util.containers import CaselessDict, CaselessWeakValueDict
from .util.log import Logger

__all__ = ["TaurusPollingTimer"]

__docformat__ = "restructuredtext"


class TaurusPollingTimer(Logger):
    """Polling timer manages a list of attributes that have to be polled in
    the same period
    """

    def __init__(self, period, parent=None):
        """Constructor

        :param period: polling period (miliseconds)
        :type period: int
        :param parent: parent object (default is None)
        :type parent: Logger
        """
        name = "TaurusPollingTimer[%d]" % period
        super(TaurusPollingTimer, self).__init__(name=name, parent=parent)
        self._period = period / 1000.0  # we store it internally in seconds
        self.dev_dict = {}
        self.attr_nb = 0
        self.timer = None
        self.lock = threading.Lock()
        self.__thread = threading.Thread(target=self.__run, name=name)
        self.__thread.daemon = True
        self._started = True
        self._finished = False
        if application.state == ApplicationStates.STARTING:
            application.application_ready_eg.subscribeEvent(
                self.on_application_ready, with_first_event=False
            )
        else:
            self.__thread.start()

    def __run(self):
        """Private Thread Function"""
        next_time = time.time() + self._period
        while True and not self._finished:
            if not self._started:
                # emulate stopped
                time.sleep(self._period)
                continue
            self._pollAttributes()
            curr_time = time.time()
            nap = max(0, next_time - curr_time)
            if curr_time > next_time:
                self.warning(
                    "loop function took more than loop interval (%ss)",
                    self._period,
                )
            next_time += self._period
            time.sleep(nap)

    def start(self):
        """Starts the polling timer"""
        self.deprecated("TaurusPollingTimer.start()", rel="4.7.1")
        self._started = True

    def stop(self, sync=False):
        """Stop the polling timer"""
        self.deprecated("TaurusPollingTimer.stop()", rel="4.7.1")
        self._started = False

    def finish(self):
        self._finished = True

    def containsAttribute(self, attribute):
        """Determines if the polling timer already contains this attribute

        :param attribute: the attribute
        :type attribute: taurus.core.taurusattribute.TaurusAttribute
        :return: True if the attribute is registered for polling or False
            otherwise
        :rtype: bool
        """
        dev, attr_name = attribute.getParentObj(), attribute.getSimpleName()
        with self.lock:
            attr_dict = self.dev_dict.get(dev)
            return attr_dict and attr_name in attr_dict

    def getAttributeCount(self):
        """Returns the number of attributes registered for polling

        :return: the number of attributes registered for polling
        :rtype: int
        """
        return self.attr_nb

    def addAttribute(self, attribute, auto_start=None):
        """Registers the attribute in this polling.

        :param attribute: the attribute to be added
        :type attribute: taurus.core.taurusattribute.TaurusAttribute
        :param auto_start: deprecated. Ignored (always autostarts)
        :type auto_start: bool
        """
        if auto_start is False:
            self.deprecated(
                "TaurusPollingTimer.addAttribute auto_start argument",
                rel="4.7.1",
            )

        with self.lock:
            dev, attr_name = (
                attribute.getParentObj(),
                attribute.getSimpleName(),
            )
            attr_dict = self.dev_dict.get(dev)
            if attr_dict is None:
                if attribute.factory().caseSensitive:
                    self.dev_dict[dev] = attr_dict = weakref.WeakValueDictionary()
                else:
                    self.dev_dict[dev] = attr_dict = CaselessWeakValueDict()
            if attr_name not in attr_dict:
                attr_dict[attr_name] = attribute
                self.attr_nb += 1

    def removeAttribute(self, attribute):
        """Unregisters the attribute from this polling. If the number of
        registered attributes decreses to 0 the polling is stopped
        automatically in order to save resources.

        :param attribute: the attribute to be added
        :type attribute: taurus.core.taurusattribute.TaurusAttribute
        """
        with self.lock:
            dev, attr_name = (
                attribute.getParentObj(),
                attribute.getSimpleName(),
            )
            attr_dict = self.dev_dict.get(dev)
            if attr_dict is None:
                return
            if attr_name in attr_dict:
                del attr_dict[attr_name]
                self.attr_nb -= 1
            if not attr_dict:
                del self.dev_dict[dev]

    def _pollAttributes(self):
        """Polls the registered attributes. This method is called by the timer
        when it is time to poll. Do not call this method directly
        """
        with self.lock:
            req_ids = {}
            dev_dict = {}
            for dev, attrs in self.dev_dict.items():
                if dev.factory().caseSensitive:
                    dev_dict[dev] = dict(attrs)
                else:
                    dev_dict[dev] = CaselessDict(attrs)

        for dev, attrs in dev_dict.items():
            try:
                req_id = dev.poll(attrs, asynch=True)
                req_ids[dev] = attrs, req_id
            except Exception:
                self.error("poll_asynch error")
                self.debug("Details:", exc_info=1)

        for dev, (attrs, req_id) in req_ids.items():
            try:
                dev.poll(attrs, req_id=req_id)
            except Exception as e:
                self.error("poll_reply error %r", e)

    def on_application_ready(self, *args):
        if not self.__thread.is_alive():
            self.__thread.start()
