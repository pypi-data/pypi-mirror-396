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
Release data for the taurus project. It contains the following members:

    - version : (str) version string
    - description : (str) brief description
    - long_description : (str) a long description
    - license : (str) license
    - authors : (dict<str, tuple<str,str>>) the list of authors
    - url : (str) the project url
    - download_url : (str) the project download url
    - platforms : list<str> list of supported platforms
    - keywords : list<str> list of keywords

The version string follows PEP440 (https://www.python.org/dev/peps/pep-0440)
Normally the release segment consists of 3 dot-separated numbers with the
same meanings as the "major", "minor" and "patch" components in
Semantic Versioning (http://semver.org/).

Exceptionally, we may use additional numbers in the release segment to
preserve a reasonable version sorting in the case of parallel releases (see
e.g. https://gitlab.com/taurus-org/taurus/-/issues/1192)
"""

__docformat__ = "restructuredtext"

# The version string is normally bumped using bumpversion script
# (https://github.com/peritus/bumpversion), except when adding/removing
# extra numbers in the release segment (e.g. for hotfixes), which is done
# manually.
version = "5.4.0.dev0"

name = "taurus"

description = "A framework for scientific/industrial CLIs and GUIs"

long_description = """Taurus is a python framework for control and data
acquisition CLIs and GUIs in scientific/industrial environments.
It supports multiple control systems or data sources: Tango, EPICS,...
New control system libraries can be integrated through plugins."""

license = "LGPL"

authors = {
    "Tiago_et_al": ("Tiago Coutinho et al.", ""),
    "Community": ("Taurus Community", "tauruslib-devel@lists.sourceforge.net"),
}

url = "http://www.taurus-scada.org"

download_url = "http://pypi.python.org/packages/source/t/taurus"

platforms = ["Linux", "Windows"]

keywords = ["CLI", "GUI", "PyTango", "Tango", "Shell", "Epics"]
