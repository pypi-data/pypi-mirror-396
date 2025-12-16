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

"""This package contains a collection of taurus Qt graphics view widgets"""

from .taurusgraphic import (
    TYPE_TO_GRAPHICS,
    QGraphicsTextBoxing,
    QSpline,
    SynopticSelectionStyle,
    TaurusBaseGraphicsFactory,
    TaurusEllipseStateItem,
    TaurusGraphicsAttributeItem,
    TaurusGraphicsItem,
    TaurusGraphicsScene,
    TaurusGraphicsStateItem,
    TaurusGraphicsUpdateThread,
    TaurusGroupItem,
    TaurusGroupStateItem,
    TaurusLineStateItem,
    TaurusPolygonStateItem,
    TaurusRectStateItem,
    TaurusRoundRectItem,
    TaurusRoundRectStateItem,
    TaurusSplineStateItem,
    TaurusTextAttributeItem,
    TaurusTextStateItem,
    parseTangoUri,
)
from .taurusgraphicview import TaurusGraphicsView

try:
    from .jdraw import TaurusJDrawGraphicsFactory, TaurusJDrawSynopticsView
except Exception:
    import taurus.core.util.log

    _logger = taurus.core.util.log.Logger(__name__)
    _logger.debug("jdraw widgets could not be initialized")
    _logger.traceback()


__all__ = [
    "SynopticSelectionStyle",
    "parseTangoUri",
    "TaurusGraphicsUpdateThread",
    "TaurusGraphicsScene",
    "QGraphicsTextBoxing",
    "QSpline",
    "TaurusGraphicsItem",
    "TaurusGraphicsAttributeItem",
    "TaurusGraphicsStateItem",
    "TaurusEllipseStateItem",
    "TaurusRectStateItem",
    "TaurusSplineStateItem",
    "TaurusRoundRectItem",
    "TaurusRoundRectStateItem",
    "TaurusGroupItem",
    "TaurusGroupStateItem",
    "TaurusPolygonStateItem",
    "TaurusLineStateItem",
    "TaurusTextStateItem",
    "TaurusTextAttributeItem",
    "TYPE_TO_GRAPHICS",
    "TaurusBaseGraphicsFactory",
    "TaurusJDrawGraphicsFactory",
    "TaurusJDrawSynopticsView",
    "TaurusGraphicsView",
]
__docformat__ = "restructuredtext"
