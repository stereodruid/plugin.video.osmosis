# Original-Author: Roman Miroshnychenko aka Roman V.M. (https://github.com/romanvm/pyxbmct.demo)
# Licence: GPL v.3 <http://www.gnu.org/licenses/gpl.html>
# This file is part of OSMOSIS.
#
# OSMOSIS is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# OSMOSIS is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

import os

import pyxbmct.addonwindow as pyxbmct
import xbmcaddon
import xbmcgui


_addon = xbmcaddon.Addon()
_path = _addon.getAddonInfo("path")
_check_icon = os.path.join(_path, "iconRemove.png") # Don't decode _path to utf-8!!!


class MultiChoiceDialog(pyxbmct.AddonDialogWindow):
    def __init__(self, title="", items=None):
        super(MultiChoiceDialog, self).__init__(title)
        self.setGeometry(600, 400, 4, 4)
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
        self.placeControl(self.listing, 0,1, rowspan=4, columnspan=4)
        self.ok_button = pyxbmct.Button("Delete")
        self.placeControl(self.ok_button, 0, 0)
        self.cancel_button = pyxbmct.Button("Cancel")
        self.placeControl(self.cancel_button, 1, 0)

    def connect_controls(self):
        self.connect(self.listing, self.check_uncheck)
        self.connect(self.ok_button, self.ok)
        self.connect(self.cancel_button, self.close)

    def set_navigation(self):
        self.listing.controlUp(self.ok_button)
        self.listing.controlDown(self.ok_button)
        self.ok_button.setNavigation(self.listing, self.listing, self.cancel_button, self.cancel_button)
        self.cancel_button.setNavigation(self.listing, self.listing, self.ok_button, self.ok_button)
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
