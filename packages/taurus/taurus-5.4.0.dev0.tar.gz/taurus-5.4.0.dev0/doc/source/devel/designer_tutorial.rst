.. _taurusqtdesigner-tutorial:

============================
Taurus Qt Designer tutorial
============================

Taurus widgets behave just as any other Qt widget, and as such, they can be used
to create GUIs in a regular way, both programmatically or using the Qt designer.
For convenience, Taurus provides the `taurus designer` command that launches the
standard Qt designer application extended to show also the widgets provided by
Taurus.

To launch it, just execute::

  taurus designer

.. tip::

  ``--help`` argument will give you the complete list of options


.. figure:: /_static/designer01.png
  :scale: 75

You can then design your application/widget using not only the standard Qt
widgets but also the taurus widgets.

You can use the Taurus Qt Designer to define a full GUI, but instead
we recommend to create the GUIs using the
:ref:`TaurusGUI framework <taurusgui_newgui>` and use the
Taurus Qt Designer just for creating widgets to be inserted as panels in a
:class:`taurus.qt.qtgui.taurusgui.TaurusGui`-based GUI.



Using the .ui file
-------------------

The Qt designer will produce a .ui file that is an XML representation of the
application/widget that you designed.

This .ui file can then be used in your own widget by using the
:func:`taurus.qt.qtgui.util.UILoadable` decorator.

See `TEP11 <http://sf.net/p/sardana/wiki/SEP11/>`_ for more details.


Known issues
------------

.. _designer_pyqt515_issue:

Missing Taurus Widgets in Qt Designer with Conda and PyQt5 >= 5.15.4
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
When launching ``taurus designer``, custom Taurus widgets do not appear
in Qt Designer on Conda environments with PyQt5 version 5.15.4 or higher.
This issue occurs because the conda-forge build is missing the
``libpyqt5.so`` library (see
`this issue <https://github.com/conda-forge/pyqt-feedstock/issues/113>`_),
causing external plugin loading to fail.

While not ideal, there are a couple of workarounds to continue using Taurus
Designer in a Linux Conda installation:

Option 1
  Use a dedicated Conda environment with PyQt5 version 5.12 specifically for
  running the designer. Due to that ``guiqwt`` library version installed
  will be 3.0.7 and to maintain API compatibility you have to downgrade
  ``guidata`` library from 3.1.0 to 2.3.1.

Option 2
  Copy the missing ``libpyqt5.so`` file to the appropriate folder in the Conda
  environment with PyQt5 version>=5.15.4, which lacks the file. The destination
  folder is: ``/path/to/conda/envs/<env_name>/plugins/designer/``.

  The ``libpyqt5.so`` can be obtained from:

  - Another Conda environment with PyQt5 version 5.12. The file can be found in
    the same folder, and the environment can be removed afterward.

  - A system installation of PyQt5, typically located at:
    ``/usr/lib/x86_64-linux-gnu/qt5/plugins/designer/``.

  In both cases, ensure the Python version in the source environment matches
  the one in the destination Conda environment.
