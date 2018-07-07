#!/usr/bin/python


import xbmcaddon
import xbmcgui
import xbmc
import random
import os
from datetime import datetime

# import xbmc, xbmcaddon, xbmcvfs, xbmcgui

ADDON_ID = 'screensaver.ngdrive.piframe'
addon = xbmcaddon.Addon(id=ADDON_ID)
addon_path = (addon.getAddonInfo('path').decode('utf-8'))


animation_duration = [10,20,30,40,50,60,70,80,90,100,110,120][int(addon.getSetting("duration"))] 
image_directory_path = str(addon.getSetting("path")) 

xbmc.log("Addon path : " + str(addon_path), xbmc.LOGERROR)
xbmc.log("Duration received from settings : " + str(animation_duration), xbmc.LOGERROR)
xbmc.log("Path received from settings : " + str(image_directory_path), xbmc.LOGERROR)


# if __name__ == '__main__':
#     log('script started')
#     import gui
#     screensaver_gui = gui.Screensaver('default.xml', CWD, 'default')
#     screensaver_gui.doModal()
#     del screensaver_gui
# log('script stopped')

class Screensaver(xbmcgui.WindowXMLDialog):

    class ExitMonitor(xbmc.Monitor):

        def __init__(self, exit_callback):
            self.exit_callback = exit_callback

        def onScreensaverDeactivated(self):
            self.exit_callback()

    def onInit(self):
        self.log('onInit')
        # buffer = struct.pack('LLLL',0,1,0,0)
        # dev = os.open('/dev/disp', os.O_RDWR)
        # try:
        #     fcntl.ioctl(dev, 0x0C, buffer)
        # finally:
        #     os.close(dev)
        self.exit_monitor = self.ExitMonitor(self.exit)

    def exit(self):
        self.abort_requested = True
        self.exit_monitor = None
        # buffer = struct.pack('LLLL',0,0,0,0)
        # dev = os.open('/dev/disp', os.O_RDWR)
        # try:
        #     fcntl.ioctl(dev, 0x0C, buffer)
        # finally:
        #     os.close(dev)
        self.log('exit')
        self.close()

    def log(self, msg):
        xbmc.log(u'PiFrame: %s' % msg)


if __name__ == '__main__':
    screensaver = Screensaver(
        'screensaver-piframe.xml',
        addon_path,
        'default',
        ''
    )
    # 'screensaver-kaster.xml',
    #     PATH,
    #     'default',
    #     '',
    screensaver.doModal()
    del screensaver
    sys.modules.clear()