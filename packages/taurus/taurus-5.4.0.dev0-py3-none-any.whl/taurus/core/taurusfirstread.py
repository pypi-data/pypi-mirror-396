#!/usr/bin/env python

# ###########################################################################
#
# This file is part of Taurus
#
# http://taurus-scada.org
#
# Copyright 2025 CELLS / ALBA Synchrotron, Bellaterra, Spain
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

import queue
import threading
import time
import traceback
import weakref
from typing import Optional

from taurus.taurusstatecontroller import ApplicationStates, application

from . import TaurusAttribute
from .util.containers import CaselessWeakValueDict
from .util.log import Logger
from .util.singleton import Singleton

__all__ = ["TaurusFirstRead"]

__docformat__ = "restructuredtext"


class TaurusFirstRead(Singleton, Logger):
    """First read manages a list of attributes that have to be read in
    the same period.

    The helper runs a lightweight background thread that consumes an internal
    queue and performs a one-shot poll for every attribute requested. The
    thread auto-stops after a period of inactivity and is transparently
    restarted on demand whenever a new attribute is enqueued.
    """

    # Time (seconds) of inactivity before the worker stops itself.
    _idle_timeout_secs = 3.0

    _instance = None
    _lock = threading.Lock()
    _thread = None

    def __init__(self):
        pass

    def init(self):
        """Initializes the internal state and starts the background reading thread.

        This method is intended to be called only once, during the first creation of
        the singleton instance. It sets up the task queue, control flags, and launches
        a daemon thread that continuously processes attribute read requests.

        It uses an internal `_initialized` flag to prevent repeated initialization in
        case the method is accidentally invoked more than once.
        """
        name = self.__class__.__name__
        self.call__init__(Logger, name)

        if not hasattr(self, "_initialized"):
            self._initialized = True
            self._task_queue = queue.Queue()
            self._stop_event = threading.Event()
            self.execute()

    def execute(self, force_restart: bool = False):
        """Start the worker thread if needed, optionally forcing a restart.

        The worker is restarted on demand when ``force_restart`` is True, clearing
        the stop flag. If a live worker already exists and ``force_restart`` is
        False, this is a no-op.
        """
        if self._thread is not None and self._thread.is_alive():
            if not force_restart:
                return
            self.stop(wait=False)
            try:
                self._thread.join(timeout=0.1)
            except Exception as e:
                self.warning(f"Unable to join FirstReadThread:{self._thread}\n{e}")
            finally:
                if self._thread is not None and self._thread.is_alive():
                    self.warning("FirstRead thread still alive after join timeout")
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def _ensure_thread_running(self):
        """Guarantee that a worker thread is running before enqueuing work."""
        if self._thread is None or not self._thread.is_alive():
            self.execute()

    def _run(self):
        """Worker loop that polls attributes in batches until idle timeout."""
        _processed = 0
        _batch_count = 0
        last_activity = time.monotonic()
        while True:
            attr_dict = {}
            try:
                attribute = self._task_queue.get(timeout=0.1)
                last_activity = time.monotonic()
            except queue.Empty:
                now = time.monotonic()
                if self._stop_event.is_set():
                    break
                if (
                    application.state == ApplicationStates.STARTED
                    and (now - last_activity) >= self._idle_timeout_secs
                ):
                    self._stop_event.set()
                continue

            if attribute.factory().caseSensitive:
                attr_dict = weakref.WeakValueDictionary()
            else:
                attr_dict = CaselessWeakValueDict()

            try:
                dev, attr_name = (
                    attribute.getParentObj(),
                    attribute.getSimpleName(),
                )
                attr_dict[attr_name] = attribute
                req_id = dev.poll(attr_dict, asynch=True)
                dev.poll(attr_dict, req_id=req_id)
            except Exception as e:
                self.error(f"Problems in FirstRead thread:{attr_name}\n{e}")
                self.error(traceback.format_exc())
            finally:
                _processed += 1
                _batch_count += 1
                self._task_queue.task_done()
                if self._task_queue.empty():
                    last_activity = time.monotonic()

        self.info(f"Ending FirstRead thread. Attributes processed: {_processed}")

    def stop(self, wait: bool = False, timeout: Optional[float] = None):
        """Request thread shutdown and optionally wait until it finishes.

        :param wait: If True, drain pending work and block until the thread finishes.
        :param timeout: Max seconds to wait when ``wait`` is True.
        """
        self._stop_event.set()
        if wait:
            # Ensure we do not exit before processing everything already queued
            self._task_queue.join()
            if self._thread is not None:
                self._thread.join(timeout=timeout)
        self._thread = None

    def addAttribute(self, attr: TaurusAttribute):
        """Adds an attribute to the queue for asynchronous reading.

        The attribute will be processed by the internal background thread that batches
        reads occurring within the same polling period. This allows grouping and
        optimizing communication with devices.

        :param attr: Object to be read.
        :type attr: TaurusAttribute
        """
        self._ensure_thread_running()
        self._task_queue.put(attr, block=False)

    def wait_until_idle(self):
        """Block until all queued attributes have been processed."""
        self._task_queue.join()
