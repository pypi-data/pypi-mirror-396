
.. _getting_started:

===============
Getting started
===============

.. _installing:

Installing
----------

Installing with pip (platform-independent)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Taurus can be installed using pip. The following command will automatically
download and install the latest release of Taurus (see pip --help for options)::

       pip install taurus

You can test the installation by running::

       python -c "import taurus; print(taurus.Release.version)"


Note: some "extra" features of taurus have additional dependencies_.


Linux (Debian-based)
~~~~~~~~~~~~~~~~~~~~

Taurus is part of the official repositories of Debian (and Ubuntu
and other Debian-based distros). You can install it and all its dependencies by
doing (as root)::

       apt-get install python-taurus

Note: `python3-taurus` and `python3-taurus-pyqtgraph` packages are already
built in https://salsa.debian.org , but are not yet part of the official debian
repositories


Installing in a conda environment (platform-independent)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In a conda environment (we recommend creating one specifically for taurus)::

    conda install -c conda-forge taurus taurus_pyqtgraph

optionally, you may also want to install tango::

    conda install -c conda-forge pytango

Note: for windows, until pytango is available on conda-forge, you may need to use 
`pip install pytango` for installing it.

.. warning::

   There is a known issue with PyQt5 versions >= 5.15.4 where Taurus Designer is
   not showing Taurus widgets. See :ref:`Designer known issues<designer_pyqt515_issue>` 
   for possible workarounds.


Working from Git source directly (in develop mode)
--------------------------------------------------

If you intend to do changes to Taurus itself, or want to try the latest
developments, it is convenient to work directly from the git source in
"develop" (aka "editable") mode, so that you do not need to re-install
on each change::

    # optional: if using a conda environment, pre-install dependencies:
    # e.g, for basic dependencies:
    conda install -c conda-forge python=3 click numpy pint pyqt ply lxml guiqwt pyqtgraph
    # ... and some extra dependencies (pick the ones you need)
    conda install -c conda-forge pytango pyepics spyder pymca
    # ... and if you want to run the test suite:
    conda install -c conda-forge pytest pytest-qt pytest-xvfb pytest-forked pytest-xdist flaky
    # ... and for auto-checking code style for contributing:
    conda install -c conda-forge pre-commit
    # ... and for building the docs:
    conda install -c conda-forge sphinx sphinx_rtd_theme graphviz

    # install taurus in develop mode
    git clone https://gitlab.com/taurus-org/taurus.git
    pip install -e ./taurus  # <-- Note the -e !!

    # install taurus_pyqtgraph in develop mode
    git clone https://gitlab.com/taurus-org/taurus_pyqtgraph.git
    pip install -e ./taurus_pyqtgraph  # <-- Note the -e !!


.. _dependencies:

Dependencies
------------

Strictly speaking, Taurus only depends on numpy_, click_, and pint_
but that will leave out most of the features normally
expected of Taurus (which are considered "extras"). For example:

- Interacting with a Tango controls system requires PyTango_.

- Interacting with an Epics controls system requires pyepics_.

- Using the taurus Qt_ widgets, requires either PyQt_ (v5)
  or PySide_ (v2). Note that most development and testing
  is done with PyQt5, so many features may not be
  regularly tested with PySide2.

- The image widgets require the guiqwt_ library.

- The JDraw synoptics widgets require the PLY_ package.

- The NeXus browser widget requires PyMca5_.

- The TaurusEditor widget requires spyder_.

- The TaurusGui module requires lxml_.


For a complete list of "extra" features and their corresponding
requirements, execute the following command::

    taurus check-deps


How you install the required dependencies depends on your preferred
installation method:

- For GNU/Linux, it is in general better to install the dependencies from
  your distribution repositories if available. A Conda_ environment can be
  used alternatively (interesting for testing new features in isolation)

- For Windows users, the recommended option is to use a Conda_ environment
  (see above).

- The `taurus-test Docker container`_ provides a Docker container (based
  on Debian) with all the dependencies pre-installed (including Tango and
  Epics running environments) on which you can install taurus straight
  away.


.. _numpy: http://numpy.org/
.. _pint: http://pint.readthedocs.org/
.. _PLY: http://www.dabeaz.com/ply/
.. _Tango: http://www.tango-controls.org/
.. _PyTango: http://pytango.readthedocs.io
.. _Qt: http://qt.nokia.com/products/
.. _PyQt: http://www.riverbankcomputing.co.uk/software/pyqt/
.. _PySide: https://wiki.qt.io/Qt_for_Python
.. _PyQwt: http://pyqwt.sourceforge.net/
.. _taurus_pyqtgraph: https://gitlab.com/taurus-org/taurus_pyqtgraph
.. _guiqwt: https://pypi.org/project/guiqwt/
.. _IPython: http://ipython.org
.. _PyMca5: http://pymca.sourceforge.net/
.. _pyepics: https://pypi.org/project/pyepics/
.. _spyder: http://pythonhosted.org/spyder
.. _lxml: http://lxml.de
.. _Conda: http://conda.io/docs/
.. _click: https://pypi.org/project/click/
.. _taurus-test Docker container: http://hub.docker.com/r/cpascual/taurus-test/
