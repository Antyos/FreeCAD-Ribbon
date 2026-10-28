# *************************************************************************
# *                                                                       *
# * Copyright (c) 2019-2024 Paul Ebbers                                   *
# *                                                                       *
# * This program is free software; you can redistribute it and/or modify  *
# * it under the terms of the GNU Lesser General Public License (LGPL)    *
# * as published by the Free Software Foundation; either version 3 of     *
# * the License, or (at your option) any later version.                   *
# * for detail see the LICENSE text file.                                 *
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

import FreeCADGui as Gui
from PySide.QtCore import Qt

from . import Standard_Functions_Ribbon as StandardFunctions
from .Parameters_Ribbon import Parameters
from .resources.ui import CombinePanel_ui


class LoadDialog(CombinePanel_ui.Ui_Form):
    def __init__(self):

        # Makes "self.on_CreateBOM_clicked" listen to the changed control values instead initial values
        super(LoadDialog, self).__init__()

        # Get the main window from FreeCAD
        mw = Gui.getMainWindow()

        # # this will create a Qt widget from our ui file
        self.form = Gui.PySideUic.loadUi(Parameters.UI_LOCATION / "CombinePanel.ui")

        # Get the address of the repository address
        self.ReproAdress = StandardFunctions.ReturnXML_Value(
            "package.xml", "url", "type", "repository"
        )

        # Make sure that the dialog stays on top
        self.form.raise_()
        self.form.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint)
        # self.form.setWindowFlags(Qt.WindowType.Tool)
        # self.form.setWindowModality(Qt.WindowModality.WindowModal)

        # Position the dialog in front of FreeCAD
        centerPoint = mw.geometry().center()
        Rectangle = self.form.frameGeometry()
        Rectangle.moveCenter(centerPoint)
        self.form.move(Rectangle.topLeft())


def main():
    # Get the form
    Dialog = LoadDialog().form
    # Show the form
    Dialog.show()

    return
