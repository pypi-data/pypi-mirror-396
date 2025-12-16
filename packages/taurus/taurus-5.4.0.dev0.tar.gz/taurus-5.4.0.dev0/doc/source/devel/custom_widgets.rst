.. _custom-widgets:

==================
Custom Widgets
==================

There are several approaches to developing and customizing a GUI with Taurus.
The easiest approach (which may not even require programming in python) is
to :ref:`create a Taurus GUI using the TaurusGUI framework<taurusgui_newgui>` ,
populating it with panels created from existing Taurus or 3rd party widgets and
attaching models to provide functionality. This is the most common (and
recommended) approach, considering that many Taurus widgets can be further
configured from the GUI itself and these configurations can be automatically
restored, allowing for a level of customization that is sufficient for many
applications.

Sometimes however, one may need to customize the widgets at a lower level
(e.g., for accessing properties that are not accessible via the GUI, or for
grouping several existing widgets together, etc). This can be done by using the
Taurus widgets just as one would use any other Qt widget (either using the
:ref:`Qt Designer<taurusqtdesigner-tutorial>` or in a purely programmatic way).

Finally, in some cases neither Taurus nor other third party modules provide the
required functionality, and a new widget needs to be created. If such widget
requires to interact with a control system or other data sources supported via
:ref:`Taurus model objects<taurus-core-tutorial>`, the recommended approach is
to create a widget that inherits both from a :class:`QWidget` (or a
`QWidget`-derived class) and from the
:class:`taurus.qt.qtgui.base.TaurusBaseComponent` mixin class (or one of its
derived mixin classes from :mod:`taurus.qt.qtgui.base`). These Taurus mixin
classes provide several APIs that are expected from Taurus widgets, such as:

- model support API
- configuration API
- logger API
- formatter API

For this reason, this is sometimes informally called "*Taurus-ifying* a pure Qt
class". The following is a simple example of creating a Taurus "power-meter"
widget that displays the value of its attached attribute model as a bar (like
e.g. in an equalizer). For this we are going to compose a :class:`QProgressBar`
with a :class:`taurus.qt.qtgui.base.TaurusBaseComponent` mixin class:

.. literalinclude:: ./examples/powermeter.py
   :language: python
   :linenos:
   :emphasize-lines: 6, 10-11, 19-24

As you can see, the mixin class provides all the taurus fucntionality
regarding setting and subscribing to models, and all one needs to do is to
implement the ``handleEvent`` method that will be called whenever the attached
taurus model is updated.

.. note:: if you create a generic enough widget which could be useful for other
    people, consider contributing it to Taurus, either to be included directly
    in the official taurus module or to be distributed as a :ref:`Taurus
    plugin<plugins>`.

.. tip:: we recommend to try to use the highest level approach compatible
    with your requirements, and limit the customization to the smallest
    possible portion of code. For example: consider that you need a GUI that
    includes a "virtual gamepad" widget to control a robot arm. Since such
    "gamepad" is not provided by Taurus, we recommend that you implement *only*
    the "gamepad" widget (maybe using the Designer to put together several
    :class:`QPushButtons` within a :class:`TaurusWidget`) in a custom module
    and then use that widget within a panel in a TaurusGUI (as opposed to
    implementing the whole GUI with the Designer). In this way you improve the
    re-usability of your widget *and* you profit from the built-in mechanisms
    of the Taurus GUIs such as handling of perspectives, saving-restoring of
    settings, etc


.. _multi-model:

Multi-model support: model-composer
-----------------------------------

Before Taurus TEP20_ (implemented in Taurus 5.1)
:class:`taurus.qt.qtgui.base.TaurusBaseComponent` and its derived classes only
provided support for a single model to be associated with the QWidget /
QObject. Because of this, many taurus widgets that required to be attached to
more than one model had to implement the multi-model support in their own
specific (and sometimes inconsistent) ways.

With the introduction of TEP20_, the taurus base classes support multiple
models. As an example, consider the following modification of the above
"PowerMeter" class adding support for a second model consisting on an attribute
that provides a color name that controls the background color of the bar:

.. literalinclude:: ./examples/powermeter2.py
   :language: python
   :linenos:
   :emphasize-lines: 13-14,25,27-28,39

The relevant differences of the PowerMeter2 class with respect to the previous
single-model version have been highlighted in the above code snippet:
essentially one just needs to define the supported model keys in the
``.modelKeys`` class method and then handle the different possible sources of
the events received in ``handleEvent``. Note that the first key in
``modelKeys`` is to be used as the default when not explicitly passed to the
model API methods.

The multi-model API also facilitates the implementation of widgets that operate
on lists of models, by using the special constant ``MLIST`` defined in
:mod:`taurus.qt.qtgui.base` and also accessible as
``TaurusBaseComponent.MLIST``. For example the following code implements a very
simple widget that logs events received from an arbitrary list of attributes:

.. literalinclude:: ./examples/eventlogger.py
   :language: python
   :linenos:

The multi-model API treats the ``MLIST`` in a special way: when calling
``setModel`` with ``key=MLIST``, the ``model`` argument is expected to be a
*sequence* of model names; new model keys are automatically added to the
widget's ``modelList`` attribute and the corresponding models are attached
using those keys. The new keys are of the form ``(MLIST, i)`` where ``i`` is
the index of the corresponding model name in the model sequence. The new models
can be accessed individually with the standard multi-model API using the
generated model keys.

Another typical pattern that can be implemented with the ``MLIST`` support is
the model delegates container, where the widget does not handle the events by
itself but instead it dynamically creates other taurus subwidgets (e.g. when
the model is set) and then delegates the handling of events to those subwidgets
(similar to what :class:`taurus.qt.qtgui.panel.TaurusForm` does). The following
example shows a simplistic implementation of a form widget that shows the model
name and its value for each model attached to it:

.. literalinclude:: ./examples/simpleform.py
   :language: python
   :linenos:

Note that, contrary to previous examples, this form does not re-implement 
the ``handleEvent`` method (i.e. it ignores the events from its models) but 
instead it calls ``setModel`` on its subwidgets, letting them handle their 
respective models' events.


.. _TEP20: http://taurus-scada.org/tep/?TEP20.md
