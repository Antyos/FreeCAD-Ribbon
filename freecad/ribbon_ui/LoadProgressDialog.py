# *************************************************************************
# *                                                                       *
# * Copyright (c) 2019-2024 Paul Ebbers                                   *
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
import os
import sys

import FreeCADGui as Gui
from PySide.QtCore import Qt

from .Parameters_Ribbon import Parameters
from .resources.ui import ui_ProgressDialog


class LoadDialog(ui_ProgressDialog.Ui_dialog):
    Text = ""

    def __init__(self, Text):
        # Makes "self.on_CreateBOM_clicked" listen to the changed control values instead initial values
        super(LoadDialog, self).__init__()

        # # this will create a Qt widget from our ui file
        self.form = Gui.PySideUic.loadUi(os.path.join(Parameters.UI_LOCATION, "ProgressDialog.ui"))

        # Make sure that the dialog stays on top
        # self.form.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint)
        self.form.setWindowFlags(Qt.WindowType.Tool)
        self.form.setWindowModality(Qt.WindowModality.WindowModal)

        # Get the style from the main window and use it for this form
        mw = Gui.getMainWindow()
        palette = mw.palette()
        self.form.setPalette(palette)
        Style = mw.style()
        self.form.setStyle(Style)

        # Set the text
        self.form.label.setText(Text)

        return

    @classmethod
    def update(self, value):
        self.Text += value

        return


def main(Text):
    # Get the form
    Dialog = LoadDialog(Text).form

    # Show the form
    Dialog.show()

    return
