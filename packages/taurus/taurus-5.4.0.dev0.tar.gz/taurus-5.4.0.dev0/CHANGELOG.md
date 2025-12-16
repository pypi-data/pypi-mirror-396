# Change Log
All notable changes to this project will be documented in this file.

This project uses [PEP440] versioning where released versions start with 3 dot
separated numbers (`MAJOR.MINOR.PATCH`), which should be interpreted as
their homonym components in [Semantic Versioning].

This file follows the formats and conventions from [keepachangelog.com]

Note: changes in the [support-3.x] branch (which was split from
the master branch after [3.7.1] and maintained in parallel to the
develop branch) won't be reflected in this file.

## Unreleased

### Added
- Support for Tango `EventSubMode` in attribute event subscriptions. This enables
  selecting the subscription mode (`Sync`, `SyncRead`, `Async`, `AsyncRead`, `Stateless`)
  when subscribing to attribute events (!1358).
- Asynchronous modes (`Async`, `AsyncRead`) handle initial subscription notifications,
  allowing the client to distinguish between successful subscriptions and cases where
  a polling fallback is required.
- First-time attribute reads during client initialization. Attributes can be read
  once before event subscriptions for attribute with events with "no read" modes
  (`Sync`, `Async`) to ensure cached values are initialized.
- Ability to change or disable Tango event subscriptions from Taurus custom settings,
  CLI, or programmatically through the `TangoFactory` API.

### Changed
- Default subscription mode is now `AsyncRead` when `EventSubMode` is available (Tango >= 10.1).
  To retain the previous Taurus behavior, `SyncRead` can be selected via Taurus custom settings.

## [5.3.2] - 2025-11-28
Patch release with bug fixes.

IMPORTANT: This patch release has not undergone the usual cross-platform manual testing and is not merged into the stable branch. Please report any issues you encounter.

### Fixed
- Updated Tango formatter so `DevState` values display the state name correctly in labels (!1353, #1406).
- Correct `DevState` enum handling after migration to the `tango` namespace when using PyTango<9.4 (!1377).
- Fixed issue with TaurusValueCheckBox. Reimplementation of handleEvent method to update value at widget startup (!1375, #1408)
- Fixed issue with ElementTree library. Fixed method to access custom widgets due to API change (!1381)
- Fixed circular import in taurusgui (!1834)
- Add Qt.qApp proxy for backwards compatibility with GUIs accessing Qt.qApp.SDM, ensuring compatibility with both Qt5 and Qt6 (!1378).
- Exception in `TaurusModelChooser` caused by `UpdateAttrs` signal definition; updated for PyQt6/PySide6 compatibility (!1374, #1445).
- Derive the path to the PySide6 Designer dynamically instead of using a hard-coded location (!1380).
- Fixed issue with TaurusValueSpinBox for non-multiplicative unit (!1379, #1448).
- Avoid `Qt.ItemFlags` instantiation to prevent `AttributeError` with PyQt6 by returning the combined flags directly (!1385).

### Changed
- Replaced Black and Flake8 with Ruff for formatting and linting, and updated Taurus
  code to comply with Ruff rules (!1359)

## [5.3.1] - 2025-09-15
Hotfix to fix #1442

### Fixed
- Restored dot-separated logger names to preserve parent/child hierarchy in Python
  logging. This ensures handler inheritance and log propagation. The issue was
  detected as missing output in Sardana Spock CLI (!1370, #1442)

## [5.3.0] - 2025-08-24
[Jul25 milestone](https://gitlab.com/taurus-org/taurus/-/milestones/21)

Release adding Qt6 support and dropping support for python<3.7 and PyTango<9.2.0.

### Added
- Qt6 compatibility across the codebase, including support for PyQt6 and PySide6,
  while retaining support for PyQt5 and PySide2. PyQt5 remains the default binding
  (!1300, #1299)
- Support for custom Tango device state color policies via the
  TANGO_DEVICE_STATE_COLOR_POLICY setting. `Taurus` policy (default) preserves
  current colors, and a new `Tango` policy is available to match Tango ATK colors.
  More policies can be added in the future (!1361, #1391)

### Changed
- Increased minimum supported PyTango version to 9.2.0 (!1347)
- Updated minimum Python version to 3.7 (!1364)
- TaurusForm now uses `TaurusModelSelector` instead of `TaurusModelChooser` for model
  selection, enabling plugin discovery (!1294, #1353)

### Fixed
- Fixed incorrect pending operations display for Tango attributes pushing change
  events from code. This is caused due to `w_value` not being updated in the received
  event after write. Taurus now always uses `write_read_attribute()` to ensure
  consistency (!1360)
- Avoid None on initial read state in Tango device (!1362)
- Fix setting model in taurus form using the full Tango host when no `TANGO_HOST`
  variable is set (!1363, #1421)
- Prevent TaurusValue to return a non-list result as default read widget and to
  destroy an unexisting widget (!1323, #1379)


## [5.2.4] - 2025-04-29
Unofficial release with bug fixes and small additions.

IMPORTANT: this is a not-fully-official release: it did not undergo the usual
release manual tests on various platforms and it is not merged into the stable
branch. However, it has been used in production in ALBA for some weeks already
without issues.

### Added
- New dropdown widget for handling Tango DevEnum attributes. (!1352)
- Support for plotting of spectra and images in TaurusNeXusBrowser. (!1351, #1410)

## [5.2.3] - 2025-02-25
Unofficial release with bug fixes and small additions.

IMPORTANT: this is a not-fully-official release: it did not undergo the usual
release manual tests on various platforms and it is not merged into the stable
branch. However, it has been used in production in ALBA for some weeks already
without issues.

### Fixed
- Allow TaurusPollingTimer to end its infinite loop before removing the object so it doesn't create orphan threads. (!1345)
- Problems updating bgRole color in TaurusLabels (!1344, #1400)
- Fixed right-click context menu action in TaurusGraphicsScene. Now it correctly sets the model in TaurusDevicePanel launched from JDraw synoptics (!1343, #1399)

## [5.2.2] - 2025-01-22
Unofficial release with bug fixes and small additions.

IMPORTANT: this is a not-fully-official release: it did not undergo the usual
release manual tests on various platforms and it is not merged into the stable
branch. However, it has been used in production in ALBA for some weeks already
without issues.

### Added
- Added support for Lima video `imageMode`=19 (YUV422PACKED) considering it the same as `imageMode`=16 (YUV422) for decoding. (!1339)
- Documented API incompatibility between guiqwt and guidata for PyQt<5.15 in known issues. (!1340, #1396)

### Fixed
- Removed guiqwt CLI command causing wrong output of `taurus --help` option. (!1336, #1389)
- Issue with `TaurusAttribute` value comparison failing due to `numpy.allclose` default tolerance. This caused some `wvalue` changes to not be identified correctly. (!1338, #1394)
- Properly close `TaurusGraphicsScene` thread when its parent widget is destroyed. (!1328)

## [5.2.1] - 2024-12-20
Unnoficial release with bug fixes and small additions.

IMPORTANT: this is a not-fully-official release: it did not undergo the usual
release manual tests on various platforms and it is not merged into the stable
branch. However, it has been used in production in ALBA for some weeks already
without issues.

### Added
- Added option to disable tango event subscription. This behavior can be toggled via custom setting, cli option and method in TangoFactory. Using the CLI or TangoFactory method will disable the subscription to all events regardless of the custom settings (!1326)
    - CLI: add --disable-tango-event-subscription
    - TangoFactory: call set_tango_event_subscription_disabled(True)
    - Custom setting: set TANGO_EVENTS_TO_SUBSCRIBE=[].
  Configuration events are not affected by these options, for them set the already existing custom setting TANGO_AUTOSUBSCRIBE_CONF=False
- Close TaurusApplication on CTRL+C (SIGINT signal) (!1319)
- Added basic support for Tango `DevEnum` type using DataType.Integer (!1331, #1342)

### Changed
- Prepend taurus path to PYQTDESIGNERPATH instead of overwriting it (!1324, #1380)
- CI pipeline tests: Removed Debian stretch. Added Debian bookworm. (!1325)

### Fixed
- Resolved issue with multiple TangoDBs that prevented access to databases not defined in TANGO_HOST (!1330, #1387)
- Fixed exception on eval attributes caused by None values on startup (!1335, #1390)
- Forced int type when setting Qt.QColor in JDraw (!1327)

## [5.2.0] - 2024-10-25
[Oct24 milestone](https://gitlab.com/taurus-org/taurus/-/milestones/20)

Release containing improvements related with TEP21 (Taurus Performance Optimizations).
It includes some potential breaking changes for specific use cases.

### Added
- Support for multiple TangoDB. (!1270, #929)
- Solve TaurusWheel exception.(!1278, #1249)
- Improvements in CI pipeline. (!1282, !1310)
- Taurus designer .ui files can now be opened with _taurus loadui uifile.ui_ command. (!1281)
- Add the possibility to save TaurusMainWindow state from _File_ contextual menu (!1291, #1343)
- Add a new TaurusCustomSetting able to manage the default behaviour of save state method (!1291, #1343)
- Support for NumPy 2.0 (!1293, #1352)
- Solve ValuechangedSignal not emited (!1279, #1338)

### Fixed
- Solve memory leak when attributes are not avalaible. (!1276, #1318)
- Make `PyQtWebEngine` mandatory dependency for `taurus-qt` to fix issues
  with Taurus Manual panel when the dependency is not installed (!1272, #1287)
- **Potential breaking change**: The deviceState of TaurusDevice corresponding to non existent tango devices, is now Undefined instead of NotReady. The deviceState of TaurusDevice corresponding to a running tango device in UNKNOWN state, is now NotReady instead of Undefined. This may break scripts that do something according to NotReady or Undefined deviceStatus. (!1251, #1223)
- Avoid an unnecessary read in ATTR_CONF_EVENT callback. (!1248/!1288, #1275). This read is necessary so the attributes without event get an initial value and doesn't depend on the polling thread, so it was moved to the subscription failure (!1289)
- Update color names to match Web colors. The colors that are not exactly a Web color, are named "Taurus - x", where x is the most similar Web color (!1287)
- Avoid multiple _getElementAlias()_ calls (!1283, #1305)
- Avoid multiple _fqdn_no_alias()_ calls (!1286, #1306)
- Fix error when loading an xml from a previously created gui using the _taurus newgui_ wizard (!1296, #1333/#1200)
- Fix incorrect taurus-h5file requirement (!1297, #1335)
- Fix example in TaurusPlot documentation (!1298, #1349)
- Fix the bug where the polling thread starts without having anything to poll, causing an initial sleep. Fix the bug (related to the previous one) where timeout attributes caused a 9s GUI startup. (!1306, #1278)
- Fix TangoAttribute _read()_ cache not expiring (!1306, #1276)
- Fix manually activating polling using _attribute.activatePolling(time, force=True)_ causing an exception when reading the attribute. (!1306, #1357)
- Fix TangoAttribute error timestamp being the read start instead of raise error time (!1302)
- Fix error in NeXus Browser when clicking any node that is not a Dataset (!1285, #1350)
- Handling of multiple values when `equal=False` in `AttributeEventWait.waitForEvent()`: it now waits for an event that differs from all given values, rather than just one (!1307)
- Added workaround documentation for taurus designer problem with PyQt 5.15 (!1309)
- Fix TangoAttribute not correctly reenabling polling after Tango events are disabled. (!1301, #1340)
- Fix multiple tango host incorrectly splitting when selecting model using Advanced Settings (!1290, #1337)

### Changed
- Default pickle protocol changed from HIGHEST to DEFAULT (!1229, #1339)
- Updated documentation (!1303, !1308, !1315)
- `val` parameter in EventGenerator's _fireEvent_ method is now optional, so you can send events without value (a notification event). (!1306)
- **Potential breaking change**: Now TangoAttribute _read()_ cache doesn't expire if `cache=True`. To make it expire you can still use _read(time\_in\_ms)_. This may break code that assumed that _read()_ and _read(True)_ made the cache to expire in 3s (or the default polling time you set). However, the cache was not expiring anyways due to a bug (#1276), so the behavior should be the same even with this change. (!1306, #1358)
- Taurus now doesn't read the tango attribute value when the subscription to change events fails. This implies that TaurusApplications start without values for attributes that don't send events, letting the polling thread get the values once the application finished starting. The old behavior can still be used by setting the new taurus custom setting `TANGO_FORCE_READ_IF_SUBSCRIPTION_FAILS` to "ALWAYS". (!1306, #1275, makes !1289 optional)
- **Potential breaking change**: Now TangoAttribute _read()_ method will always return the cached value when the Application is in `STARTING` state. This should be taken into account for programatic GUIs in the case there an Attribute object is created and read during GUI creation, as it will return `None` if `cache=False` is not specified since no value will be available yet.
- Removed Print option from taurus image (!1312, #1334)
- Conda images for CI pipeline now include pytango version in the name (!1314)
- Increased minimum numpy version to 1.16 (!1318)


## [5.1.8] 2023-11-09
Unnoficial release with some bug fixes. Compatibility with PyTango >= 9.5.

IMPORTANT: this is a not-fully-official release: it did not undergo the usual
release manual tests on various platforms and it is not merged into the stable
branch. However, it has been used in production in ALBA for some weeks already
without issues.

### Fixed
- Fix documentation not building because of docstrings style (!1263)
- Fix date format in date of release (!1264)
- Removed CmdArgType.DevInt (!1261)
- Fix memory leak when attributes are not allowed to read or returning exceptions (!1266)

## [5.1.7] 2023-10-17
Unnoficial release with some bug fixes.

IMPORTANT: this is a not-fully-official release: it did not undergo the usual
release manual tests on various platforms and it is not merged into the stable
branch. However, it has been used in production in ALBA for some weeks already
without issues.

### Fixed
- Avoid creation of `TangoAuthority` twice for each attribute (!1260)
- Avoid creation of polling threads on `addAttributeToPolling()` (!1253)

## [5.1.6] 2023-06-13
Unnoficial release with some bug fixes.

IMPORTANT: this is a not-fully-official release: it did not undergo the usual
release manual tests on various platforms and it is not merged into the stable
branch. However, it has been used in production in ALBA for some weeks already
without issues.

### Added:
- Run testsuite on conda-py3.10 and conda-py3.11 Docker images (!1257)

### Fixed:
- Compatibility with Python 3.11 (#1289, !1254)
- Compatibility with pint 0.21 (!1255, #1290)
- Compatibility of tests with PyTango 9.4.0 with regard to attr w_value (!1256)
- Inspect module deprecation fix with Python 3.11 (!1258)

## [5.1.5] - 2022-12-22
Unnoficial release with some bug fixes.

IMPORTANT: this is a not-fully-official release: it did not undergo the usual
release manual tests on various platforms and it is not merged into the stable
branch. However, it has been used in production in ALBA for some weeks already
without issues.

### Fixed:
- Consider Tango attribute error as valid attribute cache (!1247)
- Adapt jdraw synoptic to python 3.10 (!1246)
- `TaurusNeXusBrowser` with scalar datasets (!1245)
- Locating qt designer on Windows when more that one is installed (#1267, !1244)

## [5.1.4] - 2022-04-08
Unnoficial release to make the multi-model support [TEP20] available in pypi
and conda packages.

IMPORTANT: this is a not-fully-official release: it did not undergo the usual
release manual tests on various platforms and it is not merged into the stable
branch. However, it was throughly tested as part of the [TEP20] approval and
it has been used in production in ALBA for 2 weeks already without issues.
Also, CI testsuite now includes stretch and buster in the test environments
matrix.

### Added:
- Multi-model support in TaurusBaseComponent and derived classes ([TEP20], !1218)
- By default, now the user is prompted on whether to save settings before
  closing a TaurusMainWindow (!1225)
- Pre-commit hook configuration (!1227, !1231)
- CI tests for old debian9 and debian10 (!1238)
- Test reports in CI web UI (!1234)

### Changed:
- By default, config versions are now class-specific (prevents unintentionally
  applying a configuration from a different widget class) (!1225)
- TaurusMainWindow now uses TaurusMessageBox instead of QMessageBox settings
  load failures to facilitate issue reporting (!1225)
- taurus config browser now shows the ConfigVersion for each item (!1225)
- Use pyproject.toml as per PEP518 (!1223)
- Improved CI (!1224)
- Nexus widget demo method now accepts a path arg (!1226)
- all parent model API methods (already deprecated in [4.4.0]) now issue
  deprecation warnings (not just when enabling the feature) (!1218)

### Deprecated:

- `findModelClass`, `setModelCheck`, `setModelName` methods of
  `TaurusBaseComponent` and derived classes ([TEP20], !1218)
- `__UNVERSIONED__` ConfigVersion (auto-replaced on next save of settings)
  (!1225)

### Fixed:
- some configurations not restored in TaurusForm (and maybe others) (!1225)
- deprecation warnings in taurustrend2d (!1229)
- TaurusNeXusBrowser now closes opened files on close (!1228)
- TaurusLED color for Tango DevState.INSERT should be white (!1235)
- exception in DevicePanel with python 3.10 (!1239)
- issues affecting python 3.5 (!1238)
- Input sanitizing issues in newgui wizard (!1230, !1232)
- exception when closing GUI if PyQtWebEngine not installed (!1233)


## [5.0.0.1] - 2022-03-14

Hotfix for #1259

### Fixed
- issue loading paths with taurus gui (!1240)
- black reformatting (!1240)
- removed usage of deprecated distutil.version (!1240)


## [5.0.0] - 2021-11-15

Major release that removes support of Python2 and Qt4 (from here we support
python >= 3.5 and the PyQt5 and PySide2 bindings). Other than that there should
not be any other backwards incompatibility between 5.x and 4.x (we
intentionally avoided enforcing the pending deprecations of 4.x even if this
is a major version bump)

### Removed
- python2 support (use python >= 3.5 instead) (!1192)
- Qt4 (PyQt4 and PySide) support (use PyQt5 or PySide2 instead)
- `taurus.qt.qtgui.qwt5` (use taurus_pyqtgraph instead)
- `taurus.test.testsuite` (use pytest instead)

### Added
- Support for loading settings from user and system .ini files (!1205)
- `taurus.__version__`  (!1200)
- `taurus.external.qt.QtWebEngine` and `taurus.external.qt.QtWebEngineWidgets`
  (!1209)
- `pyproject.toml` with configuration of black for the project (!1193)
- `.flake8` with configuration of flake for the project (!1193)
- `PySide2` CI tests (!1208)

### Changed
- extensive refactoring to clean taurus code. It is now flake8 and
  black compliant. Tests enforce in CI for flake8 and black (!1193)
- refactor import hierarchy in Taurus. Official API is now defined via
  inclusion in `__all__` variables (!1199)
- docstrings now use standard reST formatting (removed custom taurus
  preprocessing of docstrings) (!1193)
- The following APIs changed to use `"module:class"` for specificating
  a widget class (!1217):
  - the widget class in `TaurusLauncherButton`
  - the class name in `TaurusGraphicsScene.getClass`
  - the class ID in `TaurusValue.set*WidgetClass()` methods
  - the class name in taurusgui's `*Description` classes
  - the `defaultCandidates` and `extraWidgets` values in `WidgetPage`
  - The widget name in DockWidgetPanel.setWidgetFromClassName()
- `tauruspluginplugin` uses an explicit list of widgets instead of
  introspection (!1217)
- `taurusdemo` uses an explicit list of submodules instead of
  introspection (!1217)
- all usages of deprecated `imp` module replaced by `importlib` equivalents
- Pending operations check now compares quantities allowing for rounding
  errors (!1195)
- `QtWebkit.QWebView` replaced by `QtWebEngineWidgets.QWebEngineView`
  (!1209, !1213)
- Improved CI tests, based on taurus-docker images (!1210, !1214)

### Deprecated
- `TaurusWidgetFactory` (!1217)
- `taurus.qt.qtgui.style`
- `taurus.core.util.property_parser`
- `AttributeEventWait.waitEvent` replaced by `AttributeEventWait.waitForEvent`
  (!1191)
- `taurus.qt.qtgui.editor` (#1250)

### Fixed
- `TaurusLed` display of faulty and inverted signals (!1201)
- `TaurusValueLineEdit` issues with integers writes starting by "0" (!1202)
- refresh issues with `TaurusValuesTable` (!1221)
- GUIs blocked when accessing DSs raising exceptions on reads (!1219)
- Inheritance issues with PySide2 (!1207, !1220)
- PySide2 issue in `TaurusValuesTable` (!1211)
- missing modules in API auto-documentation (!1199)
- warnings from pint unit redefinitions (!1198)
- exception while handling an exceptions in guiqwt image items (!1212)


## [4.8.1] - 2021-09-22

Hotfix to backport !1219 to 4.x

### Fixed
- Protect against exceptions in async reads from Tango DSs (!1219)


## [4.8.0] - 2021-06-03
[Jun21 milestone](https://gitlab.com/taurus-org/taurus/-/milestones/16)

### Added

- Official conda-forge packages (#1172, !1187)
- `TangoAttribute.read` accepts a timeout in the `cache` argument (!1105)
- `QtCore.QtInfoMsg` in QT_LEVEL_MATCHER: __log.info (!1156)

### Changed
- Taurus project moved from Github to Gitlab ([TEP19], !1182)
- Support for taurus_pyqtgraph plugin becomes official ([TEP17])
- Support for setuptools entry_point-based plugins becomes official ([TEP13])
- Switched version convention to PEP440 (!1189)
- Testsuite refactored to not require a tango DB (!1180)
- Optimized TaurusGui initialization times when loading Pool info (!1183)

### Fixed
- BaseConfigurableClass leaves files unclosed (!1184)
- deadlock in TaurusPollingTimer (!1181)
- Issues with TaurusLabel (!1151)
- Issues with the trend subcommand (!1154)
- Exception at exit when using old PyTango versions (#1211)
- Problems when exporting TaurusGui config to xml (#1129)
- Outdated ALBA ticket address (!1186)


## [4.7.1.1] - 2021-05-07

Hotfix to avoid zombie processes during tests

### Fixed
- Avoid _zombie_ device server processes left after running
  the `ProcessStarter` on Windows (!1188)


## [4.7.1] - 2021-04-08

A hotfix fixing an old issue affecting Windows tango clients (#709)

### Fixed
- Tango client application crashes at exit on Windows (!1185)


## [4.7.0] - 2020-08-07
[Jul20 milestone](https://gitlab.com/taurus-org/taurus/-/milestones/15)

### Added
- `plot`, `trend`, `trend2d`, `image` first-level taurus subcommands (#1120)
- `"taurus.*.alt"` entry-point groups for registering alternative
  implementations of `plot`, `trend`, `trend2d`, `image` (#1120)
- check-deps subcommand (#988)
- `taurus.cli.register_subcommands()` and `taurus.cli.taurus_cmd()` (#991)
- Support for `ºC` as degree celsius in units (#1033)
- Support for spyder v4 in `taurus.qt.qtgui.editor` (#1038)
- Entry-point ("taurus.qt.formatters") for registering formatters via plugins (#1039)
- New `worker_cls` argument for `taurus.core.util.ThreadPool` costructor (#1081)
- `taurus.core.util.lazymodule` for delayed entry-point loading of modules (#1090)
- `"taurus.form.item_factories"` entry-point group (#1108)
- `tauruscustomsettings.TANGO_AUTOSUBSCRIBE_CONF` to allow skipping of config
  event subscription by `TangoAttribute`
- Official taurus packages are now automatically published in the taurus-org
  Anaconda channel

### Changed
- Improved Qt binding selection mechanism (and prioritize PyQt5 over PyQt4) (#1121)
- Qt theme no longer set to TangoIcons by default (for coherence with docs) (#1012)
- Improved Configuration options for TaurusGui (#940)
- Passing `cmd_line_parser=None` to TaurusApplication is no longer required (#1089)
- (for developers) Support of tox and change to pytest. More platforms
  being now automatically tested by travis (#994)
- TaurusForm provides more debugging info when failing to handle a model (#1049)
- Improved GUI dialog for changing the formatter of a widget (#1039)
- Modules registered with `"taurus.qt.qtgui"` entry-point are now lazy-loaded (#1090)
- The control over which custom widgets are to be used in a TaurusForm is now
  done by registering factories to `"taurus.form.item_factories"` entry-point (#1108)
- Allow case-insensitive values for the `taurus --log-level` option (#1112)
- Qt unit tests reimplemented using pytest-qt (#1114)
- `"'taurus.qt.qtgui.panel.TaurusModelSelector.items"` entry-point group
  renamed to `"taurus.model_selector.items"`
- Added support for 3rd party widgets in TaurusValue config settings (#1066)
- Improved documentation (#1044, #1056, #1059, #1120)

### Deprecated
- `qwt5` and `guiqwt` CLI subcommands (#1120)
- `TaurusBaseWidget.showFormatterDlg()` (#1039)
- Custom widget API in TaurusForm, TaurusValue and TaurusGui (#1108)
- `tauruscustomsettings.T_FORM_CUSTOM_WIDGET_MAP` (#1108)
- `BaseWidgetTestCase` and `GenericWidgetTestCase` (#1114)
- `TimeOut` Device Server (#1114)

### Fixed
- Several issues in TaurusWheelEdit (#1010, #1021)
- Several issues affecting synoptics (#1005, #1029, #1082)
- Issues with TaurusValueComboBox (#1102, #1032)
- Issues with TaurusValueLineEdit (#1072)
- TaurusValueLineEdit could not be enabled (#1117)
- Support dns aliases for the authority name in tango model names (#998)
- Py3 exception in `TaurusModelChooser.getListedModels()` (#1008)
- Thread safety issues in `TaurusPollingTimer`'s add/remove attributes API (#1002)
- Problem preventing editing existing GUIs with Taurus New Gui wizard (#1126)
- (for py2) Improved backwards compatibility of `taurus.qt.qtgui.plot` (#1027)
- Issues with events and subscriptions in Tango (#1030, #1061, #1113)
- Compatibility issue in deprecated TangoAttribute's `isScalar()` and `isSpectrum()` (#1034)
- Tooltip issues in case of device connection problems (#1087)
- Some issues in taurus v3 to v4 migration support (#1059)
- Some CI test issues (#1042, #1069, #1073, #1075, #1109, #1114)


## 4.6.1 - 2019-08-19
Hotfix for auto-deployment in PyPI with Travis. No other difference from 4.6.0.

### Fixed
- Travis not deploying tar.gz (#990)


## [4.6.0] - 2019-08-19
[Jul19 milestone](https://gitlab.com/taurus-org/taurus/-/milestones/13)

### Added
- New CLI API based on click and `taurus` command supporting pluggable subcommands (#856)
- TaurusGui now accepts a `settingsname` argument to specify the settings file to
  be loaded. Also accessible from the CLI as `taurus gui --ini NAME` (#570)
- `TaurusModelSelector` and `TaurusModelSelectorItem` classes and the
  (experimental) `"taurus.qt.qtgui.panel.TaurusModelSelector.items"` entry point (#869)
- `TaurusFactory.getValidatorFromName` method and `getValidatorFromName` helper (#893)
- New options API for TaurusMainWindow and TaurusGui (#858)
- New optional set of color-blind friendly LED icons for Tango states (#902)
- New configuration options in QWheelEdit to customize its internal editor (#832)
- New `Utf8Codec` (#960)
- Support for RGB24 in VideoImageCodec (#832)

### Removed
- Functions implementing the old CLI scripts (#856).
  Note: these functions and the corresponding console scripts are still provided
  by the "[taurus_legacy_cli]" plugin. (#856)
- Unused ini file `<taurus>/qt/qtgui/taurusgui/conf/tgconf_macrogui/tgconf_macrogui.ini`

### Changed
- Old CLI scripts (taurusform, taurusdemo, etc.) are replaced by equivalent
  subcommands to the `taurus` command.  (#856)
- TaurusDevPanel now is able to show the attributes independently of the
  state of the device (#946)
- `JsonCodec.encode` now outputs strings (in v4.5, it was inconsistently returning bytes when in py3) (#960)
- TaurusDevPanel is now a TaurusGui (new panels can be added by the user) (#939)
- Taurus mixin classes (e.g. `TaurusBaseComponent`) are now `super()`-friendly (#934)

### Deprecated
- `taurus.core.util.argparse` (#856)
- `TaurusAttribute._(un)subscribeEvents` API (#876)
- `TaurusBaseComponent` "taurus popup menu" API (#906)
- `TaurusMainWindow` old option names (`_heartbeat`, `_show*Menu`, `_showLogger`,
  `_supportUserPerspectives`, `_splashLogo`, `_splashMessage`) (#858)

### Fixed
- taurusgui not running if tango not installed (#912)
- Outdated template for new guis created with `taurus newgui` (#933)
- wrong return value of `isValidName` in some cases (#897)
- exception when calling TangoAtribute.write with a list of integers (#915)
- several issues related to py2+p3 simultaneous support (#878, #879, #881, #885, #886, #894, #947)
- several issues related to multiple Qt bindings support (#875, #890, #895, #962)
- Some modules not being autodocumented (#941)
- TaurusArrayEditorButton used in forms even if Qwt5 is not available (#973)
- TaurusGuis do not show output in console on Windows (#868)
- TaurusConfigEditor not working on Windows (#950, #957)
- TaurusDesigner not working on Windows (#955, #968)
- Other (#956, #954, #948, #925)


## [4.5.1] - 2019-02-15

Together with [4.5.0], they cover the [Jan19 milestone](https://gitlab.com/taurus-org/taurus/-/milestones/12)

### Fixed
- redundant units shown in TaurusForm write widget (#860)
- deprecation warning in tauruspanel
- infinite recursion issue in TangoDevice
- Other (#855)


## [4.5.0] - 2019-01-29

This is a special release for meeting the deadline of debian buster
freeze (debian 10).

### Added
- Support of Python3 (beta stage, not yet production ready) (#703, #829, #835)
- Support of other Qt bindings: PyQt4, PyQt5, PySide2, PySide
  (beta stage, not yet production ready) (TEP18)
- (experimental) Entry point for schemes in TaurusManager (#833)

### Removed
- taurus.qt.qtgui.tree.taurusdevicetree submodule (obsolete, unused)
- Trend dockwidget in TaurusDevPanel
- `taurus.qt.qtgui.taurusgui.macrolistener` (now provided by
  `sardana.taurus.qt.qtgui.macrolistener`)

### Changed
- `taurus.qt.qtgui.plot` is now deprecated, but the same Qwt5-based
  API is now available in `taurus.qt.qtgui.qwt5`
- `taurus.qt.qtcore.util.emmiter.QEmitter.doSomething` signal signature
  changes from `collections.Iterable` to `list`
- Updated Pypy's Trove classifiers (we are now officially stable!) (#844)
- Default serialization mode for Tango reverted to `TangoSerial` (in 4.4.0
  the defaultfor Tango was changed to `Serial`) (#850)

### Fixed
- bug when copying tango or evaluation attribute values (#831, #849)
- bug when adding listener to non-ready Tango device (#792)
- Various issues with Taurus Forms (#800, #805)
- problem when displaying TaurusWheelEdit in vertically-limited space (#788)
- bug when managing subscription event in Tango (#809)
- Other (#793, #819)

### Deprecated
- `taurus.qt.qtgui.plot`
- `QtColorPalette.qvariant()`
- `TaurusBaseTreeItem.qdisplay()`
- `taurus.qt.qtdesigner.qtdesigner_prepare_taurus()`
- The following have been implicitly deprecated since 4.0 (when API1
 support was dropped) but only now we deprecate them explicitly
    - `taurus.external.qt.QtCore.QString`
    - `taurus.external.qt.QtCore.QVariant`
    - `taurus.external.qt.QtCore.from_qvariant`
    - `taurus.external.qt.QtCore.to_qvariant`


## [4.4.0] - 2018-07-26
[Jul18 milestone](https://gitlab.com/taurus-org/taurus/-/milestones/11)

### Deprecated
- pint, enum, unittest and argparse submodules of taurus.external (#723)
- useParentModel feature (warn of deprecation only when enabling) (#769)

### Added
- Support fragment-based slicing of attributes ([TEP15])
- New serialization mode in which events are serialized by a Taurus
  internal queue (the former "Serial" mode that was tango-centric is
  now deprecated and renamed "TangoSerial") (#738)

### Changed
- Serialization mode now is explicitly set to Serial in the case
  of TangoFactory (Taurus defaults to Concurrent) (#678)
- Improved API to set formatter on forms (#767, #759)
- TaurusCommadnForm is now populated regardless of the state of
  the device (#728)
- Improved UI for TaurusSpinBox (#736)
- Improved responsiveness of ImageCounterDevice (#698)
- Improved docs and doc generation (#778, #766, #571, #724, #725)

### Fixed
- TaurusModel ignoring the serialization mode (#678)
- modelIndex support (#648, #687, #729)
- refresh issue in TaurusTrend (#775)
- Issue with permanent text inTaurusLabel (#735)
- Issue when importing ascii files with dates in TaurusPlot (#748)
- Case-sensitivity issues with models of forms and plots (#780, #697)
- Some FQDN-related issues affecting mostly Sardana (#762, #719, #658)
- Missing ref in TangoAttrValue (#758)
- [Many other issues](https://github.com/taurus-org/taurus/issues?utf8=%E2%9C%93&q=milestone%3AJul18%20label%3Abug%20)

### Removed
- All 3rd party code from taurus.external (now using dependencies
  instead of embeded 3rd party code)
- CTRL and ALT keys are no longer used to modify step size in
  TaurusValueLineEdit and TaurusValueSpinbox (#749)
- TaurusMainWindow's "Change Tango Host" action is now invisible
  and its key shortcut has been removed (#781)


## [4.3.1] - 2018-03-14
A hotfix release needed for sardana 2.4

### Fixed
- consistency issues in stepping support in spinboxes and line edits (#749)
- duplicated "tango://" prefix in panels created from Pool for sardana>=2.4
- avoid problems if channel dimension info is set to None by sardana (#722)
- unexpected "inf" values in tangoAttribute range, warning and alarm
  attributes (#750)


## [4.3.0] - 2018-03-01
[Jan18 milestone](https://gitlab.com/taurus-org/taurus/-/milestones/10)

### Deprecated
- taurus.core.tango.search
- TaurusMainWindow's "Change Tango Host" action (#379)

### Added
- User Interface to set custom formatters (#564)
- Re-added `taurus.external.ordereddict` (#599)
- Option to ignore outdated Tango events (#559)
- Travis-built docs (not yet replacing the RTD ones) (#572)
- TaurusLed now supports non-boolean attributes (#617)
- Support for arbitrary bgRole in labels (#629)
- `--import-ascii` option in `taurusplot` launcher (#632)
- State and event support in TangoSchemeTest DS (#628, #655)
- Model info in widget tooltips (#640)
- (experimental) Delayed event subscription API (#605, #593)
- (experimental) Entry point for taurus.qt.qtgui extensions (#684)
- Support DevVoid in Tango-to-numpy type translation dicts (#666)
- `removeLogHandler` method to `Logger` class (#691)
- modelChooserDlg static method now accepts listedModels arg (#693)

### Changed
- Treat unit="No unit" as unitless in Tango attributes (#662)
- taurus.qt widgets can now be used without installing PyTango (#590)
- Tango model name validators now always return FQDN instead of PQDN
  for the tango host (#488, #589)
- Improved docs (#525, #540, #546, #548, #636) (thanks @PhilLAL !)
- Make spyder dependency optional (#556)

### Fixed
- Wrong "missing units" warnings for non-numerical attributes (#580)
- Taurus3 backwards compatibility issues (#496, #550)
- False positives in taurus.check_dependencies (#612)
- Main Window Splash screen not showing (#595)
- TaurusTrend2DDialog not usable from designer (#597)
- Missing icons in buttons (#583, #598)
- Exception in TaurusCommandForm (#608)
- Launchers not showing output on MS Windows (#644)
- Various issues with input widgets (#623, #661, #663, #669, #674, #681)
- Exceptions in TaurusMessagePanel (#704)
- TangoAttribute receiving events after being deleted (#692)
- Regressions in:
  - TaurusTrend (#618)
  - TaurusGrid (#609)
  - TaurusGUI edit with `taurusgui --new-gui` (#532)
- Epics scheme is now case sensitive (#694)
- [Many other issues](https://github.com/taurus-org/taurus/issues?utf8=%E2%9C%93&q=milestone%3AJan18%20label%3Abug%20)

### Removed
- taurus.qt.qtgui.panel.taurusfilterpanel


## [4.1.1] - 2017-07-21
Hotfix release needed just for PyPI

### Fixed
- Issue with PyPI metadata (hotfix 4.1.1)


## [4.1.0] - 2017-07-21
[Jul17 milestone](https://gitlab.com/taurus-org/taurus/-/milestones/9)

### Added
- Formatting API in TaurusBaseComponent (#444)
- TangoAttribute.format_spec and taurus.core.util.tangoFormatter
- Write support for eval scheme (#425)
- Arbitrary module support in eval scheme (#423)
- TaurusGUI New GUI wizard generates setuptools distribution (#477)
- TaurusModel.parentObject property (#415)
- TangoAttribute.getAttributeProxy (#450)
- `taurusdemo` launcher (#416)

### Changed
- pint_local updated to v 0.8 (#445)
- Improve config properties of TaurusTrend2D (#489)
- Make taurusplot and taurustrend (re)store their geometry (#508)
- Improve logs when handling unsupported units in
  TangoAttributes (#420, #495, #403)
- Improve logs when TangoAttribute read fails (#478)
- Allow subscribing to Tango attributess without emiting firsat event (#482)
- Use dependencies (and optional deps) in setuptools distribution (#479)
- Make TaurusPlot inspector mode use the attribute format for display (#509)

### Deprecated
- TangoAttribute.format
- taurus.qt.qtgui.console (#385)
- taurustrend1d (#514)
- tauruscurve (#514)

### Removed
- `taurus.external.ordereddict` (#223)
- `taurus.qt.qtgui.Q*` modules (Qt, QtCore, QtGui, Qwt5,...)
- `taurus.qt.qtgui.util.taurusropepatch` module
- `taurusqt.qtgui.util.genwidget`

### Fixed
- Taurus4 ignoring Tango format (#392)
- Incompatibility with Tango9.2 (#458)
- Bug in handling of nanoseconds by TaurusTimeVal (#453)
- Import error when PyTango is not installed (#398)
- Issues affecting TaurusPlot (and Trends) (#422, #438, #440, #475, #508 )
- Issues affecting TaurusLCD (#467)
- Issues when changing tango host (#79, #378, #382, #487)
- Issues affecting Eval (#428, #448)
- Docs issues (#249, #267,  #397, #430, #490)
- [Many other issues](https://github.com/taurus-org/taurus/issues?q=milestone%3AJul17+label%3Abug)


## [4.0.3] - 2017-01-16
[Jan17 milestone](https://gitlab.com/taurus-org/taurus/-/milestones/1)
Bugfix release.
For a full log of commits since Jul16, run (in your git repo):
`git log 4.0.1..4.0.3`

### Added
- Generic Attribute, Device and  Authority getters in TaurusFactory
- spyder >=3 support (#343)
- bumpversion support (for maintainers) (#347)
- Contribution policy explicited in CONTRIBUTING.md
- Continuous Integration for Windows support (Appveyor) (PR#10)

### Changed
- TangoAttribute now decodes uchars as integers instead of strings (#367)
- Allow empty path in Attr and Dev URIs (#269)
- Project migrated to Github (TEP16)
- Versioning policy (use of `-alpha` suffix for unreleased branches)

### Deprecated
- `taurus.Release.version_info` and `taurus.Release.revision` variables
- `TaurusAttribute.isState` (#2)
- `taurus.external.ordereddict` (#8)

### Fixed
- Taurus4 regressions in:
    - TangoAttribute (when handling Tango config errors) (#365)
    - TaurusValueSpinBox (#7)
    - taurusgui --new-gui (#275)
    - TaurusGui Sardana instrument panels (#372)
    - Macrolistener (affects sardana) (#373)
    - Synoptics (#363)
    - TaurusValueLineEdit (#265)
    - taurusgui.macrolistener (#260)
    - TaurusEditor (#343)
- Bug causing high CPU usage in TaurusForms (#247)
- Deprecation warnings in `TaurusWheelEdit` (#337)
- Exceptions in `taurusconfigurationpanel` for non-tango models (#354)
- Exception when creating non-exported tango devices (#262)
- Bug causing random failures in the test suite(#261)
- Documentation issues(#351, #350, #349)

### Removed
- `TaurusBaseEditor2` class


## [4.0.1] - 2016-07-19
Jul16 milestone.
First release of the Taurus 4 series.
Largely (but not 100%) compatible with taurus 3 series.
For a full log of commits since Jan16, run (in your git repo):
`git log 3.7.0..4.0.1`

### Added
- Quantities (units) support ([TEP14])
- Scheme-agnostic core helpers ([TEP3])
- Model fragment support ([TEP14])
- PyQt new-style signals support (#187)
- support for guiqwt >= 3 (#270)
- New icon API (taurus.qt.qtgui.icon) (#280)
- New `taurusiconcatalog` application (#280)
- Backwards compatibility layer for migration from Taurus 3.x ([TEP14])
- New deprecation API (`Logger.deprecated` and `deprecation_decorator`)
- new unit tests (from ~50 to ~550 unit tests)
- This CHANGELOG.md file

### Changed
- Tango dependency is now **optional** ([TEP3])
- Improved and simplified core API ([TEP3], [TEP14]):
    - Configuration and Attribute Models are now merged into Attribute
    - Taurus model base classes are now scheme-agnostic
    - Improved model name validators (enforcing RFC3986 -compliant model
    names)
- Eval scheme improved (more natural and powerful syntax) ([TEP14])
- Epics scheme plugin improved (and is now installed) (#215)
- Improved installation and distribution scripts (now using setuptools),
(#279)
- Improved testsuite (new `taurustestsuite` command allowing regexp
exclusions)
- Improved Icon Theme support (also for windows)
- taurus.qt now depends on PyQt>=4.8 (before was 4.4)
- taurus.qt.qtgui.extra_nexus now depends on PyMca5 (before was 4.7)
- Updated documentation (#221)

### Deprecated
- Support for old-style signals
- Support for PyQt API1
- Taurus3.x tango-centric API (see [TEP3], [TEP14])
- old-style tango and eval model names (non-RFC3986 compliant)
- taurus.qt.qtgui.resource module
- taurus.external.ordereddict

### Removed
- Deprecated modules (see #234 for details & replacements)
    - taurus.core.utils
    - taurus.core.util.decorator.deprecated
    - taurus.qt.qtgui.table.taurusvaluestable_ro
    - taurus.qt.qtgui.panel.taurusattributechooser
    - taurus.qt.qtgui.panel.taurusconfigbrowser
    - taurus.qt.qtgui.base.taurusqattribute
    - taurus.qt.gtgui.extra_xterm
    - taurus.qt.gtgui.extra_pool
    - taurus.qt.gtgui.extra_macroexecutor
    - taurus.qt.gtgui.extra_sardana
    - taurus.qt.gtgui.gauge
    - taurus.qt.qtgui.image
    - taurus.qt.qtopengl
    - taurus.qt.uic
    - taurus.web
- `spec` scheme plugin (#216)
- `sim` scheme plugin (#217)
- Obsolete `setup.py` commands (`build_resources`, `build_doc`,...)
(#279)
- Icon resource files (but the icons are still available and accessible)
(#280)

### Fixed
- Installation now possible with pip (no need of --egg workaround)
- Documentation generation issues (#288, #273, #221)
- Several bugs and feature-req in TaurusTrend2D
- Issues in TaurusArrayEditor (#260, #261)
- TaurusTrend Export to ASCII issues (#300, #277, #253)
- `resource` scheme plugin (#218)
- windows installer (#278)
- [Many other issues](https://sf.net/p/tauruslib/tickets/milestone/Jul16/)


## [3.7.1] - 2016-03-17
Hotfix for RTD (no library changes)

### Fixed
- RTD issue (bug 273)


## [3.7.0] - 2016-02-17
Jan16 milestone.
For a full log of commits since Jul15, run (in your git repo):
`git log 3.6.0..3.7.0`

### Added
- Support for sqlite DB in Tango (ticket #148)

### Fixed
- Many usability bugs in TaurusTrend2D and other
  guiqwt-based widgets (#238, #240, #244, #247, #251, #258)
- Issues with "export to ASCII" feature of plots
- Issues with PLY optimization (#262)
- "taurus-polling-period" argument works for evaluation
  attributes now too (#249)
- [Many other issues](http://sf.net/p/tauruslib/tickets/milestone/Jan16/)


## [3.6.1] - 2015-10-01
Hotfix for docs (no library changes)

### Fixed
- documentation issues (#181, #191, #194)


## [3.6.0] - 2015-07-22
Jul15 milestone.
For a full log of commits since Jan15, run (in your git repo):
`git log 3.4.0..3.6.0`

### Added
- support of user creation/removal of custom external application
launchers at run time (see #158)
- support of LimaCCDs DS (see #175) and improvements in the codecs

### Changed
- taurusplot/trend uses the same order than the legend for exported
data (see #161)
- Docs: several improvements and made ReadTheDocs-compliant

### Fixed
- Fixed memory leaks in plots/trends (see #171)
- [fixed many bugs in TaurusPlot,  TaurusWheel,  TaurusImageDialog,
and several other places](https://sf.net/p/tauruslib/tickets/milestone/Jul15/)



[keepachangelog.com]: http://keepachangelog.com
[PEP440]: https://www.python.org/dev/peps/pep-0440
[Semantic Versioning]: http://semver.org/
[TEP3]: http://www.taurus-scada.org/tep/?TEP3.md
[TEP13]: http://www.taurus-scada.org/tep/?TEP13.md
[TEP14]: http://www.taurus-scada.org/tep/?TEP14.md
[TEP15]: http://www.taurus-scada.org/tep/?TEP15.md
[TEP17]: http://www.taurus-scada.org/tep/?TEP17.md
[TEP19]: http://www.taurus-scada.org/tep/?TEP19.md
[TEP20]: http://www.taurus-scada.org/tep/?TEP20.md
[Unreleased]: https://gitlab.com/taurus-org/taurus/-/tree/develop
[5.3.2]: https://gitlab.com/taurus-org/taurus/-/tree/5.3.2
[5.3.1]: https://gitlab.com/taurus-org/taurus/-/tree/5.3.1
[5.3.0]: https://gitlab.com/taurus-org/taurus/-/tree/5.3.0
[5.2.4]: https://gitlab.com/taurus-org/taurus/-/tree/5.2.4
[5.2.3]: https://gitlab.com/taurus-org/taurus/-/tree/5.2.3
[5.2.2]: https://gitlab.com/taurus-org/taurus/-/tree/5.2.2
[5.2.1]: https://gitlab.com/taurus-org/taurus/-/tree/5.2.1
[5.2.0]: https://gitlab.com/taurus-org/taurus/-/tree/5.2.0
[5.1.8]: https://gitlab.com/taurus-org/taurus/-/tree/5.1.8
[5.1.7]: https://gitlab.com/taurus-org/taurus/-/tree/5.1.7
[5.1.6]: https://gitlab.com/taurus-org/taurus/-/tree/5.1.6
[5.1.5]: https://gitlab.com/taurus-org/taurus/-/tree/5.1.5
[5.1.4]: https://gitlab.com/taurus-org/taurus/-/tree/5.1.4
[5.0.0.1]: https://gitlab.com/taurus-org/taurus/-/tree/5.0.0.1
[5.0.0]: https://gitlab.com/taurus-org/taurus/-/tree/5.0.0
[4.8.1]: https://gitlab.com/taurus-org/taurus/-/tree/4.8.1
[4.8.0]: https://gitlab.com/taurus-org/taurus/-/tree/4.8.0
[4.7.1.1]: https://gitlab.com/taurus-org/taurus/-/tree/4.7.1.1
[4.7.1]: https://gitlab.com/taurus-org/taurus/-/tree/4.7.1
[4.7.0]: https://gitlab.com/taurus-org/taurus/-/tree/4.7.0
[4.6.0]: https://gitlab.com/taurus-org/taurus/-/tree/4.6.0
[4.5.1]: https://gitlab.com/taurus-org/taurus/-/tree/4.5.1
[4.5.0]: https://gitlab.com/taurus-org/taurus/-/tree/4.5.0
[4.4.0]: https://gitlab.com/taurus-org/taurus/-/tree/4.4.0
[4.3.1]: https://gitlab.com/taurus-org/taurus/-/tree/4.3.1
[4.3.0]: https://gitlab.com/taurus-org/taurus/-/tree/4.3.0
[4.1.1]: https://gitlab.com/taurus-org/taurus/-/tree/4.1.1
[4.1.0]: https://gitlab.com/taurus-org/taurus/-/tree/4.1.0
[4.0.3]: https://gitlab.com/taurus-org/taurus/-/tree/4.0.3
[4.0.1]: https://gitlab.com/taurus-org/taurus/-/tree/4.0.1
[3.7.1]: https://gitlab.com/taurus-org/taurus/-/tree/3.7.1
[3.7.0]: https://gitlab.com/taurus-org/taurus/-/tree/3.7.0
[3.6.0]: https://gitlab.com/taurus-org/taurus/-/tree/3.6.0
[support-3.x]: https://gitlab.com/taurus-org/taurus/-/tree/support-3.x
[taurus_legacy_cli]: https://github.com/taurus-org/taurus_legacy_cli


