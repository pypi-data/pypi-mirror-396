# -*- coding: utf-8 -*-
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
"""This module provides qt6 compatibility methods"""

from . import PYQT6  # noqa: E402

if PYQT6:
    import enum

    import PyQt6.sip

    def promote_enums(module):
        """
        Search enums in the given module and allow unscoped access.

        Taken from:
        https://github.com/pyqtgraph/pyqtgraph/blob/pyqtgraph-0.12.1/pyqtgraph/Qt.py#L331-L377
        and adapted to also copy enum values aliased under different names.

        """
        class_names = [name for name in dir(module) if name.startswith("Q")]
        for class_name in class_names:
            klass = getattr(module, class_name)
            if not isinstance(klass, PyQt6.sip.wrappertype):
                continue
            attrib_names = [name for name in dir(klass) if name[0].isupper()]
            for attrib_name in attrib_names:
                attrib = getattr(klass, attrib_name)
                if not isinstance(attrib, enum.EnumMeta):
                    continue
                for name, value in attrib.__members__.items():
                    setattr(klass, name, value)
