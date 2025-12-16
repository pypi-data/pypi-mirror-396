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

"""deprecated. See taurus._release"""

from taurus import deprecated

from .._release import (  # noqa
    authors,
    description,
    download_url,
    keywords,
    license,
    long_description,
    name,
    platforms,
    url,
    version,
)

deprecated(dep="taurus.core.release", alt="taurus.Release", rel="5.0.0")

# generate version_info and revision (**deprecated** since version 4.0.2-dev).
if "-" in version:
    (_v, _rel), _r = version.split("-"), "0"
elif ".dev" in version:
    (_v, _r), _rel = version.split(".dev"), "dev"
else:
    _v, _rel, _r = version, "", "0"
_v = tuple([int(n) for n in _v.split(".")])
version_info = _v + (_rel, int(_r))  # deprecated, do not use
revision = _r  # deprecated, do not use
