
.. _tauruscustomsettings:

=======================
Taurus custom settings
=======================

Taurus provides a module located at its root directory called
`tauruscustomsettings` which exposes global configuration options.

It can be accessed programmatically at run time for setting options
for the current execution.

System and user settings files
------------------------------

If one wants to permanently modify options for all applications, the
recommended way is to do it by declaring them in the system-wide or
user-specific configuration files (which are loaded automatically when
importing `tauruscustomsettings`).

The default location of the system-wide and user-specific configuration
files is set in `tauruscustomsettings.SYSTEM_CFG_FILE` and
`tauruscustomsettings.USER_CFG_FILE`, respectively. The values are
platform-dependent:

- on posix systems we follow the xdg standard: `/etc/xdg/taurus/taurus.ini`
  for system and `~/.config/taurus/taurus.ini` for user.
- on windows machines we use `%PROGRAMDATA%\taurus\taurus.ini` for system
  and `%APPDATA%\taurus\taurus.ini` for user

In case of conflict, the user settings take precedence over the system
settings.

Custom setting file locations
-----------------------------

Apart from the default setting file locations, one can use the `--settings`
option when invoking the taurus CLI command to pass additional settings
file locations.

One can also programmatically call the `tauruscustomsettings.load_configs()`
function at any point to load other configuration files

In both cases, the values of existing variables in `tauruscustomsettings`
are overwritten in case of conflict).

Format of the settings files
----------------------------

The settings files are plain-text .ini files of the form::

    [taurus]
    FOO = "bar"
    BAR = [1, 2, 3]
    baz = False

The keys, which are **key-sensitive**, are exposed as `tauruscustomsettings`
variables and their **values are parsed as python literals** (e.g., in the above example,
`tauruscustomsettings.FOO` would be the `bar` string,
`tauruscustomsettings.BAR` would be a list and `tauruscustomsettings.baz`
would be a boolean).

Note that all key-values must be declared within a `[taurus]` section.


Default members of tauruscustomsettings
---------------------------------------

.. automodule:: taurus.tauruscustomsettings
    :members:
    :noindex:
    :undoc-members:
    :exclude-members: FORCE_READ_OPTIONS, load_configs
