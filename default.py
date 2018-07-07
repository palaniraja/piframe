#!/usr/bin/python


import xbmcaddon
import xbmcgui
import xbmc
import xbmcvfs

import random
from random import randint, shuffle

from datetime import datetime

import os
from os import listdir
from os.path import isfile, join


# import xbmc, xbmcaddon, xbmcvfs, xbmcgui

ADDON_ID = 'screensaver.ngdrive.piframe'
addon = xbmcaddon.Addon(id=ADDON_ID)
addon_path = (addon.getAddonInfo('path').decode('utf-8'))


animation_duration = [2,10,20,30,40,50,60,70,80,90,100,110,120][int(addon.getSetting("duration"))] 
image_directory_path = str(addon.getSetting("path")) 

xbmc.log("Addon path : " + str(addon_path), xbmc.LOGERROR)
xbmc.log("Duration received from settings : " + str(animation_duration), xbmc.LOGERROR)
xbmc.log("Path received from settings : " + str(image_directory_path), xbmc.LOGERROR)


class Screensaver(xbmcgui.WindowXMLDialog):

    class ExitMonitor(xbmc.Monitor):

        def __init__(self, exit_callback):
            self.exit_callback = exit_callback

        def onScreensaverDeactivated(self):
            self.exit_callback()

    def onInit(self):
        self.log('onInit')
        self.images = []
        self.currentIndex = 0
        self.exit_monitor = self.ExitMonitor(self.exit)
        self.background = self.getControl(32501)
        self.timeLabel = self.getControl(32502)
        self.cpuLabel = self.getControl(32503)
        self.loadImages()
        msg = "Total images found: %s" % len(self.images)
        self.cpuLabel.setLabel(msg)
        self.log(msg)

        if self.images:
            while not self.exit_monitor.abortRequested():
                # rand_index = randint(0, len(self.images)-1)
                rand_index = self.currentIndex

                imgFile = '%s%s'%(xbmc.translatePath(image_directory_path), self.images[rand_index])
                self.log(imgFile)
                self.timeLabel.setLabel(str(rand_index))
                self.cpuLabel.setLabel(self.images[rand_index])
                self.background.setImage(imgFile)
                self.exit_monitor.waitForAbort(animation_duration)
                self.log(str(self.currentIndex))
                self.log(str(len(self.images)))
                if (self.currentIndex+1) >= len(self.images):
                    self.currentIndex = 0
                else:     
                    self.currentIndex = self.currentIndex + 1


    def exit(self):
        self.abort_requested = True
        self.exit_monitor = None
        self.log('exit')
        self.close()

    def log(self, msg):
        xbmc.log(u'PiFrame: %s' % msg, xbmc.LOGERROR)


    def loadImages(self):
        self.log('inside load Images')
        if image_directory_path and xbmcvfs.exists(xbmc.translatePath(image_directory_path)):
            for image in listdir(image_directory_path):
                # self.log(image)
                if isfile(join(image_directory_path, image)):
                    self.images.append(image)
            # xbmc.log(join(self.images), xbmc.LOGERROR)


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