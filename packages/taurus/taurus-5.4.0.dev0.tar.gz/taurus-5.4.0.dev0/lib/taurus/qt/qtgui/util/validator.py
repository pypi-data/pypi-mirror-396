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


import re

import pint
from pint import DimensionalityError

from taurus.core.units import Quantity
from taurus.external.qt import Qt


class PintValidator(Qt.QValidator):
    """A QValidator for pint Quantities"""

    _top = None
    _bottom = None
    _implicit_units = None

    @property
    def top(self):
        """
        :return: maximum accepted or None if it is not enforced
        :rtype: Quantity or None
        """
        return self._top

    def setTop(self, top):
        """
        Set maximum limit

        :param top: maximum acceptable value or None if it is not to be
            enforced
        :type top: Quantity or None
        """
        self._top = Quantity(top)

    @property
    def units(self):
        """
        :return: base units or None if it should not be enforced
        :rtype: pint.Unit or None
        """
        return self._implicit_units

    def setUnits(self, units):
        """Set implicit units. They will be assumed when the text does not
        explicit the unit. They will also be used for dimensionality coherence
        checks.

        :param units: The implicit unit. If None, implicit dimension is
            "unitless" and no dimensionality checks will be performed (other
            than those inherent to range enforcement)
        :type units: pint.Unit or None
        """
        self._implicit_units = units

    @property
    def bottom(self):
        """
        :return: minimum accepted or None if it is not enforced
        :rtype: Quantity or None
        """
        return self._bottom

    def setBottom(self, bottom):
        """
        Set minimum limit

        :param bottom: minimum acceptable value or None if it is not to be
            enforced
        :type bottom: Quantity or None
        """
        self._bottom = Quantity(bottom)

    def validate(self, input, pos):
        """Reimplemented from :class:`QValidator` to validate if the input
        string is a representation of a quantity within the set bottom and top
        limits
        """
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # workaround for
        # https://github.com/hgrecco/pint/issues/614
        # see it also in TaurusLineEdit.getValue()
        if re.match(r"^[\+\-]?\s*0+[1-9]+[^.]*$", input.strip()):
            return Qt.QValidator.Intermediate, input, pos
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        try:
            q = Quantity(input)
        except pint.errors.OffsetUnitCalculusError:
            value, units = input.split()
            q = Quantity(float(value), units)
        except Exception:
            return Qt.QValidator.Intermediate, input, pos
        if self._implicit_units is not None:
            if q.unitless:
                # "cast" to implicit units
                q = Quantity(q.magnitude, self.units)
            # check coherence with implicit units
            elif self._implicit_units.dimensionality != q.dimensionality:
                return Qt.QValidator.Intermediate, input, pos
        try:
            if self.bottom is not None and q < self.bottom:
                return Qt.QValidator.Intermediate, input, pos
            if self.top is not None and q > self.top:
                return Qt.QValidator.Intermediate, input, pos
        except DimensionalityError:
            return Qt.QValidator.Intermediate, input, pos
        return Qt.QValidator.Acceptable, input, pos
