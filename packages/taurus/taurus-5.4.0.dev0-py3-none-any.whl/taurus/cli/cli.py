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

import click
import pkg_resources

import taurus
import taurus.cli.common

from . import common


@click.group("taurus")
@common.log_level
@common.poll_period
@common.serial_mode
@common.default_formatter
@common.disable_tango_event_subscription
@common.tango_event_sub_mode
@click.option(
    "--rconsole",
    "rconsole_port",
    type=click.INT,
    metavar="PORT",
    default=None,
    help="Enable remote debugging with rfoo on the given PORT",
)
@common.settings_files
@click.version_option(version=taurus.Release.version)
def taurus_cmd(
    log_level,
    polling_period,
    serialization_mode,
    default_formatter,
    disable_tango_event_subscription,
    tango_event_sub_mode,
    rconsole_port,
    settings_files,
):
    """The main taurus command"""
    from taurus import tauruscustomsettings

    # set log level
    taurus.setLogLevel(getattr(taurus, log_level))

    if settings_files:
        from taurus.tauruscustomsettings import load_configs

        load_configs(settings_files)
    # set polling period
    if polling_period is not None:
        taurus.changeDefaultPollingPeriod(polling_period)

    # set serialization mode
    if serialization_mode is not None:
        from taurus.core.taurusbasetypes import TaurusSerializationMode

        m = getattr(TaurusSerializationMode, serialization_mode)
        taurus.Manager().setSerializationMode(m)

    # enable the remote console port
    if rconsole_port is not None:
        try:
            import rfoo.utils.rconsole

            rfoo.utils.rconsole.spawn_server(port=rconsole_port)
            taurus.info(
                (
                    "rconsole started. "
                    + "You can connect to it by typing: rconsole -p %d"
                ),
                rconsole_port,
            )
        except Exception as e:
            taurus.warning("Cannot spawn debugger. Reason: %s", e)

    # set the default formatter
    if default_formatter is not None:
        setattr(tauruscustomsettings, "DEFAULT_FORMATTER", default_formatter)

    if disable_tango_event_subscription:
        taurus.Factory().set_tango_event_subscription_disabled(
            disable_tango_event_subscription
        )

    if tango_event_sub_mode is not None:
        setattr(
            tauruscustomsettings,
            "TANGO_EVENT_SUB_MODE",
            tango_event_sub_mode.upper(),
        )


def register_subcommands():
    """Discover and add subcommands to taurus_cmd"""

    # Add subcommands from the taurus_subcommands entry point
    for ep in pkg_resources.iter_entry_points("taurus.cli.subcommands"):
        try:
            subcommand = ep.load()
            taurus_cmd.add_command(subcommand)
        except Exception as e:
            taurus.warning(
                'Cannot add "%s" subcommand to taurus. Reason: %r', ep.name, e
            )


def main():
    """Register subcommands and run taurus_cmd"""

    # set the log level to WARNING avoid spamming the CLI while loading
    # subcommands
    # it will be restored to the desired one first thing in taurus_cmd()
    taurus.setLogLevel(taurus.Warning)

    # register the subcommands
    register_subcommands()

    # launch the taurus command
    taurus_cmd()


if __name__ == "__main__":
    main()
