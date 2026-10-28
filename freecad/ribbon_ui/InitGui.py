# *************************************************************************
# *                                                                       *
# * Copyright (c) 2019-2024 Hakan Seven, Geolta, Paul Ebbers              *
# *                                                                       *
# * This program is free software; you can redistribute it and/or modify  *
# * it under the terms of the GNU Lesser General Public License (LGPL)    *
# * as published by the Free Software Foundation; either version 3 of     *
# * the License, or (at your option) any later version.                   *
# * for detail see the LICENCE text file.                                 *
# *                                                                       *
# * This program is distributed in the hope that it will be useful,       *
# * but WITHOUT ANY WARRANTY; without even the implied warranty of        *
# * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
# * GNU Library General Public License for more details.                  *
# *                                                                       *
# * You should have received a copy of the GNU Library General Public     *
# * License along with this program; if not, write to the Free Software   *
# * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  *
# * USA                                                                   *
# *                                                                       *
# *************************************************************************
import logging
import os
import shutil
import sys
from pathlib import Path

import FreeCADGui as Gui
from FreeCAD.Qt import translate
from PySide.QtCore import Qt
from PySide.QtWidgets import QApplication, QDockWidget

import FreeCAD as App

from . import FCBinding
from .Parameters_Ribbon import Parameters

# Set the logger levels to avoid extra output in the report panel
logging.getLogger("urllib3").setLevel(logging.INFO)


CurrentStructureVersion = 2


def QT_TRANSLATE_NOOP(context, text):
    return text


# Get the resources
ConfigDirectory = Parameters.CONFIG_DIR


# Set the wait cursor
QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)

# Move the data files to the new location for fixing issue with the new addon manager
# Function to move the data files out the addon folder to fix issue with the new addon manager
#
# Create the new folder for the data
ConfigDirectory.mkdir(parents=True, exist_ok=True)

SourceDir = Path(__file__).parent.parent.parent

# Move the files if present
if Parameters.RIBBON_STRUCTURE_JSON == SourceDir / "RibbonStructure.json":
    try:
        # Update the paths for the ribbon structure and the backup folder
        Parameters.RIBBON_STRUCTURE_JSON = ConfigDirectory / "RibbonStructure.json"
        # Copy the data files if they exits
        if (SourceDir / "RibbonStructure.json").exists():
            shutil.copyfile(
                SourceDir / "RibbonStructure.json",
                ConfigDirectory / "RibbonStructure.json",
            )
        if (SourceDir / "RibbonDataFile.dat").exists():
            shutil.copyfile(
                SourceDir / "RibbonDataFile.dat",
                ConfigDirectory / "RibbonDataFile.dat",
            )
        if (SourceDir / "RibbonDataFile2.dat").exists():
            shutil.copyfile(
                SourceDir / "RibbonDataFile2.dat",
                ConfigDirectory / "RibbonDataFile2.dat",
            )
    except Exception as e:
        print(e)
        pass

if Parameters.BACKUP_LOCATION == SourceDir / "BackupFolder":
    try:
        Parameters.BACKUP_LOCATION = ConfigDirectory / "Backups"
        if (SourceDir / "Backups").exists():
            shutil.copytree(SourceDir / "Backups", ConfigDirectory / "Backups")
    except Exception:
        pass

# check if there is a "RibbonStructure.json". if not create one
ribbon_file = ConfigDirectory / "RibbonStructure.json"
default_ribbon_file = ConfigDirectory / "RibbonStructure_default.json"
source = SourceDir / "CreateStructure.txt"
source_default = SourceDir / "CreateStructure.txt"

# if not, copy and rename
if not ribbon_file.exists():
    shutil.copy(source, ribbon_file)

# check if file exits
fileExists = os.path.isfile(default_ribbon_file)
# if not, copy and rename
if not default_ribbon_file.exists() or Parameters.RibbonStructureVersion >= CurrentStructureVersion:
    shutil.copy(source_default, default_ribbon_file)
    Parameters.RibbonStructureVersion = CurrentStructureVersion

# Make sure that the parameter for the ribbon structure is correct
if not Parameters.RIBBON_STRUCTURE_JSON.exists():
    Parameters.RIBBON_STRUCTURE_JSON = ConfigDirectory / "RibbonStructure.json"

# Make sure that the parameter for the backup folder is correct
if not Parameters.BACKUP_LOCATION.exists():
    Parameters.BACKUP_LOCATION = ConfigDirectory / "Backups"

# remove the test workbench
try:
    Gui.removeWorkbench("TestWorkbench")
except Exception:
    pass

# Get the overlay settings
preferences_DockWindows = App.ParamGet("User parameter:BaseApp/Preferences/DockWindows")
if preferences_DockWindows.GetBool("ActivateOverlay"):
    Parameters.USE_OVERLAY = True
    if Parameters.OVERLAYSTATE == 2 and Parameters.STORED_OVERLAY_STATE:
        OverlayParam_Top = App.ParamGet("User parameter:BaseApp/MainWindow/DockWindows/OverlayTop")
        # Set the new string in parameters
        OverlayParam_Top.SetString("Widgets", Parameters.STORED_OVERLAY_STATE)

# Check if a reset is present for the overlay function
if (SourceDir / "OVERLAY_DISABLED").exists():
    print("Overlay function is disabled by RibbonUI")
    preferences_DockWindows.SetBool("ActivateOverlay", False)
    Parameters.USE_OVERLAY = False
try:
    print(translate("FreeCAD Ribbon", "Activating Ribbon UI..."))
    mw = Gui.getMainWindow()

    if not Parameters.HIDE_TITLEBAR_FC:
        mw.setWindowFlags(Qt.WindowType.WindowFullscreenButtonHint)
        mw.workbenchActivated.connect(FCBinding.run)

    # Hide the Titlebar of FreeCAD
    else:
        # make a customized toolbar and hide all the buttons.
        # This works better than a frameless window
        mw.setWindowFlags(Qt.WindowType.CustomizeWindowHint)
        mw.setWindowFlag(Qt.WindowType.WindowMinMaxButtonsHint, False)
        mw.setWindowFlag(Qt.WindowType.WindowCloseButtonHint, False)
        # Connect the ribbon when the workbench is activated
        mw.workbenchActivated.connect(FCBinding.run)
        # Normally after setting the window frameless you show the window with mw.show()
        # This is now done in FCBinding with an eventfilter class
        print(translate("FreeCAD Ribbon", "Ribbon UI: FreeCAD loaded without titlebar"))

    # Set the mainwindow to the last state
    if Parameters.MainWindowState == "Maximized":
        mw.showMaximized()

    # Restore the cursor
    QApplication.restoreOverrideCursor()
    QApplication.restoreOverrideCursor()

    if (ribbon := mw.findChild(QDockWidget, "Ribbon")) is not None:
        ribbon.show()

except Exception as e:
    # raise e
    if Parameters.DEBUG_MODE:
        print(f"{e.with_traceback(e.__traceback__)}, 0")

Gui.addLanguagePath(str(SourceDir / "translations"))
Gui.updateLocale()
