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
resfactory.py:
"""

import importlib
import os
from collections.abc import Mapping

from taurus import Manager
from taurus.core.taurusexception import TaurusException
from taurus.core.taurusfactory import TaurusFactory
from taurus.core.util.log import Logger
from taurus.core.util.singleton import Singleton


class ResourcesFactory(Singleton, TaurusFactory, Logger):
    """A Singleton class designed to provide Simulation related objects."""

    #: the list of schemes that this factory supports. For this factory: 'res'
    #: and 'resources' are the supported schemes
    schemes = (
        "res",
        "resource",
    )

    #: the default resource file name
    DftResourceName = "taurus_resources.py"

    #: priority for the default resource
    DftResourcePriority = 10

    def __init__(self):
        """Initialization. Nothing to be done here for now."""
        pass

    def init(self, *args, **kwargs):
        """Singleton instance initialization.
        **For internal usage only**
        """
        name = self.__class__.__name__
        self.call__init__(Logger, name)
        self.call__init__(TaurusFactory)
        self.clear()

    def clear(self):
        self._resource_map = {}
        self._resource_priority = {}
        self._resource_priority_keys = []
        self._resource_count = 0

    def reloadResource(self, obj=None, priority=1, name=None):
        """(Re)Loads the given resource.

        :param obj: the resource object. Default is None meaning in will
            (re)load the default resource: taurus_resources.py from the
            application directory
        :type obj: dict or file or None
        :param priority: the resource priority. Default is 1 meaning maximum
            priority
        :type priority: int
        :param name: an optional name to give to the resource
        :type name: str
        :return: a dictionary version of the given resource object
        :rtype: dict
        """
        if priority < 1:
            raise ValueError("priority must be >=1")
        if isinstance(obj, Mapping):
            name = name or "DICT%02d" % priority
        elif type(obj) in (str,) or obj is None:
            name, mod = self.__reloadResource(obj)
            obj = {}
            for k, v in mod.__dict__.items():
                if not k.startswith("_") and isinstance(v, str):
                    obj[k] = v
        else:
            raise TypeError

        if self._resource_map.get(name) is None:
            self._resource_count += 1
        self._resource_map[name] = obj
        if self._resource_count == 1:
            self._first_resource = obj

        pl = self._resource_priority.get(priority)
        if pl is None:
            self._resource_priority[priority] = pl = []
        pl.append(name)
        self._resource_priority_keys = list(self._resource_priority.keys())
        self._resource_priority_keys.sort()
        return obj

    loadResource = reloadResource
    loadResource.__doc__ = reloadResource.__doc__

    def __reloadResource(self, name=None):
        path = os.path.curdir
        if name is None:
            file_name = ResourcesFactory.DftResourceName
        else:
            path, file_name = os.path.split(name)
            if not path:
                path = os.path.curdir
        path = os.path.abspath(path)

        full_name = os.path.join(path, file_name)

        if not os.path.isfile(full_name):
            raise ImportError

        module_name, ext = os.path.splitext(file_name)

        # import module from path
        _spec = importlib.util.spec_from_file_location(module_name, full_name)
        m = importlib.util.module_from_spec(_spec)
        _spec.loader.exec_module(m)

        return full_name, m

    def getValue(self, key):
        """Returns the value for a given key

        :param key: a key
        :type key: str
        :return: the value for the given key
        :rtype: str
        """
        if self._resource_count == 0:
            try:
                self.reloadResource(priority=self.DftResourcePriority)
            except Exception:
                return None

        # optimization: many applications contain only one resource: in that
        # case avoid the loop
        if self._resource_count == 1:
            return self._first_resource.get(key, None)

        for p in self._resource_priority_keys:
            for resource_name in self._resource_priority[p]:
                resource = self._resource_map[resource_name]
                try:
                    return resource[key]
                except Exception:
                    pass

    def findObjectClass(self, absolute_name):
        """
        Obtain the class object corresponding to the given name.

        :param absolute_name: the object absolute name string
        :type absolute_name: str
        :return: the class for the model object mapped by absolute_name, or
            None if absolute_name is invalid.
        :rtype: taurus.core.taurusmodel.TaurusModel or None
        """
        validators = (
            self.getAttributeNameValidator(),
            self.getDeviceNameValidator(),
            self.getAuthorityNameValidator(),
        )

        for v in validators:
            try:
                value = self.getValue(v.getUriGroups(absolute_name)["_resname"])
                return Manager().findObjectClass(value)
            except Exception:
                pass
        return None

    def getAuthority(self, name=None):
        """
        Obtain the authority model object referenced by name.

        :param name: name
        :type name: str
        :return: authority object :raise:
            (taurus.core.taurusexception.TaurusException) if name is invalid
        :rtype: taurus.core.taurusauthority.TaurusAuthority
        """
        groups = self.getAuthorityNameValidator().getUriGroups(name)
        if groups is None:
            raise TaurusException('Invalid name "%s"' % name)
        res_name = groups["_resname"]
        value = self.getValue(res_name)
        return Manager().getAuthority(value)

    def getDevice(self, name):
        """
        Obtain the device model object referenced by name.

        :param name: name
        :type name: str
        :return: device object :raise:
            (taurus.core.taurusexception.TaurusException) if name is invalid
        :rtype: taurus.core.taurusdevice.TaurusDevice
        """
        groups = self.getDeviceNameValidator().getUriGroups(name)
        if groups is None:
            raise TaurusException('Invalid name "%s"' % name)
        res_name = groups["_resname"]
        value = self.getValue(res_name)
        return Manager().getDevice(value)

    def getAttribute(self, name):
        """
        Obtain the attribute model object referenced by name.

        :param name: name
        :type name: str
        :return: attribute object :raise:
            (taurus.core.taurusexception.TaurusException) if name is invalid
        :rtype: taurus.core.taurusattribute.TaurusAttribute
        """
        groups = self.getAttributeNameValidator().getUriGroups(name)
        if groups is None:
            raise TaurusException('Invalid name "%s"' % name)
        res_name = groups["_resname"]
        value = self.getValue(res_name)
        return Manager().getAttribute(value)

    def getAuthorityNameValidator(self):
        """Return ResourceAuthorityNameValidator"""
        from . import resvalidator

        return resvalidator.ResourceAuthorityNameValidator()

    def getDeviceNameValidator(self):
        """Return ResourceDeviceNameValidator"""
        from . import resvalidator

        return resvalidator.ResourceDeviceNameValidator()

    def getAttributeNameValidator(self):
        """Return ResourceAttributeNameValidator"""
        from . import resvalidator

        return resvalidator.ResourceAttributeNameValidator()
