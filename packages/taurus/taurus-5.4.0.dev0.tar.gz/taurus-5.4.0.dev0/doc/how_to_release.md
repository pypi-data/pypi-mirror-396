# How to release

This is a guide for taurus release managers: it details the
steps for making an official release, including a checklist
of stuff that should be manually tested.

## The release process

1. During all the development, use the Milestones to keep track of the intended release for each issue
2. Previous to the release deadline, re-check the open issues/MR and update the assignation issues/MR to the release milestone. Request feedback from the devel community.
3. Work to close all the MR/issues remaining open in the milestone. This can be either done in develop or in a release branch called `release-XXX` (where `XXX` is the milestone name, e.g. `Jul17`). If a release branch is used, `develop` is freed to continue with integrations that may not be suitable for this release. On the other hand, it adds a bit more work  because the release-related PRs (which are done against the `release-XXX` branch), may need to be also merged to develop. Note: the `release-XXX` branch *can* live in the taurus-org repo or on a personal fork (in which case you should do step 4.iv **now** to allow other integrators to push directly to it).
4. Create the release branch if it was not done already in the previous step and:
    1. Review and update the CHANGELOG.md if necessary. See [this](http://keepachangelog.com)
    2. Bump version using `bumpversion <major|minor|patch>`  (use [semver](http://semver.org/) criteria to choose amongst `major`, `minor` or `patch`
    3. Create a MR to merge the `release-XXX` against the **`stable`** branch of the taurus-org repo
5. Request reviews in the MR from at least one integrator from each participating institute. The stable branch is protected, so the reviews need to be cleared (or dismissed with an explanation) before the release can be merged.
6. Perform manual tests (see checklist below). You may use the CI artifacts (e.g., from appveyor). To avoid spamming the MR comments with the manual test results, a new issue can be created to report the tests results on each platform (and just use a single check for each platform in the MR).
7. Once all reviews a cleared, update the date of the release in the CHANGELOG.md, run `bumpversion release`, push and merge the MR and tag in stable
8. Check that travis-ci correctly uploaded to PyPI (triggered on tag push).
9. Merge also the  `release-XXX` branch into develop, and bump the version of develop with `bumpversion patch`
10. Complete Gitlab release (upload artifacts, edit text)
11. Create news in www.tango-controls.org
    1. On the News page click on Submit a news and fill up the form (if it doesn't work, try opening in new tab):
       * Title: New Release Of Taurus X.X.X (Jan|JulXX)
       * Ilustration: Taurus official logo (use png)
       * Summary: short summary of the news (do not include the whole changelog here..)
       * Categories: Release
    2. After submitting click on Modify this content text of the area \<\<Content\>\> and provide detailes of the release e.g. changelog.
12. Notify mailing lists (taurus-users@lists.sourceforge.net, taurus-devel@lists.sourceforge.net, info@tango-controls.org)



## Manual test checklist

This is a check-list of manual tests. It is just orientative. Expand it at will.
This list assumes a clean environment with all Taurus dependencies already installed
and access to a Tango system with the TangoTest DS running.

This list can be used as a template to be copy-pasted on an issue linked from the release MR.  

```
# Taurus Manual Testing Guide

## Installation

### Conda environment
- [ ] Create new conda environment: `conda create -n taurus_testing -c conda-forge python=3.10 pytango=9.3 pyqt=5.15`.
- [ ] Activate conda environment: `conda activate taurus_testing`
- [ ] Obtain the source distribution tarball. During the release process it must be done by downloading the artifacts.zip file from the build-pypi-package job of the last successful release branch CI/CD pipeline execution and unzipping it.
- [ ] Install Taurus from the tarball: pip install <source_distribution_tarball>
- [ ] Check installed version of taurus: : `taurus --version`. It should be the same version you can find in [release file](https://gitlab.com/taurus-org/taurus/-/blob/develop/lib/taurus/_release.py).
- [ ] Ensure that the environment variable TANGO_HOST is set to a valid TangoDB with an alive TangoTest device.

### System installation

- [ ] Make sure that your system has Python, PyTango and PyQt installed.
- [ ] Obtain the source distribution tarball. During the release process it must be done by downloading the artifacts.zip file from the build-pypi-package job of the last successful release branch CI/CD pipeline execution and unzipping it.
- [ ] Install Taurus from the tarball: pip install <source_distribution_tarball>
- [ ] Check installed version of taurus: : `taurus --version`. It should be the same version you can find in [release file](https://gitlab.com/taurus-org/taurus/-/blob/develop/lib/taurus/_release.py).
- [ ] Ensure that the environment variable TANGO_HOST is set to a valid TangoDB with an alive TangoTest device.

## taurus demo

- [ ] Execute: `taurus demo`.
- [ ] Test all of the buttons of the taurus demo. All demos should launch correctly.
- [ ] Click on the _Label_ button. Check foreground role, the background role, the prefix, the suffix, the formatter, etc.
    - [ ] In order to test the background role=value, you can use the following attribute: `eval:["FAULT","ON","OFF","ALARM"][randint(4)]`
    - [ ] Use a model with fragment (e.g., `sys/tg_test/1/ampli#rvalue.magnitude`, `eval:Q('1mm')#rvalue.units`, `eval:10*arange(9)#rvalue[3:4]`)
- [ ] Click on the _LCD_ button. Test the foreground roles and the background role.
- [ ] Click on the _Led_ button. Use `eval:False` as a model for testing. Test the colors, ON color, Off color.

## taurus image

- [ ] Execute `taurus image --demo`
- [ ] Test resize the image and pan it using the right button of the mouse.
- [ ] Test recover original view using third mouse button (wheel button).
- [ ] Right click on a white part of the widget. Select _X-Axis and Y-Axis cross section_. Widgets update values.
- [ ] Right click on a white part of the widget. Select _Contrast Adjustment_. Click on the right down second button and adjust contrast level to 2%.
- [ ] Right click on a white part of the widget. Select _Colormap_. Change by another colormap.
- [ ] Right click on a white part of the widget. Select _Change Taurus Model_ by _sys/tg_test/1/double_image_ro_

## taurus trend2d

- [ ] Execute: `taurus --polling-period 333 trend2d --demo`
- [ ] Execute: `taurus --polling-period 333 trend2d -xe --demo`
- [ ] Execute: `taurus --polling-period 333 trend2d --demo -b 10`
  (deactivate auto-scale bottom axis and see that the plot is limited to the
  last 10 values, use the third button of the mouse to move the axis)
- [ ] Test auto-scroll and auto-scale tools (from context menu)

## taurus designer
**Known problem**: taurus designer doesn't include the Taurus widgets when using PyQt 5.15.x in a conda virtual environment. If you are using the environment provided in this guide, you can try to use [this workaround](https://www.taurus-scada.org/devel/designer_tutorial.html#designer-pyqt515-issue) or skip this test. However, if you have another conda envirnoment with 5.12 or you are testing on a system installation, you should be able to perform the tests without problems.
- [ ] Execute `taurus designer`. Create a new MainWindow.
- [ ] Check that the taurus widgets are present in the catalog.
- [ ] Create an empty widget and drag any taurus widgets to it (they should be correctly dropped).
- [ ] Set some taurus-specific properties. Set the model of any attribute to sys/tg_test/1/double_scalar (or any other device and attribute that periodically changes its value).
- [ ] Save the designed GUI as a .ui file.
- [ ] Execute `taurus loadui file.ui`. Check that everything loads as the GUI you created and the widget where you set the model is updating with the changing value.
- [ ] Repeat the previous steps but creating a Widget instead of a MainWindow.

## taurus device
- [ ] Execute: `taurus device sys/tg_test/1`
- [ ] Check that it opens correctly and that the attrs and commands are populated
- [ ] Execute SwitchStates command (see that the state label changes to FAULT and its color to red)
      and then execute the Init command and the label returns to RUNNING (blue)

## taurus panel
- [ ] Execute: `taurus panel`
- [ ] Navigate in the tree and select the TangoTest device (the Attributes an Commands panels should be populated).
- [ ] Execute SwitchStates command to put it in FAULT. Check that the State attribute reflects this change with the LED color.
- [ ] Close the GUI and reopen it. Repeat previous point again so the State is not in FAULT anymore.

## taurus form
More information about the features in the [User's Guide](http://taurus-scada.org/users/ui/index.html)

- [ ] Launch `taurus form sys/tg_test/1/short_scalar`
- Rigth click on attribute name label, go to _'Configuration/All...'_, set range to (-1000, 1000), alarm to (-500, 500) and unit to `mm`. Close the form and relaunch. The new units should be used.
    - [ ] Change the the write value and check that the orange color is used when in warning values.
    - [ ] Check that the write widget does not allow to write values out of range.
- [ ] Check drag and drop of same attribute (_sys/tg_test/1/short_scalar_) onto the same form many times (4 times). It would not crash. Remove all added attributes.
- Right click on an empty part of the widget and test the compact mode:
    - [ ] Switch to compact mode.
    - [ ] Edit form in compact mode.
    - [ ] Doble click in Taurus Value and change attribute value.
    - [ ] Switch to standad mode (noncompact).
- [ ] Right click on attribute name label, go _'Set Formatter'_. Change the formatter (use, e.g. `>>{}<<`). Do this in compact and non compact modes.
- [ ] Rigth click on attribute name label, go to _'Change Label'_. Test changing attribute label.
- [ ] Right click on an empty part of the widget and open _'Modify Contents'_. Add sys/tg_test/1 and all of its attributes. They should all show ok.
- [ ] Test compact mode for all values.
- [ ] Test changing labels for all values.
- [ ] Test changing the formatter for all values (from the context menu of the whole form)
- [ ] Test re-order of values with "Modify contents".
- [ ] Test the different "show" buttons (tables, images, spectra)
- [ ] Right click on attribute double_scalar label, go _'Change Write Widget'_.Change the write widget by a TaurusWheelEdit,
- [ ] Change other read and write widgets.
- [ ] After the previous changes, you should have a quite "custom" form. Right click on an empty part of the widget and got to _'Save current Settings'_. Save widget configuration to "tf.pck". Close the form and reopen it with `taurus form --config tf.pck`
- [ ] Test eval tool launching `taurus form eval:'2 + 2'`

## taurus gui
More information about the features in the [User's Guide](https://taurus-scada.org/users/ui/taurusgui.html).

### Existing taurus gui
**1. General GUI**
- [ ] Launch `taurus gui example01`
- [ ] If you don't have the optional dependency PyMca5 installed, an error will pop. You can either click on Abort, install the dependency and run it again to test the NexusBrowser, or click Ignore and it won't load.
- [ ] Try to move the synoptic panel (syn2). You shoudn't be able to as the view is locked (floating panels are not blocked as they aren't in the main window).
- [ ] Unlock the view (View -> Lock View).
- [ ] Move the panels (including the synoptic panel) and place them in different positions. Place some of them on top of others to create new tabs.
- [ ] Lock the view. Check that you can't move the panels anymore. Unlock the view again.
- [ ] Create a new TaurusForm Panel (Panels -> New Panel... -> TaurusForm) and drag and drop several models from other forms.
- [ ] Test drag&drop from a form to a trend. Check that the new curve was added and it has a different color.
- [ ] Right click on the new panel and click on Modify Contents. Add more models from the Model Chooser.

**2. Perspectives**
- [ ] Save the current perspective with the Save button (next to "Load perspectives").
- [ ] Move some panels, change the label, unit, format... of some Forms and save the new perspective.
- [ ] Load the previous perspective and check that the old configuration is correctly loaded.
 ** Loading the perspective may raise an error saying that some settings may not be restored. When this happens the Manual panel will be empty, but everthing else should load correctly and apply the perspective settings ([!1354](https://gitlab.com/taurus-org/taurus/-/issues/1354)).
- [ ] Load the new perspective and check that the new configuration is correctly loaded.

**3. Synoptic**
- [ ] Test clicking on "example01 synoptic" elements and check that the corresponding panel is raised (the tab changes to make it visible).
- [ ] Test that selecting a panel changes the selection on "example01 synoptic" (the blue square).

**4. Actions menu**
- [ ] Check exporting and importing settings (File -> Export Settings and File -> Import Settings).
- [ ] Check saving current settings (File -> Save Settings). The file should be created in the default path (e.g. ~/.config/Taurus/'EXAMPLE 01.ini').
- [ ] Check the other actions under the different options in the top menu bar: enabling and disabling Taurus Logs, Tool Bars, Full Screen, running external Applications (it will fail if they are not installed), hide and show all Panels, showing the About information...
- [ ] Create a new Panel (you can use the previously created TaurusForm if you didn't make it permanent yet). Click _Export current Panel configuration to XML_. Move the new panel to the Exported section. Export the panel and check that the panel exists in the exported XML file.

### New taurus gui
- [ ] Create a new TaurusGui (call it `foogui`) with `taurus newgui`.
    - In the wizard, set the path, GUI name, and organization.
    - Click Next until you reach the *Panels Editor* step.
    - Click "Add Panel", select TaurusForm (the first widget type), and give it a name (e.g., form1).
    - Click on "Advanced settings".
    - In the new dialog, click on the small button next to the Model textbox to open the Model selector.
    - Select one attribute from the tree (e.g., `sys/tg_test/1/ampli`), add it to the list with the "+" button, and click "Apply".
    - The model should appear in the textbox of the Model field in Advanced Settings.
    - Click "Finish" to close the settings, and then click "Next" to complete all other steps.
- [ ] Install `foogui` with pip (you can install it in a conda or virtualenv).
- [ ] Launch `foogui` using the script that has been installed. You should see the application with the default "Manual" panel showing Taurus documentation and the "form1" you created.
- [ ] Test some features from the [User's Guide](https://taurus-scada.org/users/ui/taurusgui.html). You can test the ones that you commonly use or the strangest ones you can find, you choose.

### Programatic GUI
For programatic GUIs we are going to use some examples of taurus-training. Clone the [taurus-training repo](https://gitlab.com/taurus-org/taurus-training) if you don't have it and open the examples folder.

**1. Declarative GUI (Panel Descriptions)**
- [ ] Launch `taurus gui paneldescriptions.py`.
- [ ] Move the panels and attatch them to the main window so it looks like a real GUI. If you already did it in the past, they may be already placed if you saved the configuration.
- [ ] See the image as reference of how it may look after moving the panels. If you don't have sardana installed the Motor widgets on the Motors panel will show a "Show Device" button:  ![paneldescriptions](https://gitlab.com/taurus-org/taurus-training/-/raw/main/img/paneldescriptions_complex.png?ref_type=heads)

**2. TaurusWidget**
- [ ] Launch `python tauruswidget.py`.
- [ ] Check that it looks like the image. ![tauruswidget](https://gitlab.com/taurus-org/taurus-training/-/raw/main/img/tauruswidget_complex.png?ref_type=heads)

**3. TaurusMainWindow**
- [ ] Launch `python taurusmainwindow.py`.
- [ ] Check that it looks like the image. ![taurusmainwindow](https://gitlab.com/taurus-org/taurus-training/-/raw/main/img/taurusmainwindow_complex.png?ref_type=heads)
- [ ] Check that the "short_scalar" form enables and disables when checking and unchecking the "Expert" checkbox.
- [ ] Click on the "Add random curve" button. Each press should add a curve to the "Random trend" tab.
- [ ] Multi-model support: Check that the power meter (the widget next to the "short_scalar" form) changes in both value and color.

**4. TaurusGUI**
- [ ] Launch `python taurusgui.py`.
- [ ] Check that it looks like the image. ![taurusgui](https://gitlab.com/taurus-org/taurus-training/-/raw/main/img/taurusgui_complex.png?ref_type=heads)
- [ ] Move panels and create new ones repeating the steps in the test _taurus gui -> Existing taurus gui -> 1. General GUI_. You won't be able to click on "Modify Contents" on the existing panels, as their contents are defined in the python file.

## taurus config
- [ ] Open an ini file with taurus config and check that it is loaded correctly. _ini_ files are normally located at /home/$USER/.config/$ORGANIZATION (ej. /home/taurus_user/.config/TAURUS)

## taurus icons catalog
- [ ] Launch `taurus icons`. Several tabs with an array of icons [should be displayed.](http://taurus-scada.org/devel/icon_guide.html#taurus-icon-catalog)
- [ ] Check that tooltips give info on each icon.
- [ ] Click on some icons and check that they give a bigger view of the icon and more info.

## taurus_pyqtgraph

### Installation
- [ ] Using the taurus installation from the above steps install taurus_pyqtgraph with Archiving support. `pip install taurus_pyqtgraph[Archiving]`
- [ ] Check that pyhdbpp is installed along with taurus_pyqtgraph
- [ ] Chech that taurus trend opens without crash (ignore failures on pyhdbpp if it is not configured). `taurus trend`
- [ ] Remove taurus_pyqtgraph and pyhdbpp. `pip uninstall taurus_pyqtgraph pyhdbpp`
- [ ] Using the taurus installation from the above steps install taurus_pyqtgraph. `pip install taurus_pyqtgraph`
- [ ] Check that the version is the same than 0.9.3 `python3 -c "import taurus_pyqtgraph; print(taurus_pyqtgraph.__version__)"`


### taurus_pyqtgraph plot
- [ ] Execute `taurus plot --ls-alt` (check that it lists "tpg")
- [ ] Execute: `taurus plot "eval:Q(rand(333),'mm')" sys/tg_test/1/wave`
- [ ] Check zoom / panning (drag with right / left button), and Use (A) button to auto-range
- [ ] Test inspector tool
  - **-->It works, with the limitations know from taurus-org/taurus_pyqtgraph#48**
- [ ] Move curves between axes by using the plot configuration option in context menu
- [ ] With curves in Y1 and Y2, test zooms and panning on separate axes (drag with right/left on the axis)
- [ ] Test plot configuration dialog
  - **The "Step Mode" combobox in the Line options does not seem to have any effect**
- [ ] Test changing curve titles, click on the context menu option and write {dev.name}/{attr.label}
  - **--> It shows defaultevaluator for the random attribute and the name of the device for the sys/tg_Test attribute along with the attribute.**
  - **--> Try different combinations.**
- [ ] Open the "Model selection" dialog and add/remove/reorder/edit models. Try adding models both for X and Y
- [ ] NOT YET READY <s>Test Save & restore config (change curve properties, zoom, etc & check that everything is restored)</s>

### taurus_pyqtgraph trend
- [ ] Execute `taurus trend --ls-alt` (check that it lists "tpg")
- [ ] Execute: `taurus trend "eval:Q(rand(),'mm')" sys/tg_test/1/ampli`
- [ ] Execute: `taurus trend -xn "eval:Q(rand(),'mm')" sys/tg_test/1/ampli`
  - **It correctly informs that "n" is not supported**
- [ ] Execute: `taurus trend "eval:Q(rand(),'mm')" sys/tg_test_not_exist/1/double_scalar`
  - **Through a warning terminal message it correctly informs that the attribute does not exist or the device is down**
- [ ] Check zoom / panning (drag with right / left button), and Use (A) button to auto-range (located in the bottom left corner)
- [ ] Test inspector tool
- [ ] Move curves between axes by using the plot configuration option in context menu
- [ ] With curves in Y1 and Y2, test zooms and panning on separate axes (drag with right/left on the axis)
- [ ] Test plot configuration dialog
- [ ] Test Forced reading tool
- [ ] Test Fixed Range Scale tool
- [ ] Test autoscale x mode
- [ ] Test Range Axis feature (On the context Menu, X axis)
- [ ] Test Range Axis feature (On the plot configuration tool)
- [ ] Test that Log Mode works (On the context Menu, Y axis)
- [ ] Test Save & restore config Range Axis feature (change curve properties, zoom, etc & check that everything is restored)
- [ ] Test Save & restore config changing the Range Axis feature from the plot configuration tool
  - ** This should only affect the amount of time shown at the trend, not the state from the last save. I.E. If you select a time range of 5 minutes it will save the 5 minutes and reapply it when the settings are loaded, but taking the 5 minutes of the actual time.
  ```