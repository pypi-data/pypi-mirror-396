.. _plotting-guide:

=====================
Taurus plotting guide
=====================

*TL;DR*: Use taurus_pyqtgraph_

In taurus, the following dependencies are used for its various plotting widgets:

- guiqwt_: for `TaurusImageDialog` and `TaurusTrend2DDialog` implemented in :mod:`taurus.qt.qtgui.extra_guiqwt`.
  It does not depend at all of PyQwt5, and supports py3 and Qt5 so replacing it is not urgent
  (but still it should be eventually replaced by pyqtgraph-based widgets)
- pyqtgraph_: for `TaurusPlot` and `TaurusTrend` implementions provided by the
  taurus_pyqtgraph_ plugin. It supports py3 and Qt5 and is the replacement for all taurus plotting
  widgets (TEP17_).

Note:  v<5 provided PyQwt5-based implementations of `TaurusPlot` and
`TaurusTrend`, **but they are no longer included since they only work with py2**


Tips for Getting started with taurus_pyqtgraph_
------------------------------------------------

1. install the plugin (the module will be installed as :mod:`taurus_pyqtgraph` **and** at the same time will be available as
   :mod:`taurus.qt.qtgui.tpg`)
2. The philosophy is that you should use `tpg` as an extension to regular pyqtgraph_ widgets. Therefore you should read
   `the official pyqtgraph docs <http://www.pyqtgraph.org/documentation>`_ , and also run the official demo with
   `python -m pyqtgraph.examples`
3. :mod:`taurus_pyqtgraph` also has `some examples <https://gitlab.com/taurus-org/taurus_pyqtgraph/-/tree/main/taurus_pyqtgraph/examples>`_.
   Have a look at them. Also have a look at the `__main__` sections of the files in the :mod:`taurus_pyqtgraph` module
4. See `this tutorial <https://github.com/sardana-org/sardana-followup/blob/master/20180605-Prague/08-taurus_pyqtgraph/08-taurus_pyqtgraph.md>`_.



.. _guiqwt: https://pythonhosted.org/guiqwt/
.. _pyqtgraph: http://www.pyqtgraph.org/
.. _taurus_pyqtgraph: https://gitlab.com/taurus-org/taurus_pyqtgraph
.. _taurus_tangoarchiving: https://gitlab.com/taurus-org/tangoarchiving-scheme
.. _TEP17: http://www.taurus-scada.org/tep/?TEP17.md
