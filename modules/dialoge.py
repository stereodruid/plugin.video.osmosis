# Copyright (C) 2016 stereodruid(J.G.)
#
#
# This file is part of OSMOSIS
#
# OSMOSIS is free software: you can redistribute it. 
# You can modify it for private use only.
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# OSMOSIS is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
import os
import sys

import pyxbmct.addonwindow as pyxbmct
import xbmcaddon
import xbmcgui
import urlparse


_addon = xbmcaddon.Addon()
_path = _addon.getAddonInfo("path")
_check_icon = os.path.join(_path, "iconRemove.png") # Don't decode _path to utf-8!!!


class MultiChoiceDialog(pyxbmct.AddonDialogWindow):
    def __init__(self, title="", items=None):
        super(MultiChoiceDialog, self).__init__(title)
        self.setGeometry(800, 600, 4, 4)
        self.selected = []
        self.selectedLabels = []
        self.set_controls()
        self.connect_controls()
        self.listing.addItems(items or [])
        self.set_navigation()

    def set_controls(self):
        # Text label
        label = pyxbmct.Label('Note: You can select mulltiple items! To delete click on  "delete"')
        self.placeControl(label, 4, 0,columnspan=4)
        self.listing = pyxbmct.List(_imageWidth=20)
        self.placeControl(self.listing, 0,1, rowspan=4, columnspan=3)
        self.ok_button = pyxbmct.Button("Delete")
        self.placeControl(self.ok_button, 0,0)
        self.cancel_button = pyxbmct.Button("Cancel")
        self.placeControl(self.cancel_button, 1,0)

    def connect_controls(self):
        self.connect(self.listing, self.check_uncheck)
        self.connect(self.ok_button, self.ok)
        self.connect(self.cancel_button, self.close)

    def set_navigation(self):
        self.listing.setNavigation(self.listing, self.listing, self.ok_button, self.ok_button)
        self.ok_button.setNavigation(self.cancel_button, self.cancel_button, self.listing, self.listing)
        self.cancel_button.setNavigation(self.ok_button, self.ok_button, self.listing, self.listing)
        if self.listing.size():
            self.setFocus(self.listing)
        else:
            self.setFocus(self.cancel_button)

    def check_uncheck(self):
        list_item = self.listing.getSelectedItem()
        if list_item.getLabel2() == "checked":
            list_item.setIconImage("")
            list_item.setLabel2("unchecked")
        else:
            list_item.setIconImage(_check_icon)
            list_item.setLabel2("checked")

    def ok(self):
        self.selected = [index for index in xrange(self.listing.size())
                                if self.listing.getListItem(index).getLabel2() == "checked"]
        for i in self.selected:
            self.selectedLabels.append(self.listing.getListItem(i).getLabel())
        super(MultiChoiceDialog, self).close()

    def close(self):
        self.selected = []
        self.selectedLabels = []
        super(MultiChoiceDialog, self).close()

def createPopupWindow(jsonMessageParams, popTime):
        jsonMessageParams = urlparse.parse_qs('&'.join(sys.argv[1:]))
        window = PopupWindow(**jsonMessageParams)
        window.show()
        xbmc.sleep(popTime)
        window.close()
        del window

def PopupWindow(elements):
    # Create a window instance.
    window = pyxbmct.AddonDialogWindow(elements[0])
    # Set window width, height and grid resolution.
    window.setGeometry(700, 250, 2, 1)
    textbox = pyxbmct.TextBox(textColor='0xFFFFFFFF')
    
    window.placeControl(textbox, 0, 0,2,1)
    textbox.setText(elements[1] + " " +  elements[2]+ " " +  elements[3])
#     label = pyxbmct.Label(elements[1], alignment=pyxbmct.ALIGN_LEFT)
#     label2 = pyxbmct.Label(elements[2], alignment=pyxbmct.ALIGN_LEFT)
#     label3 = pyxbmct.Label(elements[3], alignment=pyxbmct.ALIGN_LEFT)
#     window.placeControl(label, 0, 0, columnspan=1)
#     window.placeControl(label2, 1, 0, columnspan=1)
#     window.placeControl(label3, 2, 0, columnspan=1)
    # Create a button.
    button = pyxbmct.Button('Close')
    # Place the button on the window grid.
    window.placeControl(button, 2, 0)
    # Set initial focus on the button.
    window.setFocus(button)
    # Connect the button to a function.
    window.connect(button, window.close)
    # Connect a key action to a function.
    window.connect(pyxbmct.ACTION_NAV_BACK, window.close)
    # Show the created window.
    window.doModal()
    # Delete the window instance when it is no longer used.
    del window 

class MyWindow(pyxbmct.AddonDialogWindow):

    def __init__(self, title=''):
        # You need to call base class' constructor.
        super(MyWindow, self).__init__(title)
        # Set the window width, height and the grid resolution: 2 rows, 3 columns.
        self.setGeometry(350, 150, 2, 3)
        # Create a text label.
        label = pyxbmct.Label('This is a PyXBMCt window.', alignment=pyxbmct.ALIGN_CENTER)
        # Place the label on the window grid.
        self.placeControl(label, 0, 0, columnspan=3)
        # Create a button.
        button = pyxbmct.Button('Close')
        # Place the button on the window grid.
        self.placeControl(button, 1, 1)
        # Set initial focus on the button.
        self.setFocus(button)
        # Connect the button to a function.
        self.connect(button, self.close)
        # Connect a key action to a function.
        self.connect(pyxbmct.ACTION_NAV_BACK, self.close)
