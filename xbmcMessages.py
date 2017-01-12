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