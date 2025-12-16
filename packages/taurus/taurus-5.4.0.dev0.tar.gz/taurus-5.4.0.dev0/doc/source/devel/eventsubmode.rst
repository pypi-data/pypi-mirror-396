===============================================================================
Tango event subscription modes
===============================================================================

This work is part of `Taurus Performance Optimization`_ (TPO) project. It adapts
taurus to the new event subscription modes that Tango introduces from 10.1.0.
The two pillars here are:

1. Selecting the **event subscription mode** (``EventSubMode``).
2. A lightweight **first read** to initialize attribute values when needed.

For background on Tango events and PyTango API see the official docs:
`Tango Events`_ and `PyTango DeviceProxy API`_. PyTango exposes the
``EventSubMode`` enum and adds ``EventReason`` in the ``EventData``
structure (see documentation in `PyTango client API`_). 

.. _Taurus Performance Optimization: http://www.taurus-scada.org/tep/?TEP21.md
.. _Tango Events: https://tango-controls.readthedocs.io/en/latest/Explanation/event.html
.. _PyTango DeviceProxy API: https://tango-controls.readthedocs.io/projects/pytango/en/latest/api/client_api/device_proxy.html
.. _PyTango client API: https://tango-controls.readthedocs.io/projects/pytango/en/latest/api/client_api/miscellaneous.html

EventSubMode in Taurus
----------------------

Taurus supports all event subscription modes that Tango >= 10.1.0 provides.
Taurus functionality should not change between modes but depending on the
nature of the attributes and devices, the performance when starting applications
may be affected. 

When available, Taurus uses ``AsyncRead`` as default ``EventSubMode``. Typically, 
the mode should not be changed as ``AsyncRead`` resulted the best compromise between
compatibility, simplicity and performance but Taurus offers the possibility to
change modes via via :ref:`Taurus custom settings <EventModesCustomSettings>`  or 
:ref:`Command-Line Interface <EventModesCLI>`.

If you experience problems when starting applications, specially with values
initialization, the mode can be changed to ``SyncRead`` to recover the previous
Taurus (< 5.4) default behaviour.

The following table (adapted from `PyTango EventSubMode`_) summarizes the available event 
subscription modes:

+-------------+-------------------------------------+--------------------------------+----------------------------+---------------------------+-----------------------------------------+
| EventSubMode| Tries subscription before returning | Raises on subscription failure | Retries automatically      | Reads entity              | First callback                          |
+=============+=====================================+================================+============================+===========================+=========================================+
| SyncRead    | Yes                                 | Yes                            | No                         | Yes, during subscription  | Immediately, with data                  |
+-------------+-------------------------------------+--------------------------------+----------------------------+---------------------------+-----------------------------------------+
| AsyncRead   | No                                  | No                             | Yes                        | Yes, after subscription   | After read, with data                   |
+-------------+-------------------------------------+--------------------------------+----------------------------+---------------------------+-----------------------------------------+
| Sync        | Yes                                 | Yes                            | No                         | No                        | Not on subscription. Only on next event |
+-------------+-------------------------------------+--------------------------------+----------------------------+---------------------------+-----------------------------------------+
| Async       | No                                  | No                             | Yes                        | No                        | After subscription, no data             |
+-------------+-------------------------------------+--------------------------------+----------------------------+---------------------------+-----------------------------------------+
| Stateless   | Yes                                 | No                             | Yes                        | Yes, during subscription  | Immediately, with data                  |
+-------------+-------------------------------------+--------------------------------+----------------------------+---------------------------+-----------------------------------------+

.. _PyTango EventSubMode: https://tango-controls.readthedocs.io/projects/pytango/en/latest/api/client_api/miscellaneous.html#tango.EventSubMode

First Read (client-side initialization)
---------------------------------------

Taurus now provides a one-shot read used when the chosen mode does not
perform an initial read by itself (``Sync`` and ``Async``). This first read
is performed asynchronously in a dedicated thread that finishes when 
all attributes have been initialized.

This feature ensures that the attribute has a value cached right after
subscription setup, delegating to Taurus the responsibility for providing
the initial attribute value.

API involved in Taurus:

- Factory helper to register a first-time read for a given attribute.
- Attribute-side helper that delegates to the factory during initialization.
 
 
.. _EventModesCustomSettings:

Changing the default mode via Custom Settings
---------------------------------------------

You can set the **default EventSubMode** machine-wide using **Taurus Custom Settings**.
See the official page: `Taurus custom settings`_.

.. _Taurus custom settings: https://taurus-scada.org/devel/tauruscustomsettings.html

.. _EventModesCLI:

Command-Line Interface (CLI)
----------------------------

Taurus provides two CLI switches to control Tango event subscriptions at launch:

- ``--disable-tango-event-subscription``
  Disables Tango change-event subscriptions and forces polling.

- ``--tango-event-sub-mode {Sync,SyncRead,Async,AsyncRead}``
  Selects the subscription mode for change events for this run.

Precedence:

1. If events are disabled via CLI, polling is used regardless of of the selected mode.
2. Otherwise, the mode is taken from CLI; if not set, from custom settings;
   otherwise Taurus uses the project default (``AsyncRead`` in this branch).

