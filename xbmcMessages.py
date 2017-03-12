# Copyright (C) 2016 stereodruid(J.G.) Mail: stereodruid@gmail.com
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

import xbmcgui
import sys
import urlparse
 
class PopupWindow(xbmcgui.WindowDialog):
    def __init__(self, image, line1, line2, line3, line4, line5):
        self.addControl(xbmcgui.ControlImage(x=25, y=25, width=150, height=150, filename=image[0]))
        self.addControl(xbmcgui.ControlLabel(x=190, y=25, width=500, height=25, label=line1[0]))
        self.addControl(xbmcgui.ControlLabel(x=190, y=50, width=500, height=25, label=line2[0]))
        self.addControl(xbmcgui.ControlLabel(x=190, y=75, width=500, height=25, label=line3[0]))
        self.addControl(xbmcgui.ControlLabel(x=190, y=100, width=500, height=25, label=line4[0]))
        self.addControl(xbmcgui.ControlLabel(x=190, y=125, width=500, height=25, label=line5[0]))
 
if __name__ == '__main__':
    params = urlparse.parse_qs('&'.join(sys.argv[1:]))
    window = PopupWindow(**params)
    window.show()
    xbmc.sleep(5000)
    window.close()
    del window