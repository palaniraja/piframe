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

import glob
import subprocess
import commands
import cmd

# import EXIFvfs

# import xbmc, xbmcaddon, xbmcvfs, xbmcgui

ADDON_ID = 'screensaver.ngdrive.piframe'
addon = xbmcaddon.Addon(id=ADDON_ID)
addon_path = (addon.getAddonInfo('path').decode('utf-8'))


animation_duration = [2,10,20,30,40,50,60,70,80,90,100,110,120][int(addon.getSetting("duration"))] 
image_directory_path = str(addon.getSetting("path")) 

xbmc.log("Addon path : " + str(addon_path), xbmc.LOGERROR)
xbmc.log("Duration received from settings : " + str(animation_duration), xbmc.LOGERROR)
xbmc.log("Path received from settings : " + str(image_directory_path), xbmc.LOGERROR)


# https://stackoverflow.com/a/13151299/240255
from threading import Timer

class RepeatedTimer(object):
    def __init__(self, interval, function, *args, **kwargs):
        self._timer     = None
        self.interval   = interval
        self.function   = function
        self.args       = args
        self.kwargs     = kwargs
        self.is_running = False
        self.start()

    def _run(self):
        self.is_running = False
        self.start()
        self.function(*self.args, **self.kwargs)

    def start(self):
        if not self.is_running:
            self._timer = Timer(self.interval, self._run)
            self._timer.start()
            self.is_running = True

    def stop(self):
        self._timer.cancel()
        self.is_running = False



class Screensaver(xbmcgui.WindowXMLDialog):

    class ExitMonitor(xbmc.Monitor):

        def __init__(self, exit_callback):
            self.exit_callback = exit_callback

        def onScreensaverDeactivated(self):
            self.exit_callback()

    class ReloadMonitor(xbmc.Monitor):
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
                # imgFile = '%s%s'%(xbmc.translatePath(image_directory_path), self.images[rand_index])
                imgFile = self.images[rand_index]
                # self.log(imgFile)

                # /opt/vc/bin/vcgencmd measure_temp | cut -d "=" -f2 | cut -d "'" -f1`
                # vcgencmd measure_temp | cut -d "=" -f2
                # cmdToRun = 'ls -l %s | wc -c'%xbmc.translatePath(image_directory_path)
                
                cmdToRun = 'date'
                self.log('command to run (%s)'%cmdToRun)
                # self.log(cmdToRun)
                result = commands.getstatusoutput(cmdToRun)
                self.log('command output: %s'%str(result[1]))

                # DATEFORMAT = xbmc.getRegion('dateshort')

                
                # self.log(self.run_command(cmdToRun))


                self.timeLabel.setLabel(str(rand_index))
                # self.cpuLabel.setLabel(self.images[rand_index])
                # $INFO[System.GPUTemperature]
                self.cpuLabel.setLabel(u'%s $INFO[System.CPUTemperature]'% str(result[1]))
                # self.cpuLabel.setLabel(f"{datetime.datetime.now():%Y-%m-%d}") #py3
                self.background.setImage(imgFile)
                self.exit_monitor.waitForAbort(animation_duration)

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
        xbmc.log('PiFrame: %s' % msg, xbmc.LOGERROR)

    def run_command(self, cmd):
        p = subprocess.Popen(["echo", "hello world"], stdout=subprocess.PIPE)
        return p.communicate()

    def loadImages(self):
        self.log('inside load Images')
        if image_directory_path and xbmcvfs.exists(xbmc.translatePath(image_directory_path)):
            # for image in listdir(image_directory_path):
            #     # self.log(image)
            #     if isfile(join(image_directory_path, image)):
            #         self.images.append(image)
            # # xbmc.log(join(self.images), xbmc.LOGERROR)

            self.images = filter(os.path.isfile, glob.glob(xbmc.translatePath(image_directory_path) + "*"))
            self.images.sort(key=lambda x: os.path.getmtime(x), reverse=True)
            # self.log(', '.join(self.images))

            self.log('total image files %s' % str(len(self.images)))





if __name__ == '__main__':
    screensaver = Screensaver(
        'screensaver-piframe.xml',
        addon_path,
        'default',
        ''
    )
    screensaver.doModal()
    del screensaver
    sys.modules.clear()