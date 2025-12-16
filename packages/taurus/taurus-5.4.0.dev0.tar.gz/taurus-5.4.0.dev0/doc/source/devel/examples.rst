
.. highlight:: python
   :linenothreshold: 6

.. currentmodule:: taurus.qt.qtgui

.. _examples:

========
Examples
========

Here you will find a set of example figures with the code that generated them.

In order for the examples to work on your computer, you need to have a 
Tango device server running. The following section explains how to do this.

.. _examples_setup:

Setup
-----

The device server used for the examples can be obtained :download:`here <examples/TaurusTest.py>`.

In order for the examples to work as they are provided a TaurusTest device must be
created and running with the following configuration:

``Server (ServerName/Instance):``
  TaurusTest/taurustest
``Class:``
  TaurusTest
``Devices:``
  sys/taurustest/1

You can easily configure it from Jive by going to Edit->Create server and type
the above parameters in the dialog that pops up.

.. _examples_common:

Common
------

For the sake of simplicity the code presented below (except for the first example)
does not include the following header and footer code lines:

header::

    import sys
    from taurus.external.qt import Qt
    from taurus.qt.qtgui.application import TaurusApplication
    
    app = TaurusApplication(sys.argv, cmd_line_parser=None)
    panel = Qt.QWidget()
    layout = Qt.QHBoxLayout()
    panel.setLayout(layout)

footer::

    panel.show()
    sys.exit(app.exec_())

**You must prepend and append the above code in order for the examples to 
work properly.**

.. _examples_display_attribute_value:

Display attribute value
-----------------------

Displaying a tango attribute value in a GUI is easy with taurus and 
:class:`display.TaurusLabel`

.. image:: /_static/label01.png
  :align: center

code::

    import sys
    from taurus.external.qt import Qt
    from taurus.qt.qtgui.application import TaurusApplication

    app = TaurusApplication(sys.argv, cmd_line_parser=None,)
    panel = Qt.QWidget()
    layout = Qt.QHBoxLayout()
    panel.setLayout(layout)

    from taurus.qt.qtgui.display import TaurusLabel
    w = TaurusLabel()
    layout.addWidget(w)
    w.model = 'sys/taurustest/1/position#rvalue.magnitude'

    panel.show()
    sys.exit(app.exec_())
    
*not much code to write, but... boring!*

Note: If the `#rvalue.magnitude` fragment is not specified in the
model (e.g., `sys/taurustest/1/position`), the units (if defined)
will also be displayed in the label widget.

Display attribute value with label
----------------------------------

Let's spice it up a bit: add the tango label for the position attribute so
it looks something like this:

.. image:: /_static/label02.png
  :align: center

code::

    from taurus.qt.qtgui.display import TaurusLabel
    w1, w2 = TaurusLabel(), TaurusLabel()
    layout.addWidget(w1)
    layout.addWidget(w2)
    w1.model, w1.bgRole = 'sys/taurustest/1/position#label', ''
    w2.model = 'sys/taurustest/1/position#rvalue.magnitude'
    
*Much better indeed!*

Display attribute value with label and separate units
-----------------------------------------------------

And little bit more... add the units.

.. image:: /_static/label03.png
  :align: center

code::
    
    from taurus.qt.qtgui.container import TaurusWidget
    from taurus.qt.qtgui.display import TaurusLabel

    w1, w2, w3 = TaurusLabel(), TaurusLabel(), TaurusLabel()
    layout.addWidget(w1)
    layout.addWidget(w2)
    layout.addWidget(w3)
    w1.model, w1.bgRole = 'sys/taurustest/1/position#label', ''
    w2.model = 'sys/taurustest/1/position#rvalue.magnitude'
    w3.model, w3.bgRole = 'sys/taurustest/1/position#rvalue.units', ''

*Nice isn't it?*

Interactively display attribute
-------------------------------

Humm... Now suppose the user wants to change this value. :class:`input.TaurusValueLineEdit`
does this job well (and so does :class:`input.TaurusValueSpinBox` and 
:class:`input.TaurusWheelEdit` |smile| )

.. |smile| unicode:: U+1F603 .. smiling face with open mouth

.. figure:: /_static/edit01.png
  :align: center
  
  With TaurusValueLineEdit

.. figure:: /_static/edit02.png
  :align: center

  With TaurusValueSpinBox

.. figure:: /_static/edit03.png
  :align: center
  
  With TaurusWheelEdit
  
code::

    from taurus.qt.qtgui.display import TaurusLabel
    from taurus.qt.qtgui.input import TaurusValueLineEdit, TaurusValueSpinBox, TaurusWheelEdit

    w1 = TaurusLabel()
    w2 = TaurusLabel()
    w3 = TaurusValueLineEdit() # or TaurusValueSpinBox or TaurusWheelEdit
    w4 = TaurusLabel()
    layout.addWidget(w1)
    layout.addWidget(w2)
    layout.addWidget(w3)
    layout.addWidget(w4)
    w1.model, w1.bgRole = 'sys/taurustest/1/position#label', ''
    w2.model = 'sys/taurustest/1/position#rvalue.magnitude'
    w3.model = 'sys/taurustest/1/position#wvalue.magnitude'
    w4.model, w4.bgRole = 'sys/taurustest/1/position#rvalue.units', ''
    
*Now it seems a little bit more useful, doesn't it?*

A higher level of abstraction: forms
------------------------------------

Now let's say you want to display not only one but a dozen attributes... the
programming becomes quite tedious. Taurus provides a higher level of
abstraction: the :class:`panel.TaurusForm`.

.. image:: /_static/forms01.png
  :align: center

code::

    from taurus.qt.qtgui.panel import TaurusForm

    panel = TaurusForm()
    props = [ 'state', 'status', 'position', 'velocity', 'acceleration' ]
    model = [ 'sys/taurustest/1/%s' % p for p in props ]
    panel.setModel(model)

...and don't worry: :class:`panel.TaurusForm` properly aligns the labels,
manages the apply buttons and most important, it automagically decides which are the most appropriate
widgets to use depending on the kind of attribute (you do not need to worry
about whether the attribute is a scalar or a spectrum; or if it is read-only or
writable; a boolean or a float, etc).

*I specially enjoyed this one... let's see what's next!*

Customizing forms
-----------------

TaurusForm is highly customizable. This example shows how you can change the 
default widget for some attributes according to the user needs.

.. image:: /_static/forms02.png
  :align: center

code::
    
    from taurus.qt.qtgui.panel import TaurusForm
    from taurus.qt.qtgui.display import TaurusLabel

    panel = TaurusForm()
    props = [ 'state', 'status', 'position', 'velocity', 'acceleration' ]
    model = [ 'sys/taurustest/1/%s' % p for p in props ]
    panel.setModel(model)
    panel[0].readWidgetClass = TaurusLabel         # you can provide an arbitrary class...
    panel[2].writeWidgetClass = 'TaurusWheelEdit'  # ...or, if it is a Taurus class you can just give its name                                                   

*A little configuration goes a long way!*

You can also change style properties like font size, borders, colors...

code::

    from taurus.qt.qtgui.panel import TaurusForm

    panel = TaurusForm()
    props = [ 'state', 'status', 'position', 'velocity', 'acceleration' ]
    model = [ 'sys/taurustest/1/%s' % p for p in props ]
    panel.setModel(model)
    panel.setStyleSheet("font-size: 40px;")


The recommended way to change the style is using the *setStyleSheet* method on the TaurusForm (or any other widget).
However, if you want to apply a style on a specific widget inside a TaurusValue, you need to use Qt methods as Taurus
overrides some of the subwidget styles.

code::

    from taurus.qt.qtgui.panel import TaurusForm

    panel = TaurusForm()
    props = [ 'state', 'status', 'position', 'velocity', 'acceleration' ]
    model = [ 'sys/taurustest/1/%s' % p for p in props ]
    panel.setModel(model)
    for row in w:
      row.readWidget().setFont(Qt.QFont("Sans Serif",40))

Synoptics one-o-one
-------------------

.. todo::

    put a jdraw synoptics here

.. _examples_taurusplot:

Let's go graphical
------------------

The plot widgets are provided by the taurus_pyqtgraph_ plugin.


Simple plotting of various spectrum attributes
""""""""""""""""""""""""""""""""""""""""""""""

Say you want to plot two 1D attributes and watch them changing on-line?
The taurus_pyqtgraph_ plugin provides a very complete
widget: :class:`taurus_pyqtgraph.TaurusPlot`

code::

    from taurus_pyqtgraph import TaurusPlot
    
    panel = TaurusPlot()
    model = ['sys/taurustest/1/abscissas', 'sys/taurustest/1/curve']
    panel.setModel(model)

Scatter plots (Y vs X plots)
""""""""""""""""""""""""""""

In the former example each element of the spectrum attributes, was assigned its
position index as the x-value (i.e., the "abscissas" attribute was plotted as a
spectrum). But, what if you want to create a scatter plot where you want to read
the x-values from one attribute and the y-values from another? Then set the
attributes in a tuple, where the first element is the x-values and the second one
the y-values.


code::

    from taurus_pyqtgraph import TaurusPlot
    
    panel = TaurusPlot()
    model = [('sys/taurustest/1/abscissas', 'sys/taurustest/1/curve')]
    panel.setModel(model)
    
Note that now the `sys/taurustest/1/abscissas` attribute is being used as 
x-values instead of being considered as another spectrum to plot like before.

Plotting data that is not an attribute
""""""""""""""""""""""""""""""""""""""

A :class:`taurus_pyqtgraph.TaurusPlot` widget is a :class:`pyqtgraph.PlotWidget`

You may use the standard API from PyQtGraph_ for plotting other data:

code::

    from taurus_pyqtgraph import TaurusPlot
    import pyqtgraph as pg
    import numpy

    panel = TaurusPlot()
    model = [('sys/taurustest/1/abscissas,sys/taurustest/1/curve')]
    panel.setModel(model)

    c1 = pg.PlotDataItem(name="pg item", pen="b", fillLevel=0, brush="c")
    c1.setData(numpy.linspace(0, 2, 250))
    panel.addItem(c1)

.. _examples_taurustrend:

Plotting Trends
"""""""""""""""

Many times we are interested in showing how a scalar attribute evolves with
time. A close-cousin of the TaurusPlot called
:class:`taurus_pyqtgraph.TaurusTrend` is here to help you:

code::

    from taurus.qt.qtgui.plot import TaurusTrend
    
    panel = TaurusTrend()
    model = ['sys/taurustest/1/position']
    panel.setModel(model)
    
Note: if you pass a model that is a 1D attribute (instead of a
scalar), TaurusTrend will interpret it as a collection of scalar values and will
plot a separate trend line for each.

.. _taurus_pyqtgraph: http://gitlab.com/taurus-org/taurus_pyqtgraph
.. _PyQtGraph: http://pyqtgraph.org/


Even higher level: creating a TaurusGui 
---------------------------------------

:class:`taurusgui.TaurusGui` provides very convenient way of creating 
feature-rich and very configurable GUIs by using existing widgets as "panels".
TaurusGuis can be created via a wizard application (no programming at all!) with
a few clicks. You can try it out by running::

	taurus newgui
	
For more details and tricks regarding TaurusGui, check :ref:`this <taurusgui_newgui>`.

