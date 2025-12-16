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

"""a list of helper methods"""

import inspect
import logging
import os
import re
import sys
import threading
import traceback
import warnings
import weakref
from collections import defaultdict

import click

from taurus import tauruscustomsettings

__docformat__ = "restructuredtext"

# regexp for finding the scheme
__SCHEME_RE = re.compile(r"([^:/?#]+):.*")


def check_dependencies():
    """
    Prints a check-list of requirements and marks those that are fulfilled
    """

    # non_pypi is a dictionary with extra:req_list and req_list is a list of
    # (reqname, check) tuples where reqname is the name of a requirement and
    # check is a function that raises an exception if the requirement is not
    # fulfilled

    import pkg_resources

    d = pkg_resources.get_distribution("taurus")
    print("Dependencies for %s:" % d)
    # minimum requirements (without extras)
    for r in d.requires():
        try:
            pkg_resources.require(str(r))
            print("\t[*]", end=" ")
        except Exception:
            print("\t[ ]", end=" ")
        print("%s" % r)
    # requirements for the extras
    print("\nExtras:")
    for extra in sorted(d.extras):
        print("Dependencies for taurus[%s]:" % extra)
        # requirements from PyPI
        for r in d.requires(extras=[extra]):
            try:
                r = str(r).split(";")[0]  # remove marker if present (see #612)
                pkg_resources.require(r)
                print("\t[*]", end=" ")
            except Exception:
                print("\t[ ]", end=" ")
            print("%s" % r)


def log_dependencies():
    """deprecated since '4.0.4'"""
    from taurus import deprecated

    deprecated(dep="taurus.log_dependencies", rel="4.0.4")


def getSchemeFromName(name, implicit=True):
    """Return the scheme from a taurus name.

    :param name: taurus model name URI.
    :type name: str
    :param implicit: controls whether to return the default scheme (if implicit
        is True -default-) or None (if implicit is False) in case `model` does
        not contain the scheme name explicitly. The default scheme may be
        defined in :ref:`tauruscustomsettings` ('tango' is assumed if not
        defined)
    :type implicit: bool
    """
    m = __SCHEME_RE.match(name)
    if m is not None:
        return m.groups()[0]
    if implicit:
        return getattr(tauruscustomsettings, "DEFAULT_SCHEME", "tango")
    else:
        return None


def getValidatorFromName(name):
    """Helper for obtaining the validator object corresponding to the
    given name.

    :return: model name validator or None if name is not a supported model name
    """

    try:
        factory = Factory(scheme=getSchemeFromName(name))
    except Exception:
        return None
    return factory.getValidatorFromName(name)


def makeSchemeExplicit(name, default=None):
    """return the name guaranteeing that the scheme is present. If name already
    contains the scheme, it is returned unchanged.

    :param name: taurus model name URI.
    :type name: str
    :param default: The default scheme to use. If no default is passed, the one
        defined in tauruscustomsettings.DEFAULT_SCHEME is used.
    :type default: str
    :return: the name with the explicit scheme.
    """
    if getSchemeFromName(name, implicit=False) is None:
        if default is None:
            default = getattr(tauruscustomsettings, "DEFAULT_SCHEME", "tango")
        return "%s:%s" % (default, name)
    else:
        return name


def getValidTypesForName(name, strict=None):
    """
    Returns a list of all Taurus element types for which `name` is a valid
    model name (while in many cases a name may only be valid for one
    element type, this is not necessarily true in general)

    :param name: taurus model name
    :type name: str
    :param strict: If True, names that are not RFC3986-compliant but which
        would be accepted for backwards compatibility are considered valid.
    :type strict: bool
    :return: where element can be one of: `Attribute`, `Device` or `Authority`
    :rtype: list<TaurusElementType.element>
    """
    try:
        factory = Factory(scheme=getSchemeFromName(name))
    except Exception:
        return []
    return factory.getValidTypesForName(name, strict=strict)


def isValidName(name, etypes=None, strict=None):
    """Returns True is the given name is a valid Taurus model name. If
    `etypes` is passed, it returns True only if name is valid for at least
    one of the given the element types. Otherwise it returns False.
    For example::

        isValidName('tango:foo')--> True
        isValidName('tango:a/b/c', [TaurusElementType.Attribute]) --> False

    :param name: the string to be checked for validity
    :type name: str
    :param etypes: if given, names will only be considered valid if they
        represent one of the given element types. Supported element types are:
        `Attribute`, `Device` and `Authority`
    :type etypes: seq<TaurusElementType>
    :param strict: If True, names that are not RFC3986-compliant but which
        would be accepted for backwards compatibility are considered valid.
    :type strict: bool
    :return:
    :rtype: bool
    """
    validtypes = getValidTypesForName(name, strict=strict)
    if etypes is None:
        return bool(validtypes)
    for e in etypes:
        if e in validtypes:
            return True
    return False


def Manager():
    """Returns the one and only TaurusManager

    It is a shortcut to::

        import taurus.core
        manager = taurus.core.taurusmanager.TaurusManager()

    :return: the TaurusManager
    :rtype: :class:`taurus.core.taurusmanager.TaurusManager`

    .. seealso:: :class:`taurus.core.taurusmanager.TaurusManager`
    """
    from taurus.core.taurusmanager import TaurusManager

    return TaurusManager()


def Factory(scheme=None):
    """Returns the one and only Factory for the given scheme

    It is a shortcut to::

        import taurus.core.taurusmanager
        manager = taurus.core.taurusmanager.TaurusManager()
        factory = manager.getFactory(scheme)

    :param scheme: a string representing the scheme. Default value is None
        meaning ``tango`` scheme
    :type scheme: str
    :return: a taurus factory
    :rtype: :class:`taurus.core.taurusfactory.TaurusFactory`
    """
    manager = Manager()
    f = manager.getFactory(scheme=scheme)
    if f is None:
        from taurus.core.taurusexception import TaurusException

        if scheme is None:
            scheme = "default scheme '" + manager.default_scheme + "'"
        else:
            scheme = "'" + scheme + "'"
        raise TaurusException("Cannot create Factory for %s" % scheme)
    return f()


def Device(device_name):
    """Returns the taurus device for the given device name

    It is a shortcut to::

        import taurus.core.taurusmanager
        manager = taurus.core.taurusmanager.TaurusManager()
        factory = manager.getFactory()
        device  = factory.getDevice(device_name)

    :param device_name: the device name
    :type device_name: str
    :return: a taurus device
    :rtype: :class:`taurus.core.taurusdevice.TaurusDevice`
    """
    return Factory(scheme=getSchemeFromName(device_name)).getDevice(device_name)


def Attribute(dev_or_attr_name, attr_name=None):
    """Returns the taurus attribute for either the pair (device name, attribute
    name) or full attribute name

    - Attribute(full_attribute_name)
    - Attribute(device_name, attribute_name)

    It is a shortcut to::

        import taurus.core.taurusmanager
        manager = taurus.core.taurusmanager.TaurusManager()
        factory = manager.getFactory()
        attribute  = factory.getAttribute(full_attribute_name)

    or::

        import taurus.core.taurusmanager
        manager = taurus.core.taurusmanager.TaurusManager()
        factory = manager.getFactory()
        device  = factory.getDevice(device_name)
        attribute = device.getAttribute(attribute_name)

    :param dev_or_attr_name: the device name or full attribute name
    :type dev_or_attr_name: str or TaurusDevice
    :param attr_name: attribute name
    :type attr_name: str
    :return: a taurus attribute
    :rtype: :class:`taurus.core.taurusattribute.TaurusAttribute`
    """

    if attr_name is None:
        return Factory(scheme=getSchemeFromName(dev_or_attr_name)).getAttribute(
            dev_or_attr_name
        )
    else:
        if isinstance(dev_or_attr_name, str):
            dev = Device(dev_or_attr_name)
        else:
            dev = dev_or_attr_name
        return dev.getAttribute(attr_name)


def Configuration(attr_or_conf_name, conf_name=None):
    """Deprecated"""
    from taurus.core.util.log import deprecated

    deprecated(dep="Configuration", alt="Attribute", rel="4.0")
    return Attribute(attr_or_conf_name)


def Database(name=None):
    """Deprecated"""
    from taurus.core.util.log import deprecated

    deprecated(dep="Database", alt="Authority", rel="4.0")
    return Authority(name=name)


def Authority(name=None):
    """Returns a taurus authority

    It is a shortcut to::

        import taurus.core.taurusmanager
        manager = taurus.core.taurusmanager.TaurusManager()
        factory = manager.getFactory()
        db  = factory.getAuthority(dname)

    :param name: authority name. If None (default) it will return the default
        authority of the default scheme. For example, if the default scheme is
        tango, it will return the default TANGO_HOST database
    :type name: str or None
    :return: a taurus authority
    :rtype: :class:`taurus.core.taurusauthority.TaurusAuthority`
    """
    return Factory(getSchemeFromName(name or "")).getAuthority(name)


def Object(*args):
    """Returns an taurus object of given class for the given name

    Can be called as:

      - Object(name)
      - Object(cls, name)

    Where:

      - `name` is a model name (str)
      - `cls` is a class derived from TaurusModel

    If `cls` is not given, Object() will try to guess it from `name`.

    :return: a taurus object
    :rtype: :class:`taurus.core.taurusmodel.TaurusModel`
    """
    if len(args) == 1:
        klass, name = None, args[0]
    elif len(args) == 2:
        klass, name = args
    else:
        msg = "Object() takes either 1 or 2 arguments (%i given)" % len(args)
        raise TypeError(msg)
    factory = Factory(getSchemeFromName(name))
    if klass is None:
        klass = factory.findObjectClass(name)
    return factory.getObject(klass, name)


@click.command("check-deps")
def check_dependencies_cmd():
    """
    Shows the taurus dependencies and checks if they are available
    """
    check_dependencies()


def changeDefaultPollingPeriod(period):
    Manager().changeDefaultPollingPeriod(period)


class _DeprecationCounter(defaultdict):
    def __init__(self):
        defaultdict.__init__(self, int)

    def getTotal(self):
        c = 0
        for v in self.values():
            c += v
        return c

    def pretty(self):
        from operator import itemgetter

        sorted_items = sorted(self.items(), key=itemgetter(1), reverse=True)
        ret = "\n".join(['\t%d * "%s"' % (v, k) for k, v in sorted_items])
        return "< Deprecation Counts (%d):\n%s >" % (self.getTotal(), ret)


_DEPRECATION_COUNT = _DeprecationCounter()

TRACE = 5
logging.addLevelName(TRACE, "TRACE")


class _BaseObject(object):
    def __init__(self):
        pass

    def call__init__(self, klass, *args, **kw):
        """Method to be called from subclasses to call superclass corresponding
        __init__ method. This method ensures that classes from diamond like
        class hierarquies don't call their super classes __init__ more than
        once.
        """

        if "inited_class_list" not in self.__dict__:
            self.inited_class_list = []

        if klass not in self.inited_class_list:
            self.inited_class_list.append(klass)
            klass.__init__(self, *args, **kw)

    def call__init__wo_kw(self, klass, *args):
        """
        Same as call__init__ but without keyword arguments because PyQt4 does
        not support them.
        """

        if "inited_class_list" not in self.__dict__:
            self.inited_class_list = []

        if klass not in self.inited_class_list:
            self.inited_class_list.append(klass)
            klass.__init__(self, *args)

    def getAttrDict(self):
        attr = dict(self.__dict__)
        if "inited_class_list" in attr:
            del attr["inited_class_list"]
        return attr

    def updateAttrDict(self, other):
        attr = other.getAttrDict()
        self.__dict__.update(attr)


class Logger(_BaseObject):
    """The taurus logger class. All taurus pertinent classes should inherit
    directly or indirectly from this class if they need taurus logging
    facilities.
    """

    #: Internal usage
    root_inited = False

    #: Internal usage
    root_init_lock = threading.Lock()

    #: Critical message level (constant)
    Critical = logging.CRITICAL

    #: Fatal message level (constant)
    Fatal = logging.FATAL

    #: Error message level (constant)
    Error = logging.ERROR

    #: Warning message level (constant)
    Warning = logging.WARNING

    #: Info message level (constant)
    Info = logging.INFO

    #: Debug message level (constant)
    Debug = logging.DEBUG

    #: Trace message level (constant)
    Trace = TRACE

    #: Default log level (constant)
    DftLogLevel = Info

    #: Default log message format (constant)
    DftLogMessageFormat = (
        "%(threadName)-14s %(levelname)-8s %(asctime)s %(name)s: %(message)s"
    )

    #: Default log format (constant)
    DftLogFormat = logging.Formatter(DftLogMessageFormat)

    #: Current global log level
    log_level = DftLogLevel

    #: Default log message format
    log_format = DftLogFormat

    #: the main stream handler
    stream_handler = None

    def __init__(self, name="", parent=None, format=None):
        """The Logger constructor

        :param name: the logger name (default is empty string)
        :type name: str
        :param parent: the parent logger or None if no parent exists (default
            is None)
        :type parent: Logger
        :param format: the log message format or None to use the default log
            format (default is None)
        :type format: str
        """
        self.call__init__(_BaseObject)

        if format:
            self.log_format = format
        Logger.initRoot()

        if name is None or len(name) == 0:
            name = self.__class__.__name__
        self.log_name = name
        if parent is not None:
            self.log_full_name = "%s.%s" % (parent.log_full_name, name)
        else:
            self.log_full_name = name

        self.log_obj = self._getLogger(self.log_full_name)
        self.log_handlers = []

        self.log_parent = None
        self.log_children = {}
        if parent is not None:
            self.log_parent = weakref.ref(parent)
            parent.addChild(self)

    def cleanUp(self):
        """The cleanUp. Default implementation does nothing
        Overwrite when necessary
        """
        pass

    @classmethod
    def initRoot(cls):
        """Class method to initialize the root logger. Do **NOT** call this
        method directly in your code
        """
        if cls.root_inited:
            return cls._getLogger()

        try:
            cls.root_init_lock.acquire()
            root_logger = cls._getLogger()
            logging.addLevelName(cls.Trace, "TRACE")
            cls.stream_handler = logging.StreamHandler(sys.__stderr__)
            cls.stream_handler.setFormatter(cls.log_format)
            root_logger.addHandler(cls.stream_handler)

            console_log_level = os.environ.get("TAURUSLOGLEVEL", None)
            if console_log_level is not None:
                console_log_level = console_log_level.capitalize()
                if hasattr(cls, console_log_level):
                    cls.log_level = getattr(cls, console_log_level)
            root_logger.setLevel(cls.log_level)
            Logger.root_inited = True
        finally:
            cls.root_init_lock.release()
        return root_logger

    @classmethod
    def addRootLogHandler(cls, h):
        """Adds a new handler to the root logger

        :param h: the new log handler
        :type h: logging.Handler
        """
        h.setFormatter(cls.getLogFormat())
        cls.initRoot().addHandler(h)

    @classmethod
    def removeRootLogHandler(cls, h):
        """Removes the given handler from the root logger

        :param h: the handler to be removed
        :type h: logging.Handler
        """
        cls.initRoot().removeHandler(h)

    @classmethod
    def enableLogOutput(cls):
        """Enables the :class:`logging.StreamHandler` which dumps log records,
        by default, to the stderr.
        """
        cls.initRoot().addHandler(cls.stream_handler)

    @classmethod
    def disableLogOutput(cls):
        """Disables the :class:`logging.StreamHandler` which dumps log records,
        by default, to the stderr.
        """
        cls.initRoot().removeHandler(cls.stream_handler)

    @classmethod
    def setLogLevel(cls, level):
        """sets the new log level (the root log level)

        :param level: the new log level
        :type level: int
        """
        cls.log_level = level
        cls.initRoot().setLevel(level)

    @classmethod
    def getLogLevel(cls):
        """Retuns the current log level (the root log level)

        :return: a number representing the log level
        :rtype: int
        """
        return cls.log_level

    @classmethod
    def setLogFormat(cls, format):
        """sets the new log message format

        :param format: the new log message format
        :type format: str
        """
        cls.log_format = logging.Formatter(format)
        root_logger = cls.initRoot()
        for h in root_logger.handlers:
            h.setFormatter(cls.log_format)

    @classmethod
    def getLogFormat(cls):
        """Retuns the current log message format (the root log format)

        :return: the log message format
        :rtype: str
        """
        return cls.log_format

    @classmethod
    def resetLogLevel(cls):
        """Resets the log level (the root log level)"""
        cls.setLogLevel(cls.DftLogLevel)

    @classmethod
    def resetLogFormat(cls):
        """Resets the log message format (the root log format)"""
        cls.setLogFormat(cls.DftLogFormat)

    @classmethod
    def addLevelName(cls, level_no, level_name):
        """Registers a new log level

        :param level_no: the level number
        :type level_no: int
        :param level_name: the corresponding name
        :type level_name: str
        """
        logging.addLevelName(level_no, level_name)
        level_name = level_name.capitalize()
        if not hasattr(cls, level_name):
            setattr(cls, level_name, level_no)

    @classmethod
    def getRootLog(cls):
        """Retuns the root logger

        :return: the root logger
        :rtype: logging.Logger
        """
        return cls.initRoot()

    @staticmethod
    def _getLogger(name=None):
        orig_logger_class = logging.getLoggerClass()
        try:
            logging.setLoggerClass(logging.Logger)
            ret = logging.getLogger(name)
            return ret
        finally:
            logging.setLoggerClass(orig_logger_class)

    @classmethod
    def getLogger(cls, name=None):
        cls.initRoot()
        return cls._getLogger(name=name)

    def getLogObj(self):
        """Returns the log object for this object

        :return: the log object
        :rtype: logging.Logger
        """
        return self.log_obj

    def getParent(self):
        """Returns the log parent for this object or None if no parent exists

        :return: the log parent for this object
        :rtype: logging.Logger or None
        """
        if self.log_parent is None:
            return None
        return self.log_parent()

    def getChildren(self):
        """Returns the log children for this object

        :return: the list of log children
        :rtype: sequence<logging.Logger
        """
        children = []
        for _, ref in self.log_children.items():
            child = ref()
            if child is not None:
                children.append(child)
        return children

    def addChild(self, child):
        """Adds a new logging child

        :param child: the new child
        :type child: logging.Logger
        """
        if not self.log_children.get(id(child)):
            self.log_children[id(child)] = weakref.ref(child)

    def addLogHandler(self, handler):
        """Registers a new handler in this object's logger

        :param handler: the new handler to be added
        :type handler: logging.Handler
        """
        self.log_obj.addHandler(handler)
        self.log_handlers.append(handler)

    def removeLogHandler(self, handler):
        """Removes the given handler from this object's logger

        :param handler: the handler to be removed
        :type handler: logging.Handler
        """
        self.log_obj.removeHandler(handler)
        self.log_handlers.remove(handler)

    def copyLogHandlers(self, other):
        """Copies the log handlers of other object to this object

        :param other: object which contains 'log_handlers'
        :type other: object
        """
        for handler in other.log_handlers:
            self.addLogHandler(handler)

    def trace(self, msg, *args, **kw):
        """Record a trace message in this object's logger. Accepted *args* and
        *kwargs* are the same as :meth:`logging.Logger.log`.

        :param msg: the message to be recorded
        :type msg: str
        :param args: list of arguments
        :param kw: list of keyword arguments
        """
        self.log_obj.log(self.Trace, msg, *args, **kw)

    def traceback(self, level=Trace, extended=True):
        """Log the usual traceback information, followed by a listing of all
        the local variables in each frame.

        :param level: the log level assigned to the traceback record
        :type level: int
        :param extended: if True, the log record message will have multiple
            lines
        :type extended: bool
        :return: The traceback string representation
        :rtype: str
        """
        out = traceback.format_exc()
        if extended:
            out += "\n"
            out += self._format_trace()

        self.log_obj.log(level, out)
        return out

    def stack(self, target=Trace):
        """Log the usual stack information, followed by a listing of all the
        local variables in each frame.

        :param target: the log level assigned to the record
        :type target: int
        :return: The stack string representation
        :rtype: str
        """
        out = self._format_stack()
        self.log_obj.log(target, out)
        return out

    def _format_trace(self):
        return self._format_stack(inspect.trace)

    def _format_stack(self, stack_func=inspect.stack):
        line_count = 3
        stack = stack_func(line_count)
        out = ""
        for frame_record in stack:
            out += "\n\t" + 60 * "-"
            frame, filename, line, funcname, lines, index = frame_record
            # out += '\n\t    depth = %d' % frame[5]
            out += "\n\t filename = %s" % filename
            out += "\n\t function = %s" % funcname
            if lines is None:
                code = "<code could not be found>"
                out += "\n\t     line = [%d]: %s" % (line, code)
            else:
                lines, line_nb = [s.strip(" \n") for s in lines], len(lines)
                if line_nb >= 3:
                    out += "\n\t     line = [%d]: %s" % (line - 1, lines[0])
                    out += "\n\t  -> line = [%d]: %s" % (line, lines[1])
                    out += "\n\t     line = [%d]: %s" % (line + 1, lines[2])
                elif line_nb > 0:
                    out += "\n\t  -> line = [%d]: %s" % (line, lines[0])
            if frame:
                out += "\n\t   locals = "
                for k, v in frame.f_locals.items():
                    out += "\n\t\t%20s = " % k
                    try:
                        cut = False
                        v = str(v)
                        i = v.find("\n")
                        if i == -1:
                            i = 80
                        else:
                            i = min(i, 80)
                            cut = True
                        if len(v) > 80:
                            cut = True
                        out += v[:i]
                        if cut:
                            out += "[...]"
                    except Exception:
                        out += "<could not find suitable string representation>"
        return out

    def log(self, level, msg, *args, **kw):
        """Record a log message in this object's logger. Accepted *args* and
        *kwargs* are the same as :meth:`logging.Logger.log`.

        :param level: the record level
        :type level: int
        :param msg: the message to be recorded
        :type msg: str
        :param args: list of arguments
        :param kw: list of keyword arguments
        """
        self.log_obj.log(level, msg, *args, **kw)

    def debug(self, msg, *args, **kw):
        """Record a debug message in this object's logger. Accepted *args* and
        *kwargs* are the same as :meth:`logging.Logger.debug`.

        :param msg: the message to be recorded
        :type msg: str
        :param args: list of arguments
        :param kw: list of keyword arguments
        """
        self.log_obj.debug(msg, *args, **kw)

    def info(self, msg, *args, **kw):
        """Record an info message in this object's logger. Accepted *args* and
        *kwargs* are the same as :meth:`logging.Logger.info`.

        :param msg: the message to be recorded
        :type msg: str
        :param args: list of arguments
        :param kw: list of keyword arguments
        """
        self.log_obj.info(msg, *args, **kw)

    def warning(self, msg, *args, **kw):
        """Record a warning message in this object's logger. Accepted *args*
        and kwargs* are the same as :meth:`logging.Logger.warning`.

        :param msg: the message to be recorded
        :type msg: str
        :param args: list of arguments
        :param kw: list of keyword arguments
        """
        self.log_obj.warning(msg, *args, **kw)

    def deprecated(
        self,
        msg=None,
        dep=None,
        alt=None,
        rel=None,
        dbg_msg=None,
        _callerinfo=None,
        **kw,
    ):
        """Record a deprecated warning message in this object's logger.
        If message is not passed, a estandard deprecation message is
        constructued using dep, alt, rel arguments.
        Also, an extra debug message can be recorded, followed by traceback
        info.

        :param msg: the message to be recorded (if None passed, it will be
            constructed using dep (and, optionally, alt and rel)
        :type msg: str
        :param dep: name of deprecated feature (in case msg is None)
        :type dep: str
        :param alt: name of alternative feature (in case msg is None)
        :type alt: str
        :param rel: name of release from which the feature was deprecated (in
            case msg is None)
        :type rel: str
        :param dbg_msg: msg for debug (or None to log only the warning)
        :type dbg_msg: str
        :param _callerinfo: for internal use only. Do not use this argument.
        :param kw: any additional keyword arguments, are passed to
            :meth:`logging.Logger.warning`
        """
        if msg is None:
            if dep is None:
                raise TypeError("deprecated takes either msg or dep argument")
            msg = "%s is deprecated" % dep
            if rel is not None:
                msg += " since %s" % rel
            if alt is not None:
                msg += ". Use %s instead" % alt

        # count the number of calls (classified by msg)
        # TODO: substitute this ugly hack (below) by a more general mechanism
        _DEPRECATION_COUNT[msg] += 1
        # limit the output to 1 deprecation message of each type
        from taurus import tauruscustomsettings

        _MAX_DEPRECATIONS_LOGGED = getattr(
            tauruscustomsettings, "_MAX_DEPRECATIONS_LOGGED", None
        )
        if _MAX_DEPRECATIONS_LOGGED is not None:
            if _MAX_DEPRECATIONS_LOGGED < 0:
                self.stack(self.Warning)
                raise Exception(msg)
            if _DEPRECATION_COUNT[msg] > _MAX_DEPRECATIONS_LOGGED:
                return
        if _callerinfo is None:
            _callerinfo = self.log_obj.findCaller()
        filename, lineno = _callerinfo[:2]
        depr_msg = warnings.formatwarning(msg, DeprecationWarning, filename, lineno)
        self.log_obj.warning(depr_msg, **kw)
        if dbg_msg:
            self.debug(dbg_msg)
            self.stack()

    def error(self, msg, *args, **kw):
        """Record an error message in this object's logger. Accepted *args* and
        *kwargs* are the same as :meth:`logging.Logger.error`.

        :param msg: the message to be recorded
        :type msg: str
        :param args: list of arguments
        :param kw: list of keyword arguments
        """
        self.log_obj.error(msg, *args, **kw)

    def fatal(self, msg, *args, **kw):
        """Record a fatal message in this object's logger. Accepted *args* and
        *kwargs* are the same as :meth:`logging.Logger.fatal`.

        :param msg: the message to be recorded
        :type msg: str
        :param args: list of arguments
        :param kw: list of keyword arguments
        """
        self.log_obj.fatal(msg, *args, **kw)

    def critical(self, msg, *args, **kw):
        """Record a critical message in this object's logger. Accepted *args*
        and kwargs* are the same as :meth:`logging.Logger.critical`.

        :param msg: the message to be recorded
        :type msg: str
        :param args: list of arguments
        :param kw: list of keyword arguments
        """
        self.log_obj.critical(msg, *args, **kw)

    def exception(self, msg, *args):
        """Log a message with severity 'ERROR' on the root logger, with
        exception information.. Accepted *args* are the same as
        :meth:`logging.Logger.exception`.

        :param msg: the message to be recorded
        :type msg: str
        :param args: list of arguments
        """
        self.log_obj.exception(msg, *args)

    def flushOutput(self):
        """Flushes the log output"""
        self.syncLog()

    def syncLog(self):
        """Synchronises the log output"""
        logger = self
        synced = []
        while logger is not None:
            for handler in logger.log_handlers:
                if handler in synced:
                    continue
                try:
                    sync = getattr(handler, "sync")
                except Exception:
                    continue
                sync()
                synced.append(handler)
            logger = logger.getParent()

    def getLogName(self):
        """Gets the log name for this object

        :return: the log name
        :rtype: str
        """
        return self.log_name

    def getLogFullName(self):
        """Gets the full log name for this object

        :return: the full log name
        :rtype: str
        """
        return self.log_full_name

    def changeLogName(self, name):
        """Change the log name for this object.

        :param name: the new log name
        :type name: str
        """
        self.log_name = name
        p = self.getParent()
        if p is not None:
            self.log_full_name = "%s.%s" % (p.log_full_name, name)
        else:
            self.log_full_name = name

        self.log_obj = logging.getLogger(self.log_full_name)
        for handler in self.log_handlers:
            self.log_obj.addHandler(handler)

        for child in self.getChildren():
            child.changeLogName(child.log_name)


Critical = Logger.Critical
Fatal = Logger.Fatal
Error = Logger.Error
Warning = Logger.Warning
Info = Logger.Info
Debug = Logger.Debug
Trace = Logger.Trace

setLogLevel = Logger.setLogLevel
setLogFormat = Logger.setLogFormat
getLogLevel = Logger.getLogLevel
getLogFormat = Logger.getLogFormat
resetLogLevel = Logger.resetLogLevel
resetLogFormat = Logger.resetLogFormat

enableLogOutput = Logger.enableLogOutput
disableLogOutput = Logger.disableLogOutput


def __getrootlogger():
    return Logger.getLogger("TaurusRootLogger")


def log(level, msg, *args, **kw):
    return __getrootlogger().log(level, msg, *args, **kw)


def trace(msg, *args, **kw):
    return log(Logger.Trace, msg, *args, **kw)


def debug(msg, *args, **kw):
    return __getrootlogger().debug(msg, *args, **kw)


def info(msg, *args, **kw):
    return __getrootlogger().info(msg, *args, **kw)


def warning(msg, *args, **kw):
    return __getrootlogger().warning(msg, *args, **kw)


def error(msg, *args, **kw):
    return __getrootlogger().error(msg, *args, **kw)


def fatal(msg, *args, **kw):
    return __getrootlogger().fatal(msg, *args, **kw)


def critical(msg, *args, **kw):
    return __getrootlogger().critical(msg, *args, **kw)


def deprecated(*args, **kw):
    kw["_callerinfo"] = __getrootlogger().findCaller()
    return Logger("TaurusRootLogger").deprecated(*args, **kw)
