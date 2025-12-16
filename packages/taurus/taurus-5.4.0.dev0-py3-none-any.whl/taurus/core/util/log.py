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

"""This module contains a set of useful logging elements based on python's
:mod:`logging` system.
"""

import functools
import logging.handlers
import os
import sys
import traceback

from taurus import (
    TRACE,
    Logger,
    critical,
    debug,
    deprecated,
    error,
    fatal,
    info,
    trace,
    warning,
)
from taurus._taurushelper import _BaseObject as Object  # noqa
from taurus._taurushelper import log as _log

from .excepthook import BaseExceptHook
from .wrap import wraps

__all__ = [
    "LogIt",
    "TraceIt",
    "DebugIt",
    "InfoIt",
    "WarnIt",
    "ErrorIt",
    "CriticalIt",
    "MemoryLogHandler",
    "LogExceptHook",
    "LogFilter",
    "_log",
    "trace",
    "debug",
    "info",
    "warning",
    "error",
    "fatal",
    "critical",
    "deprecated",
    "deprecation_decorator",
    "taurus4_deprecation",
]

__docformat__ = "restructuredtext"


#
# _srcfile is used when walking the stack to check when we've got the first
# caller stack frame.
#
if hasattr(sys, "frozen"):  # support for py2exe
    _srcfile = "logging%s__init__%s" % (os.sep, __file__[-4:])
elif __file__[-4:].lower() in [".pyc", ".pyo"]:
    _srcfile = __file__[:-4] + ".py"
else:
    _srcfile = __file__
_srcfile = os.path.normcase(_srcfile)


# currentframe filched from 1.5.2's inspect.py
if hasattr(sys, "_getframe"):

    def currentframe():
        """Return the frame object for the caller's stack frame."""
        return sys._getframe(3)

else:

    def currentframe():
        """Return the frame object for the caller's stack frame."""
        try:
            raise Exception
        except Exception:
            return sys.exc_info()[2].tb_frame.f_back


class LogIt(object):
    """A function designed to be a decorator of any method of a Logger
    subclass. The idea is to log the entrance and exit of any decorated method
    of a Logger subclass.

    Example::

        from taurus.core.util.log import Logger, LogIt

        class Example(Logger):

            @LogIt(Logger.Debug)
            def go(self):
                print("Hello world")

    This will generate two log messages of Debug level, one before the function
    go is called and another when go finishes. Example output::

        MainThread     DEBUG    2010-11-15 15:36:11,440 Example: -> go
        Hello world of mine
        MainThread     DEBUG    2010-11-15 15:36:11,441 Example: <- go

    This decorator can receive two optional arguments **showargs** and
    **showret** which are set to False by default. Enabling them will had
    verbose infomation about the parameters and return value. The following
    example::

        from taurus.core.uti.log import Logger, LogIt

        class Example(Logger):

            @LogIt(Logger.Debug, showargs=True, showret=True)
            def go(self, msg):
                msg = "Hello world",msg
                print(msg)
                return msg

    would generate an output like::

        MainThread     DEBUG    2010-11-15 15:42:02,353 Example:
            -> go('of mine',) Hello world of mine
        MainThread     DEBUG    2010-11-15 15:42:02,353 Example:
            <- go = Hello world of mine

    .. note::
        it may happen that in these examples that the output of the method
        appears before or after the log messages. This is because log messages
        are, by default, written to the *stardard error* while the print
        message inside the go method outputs to the *standard ouput*. On many
        systems these two targets are not synchronized.
    """

    def __init__(self, level=logging.DEBUG, showargs=False, showret=False, col_limit=0):
        self._level = level
        self._showargs = showargs
        self._showret = showret
        self._col_limit = col_limit

    def __call__(self, f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            f_self = args[0]
            if f_self.log_level > self._level:
                return f(*args, **kwargs)

            has_log = hasattr(f_self, "log")
            fname = f.__name__
            log_obj = f_self
            if not has_log:
                log_obj = logging.getLogger()
                try:
                    fname = "%s.%s" % (f_self.__class__.__name__, fname)
                except Exception:
                    pass
            in_msg = "-> %s" % fname
            if self._showargs:
                if len(args) > 1:
                    in_msg += str(args[1:])
                if len(kwargs):
                    in_msg += str(kwargs)
            if self._col_limit and len(in_msg) > self._col_limit:
                in_msg = "%s [...]" % in_msg[: self._col_limit - 6]
            log_obj.log(self._level, in_msg)
            out_msg = "<-"
            try:
                ret = f(*args, **kwargs)
            except Exception as e:
                exc_info = sys.exc_info()
                out_msg += " (with %s) %s" % (e.__class__.__name__, fname)
                log_obj.log(self._level, out_msg, exc_info=exc_info)
                raise
            out_msg += " %s" % fname
            if ret is not None and self._showret:
                out_msg += " = %s" % str(ret)
            if self._col_limit and len(out_msg) > self._col_limit:
                out_msg = "%s [...]" % out_msg[: self._col_limit - 6]
            log_obj.log(self._level, out_msg)
            return ret

        return wrapper


class TraceIt(LogIt):
    """Specialization of LogIt for trace level messages.
    Example::

        from taurus.core.util.log import Logger, TraceIt
        class Example(Logger):

            @TraceIt()
            def go(self):
                print("Hello world")

    .. seealso:: :class:`LogIt`
    """

    def __init__(self, showargs=False, showret=False):
        LogIt.__init__(self, level=TRACE, showargs=showargs, showret=showret)


class DebugIt(LogIt):
    """Specialization of LogIt for debug level messages.
    Example::

        from taurus.core.util.log import Logger, DebugIt
        class Example(Logger):

            @DebugIt()
            def go(self):
                print("Hello world")

    .. seealso:: :class:`LogIt`
    """

    def __init__(self, showargs=False, showret=False):
        LogIt.__init__(self, level=logging.DEBUG, showargs=showargs, showret=showret)


class InfoIt(LogIt):
    """Specialization of LogIt for info level messages.
    Example::

        from taurus.core.util.log import Logger, InfoIt
        class Example(Logger):

            @InfoIt()
            def go(self):
                print("Hello world")

    .. seealso:: :class:`LogIt`
    """

    def __init__(self, showargs=False, showret=False):
        LogIt.__init__(self, level=logging.INFO, showargs=showargs, showret=showret)


class WarnIt(LogIt):
    """Specialization of LogIt for warn level messages.
    Example::

        from taurus.core.util.log import Logger, WarnIt
        class Example(Logger):

            @WarnIt()
            def go(self):
                print("Hello world")

    .. seealso:: :class:`LogIt`
    """

    def __init__(self, showargs=False, showret=False):
        LogIt.__init__(self, level=logging.WARN, showargs=showargs, showret=showret)


class ErrorIt(LogIt):
    """Specialization of LogIt for error level messages.
    Example::

        from taurus.core.util.log import Logger, ErrorIt
        class Example(Logger):

            @ErrorIt()
            def go(self):
                print("Hello world")

    .. seealso:: :class:`LogIt`
    """

    def __init__(self, showargs=False, showret=False):
        LogIt.__init__(self, level=logging.ERROR, showargs=showargs, showret=showret)


class CriticalIt(LogIt):
    """Specialization of LogIt for critical level messages.
    Example::

        from taurus.core.util.log import Logger, CriticalIt
        class Example(Logger):

            @CriticalIt()
            def go(self):
                print("Hello world")

    .. seealso:: :class:`LogIt`
    """

    def __init__(self, showargs=False, showret=False):
        LogIt.__init__(self, level=logging.CRITICAL, showargs=showargs, showret=showret)


class PrintIt(object):
    """A decorator similar to TraceIt, DebugIt,... etc but which does not
    require the decorated class to inherit from Logger.
    It just uses print statements instead of logging. It is here just to be
    used as a replacement of those decorators if you cannot use them on a
    non-logger class.
    """

    def __init__(self, showargs=False, showret=False):
        self._showargs = showargs
        self._showret = showret

    def __call__(self, f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            fname = f.__name__
            in_msg = "-> %s" % fname
            if self._showargs:
                if len(args) > 1:
                    in_msg += str(args[1:])
                if len(kwargs):
                    in_msg += str(kwargs)
            print()
            print(in_msg)
            out_msg = "<-"
            try:
                ret = f(*args, **kwargs)
            except Exception as e:
                out_msg += " (with %s) %s" % (e.__class__.__name__, fname)
                print(out_msg)
                raise
            out_msg += " %s" % fname
            if ret is not None and self._showret:
                out_msg += " = %s" % str(ret)
            print(out_msg)
            print()
            return ret

        return wrapper


class MemoryLogHandler(list, logging.handlers.BufferingHandler):
    """An experimental log handler that stores temporary records in memory.
    When flushed it passes the records to another handler
    """

    def __init__(self, capacity=1000):
        list.__init__(self)
        logging.handlers.BufferingHandler.__init__(self, capacity=capacity)
        self._handler_list_changed = False

    def shouldFlush(self, record):
        """Determines if the given record should trigger the flush

        :param record: a log record
        :type record: logging.LogRecord
        :return: wheter or not the handler should be flushed
        :rtype: bool
        """
        return (
            (len(self.buffer) >= self.capacity)
            or (record.levelno >= Logger.getLogLevel())
            or self._handler_list_changed
        )

    def flush(self):
        """Flushes this handler"""
        for record in self.buffer:
            for handler in self:
                handler.handle(record)
        self.buffer = []

    def close(self):
        """Closes this handler"""
        self.flush()
        del self[:]
        logging.handlers.BufferingHandler.close(self)


class LogExceptHook(BaseExceptHook):
    """A callable class that acts as an excepthook that logs the exception in
    the python logging system.

    :param hook_to: callable excepthook that will be called at the end of this
        hook handling [default: None]
    :type hook_to: callable
    :param name: logger name [default: None meaning use class name]
    :type name: str
    :param level: log level [default: logging.ERROR]
    :type level: int
    """

    def __init__(self, hook_to=None, name=None, level=logging.ERROR):
        BaseExceptHook.__init__(self, hook_to=hook_to)
        name = name or self.__class__.__name__
        self._level = level
        self._log = Logger(name=name)

    def report(self, *exc_info):
        text = "".join(traceback.format_exception(*exc_info))
        if text[-1] == "\n":
            text = text[:-1]
        self._log.log(self._level, "Unhandled exception:\n%s", text)


class LogFilter(logging.Filter):
    """Experimental log filter"""

    def __init__(self, level):
        self.filter_level = level
        logging.Filter.__init__(self)

    def filter(self, record):
        ok = record.levelno == self.filter_level
        return ok


def __getrootlogger():
    return Logger.getLogger("TaurusRootLogger")


def deprecation_decorator(func=None, alt=None, rel=None, dbg_msg=None):
    """decorator to mark methods as deprecated"""
    if func is None:
        return functools.partial(
            deprecation_decorator, alt=alt, rel=rel, dbg_msg=dbg_msg
        )

    def new_func(*args, **kwargs):
        deprecated(dep=func.__name__, alt=alt, rel=rel, dbg_msg=dbg_msg)
        return func(*args, **kwargs)

    doc = func.__doc__ or ""
    doc += "\n\n.. deprecated:: %s\n" % (rel or "")
    if alt:
        doc += "   Use %s instead\n" % alt

    new_func.__name__ = func.__name__
    new_func.__doc__ = doc
    new_func.__dict__.update(func.__dict__)
    return new_func


taurus4_deprecation = functools.partial(deprecation_decorator, rel="4.0")


if __name__ == "__main__":

    @taurus4_deprecation(alt="bar")
    def foo(x):
        """Does this and that and also:

        - baz
        - zab
        """

    print(foo.__doc__)
