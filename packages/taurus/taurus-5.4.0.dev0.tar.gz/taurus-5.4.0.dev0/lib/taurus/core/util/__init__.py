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

"""This package consists of a collection of useful classes and functions. Most
of the elements are taurus independent and can be used generically."""

import taurus.tauruscustomsettings

__docformat__ = "restructuredtext"
__all__ = []

# import more stuff here for backwards-compatibility if required
if not getattr(taurus.tauruscustomsettings, "LIGHTWEIGHT_IMPORTS", False):
    from . import eventfilters  # noqa: F401
    from .codecs import *  # noqa: F403,F401
    from .colors import *  # noqa: F403,F401
    from .constant import *  # noqa: F403,F401
    from .containers import *  # noqa: F403,F401
    from .enumeration import *  # noqa: F403,F401
    from .event import *  # noqa: F403,F401
    from .log import *  # noqa: F403,F401
    from .object import *  # noqa: F403,F401
    from .prop import *  # noqa: F403,F401
    from .safeeval import *  # noqa: F403,F401
    from .singleton import *  # noqa: F403,F401
    from .threadpool import *  # noqa: F403,F401
    from .timer import *  # noqa: F403,F401
    from .user import *  # noqa: F403,F401

    try:
        from lxml import etree
    except Exception:
        etree = None
