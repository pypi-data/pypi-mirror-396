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
taurusgraphic.py:
"""

# TODO: Tango-centric

import importlib
import os
import queue
import re
import subprocess
import traceback
from collections.abc import Sequence

from taurus import Manager
from taurus.core import AttrQuality, DataType
from taurus.core.taurusattribute import TaurusAttribute
from taurus.core.taurusdevice import TaurusDevice
from taurus.core.util.containers import CaselessDefaultDict
from taurus.core.util.enumeration import Enumeration
from taurus.core.util.log import Logger, deprecation_decorator
from taurus.external.qt import Qt, compat
from taurus.qt.qtgui.base import TaurusBaseComponent
from taurus.qt.qtgui.util import (
    QT_ATTRIBUTE_QUALITY_PALETTE,
    QT_DEVICE_STATE_PALETTE,
    ExternalAppAction,
    TaurusWidgetFactory,
)

__docformat__ = "restructuredtext"


SynopticSelectionStyle = Enumeration(
    "SynopticSelectionStyle",
    [
        # A blue ellipse is displayed around the selected objects
        "ELLIPSE",
        # The own outline of selected object is displayed in blue and bolder
        "OUTLINE",
    ],
)


def parseTangoUri(name):
    # TODO: Tango-centric
    from taurus.core import tango
    from taurus.core.tango.tangovalidator import (
        TangoAttributeNameValidator,
        TangoDeviceNameValidator,
    )

    validator = {
        tango.TangoDevice: TangoDeviceNameValidator,
        tango.TangoAttribute: TangoAttributeNameValidator,
    }
    try:
        val = validator[tango.TangoFactory().findObjectClass(name)]()
        params = val.getUriGroups(name)
        return params if "_devslashname" in params else None
    except Exception:
        return None


class QEmitter(Qt.QObject):
    updateView = Qt.pyqtSignal(compat.PY_OBJECT)


class TaurusGraphicsUpdateThread(Qt.QThread):
    """
    Thread to update the :class:`TaurusGraphicsScene`.
    """

    def __init__(self, parent, scene, period=3):
        if not isinstance(scene, TaurusGraphicsScene):
            raise RuntimeError("Illegal scene for TaurusGraphicsUpdateThread")
        Qt.QThread.__init__(self, parent)
        self.scene = scene
        self.period = period
        self.log = Logger("TaurusGraphicsUpdateThread")
        self._emitter = self._createEmitter()

    def _updateView(self, v):
        # The first one is the prefered one because it improves performance
        # since updates don't come very often in comparison to with the refresh
        # rate of the monitor (~70Hz)
        if v.viewportUpdateMode() == Qt.QGraphicsView.NoViewportUpdate:
            # We call the update to the viewport instead of the view
            # itself because apparently there is a bug in QT 4.3 that
            # prevents a proper update when the view is inside a QTab
            v.viewport().update()
        # else:
        #     # @todo This is probably a bug (item_rects is not defined).
        #     #       But it is defined in .run(), see "todo" below...
        #     v.updateScene(item_rects)
        #     # v.invalidateScene(item.boundingRect())
        return

    def _createEmitter(self):
        """This have to be called by the scene thread"""
        emitter = QEmitter(Qt.QApplication.instance())
        emitter.moveToThread(Qt.QApplication.instance().thread())
        emitter.updateView.connect(self._updateView)
        return emitter

    def run(self):
        self.log.debug("run... - TaurusGraphicsUpdateThread")

        scene = self.scene
        emitter = self._emitter
        while True:
            item = scene.getQueue().get(True)
            if type(item) in (str,):
                if item == "exit":
                    break
                else:
                    continue
            if not isinstance(item, Sequence):
                item = (item,)
            # todo: Unless the call to boundingRect() has a side effect,
            #       this line is useless.
            #       probably related to todo in _updateView()
            # item_rects = [i.boundingRect() for i in item]

            for v in scene.views():
                # scene.debug("emit('updateView')")
                emitter.updateView.emit(v)
            # This sleep is needed to reduce CPU usage of the application!
            self.sleep(self.period)
            # End of while
        # End of Thread

        self.log.debug("stop - TaurusGraphicsUpdateThread")


class TaurusGraphicsScene(Qt.QGraphicsScene):
    """
    This class encapsulates TaurusJDrawSynopticsView and TaurusGraphicsScene
    signals/slots

    External events::

     Slot selectGraphicItem(const QString &) displays a selection
     mark around the TaurusGraphicsItem that matches the argument passed.

    Mouse Left-button events::

     Signal graphicItemSelected(QString) is triggered, passing the
     selected TaurusGraphicsItem.name() as argument.

    Mouse Right-button events::

     TaurusGraphicsItem.setContextMenu([(ActionName,ActionMethod(device_name))]
     allows to configure custom context menus for graphic items using a list
     of tuples. Empty tuples will insert separators in the menu.
    """

    ANY_ATTRIBUTE_SELECTS_DEVICE = True
    TRACE_ALL = False

    refreshTree2 = Qt.pyqtSignal()
    graphicItemSelected = Qt.pyqtSignal("QString")
    graphicSceneClicked = Qt.pyqtSignal("QPoint")

    def __init__(self, parent=None, strt=True):
        name = self.__class__.__name__
        Qt.QGraphicsScene.__init__(self, parent)
        self.updateQueue = None
        self.updateThread = None
        self._itemnames = CaselessDefaultDict(lambda k: set())
        self._selection = []
        self._selectedItems = []
        self._selectionStyle = SynopticSelectionStyle.OUTLINE
        self.threads = []
        self.pids = []
        self.panels = []
        self.panel_launcher = None

        try:
            self.logger = Logger(name)
            # self.logger.setLogLevel(self.logger.Info)
            if not self.TRACE_ALL:
                self.debug = self.logger.debug
                self.info = self.logger.info
                self.warning = self.logger.warning
            else:
                _w = self.logger.warning
                self.debug = self.info = self.warning = self.error = _w
        except Exception:
            print(
                "Unable to initialize TaurusGraphicsSceneLogger: %s"
                % traceback.format_exc()
            )

        try:
            if parent and parent.panelClass() is not None:
                defaultClass = parent.panelClass()
                if defaultClass and isinstance(defaultClass, str):
                    self.panel_launcher = self.getClass(defaultClass)
                    if self.panel_launcher is None:
                        self.panel_launcher = ExternalAppAction(defaultClass.split())
                else:
                    self.panel_launcher = defaultClass
            else:
                from taurus.qt.qtgui.graphic import TaurusJDrawSynopticsView

                self.panel_launcher = TaurusJDrawSynopticsView.defaultPanelClass()
        except Exception:
            self.warning(traceback.format_exc())
            self.panel_launcher = None

        self.setSelectionMark()
        if strt:
            self.start()

        self.destroyed.connect(self.stop)
        if parent is not None:
            # Stop connected to a QWidget sounds safer
            parent.destroyed.connect(self.stop)

    def __del__(self):
        self.closeAllPanels()
        self.stop()

    def showNewPanel(self, args=None, standAlone=False):
        try:
            if isinstance(args, TaurusGraphicsItem):
                objName = args._name
                clName = args.getExtensions().get("className") or self.panel_launcher
                # classParams extension overrides Model; if there's no
                # extension then object name is used
                clParam = args.getExtensions().get("classParams") or objName
                # standAlone = args.standAlone
            else:
                clName, clParam, objName = self.panel_launcher, args, args
            if not clName or clName == "noPanel":
                return
            self.debug(
                "TaurusGraphicsScene.showNewPanel(%s,%s,%s)"
                % (clName, clParam, objName)
            )
            if isinstance(clName, ExternalAppAction):
                clName.actionTriggered(
                    clParam if isinstance(clParam, (list, tuple)) else [clParam]
                )
            else:
                if isinstance(clName, str):
                    klass = self.getClass(clName)
                    if klass is None:
                        self.warning("%s Class not found!" % clName)
                        klass = self.getClass("TaurusDevicePanel")
                else:
                    klass, clName = clName, getattr(clName, "__name__", str(clName))
                widget = klass()
                try:
                    widget.setClasses(clParam)
                except Exception:
                    pass
                try:
                    widget.setModel(clParam)
                except Exception:
                    pass
                try:
                    widget.setTable(clParam)
                except Exception:
                    pass

                # if isinstance(widget,Qt.QWidget):
                # if not standAlone:
                # obj = newDialog(self.parent())
                # else:
                # obj = newDialog()
                # obj.initComponents(widget,objName,clName)
                # obj.setModal(False)
                # obj.setVisible(True)

                widget.setWindowTitle("%s - %s" % (clName, objName))
                self.panels.append(widget)
                widget.show()  # exec_()
                return widget
        except Exception:
            self.warning(traceback.format_exc())

    def closeAllPanels(self):
        """This method replaces killProcess, using
        taurus.qt.qtgui.util.ExternalAppAction instead!
        """
        try:
            self.debug("In closeAllPanels(%s,%s)" % (self.panel_launcher, self.panels))
            if isinstance(self.panel_launcher, ExternalAppAction):
                self.panel_launcher.kill()
            for p in self.panels:
                try:
                    if hasattr(p, "setModel"):
                        p.setModel(None)
                    p.close()
                except Exception:
                    pass
            while self.panels:
                self.panels.pop(0)
        except Exception:
            self.warning(traceback.format_exc())

    def addItem(self, item):
        # self.debug('addItem(%s)'%item)
        def expand(i):
            name = str(getattr(i, "_name", "")).lower()
            if name:
                self._itemnames[name].add(i)
                # self.debug('addItem(%s): %s'%(name,i))
            if isinstance(i, Qt.QGraphicsItemGroup):
                for j in i.childItems():
                    expand(j)

        expand(item)
        Qt.QGraphicsScene.addItem(self, item)

    def addWidget(self, item, flags=None):
        self.debug("addWidget(%s)" % item)
        name = str(getattr(item, "_name", "")).lower()
        if name:
            self._itemnames[name].add(item)
        if flags is None:
            Qt.QGraphicsScene.addWidget(self, item)
        else:
            Qt.QGraphicsScene.addWidget(self, item, flags)

    def getItemByName(self, item_name, strict=None):
        """
        Returns a list with all items matching a given name.

        :param strict: controls whether full_name (strict=True) or only device
            name (False) must match
        :type strict: bool or None
        :return: items
        :rtype: list
        """

        # TODO: Tango-centric
        from taurus.core.tango.tangovalidator import (
            TangoAttributeNameValidator,
            TangoDeviceNameValidator,
        )

        strict = (not self.ANY_ATTRIBUTE_SELECTS_DEVICE) if strict is None else strict
        alnum = r"(?:[a-zA-Z0-9-_\*]|(?:\.\*))(?:[a-zA-Z0-9-_\*]|(?:\.\*))*"
        target = (
            str(item_name).strip().split()[0].lower().replace("/state", "")
        )  # If it has spaces only the first word is used
        # Device names should match also its attributes or only state?
        if not strict and TangoAttributeNameValidator().getUriGroups(target):
            target = target.rsplit("/", 1)[0]
        if TangoDeviceNameValidator().getUriGroups(target):
            if strict:
                target += "(/state)?"
            else:
                target += "(/" + alnum + ")?"
        if not target.endswith("$"):
            target += "$"
        result = []
        for k in list(self._itemnames.keys()):
            if re.match(target.lower(), k.lower()):
                result.extend(self._itemnames[k])
        return result

    def getItemByPosition(self, x, y):
        """This method will try first with named objects;
        if failed then with itemAt
        """
        pos = Qt.QPointF(x, y)
        itemsAtPos = []
        for z, o in sorted(
            (i.zValue(), i)
            for v in self._itemnames.values()
            for i in v
            if i.contains(pos) or i.isUnderMouse()
        ):
            if not hasattr(o, "getExtensions"):
                self.debug(
                    "getItemByPosition(%d,%d): adding Qt primitive %s" % (x, y, o)
                )
                itemsAtPos.append(o)
            elif not o.getExtensions().get("noSelect"):
                self.debug(
                    "getItemByPosition(%d,%d): adding GraphicsItem %s" % (x, y, o)
                )
                itemsAtPos.append(o)
            else:
                self.debug("getItemByPosition(%d,%d): object ignored, %s" % (x, y, o))
        if itemsAtPos:
            obj = itemsAtPos[-1]
            return self.getTaurusParentItem(obj) or obj
        else:
            # return self.itemAt(x,y)
            self.debug("getItemByPosition(%d,%d): no items found!" % (x, y))
            return None

    def getItemClicked(self, mouseEvent):
        pos = mouseEvent.scenePos()
        x, y = pos.x(), pos.y()
        self.graphicSceneClicked.emit(Qt.QPoint(int(x), int(y)))
        obj = self.getItemByPosition(x, y)
        return obj

    def mousePressEvent(self, mouseEvent):
        try:
            obj = self.getItemClicked(mouseEvent)
            obj_name = getattr(obj, "_name", "")
            if not obj_name and isinstance(obj, QGraphicsTextBoxing):
                obj_name = obj.toPlainText()
            if mouseEvent.button() == Qt.Qt.LeftButton:
                # A null obj_name should deselect all, we don't send obj
                # because we want all similar to be matched
                if self.selectGraphicItem(obj_name):
                    self.debug(" => graphicItemSelected(QString)(%s)" % obj_name)
                    self.graphicItemSelected.emit(obj_name)
                else:
                    # It should send None but the signature do not allow it
                    self.graphicItemSelected.emit("")

            def addMenuAction(menu, k, action, last_was_separator=False):
                try:
                    if k:
                        configDialogAction = menu.addAction(k)
                        if action:
                            configDialogAction.triggered.connect(
                                lambda: action(obj_name)
                            )
                        else:
                            configDialogAction.setEnabled(False)
                        last_was_separator = False
                    elif not last_was_separator:
                        menu.addSeparator()
                        last_was_separator = True
                except Exception as e:
                    self.warning("Unable to add Menu Action: %s:%s" % (k, e))
                return last_was_separator

            if mouseEvent.button() == Qt.Qt.RightButton:
                """This function is called when right clicking on
                TaurusDevTree area. A pop up menu will be shown with the
                available options.
                """
                self.debug("RightButton Mouse Event on %s" % (obj_name))
                if isinstance(obj, TaurusGraphicsItem) and (
                    obj_name or obj.contextMenu() or obj.getExtensions()
                ):
                    menu = Qt.QMenu(None)  # self.parent)
                    last_was_separator = False
                    extensions = obj.getExtensions()
                    if obj_name and (not extensions or not extensions.get("className")):
                        # menu.addAction(obj_name)
                        addMenuAction(
                            menu,
                            "Show %s panel" % obj_name,
                            lambda x=obj_name: self.showNewPanel(x),
                        )
                    if obj.contextMenu():
                        if obj_name:
                            menu.addSeparator()
                            last_was_separator = True
                        for t in (
                            obj.contextMenu()
                        ):  # must be list of tuples (ActionName,ActionMethod)
                            last_was_separator = addMenuAction(
                                menu, t[0], t[1], last_was_separator
                            )
                    if extensions:
                        if not menu.isEmpty():
                            menu.addSeparator()
                        className = extensions.get("className")
                        if className and className != "noPanel":
                            self.debug("launching className extension object")
                            addMenuAction(
                                menu,
                                "Show %s" % className,
                                lambda d, x=obj: self.showNewPanel(x),
                            )
                        if extensions.get("shellCommand"):
                            addMenuAction(
                                menu,
                                "Execute",
                                lambda d, x=obj: self.getShellCommand(x),
                            )
                    if not menu.isEmpty():
                        menu.exec_(
                            Qt.QPoint(
                                mouseEvent.screenPos().x(),
                                mouseEvent.screenPos().y(),
                            )
                        )
                    del menu
        except Exception:
            self.warning(traceback.format_exc())

    def mouseDoubleClickEvent(self, event):
        try:
            obj = self.getItemClicked(event)
            obj_name = getattr(obj, "_name", "")
            try:
                class_name = obj.getExtensions().get("className")
            except Exception:
                class_name = "noPanel"
            self.debug("Clicked (%s,%s,%s)" % (obj, obj_name, class_name))
            if obj_name and class_name != "noPanel":
                self.showNewPanel(obj)
        except Exception:
            self.warning(traceback.format_exc())

    def setSelectionStyle(self, selectionStyle):
        # TODO We should test that selectionStyle is part of
        # SynopticSelectionStyle but there is nothing about it
        self._selectionStyle = selectionStyle

    def selectGraphicItem(self, item_name):
        """
        A blue circle is drawn around the matching item name.
        If the item_name is empty, or it is a reserved keyword,
        or it has the "noSelect" extension, then the blue circle is
        removed from the synoptic.
        """
        selected = [
            str(getattr(item, "_name", item)) for item in self._selectedItems if item
        ]
        if selected:
            iname = str(getattr(item_name, "_name", item_name))
            if not iname.strip():
                self.clearSelection()
                return False
            elif any(iname not in i for i in selected):
                self.clearSelection()
            else:
                self.debug(
                    "In TauGraphicsScene.selectGraphicItem(%s): " + "already selected!",
                    item_name,
                )
                return True
        if any(
            isinstance(item_name, t) for t in (TaurusGraphicsItem, Qt.QGraphicsItem)
        ):
            if not getattr(item_name, "_name", ""):
                self.debug(
                    "In TauGraphicsScene.selectGraphicItem(%s): item name not found.",
                    item_name,
                )
                return False
            items = [item_name]
        else:
            from .jdraw.jdraw_parser import reserved

            if not item_name or (
                str(item_name).startswith("JD") and str(item_name) in reserved
            ):
                self.debug(
                    "In TauGraphicsScene.selectGraphicItem(%s): "
                    + "item name not found or name is a reserved keyword.",
                    item_name,
                )
                return False
            items = self.getItemByName(item_name) or []
            items = [
                i
                for i in items
                if self.getTaurusParentItem(i) not in (items + self._selectedItems)
            ]
            self.debug(
                "In TaurusGraphicsScene.selectGraphicItem(%s)): " + "matched %d items",
                item_name,
                len(items),
            )

        if self._selectionStyle == SynopticSelectionStyle.ELLIPSE:
            displaySelection = self._displaySelectionAsEllipse
        elif self._selectionStyle == SynopticSelectionStyle.OUTLINE:
            displaySelection = self._displaySelectionAsOutline
        else:
            raise Exception(
                "Unexpected selectionStyle '%s'"
                % SynopticSelectionStyle.whatis(self._selectionStyle)
            )
        return displaySelection(items)

    def _displaySelectionAsEllipse(self, items):
        retval = False
        for item in items:
            try:
                if (
                    (
                        isinstance(item, TaurusGraphicsItem)
                        and item.getExtensions().get("noSelect")
                    )
                    or (item in self._selection)
                    # or (item in tangoGroup)
                ):
                    continue
                x, y = item.x(), item.y()
                rect = item.boundingRect()
                srect = self.sceneRect()
                # 0 has to be excluded to check grouped element
                if not (0 < x <= self.sceneRect().width() and 0 < y <= srect.height()):
                    rx, ry = rect.topLeft().x(), rect.topLeft().y()
                    self.debug(
                        "\tposition not well mapped (%s,%s), "
                        + "using rect bound (%s,%s) instead",
                        x,
                        y,
                        rx,
                        ry,
                    )
                    x, y = (
                        rx,
                        ry,
                    )  # If the object is in the corner it will be also 0
                w, h = rect.width(), rect.height()
                if x < 0 or y < 0:
                    self.debug(
                        "Cannot draw SelectionMark for %s(%s)(%s,%s) "
                        + "in a negative position (%f,%f)",
                        type(item).__name__,
                        item._name,
                        w,
                        h,
                        x,
                        y,
                    )
                else:
                    if type(item) in (
                        TaurusTextAttributeItem,
                        TaurusTextStateItem,
                    ) and isinstance(self.getSelectionMark(), Qt.QGraphicsPixmapItem):
                        x, y, w, h = x - 20, y, 20, 20
                    self.drawSelectionMark(x, y, w, h)
                    self.debug(
                        "> Moved the SelectionMark to " + "item %s(%s)(%s,%s) at %f,%f",
                        type(item).__name__,
                        item._name,
                        w,
                        h,
                        x,
                        y,
                    )
                if item not in self._selectedItems:
                    self._selectedItems.append(item)
                retval = True
            except Exception as e:
                self.warning(
                    "selectGraphicsItem(%s) failed! %s"
                    % (getattr(item, "_name", item), str(e))
                )
                self.warning(traceback.format_exc())
                # return False
        return retval

    def _displaySelectionAsOutline(self, items):
        def _outline(shapes):
            """ "Compute the boolean union from a list of QGraphicsItem."""
            shape = None
            # TODO we can use a stack instead of recursivity
            for s in shapes:
                # TODO we should skip text and things like that
                if isinstance(s, TaurusGroupItem):
                    s = _outline(s.childItems())
                    if s is None:
                        continue

                s = s.shape()
                if shape is not None:
                    shape = shape.united(s)
                else:
                    shape = s

            if shape is None:
                return None

            return Qt.QGraphicsPathItem(shape)

        # TODO we can cache the outline instead of computing it again and again
        selectionShape = _outline(items)
        if selectionShape:
            # copy-paste from getSelectionMark
            color = Qt.QColor(Qt.Qt.blue)
            color.setAlphaF(0.10)
            pen = Qt.QPen(Qt.Qt.SolidLine)
            pen.setWidth(4)
            pen.setColor(Qt.QColor(Qt.Qt.blue))
            selectionShape.setBrush(color)
            selectionShape.setPen(pen)

            for item in items:
                if item not in self._selectedItems:
                    self._selectedItems.append(item)

            # TODO i dont think this function work... or i dont know how...
            # self.setSelectionMark(picture=selectionShape)
            # ... Then do it it with hands...
            # copy-paste from drawSelectionMark
            self._selection.append(selectionShape)
            # It's better to add it hidden to avoid resizings
            selectionShape.hide()
            self.addItem(selectionShape)
            # Put on Top
            selectionShape.setZValue(9999)
            selectionShape.show()
            self.updateSceneViews()

            return True

        return False

    def clearSelection(self):
        # self.debug('In clearSelection([%d])'%len(self._selectedItems))
        for i in self._selection:
            i.hide()
            self.removeItem(i)
        self._selection = []
        self._selectedItems = []
        self.updateSceneViews()

    def setSelectionMark(self, picture=None, w=10, h=10):
        """This method allows to set a callable, graphic item or pixmap as
        selection mark (by default creates a blue circle).
        If picture is a callable, the object returned will be used as
        selection mark.
        If picture is a QGraphicsItem it will be used as selection mark.
        If picture is a QPixmap or a path to a pixmap a QGraphicsPixmapItem
        will be created.
        If no picture is provided, a blue ellipse will be drawn around the
        selected object.
        h/w will be used for height/width of the drawn object.
        """
        # self.debug('In setSelectionMark(%s,%d,%d)'%(picture,w,h))
        if picture is None:
            self.SelectionMark = None  # Reset of previous icon generators
        else:
            self.SelectionMark = lambda p=picture, x=w, y=h: self.getSelectionMark(
                p, x, y
            )
        return self.SelectionMark

    def getSelectionMark(self, picture=None, w=10, h=10):
        if picture is None:
            if self.SelectionMark:
                SelectionMark = self.SelectionMark()
            else:
                SelectionMark = Qt.QGraphicsEllipseItem()
                color = Qt.QColor(Qt.Qt.blue)
                color.setAlphaF(0.10)
                SelectionMark.setBrush(color)
                pen = Qt.QPen(Qt.Qt.CustomDashLine)
                pen.setWidth(4)
                pen.setColor(Qt.QColor(Qt.Qt.blue))
                SelectionMark.setPen(pen)
                SelectionMark.hide()  # hide to avoid resizings
        else:
            try:
                if isinstance(picture, Qt.QGraphicsItem):
                    SelectionMark = picture
                    SelectionMark.setRect(0, 0, w, h)
                    SelectionMark.hide()
                elif hasattr(picture, "__call__"):
                    SelectionMark = picture()
                else:
                    if isinstance(picture, Qt.QPixmap):
                        pixmap = picture
                    elif isinstance(picture, str):
                        picture = str(picture)
                        pixmap = Qt.QPixmap(os.path.realpath(picture))
                    SelectionMark = Qt.QGraphicsPixmapItem()
                    SelectionMark.setPixmap(pixmap.scaled(w, h))
                    SelectionMark.hide()
            except Exception:
                self.debug(
                    "In setSelectionMark(%s): %s" % (picture, traceback.format_exc())
                )
                picture = None
        return SelectionMark

    def drawSelectionMark(self, x, y, w, h, oversize=1):
        """
        If h or w are None the mark is drawn at x,y
        If h or w has a value the mark is drawn in the center of the
        region ((x,y)(x+w,y+h))
        """

        mark = self.getSelectionMark()
        self._selection.append(mark)
        srect = self.itemsBoundingRect()
        MAX_CIRCLE_SIZE = srect.width(), srect.height()  # 500,500 #20,20
        LIMITS = (0, 0, srect.width(), srect.height())

        def bound(coords, bounds=LIMITS):
            """x,y,w,h"""
            x, y, w, h = coords
            if x < bounds[0]:
                w, x = w - (bounds[0] - x), bounds[0]
            if y < bounds[1]:
                h, y = h - (bounds[1] - y), bounds[1]
            if x + w > bounds[2]:
                w, x = (bounds[2] - x), x
            if y + h > bounds[3]:
                h, y = (bounds[3] - y), y
            return x, y, w, h

        if isinstance(mark, Qt.QGraphicsEllipseItem):
            if None not in [w, h]:
                if w > MAX_CIRCLE_SIZE[0] or h > MAX_CIRCLE_SIZE[1]:
                    # Applying correction if the file is too big, half max
                    # circle size around the center
                    x, y = (
                        (x + w / 2.0) - 0.5 * MAX_CIRCLE_SIZE[0],
                        (y + h / 2.0) - 0.5 * MAX_CIRCLE_SIZE[1],
                    )
                    w, h = [0.5 * t for t in MAX_CIRCLE_SIZE]
                else:
                    x, y = x - 0.5 * w, y - 0.5 * h
            else:
                w, h = [0.5 * t for t in MAX_CIRCLE_SIZE]
            mark.setRect(*bound((x, y, w * 2, h * 2)))
            # mark.setRect(x,y,w*2,h*2)
        elif isinstance(mark, Qt.QGraphicsPixmapItem):
            rect = mark.boundingRect()
            if None not in [w, h]:
                x, y = x + 0.5 * w, y + 0.5 * h
            mark.setOffset(x - 0.5 * rect.width(), y - 0.5 * rect.height())
        elif isinstance(mark, Qt.QGraphicsItem):
            mark.setRect(x, y, w, h)

        mark.hide()  # It's better to add it hidden to avoid resizings
        self.addItem(mark)
        mark.setZValue(9999)  # Put on Top
        mark.show()
        self.updateSceneViews()
        return

    def getShellCommand(self, obj, wait=False):
        shellCom = (
            obj.getExtensions()
            .get("shellCommand")
            .replace("$NAME", obj._name)
            .replace("$MODEL", obj._name)
        )
        if not wait and not shellCom.endswith("&"):
            shellCom += " &"
        if obj.noPrompt:
            subprocess.call(shellCom, shell=True)
        else:
            yes = Qt.QMessageBox.Ok
            no = Qt.QMessageBox.Cancel
            result = Qt.QMessageBox.question(
                self.parent(),
                "Shell command",
                "Would you like to call shell command '" + shellCom + "' ?",
                yes,
                no,
            )
            if result == yes:
                subprocess.call(shellCom, shell=True)
        return

    def getClass(self, clName):
        if not clName or clName == "noPanel":
            return None
        elif clName in ("atkpanel.MainPanel", "atkpanel"):
            clName = "TaurusDevicePanel"
        if clName in globals():
            return globals()[clName]
        elif clName in locals():
            return locals()[clName]
        elif clName in dir(Qt):
            return getattr(Qt, clName)
        else:
            # support passing class names as 'modname:classname'
            if ":" in clName:
                # assuming pkg_resources-style spec:  modname:object[.attr]
                mod_name, class_name = self._widgetClassName.split(":")
                return getattr(importlib.import_module(mod_name), class_name, None)
            # fall back to using TaurusWidgetFactory, deprecated
            _qt_widgets = TaurusWidgetFactory()._qt_widgets
            if clName in _qt_widgets:
                _modname, _cls = _qt_widgets[clName]
                self.logger.deprecated(
                    dep="specifying class as '{}'".format(clName),
                    alt="'{}:{}'".format(_modname, clName),
                    rel="5.0.0",
                )
                return _cls
            else:
                return None

    @staticmethod
    def getTaurusParentItem(item, top=True):
        """Searches within a group hierarchy and returns a parent Taurus
        component or None if no parent TaurusBaseComponent is found.
        """
        if item is None:
            return None
        first, p = None, item.parentItem()
        while p:
            if isinstance(p, TaurusGraphicsItem):
                if first is None:
                    first = p
                    if not top:
                        break
                elif str(p.getModel()) != str(first.getModel()):
                    break
                else:
                    first = p
            p = p.parentItem()
        return first

    def getAllChildren(self, item, klass=None):
        """Returns all children elements, filtering by klass if wanted"""
        result = []
        try:
            children = item.childItems()
            result.extend(c for c in children if not klass or isinstance(c, klass))
            result.extend(
                c.childItems() for c in children if not klass or isinstance(c, klass)
            )
        except Exception:
            pass
        return result

    def start(self):
        if self.updateThread:
            return
        self.updateQueue = queue.Queue()
        self.updateThread = TaurusGraphicsUpdateThread(None, self)
        self.updateThread.start()  # Qt.QThread.HighPriority)

    def stop(self):
        if not self.updateThread:
            return

        # Clear the queue
        # No need to process anything anymore
        try:
            while True:
                self.updateQueue.get(False)
        except queue.Empty:
            pass

        self.updateQueue.put("exit")
        self.updateThread.wait()
        self.updateThread = None

    def getQueue(self):
        return self.updateQueue

    def updateSceneItem(self, item):
        self.updateQueue.put(item)

    def updateSceneItems(self, items):
        self.updateQueue.put(items)

    def updateScene(self):
        self.update()

    def updateSceneViews(self):
        for v in self.views():
            v.viewport().update()
            # v.invalidateScene(self.SelectionCircle.boundingRect())
        return


class QGraphicsTextBoxing(Qt.QGraphicsItemGroup):
    """Display a text inside a virtual box. Support horizontal and vertical
    alignment
    """

    _TEXT_RATIO = 0.8

    def __init__(self, parent=None, scene=None):
        Qt.QGraphicsItemGroup.__init__(self, parent)
        if scene is not None:
            scene.addItem(self)
        self._rect = Qt.QGraphicsRectItem(self)
        if scene is not None:
            scene.addItem(self._rect)
        self._rect.setBrush(Qt.QBrush(Qt.Qt.NoBrush))
        self._rect.setPen(Qt.QPen(Qt.Qt.NoPen))
        self._text = Qt.QGraphicsTextItem(self)
        if scene is not None:
            scene.addItem(self._text)
        self._text.setTransform(
            Qt.QTransform.fromScale(self._TEXT_RATIO, self._TEXT_RATIO), True
        )

        self._validBackground = None
        # using that like the previous code create a worst result
        self.__layoutValide = True
        self._alignment = Qt.Qt.AlignCenter | Qt.Qt.AlignVCenter

    def setRect(self, x, y, width, height):
        self._rect.setRect(x, y, width, height)
        self._invalidateLayout()

    def setPlainText(self, text):
        self._text.setPlainText(text)
        self._invalidateLayout()

    def setValidBackground(self, color):
        self._validBackground = color

    def toPlainText(self):
        return self._text.toPlainText()

    def brush(self):
        return self._rect.brush()

    def setBrush(self, brush):
        self._rect.setBrush(brush)

    def pen(self):
        return self._rect.pen()

    def setPen(self, pen):
        self._rect.setPen(pen)

    def setDefaultTextColor(self, color):
        self._text.setDefaultTextColor(color)

    def setHtml(self, html):
        self._text.setHtml(html)
        self._invalidateLayout()

    def setFont(self, font):
        self._text.setFont(font)
        self._invalidateLayout()

    def setAlignment(self, alignment):
        self._alignment = alignment
        self._invalidateLayout()

    def _invalidateLayout(self):
        """Invalidate the current location of the text"""
        if not self.__layoutValide:
            return
        self.__layoutValide = False
        self.update()

    def _validateLayout(self):
        """Compute the text location"""
        if self.__layoutValide:
            return

        rect = self._rect.rect()
        width, height = rect.width(), rect.height()
        textRect = self._text.boundingRect()

        # horizontal layout
        x = rect.x()
        alignment = int(self._alignment)
        if (alignment & int(Qt.Qt.AlignLeft)) != 0:
            x += 0
        elif (alignment & int(Qt.Qt.AlignHCenter)) != 0:
            x += width * 0.5 - textRect.width() * 0.5 * self._TEXT_RATIO
        elif (alignment & int(Qt.Qt.AlignRight)) != 0:
            x += width - textRect.width() * self._TEXT_RATIO

        # vertical layout
        y = rect.y()
        if (alignment & int(Qt.Qt.AlignTop)) != 0:
            y += 0
        elif (alignment & int(Qt.Qt.AlignVCenter)) != 0:
            y += height * 0.5 - textRect.height() * 0.5 * self._TEXT_RATIO
        elif (alignment & int(Qt.Qt.AlignBottom)) != 0:
            y += height - textRect.height() * self._TEXT_RATIO

        self._text.setPos(x, y)
        self.__layoutValide = True

    def paint(self, painter, option, widget):
        self._validateLayout()
        Qt.QGraphicsItemGroup.paint(self, painter, option, widget)


class QSpline(Qt.QGraphicsPathItem):
    def __init__(self, parent=None, closed=False, control_points=None):
        super(QSpline, self).__init__(parent)
        self.__closed = closed
        if control_points is None:
            control_points = []
        self.setControlPoints(control_points)

    def setControlPoints(self, control_points):
        self.__control_points = control_points
        self.updateSplinePath()

    def setClose(self, isClosed):
        if self.__closed == isClosed:
            return
        self.__closed = isClosed
        self.updateSplinePath()

    def updateSplinePath(self):
        path = Qt.QPainterPath()
        cp = self.__control_points
        nb_points = len(cp)
        if nb_points <= 1:
            pass
        elif nb_points == 2:
            path.moveTo(cp[0])
            path.lineTo(cp[1])
        else:
            path.moveTo(cp[0])
            for i in range(1, nb_points - 1, 3):
                p1 = cp[i + 0]
                p2 = cp[i + 1]
                end = cp[i + 2]
                path.cubicTo(p1, p2, end)
            if self.__closed:
                path.lineTo(cp[0])

        self.setPath(path)


class TaurusGraphicsItem(TaurusBaseComponent):
    """Base class for all Taurus Graphics Items"""

    def __init__(self, name=None, parent=None):
        self.call__init__(TaurusBaseComponent, name, parent)  # <- log created here
        # self.debug('TaurusGraphicsItem(%s,%s)' % (name,parent))
        self.ignoreRepaint = False
        self.setName(name)
        self._currFgBrush = None
        self._currBgBrush = None
        self._currText = None
        self._currHtmlText = None
        self._map = None
        self._default = None
        self._visible = None
        # self.getExtensions() <= It must be called AFTER set_common_params()
        # in getGraphicsItem()
        self._contextMenu = []

    def setName(self, name):
        name = str(name or self.__class__.__name__)
        # srubio@cells.es: modified to store ._name since initialization (even
        # if a model is not set)
        self._name = name

    def getName(self):
        return self._name

    def setContextMenu(self, menu):
        """Context Menu must be a list of tuples (ActionName,ActionMethod),
        empty tuples insert separators between options.
        """
        self._contextMenu = menu

    def contextMenu(self):
        return self._contextMenu

    def getExtensions(self):
        """
        Any in
        ExtensionsList,noPrompt,standAlone,noTooltip,noSelect,ignoreRepaint,
        shellCommand,className,classParams
        """
        self._extensions = getattr(self, "_extensions", {})
        if "ExtensionsList" in self._extensions:
            self._extensions.update(
                (k.strip(), True) for k in self._extensions["ExtensionsList"].split(",")
            )
            self._extensions.pop("ExtensionsList")
        for k in (
            "noPrompt",
            "standAlone",
            "noTooltip",
            "ignoreRepaint",
            "noSelect",
        ):
            if self._extensions.get(k, None) == "":
                self._extensions[k] = True
        self.noPrompt = self._extensions.get("noPrompt", False)
        self.standAlone = self._extensions.get("standAlone", False)
        self.noTooltip = self._extensions.get("noTooltip", False)
        self.ignoreRepaint = self._extensions.get("ignoreRepaint", self.ignoreRepaint)
        self.setName(self._extensions.get("name", self._name))
        tooltip = (
            ""
            if (
                self.noTooltip
                or self._name == self.__class__.__name__
                or self._name is None
            )
            else str(self._name)
        )
        # self.debug('setting %s.tooltip = %s'%(self._name,tooltip))
        self.setToolTip(tooltip)
        # self.debug('%s.getExtensions(): %s'%(self._name,self._extensions))
        return self._extensions

    # -~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~
    # Mandatory methods to be implemented in any subclass of TaurusComponent
    # -~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~

    def setModel(self, model, **kwargs):
        # self.debug('In %s.setModel(%s)'%(type(self).__name__,model))
        self.setName(model)

        if issubclass(Manager().findObjectClass(self._name), TaurusDevice):
            model = self._name + "/state"
        TaurusBaseComponent.setModel(self, model, **kwargs)

    @deprecation_decorator(rel="5.1.0", alt="_getTaurusParentItem()")
    def getParentTaurusComponent(self):
        return self._getTaurusParentItem()

    def _getTaurusParentItem(self):
        """Returns a parent Taurus component or None if no parent
        TaurusBaseComponent is found.
        """
        p = self.parentItem()
        while p and not isinstance(p, TaurusGraphicsItem):
            p = self.parentItem()
        return p

    # def fireEvent(self, type):
    def fireEvent(self, evt_src=None, evt_type=None, evt_value=None):
        """fires a value changed event to all listeners"""
        self.updateStyle()

    def updateStyle(self):
        """Method called when the component detects an event that triggers
        a change in the style.
        """
        if self.scene():
            self.scene().updateSceneItem(self)

    def isReadOnly(self):
        return True

    def __str__(self):
        return self.log_name + "(" + self.modelName + ")"

    def getModelClass(self, **kwargs):
        return TaurusAttribute


class TaurusGraphicsAttributeItem(TaurusGraphicsItem):
    """
    This class show value->text conversion in label widgets.
    Quality is shown in background
    """

    def __init__(self, name=None, parent=None):
        name = name or self.__class__.__name__
        self._unitVisible = True
        self._currValue = None
        self._userFormat = None
        self._unitVisible = True
        self.call__init__(TaurusGraphicsItem, name, parent)

    @deprecation_decorator(
        alt=".getDisplayValue(fragmentName='rvalue.units')", rel="4.0.3"
    )
    def getUnit(self):
        return self.getDisplayValue(fragmentName="rvalue.units")

    def updateStyle(self):
        v = self.getModelValueObj()
        if self.getShowQuality():
            try:
                quality = None
                if v:
                    quality = v.quality
                if quality == AttrQuality.ATTR_VALID and self._validBackground:
                    background = self._validBackground
                else:
                    background, _ = QT_ATTRIBUTE_QUALITY_PALETTE.qcolor(quality)
                self.setBrush(Qt.QBrush(background))
            except Exception:
                self.warning(
                    "In TaurusGraphicsAttributeItem(%s)"
                    + ".updateStyle(%s): colors failed!",
                    self._name,
                    self._currText,
                )
                self.warning(traceback.format_exc())

        if v and self._userFormat:
            # TODO: consider extending to use newer pyhon formatting syntax
            if hasattr(v.rvalue, "magnitude"):
                text = self._userFormat % v.rvalue.magnitude
            else:
                text = self._userFormat % v.rvalue
            if self._unitVisible:
                text = "{0} {1.rvalue.units:~s}".format(text, v)
        else:
            if self._unitVisible:
                _frName = None
            else:
                _frName = "rvalue.magnitude"
            text = self.getDisplayValue(fragmentName=_frName)

        self._currText = text
        self._currHtmlText = None

        TaurusGraphicsItem.updateStyle(self)

    def setUserFormat(self, format):
        self._userFormat = format

    def setUnitVisible(self, yesno):
        self._unitVisible = yesno


class TaurusGraphicsStateItem(TaurusGraphicsItem):
    """
    In State Item the displayValue should not override the label
    This item will modify only foreground/background colors
    """

    def __init__(self, name=None, parent=None):
        name = name or self.__class__.__name__
        self.call__init__(TaurusGraphicsItem, name, parent)

    def updateStyle(self):
        from taurus.core.tango import DevState  # Tango-centric

        v = self.getModelValueObj()

        self._currBrush = Qt.QBrush(Qt.Qt.NoBrush)
        if v:  # or self.getShowState():
            try:
                bg_brush, fg_brush = None, None
                if self.getModelObj().getType() == DataType.DevState:
                    bg_brush, fg_brush = QT_DEVICE_STATE_PALETTE.qbrush(v.rvalue)
                elif self.getModelObj().getType() == DataType.Boolean:
                    bg_brush, fg_brush = QT_DEVICE_STATE_PALETTE.qbrush(
                        (DevState.FAULT, DevState.ON)[v.rvalue]
                    )
                elif self.getShowQuality():
                    bg_brush, fg_brush = QT_ATTRIBUTE_QUALITY_PALETTE.qbrush(v.quality)
                if None not in (bg_brush, fg_brush):
                    self._currBgBrush = bg_brush
                    self._currFgBrush = fg_brush
                    # If there's no filling, applying background brush to
                    # foreground
                    if Qt.Qt.NoBrush != getattr(self, "_fillStyle", Qt.Qt.NoBrush):
                        self._currFgBrush = bg_brush
                    if self._currText:
                        self._currHtmlText = '<p style="color:%s">%s</p>' % (
                            self._currBgBrush.color().name(),
                            self._currText,
                        )
            except Exception:
                self.warning(
                    "In TaurusGraphicsStateItem(%s)"
                    + ".updateStyle(%s): colors failed!",
                    self._name,
                    self._currText,
                )
                self.warning(traceback.format_exc())

        # Parsing _map to manage visibility (a list of values for which the
        # item is visible or not)
        if v and self._map is not None and self._currText in DevState.__members__:
            if DevState[self._currText] == self._map[1]:
                self.setVisible(self._map[2])
                self._visible = self._map[2]
            else:
                self.setVisible(self._default)
                self._visible = self._default

        TaurusGraphicsItem.updateStyle(self)


class TaurusEllipseStateItem(Qt.QGraphicsEllipseItem, TaurusGraphicsStateItem):
    def __init__(self, name=None, parent=None, scene=None):
        name = name or self.__class__.__name__
        Qt.QGraphicsEllipseItem.__init__(self, parent)
        if scene is not None:
            scene.addItem(self)
        self.call__init__(TaurusGraphicsStateItem, name, parent)

    def paint(self, painter, option, widget=None):
        if self._currBgBrush:
            self._currBgBrush.setStyle(self.brush().style())
            self.setBrush(self._currBgBrush)
        Qt.QGraphicsEllipseItem.paint(self, painter, option, widget)


class TaurusRectStateItem(Qt.QGraphicsRectItem, TaurusGraphicsStateItem):
    def __init__(self, name=None, parent=None, scene=None):
        name = name or self.__class__.__name__
        Qt.QGraphicsRectItem.__init__(self, parent)
        if scene is not None:
            scene.addItem(self)
        self.call__init__(TaurusGraphicsStateItem, name, parent)

    def paint(self, painter, option, widget):
        if self._currBgBrush:
            self._currBgBrush.setStyle(self.brush().style())
            self.setBrush(self._currBgBrush)
        Qt.QGraphicsRectItem.paint(self, painter, option, widget)


class TaurusSplineStateItem(QSpline, TaurusGraphicsStateItem):
    def __init__(self, name=None, parent=None, scene=None):
        name = name or self.__class__.__name__
        QSpline.__init__(self, parent)
        if scene is not None:
            scene.addItem(self)
        self.call__init__(TaurusGraphicsStateItem, name, parent)

    def paint(self, painter, option, widget):
        if self._currBgBrush:
            self._currBgBrush.setStyle(self.brush().style())
            self.setBrush(self._currBgBrush)
        QSpline.paint(self, painter, option, widget)


class TaurusRoundRectItem(Qt.QGraphicsPathItem):
    def __init__(self, name=None, parent=None, scene=None):
        Qt.QGraphicsPathItem.__init__(self, parent)
        if scene is not None:
            scene.addItem(self)
        self.__rect = None
        self.setCornerWidth(0, 0)

    def __updatePath(self):
        if self.__rect is None:
            return
        if self.__corner is None:
            return

        path = Qt.QPainterPath()
        cornerWidth, nbPoints = self.__corner
        if cornerWidth == 0 or nbPoints == 0:
            path.addRect(self.__rect)
        elif cornerWidth * 2 > self.__rect.width():
            path.addRect(self.__rect)
        elif cornerWidth * 2 > self.__rect.height():
            path.addRect(self.__rect)
        else:
            path.addRoundedRect(self.__rect, cornerWidth, cornerWidth)
        self.setPath(path)

    def setRect(self, x, y, width, height):
        self.__rect = Qt.QRectF(x, y, width, height)
        self.__updatePath()

    def setCornerWidth(self, width, nbPoints):
        self.__corner = width, nbPoints
        self.__updatePath()


class TaurusRoundRectStateItem(TaurusRoundRectItem, TaurusGraphicsStateItem):
    def __init__(self, name=None, parent=None, scene=None):
        name = name or self.__class__.__name__
        TaurusRoundRectItem.__init__(self, parent, scene)
        self.call__init__(TaurusGraphicsStateItem, name, parent)

    def paint(self, painter, option, widget):
        if self._currBgBrush:
            self._currBgBrush.setStyle(self.brush().style())
            self.setBrush(self._currBgBrush)
        TaurusRoundRectItem.paint(self, painter, option, widget)


class TaurusGroupItem(Qt.QGraphicsItemGroup):
    def __init__(self, name=None, parent=None, scene=None):
        Qt.QGraphicsItemGroup.__init__(self, parent)
        if scene is not None:
            scene.addItem(self)


class TaurusGroupStateItem(TaurusGroupItem, TaurusGraphicsStateItem):
    def __init__(self, name=None, parent=None, scene=None):
        name = name or self.__class__.__name__
        TaurusGroupItem.__init__(self, parent, scene)
        self.call__init__(TaurusGraphicsStateItem, name, parent)

    def paint(self, painter, option, widget):
        TaurusGroupItem.paint(self, painter, option, widget)


class TaurusPolygonStateItem(Qt.QGraphicsPolygonItem, TaurusGraphicsStateItem):
    def __init__(self, name=None, parent=None, scene=None):
        name = name or self.__class__.__name__
        # Qt.QGraphicsRectItem.__init__(self, parent)
        Qt.QGraphicsPolygonItem.__init__(self, parent)
        if scene is not None:
            scene.addItem(self)
        self.call__init__(TaurusGraphicsStateItem, name, parent)

    def paint(self, painter, option, widget):
        if self._currBgBrush:
            self._currBgBrush.setStyle(self.brush().style())
            self.setBrush(self._currBgBrush)
        Qt.QGraphicsPolygonItem.paint(self, painter, option, widget)


class TaurusLineStateItem(Qt.QGraphicsLineItem, TaurusGraphicsStateItem):
    def __init__(self, name=None, parent=None, scene=None):
        name = name or self.__class__.__name__
        Qt.QGraphicsLineItem.__init__(self, parent)
        if scene is not None:
            scene.addItem(self)
        self.call__init__(TaurusGraphicsStateItem, name, parent)

    def paint(self, painter, option, widget):
        if self._currBgBrush:
            self._currBgBrush.setStyle(self.brush().style())
            self.setBrush(self._currBgBrush)
        Qt.QGraphicsLineItem.paint(self, painter, option, widget)


class TaurusTextStateItem(QGraphicsTextBoxing, TaurusGraphicsStateItem):
    """
    A QGraphicsItem that represents a text related to a device state or
    attribute quality
    """

    def __init__(self, name=None, parent=None, scene=None):
        name = name or self.__class__.__name__
        QGraphicsTextBoxing.__init__(self, parent, scene)
        self.call__init__(TaurusGraphicsStateItem, name, parent)

    def paint(self, painter, option, widget):
        if self._currHtmlText:
            self.setHtml(self._currHtmlText)
        else:
            self.setPlainText(self._currText or "")
        QGraphicsTextBoxing.paint(self, painter, option, widget)


class TaurusTextAttributeItem(QGraphicsTextBoxing, TaurusGraphicsAttributeItem):
    """
    A QGraphicsItem that represents a text related to an attribute value
    """

    def __init__(self, name=None, parent=None, scene=None):
        name = name or self.__class__.__name__
        QGraphicsTextBoxing.__init__(self, parent, scene)
        self.call__init__(TaurusGraphicsAttributeItem, name, parent)

    def paint(self, painter, option, widget):
        if self._currHtmlText:
            self.setHtml(self._currHtmlText)
        else:
            self.setPlainText(self._currText or "")
        QGraphicsTextBoxing.paint(self, painter, option, widget)


TYPE_TO_GRAPHICS = {
    None: {
        "Rectangle": Qt.QGraphicsRectItem,
        "RoundRectangle": TaurusRoundRectItem,
        "Ellipse": Qt.QGraphicsEllipseItem,
        "Polyline": Qt.QGraphicsPolygonItem,
        "Label": QGraphicsTextBoxing,
        "Line": Qt.QGraphicsLineItem,
        "Group": TaurusGroupItem,
        "SwingObject": TaurusTextAttributeItem,
        "Image": Qt.QGraphicsPixmapItem,
        "Spline": QSpline,
    },
    TaurusDevice: {
        "Rectangle": TaurusRectStateItem,
        "RoundRectangle": TaurusRoundRectStateItem,
        "Ellipse": TaurusEllipseStateItem,
        "Polyline": TaurusPolygonStateItem,
        "Label": TaurusTextStateItem,
        "Line": Qt.QGraphicsLineItem,  # TaurusLineStateItem,
        "Group": TaurusGroupStateItem,
        "SwingObject": TaurusTextAttributeItem,
        "Image": Qt.QGraphicsPixmapItem,
        "Spline": TaurusSplineStateItem,
    },
    TaurusAttribute: {
        "Rectangle": TaurusRectStateItem,
        "RoundRectangle": TaurusRoundRectStateItem,
        "Ellipse": TaurusEllipseStateItem,
        "Polyline": TaurusPolygonStateItem,
        "Label": TaurusTextAttributeItem,
        "Line": Qt.QGraphicsLineItem,  # TaurusLineStateItem,
        "Group": TaurusGroupStateItem,
        "SwingObject": TaurusTextAttributeItem,
        "Image": Qt.QGraphicsPixmapItem,
        "Spline": TaurusSplineStateItem,
    },
}


class TaurusBaseGraphicsFactory(object):
    def __init__(self):
        pass

    def getSceneObj(self):
        raise RuntimeError("Invalid call to AbstractGraphicsFactory::getSceneObj()")

    def getObj(self, name, params):
        raise RuntimeError("Invalid call to AbstractGraphicsFactory::getObj()")

    def getRectangleObj(self, params):
        raise RuntimeError("Invalid call to AbstractGraphicsFactory::getRectangleObj()")

    def getRoundRectangleObj(self, params):
        raise RuntimeError(
            "Invalid call to AbstractGraphicsFactory::getRoundRectangleObj()"
        )

    def getLineObj(self, params):
        raise RuntimeError("Invalid call to AbstractGraphicsFactory::getLineObj()")

    def getEllipseObj(self, params):
        raise RuntimeError("Invalid call to AbstractGraphicsFactory::getEllipseObj()")

    def getPolylineObj(self, params):
        raise RuntimeError("Invalid call to AbstractGraphicsFactory::getPolylineObj()")

    def getLabelObj(self, params):
        raise RuntimeError("Invalid call to AbstractGraphicsFactory::getLabelObj()")

    def getGroupObj(self, params):
        raise RuntimeError("Invalid call to AbstractGraphicsFactory::getGroupObj()")

    def getSwingObjectObj(self, params):
        raise RuntimeError(
            "Invalid call to AbstractGraphicsFactory::getSwingObjectObj()"
        )

    def getImageObj(self, parms):
        raise RuntimeError("Invalid call to AbstractGraphicsFactory::getImageObj()")

    def getSplineObj(self, params):
        raise RuntimeError("Invalid call to AbstractGraphicsFactory::getSplineObj()")

    def getGraphicsClassItem(self, cls, type_):
        ncls = cls
        try:
            if issubclass(cls, TaurusDevice):
                ncls = TaurusDevice
            elif issubclass(cls, TaurusAttribute):
                ncls = TaurusAttribute
        except Exception:
            pass
        ncls = TYPE_TO_GRAPHICS.get(ncls, TYPE_TO_GRAPHICS.get(None)).get(type_)
        return ncls

    def getGraphicsItem(self, type_, params):
        name = params.get(self.getNameParam())
        # applying alias
        for k, v in getattr(self, "alias", {}).items():
            if k in name:
                name = str(name).replace(k, v)
                params[self.getNameParam()] = name
        cls = None
        # TODO: starting slashes are allowed while we support parent model
        #       feature (taurus-org/taurus#734)
        if not name.startswith("/") and "/" in name:
            try:
                from taurus.core.tango.tangovalidator import (
                    TangoAttributeNameValidator,
                    TangoDeviceNameValidator,
                )
            except ImportError:
                pass
            else:
                if TangoDeviceNameValidator().isValid(
                    name
                ) or TangoAttributeNameValidator().isValid(name):
                    # replacing Taco identifiers in %s'%name
                    if name.lower().startswith("tango:"):
                        if name.count("/") == 2 or "tango:/" not in name.lower():  # noqa
                            nname = name.split(":", 1)[-1]
                            params[self.getNameParam()] = name = nname
                    else:
                        from taurus import warning

                        warning(
                            "if you use a tango name as JD name it must with tango:"
                        )
                    if name.lower().endswith("/state"):
                        name = name.rsplit("/", 1)[0]
                    cls = Manager().findObjectClass(name)
        else:
            if name:
                self.debug("%s does not match a tango name" % name)
        klass = self.getGraphicsClassItem(cls, type_)
        item = klass()
        # It's here were Attributes are subscribed
        self.set_common_params(item, params)
        if hasattr(item, "getExtensions"):
            item.getExtensions()  # called to get extensions from params
        return item

    def getNameParam(self):
        """Returns the name of the parameter which contains the name
        identifier.
        Default implementation returns 'name'.
        """
        return "name"

    def set_common_params(self, item, params):
        """Sets the common parameters. Default implementation does nothing.
        Overwrite has necessary.
        """
        pass
