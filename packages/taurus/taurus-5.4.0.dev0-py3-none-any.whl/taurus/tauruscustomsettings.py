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
This module exposes global configuration options. It declares the default
values of some of these options, but they may be modified when loading custom
settings configuration files (e.g., at import time).

"""

import os as _os

if _os.name == "posix":
    #: Path to the system-wide config file
    SYSTEM_CFG_FILE = "/etc/xdg/taurus/taurus.ini"
    #: Path to the user-specific config file
    USER_CFG_FILE = _os.path.join(
        _os.path.expanduser("~"), ".config", "taurus", "taurus.ini"
    )
else:
    #: Path to the system-wide config file
    SYSTEM_CFG_FILE = _os.path.join(
        _os.environ.get("PROGRAMDATA"), "taurus", "taurus.ini"
    )
    #: Path to the user-specific config file
    USER_CFG_FILE = _os.path.join(_os.environ.get("APPDATA"), "taurus", "taurus.ini")


def load_configs(filenames=None, section="taurus"):
    """Read configuration key, values from given ini files and expose them as
    members of the current module.

    The keys must appear in the given section ("taurus" by default) and are
    case-sensitive. The values are interpreted as python literals.

    In case of conflicting keys, the filenames determine the precedence
    (increasing order). If a given file cannot be read, it is skipped. The
    list of names of successfully read files is returned.

    :param filenames: sequence of ini file names in increasing precedence
        order. If None passed (default), it uses
        `(SYSTEM_CFG_FILE, USER_CFG_FILE)`
    :type filenames: sequence of str
    :param section: section of the ini files to be read (default:`taurus`)
    :type section: str
    :returns: list of names of successfully read configuration files
    :rtype: list<str>
    """
    import ast
    import configparser

    if filenames is None:
        filenames = (SYSTEM_CFG_FILE, USER_CFG_FILE)

    parser = configparser.ConfigParser()
    parser.optionxform = lambda option: option  # make keys case-sensitive
    read = parser.read(filenames)

    try:
        taurus_cfg = parser[section]
    except KeyError:
        taurus_cfg = {}
    for k, v in taurus_cfg.items():
        globals()[k] = ast.literal_eval(v)
    return read


#: Widget alternatives. Some widgets may have alternative implementations.
#: The different implementations are registered in
#: entry point groups (``taurus.plot.alt``, ``taurus.trend.alt``, ...) and they
#: are tried in alphabetical order of their registered entry point names
#: (the first one that works is used). You can restrict the set of available
#: implementation alternatives to be tried (or even just select a given
#: alternative) by setting the corresponding ``*_ALT`` variable with a name
#: regexp pattern that must be matched by the entry point name in order to be
#: tried. For example, to force the ``taurus_pyqtgraph`` implementation for the
#: plots, set ``PLOT_ALT = "tpg"``.
#:
#: The following variables control the alternatives:
#:
#: - ``PLOT_ALT``
#: - ``TREND_ALT``
#: - ``TREND2D_ALT``
#: - ``IMAGE_ALT``
#:
#: Leaving the variable undefined is equivalent to setting it to `".*"`
PLOT_ALT = ".*"

#: Widget alternatives. See ``PLOT_ALT`` for a full description.
TREND_ALT = ".*"

#: Widget alternatives. See ``PLOT_ALT`` for a full description.
TREND2D_ALT = ".*"

#: Widget alternatives. See ``PLOT_ALT`` for a full description.
IMAGE_ALT = ".*"

#: Default behaviour for ``TaurusMainWindow``. On close,
#: ``TaurusMainWindow`` will ask the user if he wants to save. Set to
#: ``True`` if you want to save automatically without being warned. Set to
#: ``False`` in case you do notwant to be asked and do not want to Save
#: current window.
SAVE_SETTINGS_ON_CLOSE = None

#: Default include and exclude patterns for ``TaurusForm`` item factories
#: See ``TaurusForm.setItemFactories`` docs. By default, all available
#: factories are enabled (and tried alphabetically)
T_FORM_ITEM_FACTORIES = {"include": (".*",), "exclude": ()}

#: Compact mode for widgets
#: True sets the preferred mode of TaurusForms to use "compact" widgets
T_FORM_COMPACT = False

#: Strict RFC3986 URI names in models.
#:
#: - ``True`` makes Taurus only use the strict URI names
#: - ``False`` False enables a backwards-compatibility mode for pre-sep3
#:   model names
STRICT_MODEL_NAMES = False

#: Lightweight imports:
#:
#: - ``True`` enables delayed imports (may break older code).
#: - ``False`` (or commented out) for backwards compatibility
LIGHTWEIGHT_IMPORTS = False

#: Default scheme (if not defined, "tango" is assumed)
DEFAULT_SCHEME = "tango"

#: Filter old tango events:
#: Sometimes ``TangoAttribute`` can receive an event with an older timestamp
#: than its current one. See https://gitlab.com/taurus-org/taurus/-/issues/216
#:
#: - ``True`` discards (Tango) events whose timestamp is older than the cached
#:   one.
#: - ``False`` (or commented out) for backwards (pre 4.1) compatibility
FILTER_OLD_TANGO_EVENTS = True

#: Extra Taurus schemes. You can add a list of modules to be loaded for
#: providing support to new schemes
#: (e.g. ``EXTRA_SCHEME_MODULES = ['myownschememodule']``
EXTRA_SCHEME_MODULES = []

#: Custom formatter. Taurus widgets use a default formatter based on the
#: attribute type, but sometimes a custom formatter is needed.
#: IMPORTANT: setting this option in this file will affect ALL widgets
#: of ALL applications (which is probably **not** what you want, since it
#: may have unexpected effects in some applications).
#: Consider using the API for modifying this on a per-widget or per-class
#: basis at runtime, or using the related `--default-formatter` parameter
#: from TaurusApplication, e.g.:
#:     $ taurus form MODEL --default-formatter='{:2.3f}'
#: The formatter can be a python format string or the name of a formatter
#: callable, e.g.
#: DEFAULT_FORMATTER = '{0}'
#: DEFAULT_FORMATTER = 'taurus.core.tango.util.tangoFormatter'
#: If not defined, taurus.qt.qtgui.base.defaultFormatter will be used


#: Default serialization mode **for the tango scheme**. Possible values are:
#: 'Serial', 'Concurrent', or 'TangoSerial' (default)
TANGO_SERIALIZATION_MODE = "TangoSerial"

#: Whether ``TangoAttribute`` is subscribed to configuration events by
#: default.
#:
#: - Setting to ``True`` (or not setting it) makes the ``TangoAttribute``
#:   auto-subscribe
#: - Setting to ``False`` avoids this subscription, which prevents issues such
#:   as https://gitlab.com/taurus-org/taurus/-/issues/1118
#:   but it also prevents clients to be notified when configurations (e.g.,
#:   units, format) change.
TANGO_AUTOSUBSCRIBE_CONF = True

#: An array with all the tango event types to subscribe when using setModel().
#: The posible options are all the existent tango event types except
#: "ATTR_CONF_EVENT" as it has its own taurus custom setting.
#: Leaving an empty array will won't subscribe to any event and will enable
#: the taurus polling.
#: Note: this setting currently only supports ["CHANGE_EVENT"] and [], but
#: it was created for future compatibility when supporting all event types
TANGO_EVENTS_TO_SUBSCRIBE = ["CHANGE_EVENT"]


class FORCE_READ_OPTIONS:
    NEVER = "NEVER"
    ONLY_CORE = "ONLY_CORE"
    ALWAYS = "ALWAYS"


#: Select when taurus will perform a tango read when the subscription to
#: change events fails (the attribute doesn't send events).
#: Possible values are the options in ``FORCE_READ_OPTIONS`` fake enum:
#:
#: - ``"NEVER"``\: never read when subscription fails.
#: - ``"ONLY_CORE"``\: (default) force read when using taurus core but avoid
#:   the read when running applications (TaurusApplication).
#: - ``"ALWAYS"``\: always read when subscription fails.
TANGO_FORCE_READ_IF_SUBSCRIPTION_FAILS = FORCE_READ_OPTIONS.ONLY_CORE


class EVENT_SUB_MODE:
    SYNC = "SYNC"
    SYNCREAD = "SYNCREAD"
    ASYNC = "ASYNC"
    ASYNCREAD = "ASYNCREAD"
    STATELESS = "STATELESS"


#: Tango Event Subscription Mode to use for change events
#: Possible values are the options in ``EVENT_SUB_MODE`` fake enum:
#:
#: - ``"SYNC"``\: Synchronous subscription without reading.
#: - ``"SYNCREAD"``\: Synchronous with reading.
#:   the read when running applications (TaurusApplication).
#: - ``"ASYNC"``\: Asynchronous, also works when the DS is down. Auto-retry.
#: - ``"ASYNCREAD"``\: (default) Asynchronous with reading. Auto-retry.
#: - ``"STATELESS"``\: Synchronous with reading. No fail. Auto-retry.
TANGO_EVENT_SUB_MODE = EVENT_SUB_MODE.ASYNCREAD

#: PLY (lex/yacc) optimization:
#: 1=Active (default) , 0=disabled.
#: Set ``PLY_OPTIMIZE = 0`` if you are getting yacc exceptions while loading
#: synoptics
PLY_OPTIMIZE = 1

# Taurus namespace  # TODO: NAMESPACE setting seems to be unused. remove?
NAMESPACE = "taurus"

# ----------------------------------------------------------------------------
# Qt configuration
# ----------------------------------------------------------------------------

#: Set preferred API (if one is not already loaded). Set to an empty string to
#: let taurus choose the first that works from the accepted values. Accepted
#: values are:
#:
#: - ``"pyqt5"``
#: - ``"pyqt6"``
#: - ``"pyside2"``
#: - ``"pyside6"``
DEFAULT_QT_API = ""

#: Auto initialize Qt logging to python logging
QT_AUTO_INIT_LOG = True

#: Remove input hook (only valid for ``PyQt``)
QT_AUTO_REMOVE_INPUTHOOK = True

#: Avoid application abort on unhandled python exceptions
#: (which happens since PyQt 5.5).
#: http://pyqt.sf.net/Docs/PyQt5/incompatibilities.html#unhandled-python-exceptions  # noqa
#: If ``True`` (or commented out) an except hook is added to force the old
#: behaviour (exception is just printed) on ``pyqt5``
QT_AVOID_ABORT_ON_EXCEPTION = True

#: Select the theme to be used.
#: The path can be absolute or relative to the dir of
#: ``taurus.qt.qtgui.icon``. If not set, the dir of
#: ``taurus.qt.qtgui.icon`` will be used.
QT_THEME_DIR = ""

#: The name of the icon theme (e.g. 'Tango', 'Oxygen', etc). Default='Tango'
QT_THEME_NAME = "Tango"

#: In Linux the ``QT_THEME_NAME`` is not applied (to respect the system theme)
#: setting ``QT_THEME_FORCE_ON_LINUX = True`` overrides this.
QT_THEME_FORCE_ON_LINUX = False

#: Full Qt designer path (including filename. Default is None, meaning
#: to look for the system designer following ``Qt.QLibraryInfo.BinariesPath``
#: If this fails, taurus tries to locate binary manually
QT_DESIGNER_PATH = None

#: Custom organization logo. Set the absolute path to an image file to be used
#: as your organization logo. Qt registered paths can also be used.
#: If not set, it defaults to "logos:taurus.png" (note that "logos:" is a Qt
#: registered path for "<taurus>/qt/qtgui/icon/logos/")
ORGANIZATION_LOGO = "logos:taurus.png"

#: Implicit optparse legacy support:
#: In taurus < 4.6.5 if ``TaurusApplication`` did not receive an explicit
#: ``cmd_line_parser`` keyword argument, it implicitly used a
#: ``optparse.OptionParser`` instance. This was inconvenient because it forced
#: the user to explicitly pass ``cmd_line_parser=None`` when using other
#: mechanisms such as ``click`` or ``argparse`` to parse CLI options.
#: In taurus >=4.6.5 this is no longer the case by default, but the old
#: behaviour can be restored by setting ``IMPLICIT_OPTPARSE = True``
IMPLICIT_OPTPARSE = False

# ----------------------------------------------------------------------------
# Deprecation handling:
# Note: this API is still experimental and may be subject to change
# (hence the "_" in the options)
# ----------------------------------------------------------------------------

#: set the maximum number of same-message deprecations to be logged.
#: None (or not set) indicates no limit. -1 indicates that an exception should
#: be raised instead of logging the message (useful for finding obsolete code)
_MAX_DEPRECATIONS_LOGGED = 1

# ----------------------------------------------------------------------------
# DEPRECATED SETTINGS
# ----------------------------------------------------------------------------

#: DEPRECATED. Use ``taurus.form.item_factories`` plugin group instead
#: A map for using custom widgets for certain devices in TaurusForms. It is a
#: dictionary with the following structure:
#: device_class_name:(classname_with_full_module_path, args, kwargs)
#: where the args and kwargs will be passed to the constructor of the class
T_FORM_CUSTOM_WIDGET_MAP = {}
_OLD_T_FORM_CUSTOM_WIDGET_MAP = {
    "SimuMotor": ("sardana.taurus.qt.qtgui.extra_pool.PoolMotorTV", (), {}),
    "Motor": ("sardana.taurus.qt.qtgui.extra_pool.PoolMotorTV", (), {}),
    "PseudoMotor": ("sardana.taurus.qt.qtgui.extra_pool.PoolMotorTV", (), {}),
    "PseudoCounter": (
        "sardana.taurus.qt.qtgui.extra_pool.PoolChannelTV",
        (),
        {},
    ),
    "CTExpChannel": (
        "sardana.taurus.qt.qtgui.extra_pool.PoolChannelTV",
        (),
        {},
    ),
    "ZeroDExpChannel": (
        "sardana.taurus.qt.qtgui.extra_pool.PoolChannelTV",
        (),
        {},
    ),
    "OneDExpChannel": (
        "sardana.taurus.qt.qtgui.extra_pool.PoolChannelTV",
        (),
        {},
    ),
    "TwoDExpChannel": (
        "sardana.taurus.qt.qtgui.extra_pool.PoolChannelTV",
        (),
        {},
    ),
    "IORegister": (
        "sardana.taurus.qt.qtgui.extra_pool.PoolIORegisterTV",
        (),
        {},
    ),
}
try:  # just for backwards compatibility. This will be removed.
    import sardana

    if sardana.release.version < "3":
        T_FORM_CUSTOM_WIDGET_MAP = _OLD_T_FORM_CUSTOM_WIDGET_MAP
    del sardana
except Exception:
    pass

# ----------------------------------------------------------------------------
# read config files
load_configs()

# Needed for documentation purposes. Internal use.
__all__ = [e for e in globals() if not e.startswith("_")]
