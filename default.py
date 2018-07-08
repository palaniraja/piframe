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

import calendar
import time

import EXIFvfs
from iptcinfovfs import IPTCInfo
from XMPvfs import XMP_Tags



ADDON_ID = 'screensaver.ngdrive.piframe'
addon = xbmcaddon.Addon(id=ADDON_ID)
addon_path = (addon.getAddonInfo('path').decode('utf-8'))


image_directory_path = str(addon.getSetting("path")) 
animation_duration = [2,10,20,30,40,50,60,70,80,90,100,110,120][int(addon.getSetting("duration"))] 
reload_interval = [1,5,10,15,20,30,60][int(addon.getSetting("reloadInterval"))] 

showTime = addon.getSetting("showTime")
showImgCount = addon.getSetting("showImgCount")
showExifDate = addon.getSetting("showExifDate")
showCpuTemp = addon.getSetting("showCpuTemp")
showWeather = addon.getSetting("showWeather")


reload_interval_sec = reload_interval * 60

xbmc.log("Addon path : " + str(addon_path), xbmc.LOGERROR)
xbmc.log("Path received from settings : " + str(image_directory_path), xbmc.LOGERROR)
xbmc.log("Duration received from settings : " + str(animation_duration), xbmc.LOGERROR)
xbmc.log("Reload interval received from settings : " + str(reload_interval), xbmc.LOGERROR)

xbmc.log('Meta settings received: time: %s imgcount: %s exif: %s cputemp:%s weather: %s' % (str(showTime),str(showImgCount),str(showExifDate),str(showCpuTemp),str(showWeather)), xbmc.LOGERROR)
xbmc.log('type of showTime: %s'%str(type(showTime)), xbmc.LOGERROR)



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
        self.lastReloadTime = calendar.timegm(time.gmtime())
        self.exit_monitor = self.ExitMonitor(self.exit)

        # time,we,tot,date,cpu
        self.background = self.getControl(32501)
        self.timeLabel = self.getControl(32502)
        self.weatherLabel = self.getControl(32503)
        self.totalLabel = self.getControl(32504)
        self.exifdateLabel = self.getControl(32505)
        self.cpuLabel = self.getControl(32506)
        self.container = self.getControl(32500)


        self.height = self.container.getHeight()
        self.width = self.container.getWidth()
        # xbmc.log(str(self.height), xbmc.LOGERROR)
        self.log('width:%s height %s'%(str(self.width), str(self.height)))

        self.images = self.loadImages()
        msg = "Total images found: %s" % len(self.images)
        
        self.log(msg)

        if self.images:
            while not self.exit_monitor.abortRequested():
                # rand_index = randint(0, len(self.images)-1)

                # Check whether we need to related the images
                currentEpoch = calendar.timegm(time.gmtime())
                diffEpoch = currentEpoch - self.lastReloadTime

                self.log('lastReloadTime: %s currentEpoch: %s'%(str(self.lastReloadTime), str(currentEpoch)))
                self.log('Diff epoch %s'%str(diffEpoch))

                if diffEpoch >= reload_interval_sec:
                    self.log('time to reload the images')
                    currentImages = self.loadImages()
                    self.log('no. of images after reloading %s'%str(len(currentImages)))
                    if set(self.images) == set(currentImages):
                        self.log('same images set no need to reload')
                    else: 
                        self.log('images changed, so reseting image set with new, reset index to 0')
                        self.images = currentImages
                        self.currentIndex=0
                # else:
                #     imgFile = self.images[rand_index]
                
                rand_index = self.currentIndex
                imgFile = self.images[rand_index]
                # imgFile = '%s%s'%(xbmc.translatePath(image_directory_path), self.images[rand_index])
                
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
                timenow = datetime.now()
                formatedTime = str(self.formatTime(timenow))
                self.log('Dateformat: %s'%formatedTime)


                
                # self.cpuLabel.setLabel(self.images[rand_index])
                
                # EXIF image date
                imgDateTime = ''
                exif = False
                try:
                    xbmcfile = xbmcvfs.File(imgFile)
                    exiftags = EXIFvfs.process_file(xbmcfile, details=False, stop_tag='DateTimeOriginal')
                    if exiftags.has_key('EXIF DateTimeOriginal'):
                        imgDateTime = str(exiftags['EXIF DateTimeOriginal']).decode('utf-8')
                        self.log('imagetime (%s)'%str(imgDateTime))
                        # sometimes exif date returns useless data, probably no date set on camera
                        if imgDateTime == '0000:00:00 00:00:00':
                            imgDateTime = ''
                        else:
                            idate = imgDateTime[:10].split(':')
                            # self.log(idate)
                            imgDateTime = "-".join(idate[::-1]) # reverse list and join 
                            exif = True
                        self.log(imgDateTime)
                except:
                    self.log('exiferror 2')
                    pass



                # Setting content and visibility

                self.background.setImage(imgFile)

                if showTime == "true":
                    self.timeLabel.setLabel('%s'%formatedTime)
                    self.timeLabel.setVisible(True)
                else:
                    self.timeLabel.setVisible(False)

                if showImgCount == "true":
                    self.totalLabel.setLabel('%s of %s'%(str(rand_index+1),str(len(self.images))))
                    self.totalLabel.setVisible(True)
                else:
                    self.totalLabel.setVisible(False)

                if showCpuTemp == "true":
                    self.cpuLabel.setLabel(u'$INFO[System.CPUTemperature]') # $INFO[System.GPUTemperature]
                    self.cpuLabel.setVisible(True)
                else:
                    self.cpuLabel.setVisible(False)


                # self.exifdateLabel.setAlign("Left")
                if showExifDate == "true":
                    self.exifdateLabel.setLabel('%s'%imgDateTime)
                    self.exifdateLabel.setVisible(True)
                else:
                    self.exifdateLabel.setVisible(False)

                if showWeather == "true":
                    self.weatherLabel.setLabel(u'$INFO[System.CPUTemperature]')
                    self.weatherLabel.setAlign("right")
                    self.weatherLabel.setVisible(True)
                else:
                    self.weatherLabel.setVisible(False)
                
                
                # positioning group container

                if rand_index%2 == 0:
                    posX = 50
                else:
                    posX = (self.width-850)

                self.container.setPosition(posX, 0)
                

                # Randomize meta label position to avoid burn-in
                # self.container.setPosition(115, 120)

                # self.cpuLabel.setLabel(f"{datetime.datetime.now():%Y-%m-%d}") #py3
                self.exit_monitor.waitForAbort(animation_duration)

                if (self.currentIndex+1) >= len(self.images):
                    self.currentIndex = 0
                else:     
                    self.currentIndex = self.currentIndex + 1



    def formatTime(self, timestamp):
        if timestamp:
            format = xbmc.getRegion('time').replace(':%S', '').replace('%H%H', '%H')
            return timestamp.strftime(format)
        else:
            return '' 


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
        images = []
        if image_directory_path and xbmcvfs.exists(xbmc.translatePath(image_directory_path)):
            # for image in listdir(image_directory_path):
            #     # self.log(image)
            #     if isfile(join(image_directory_path, image)):
            #         self.images.append(image)
            # # xbmc.log(join(self.images), xbmc.LOGERROR)
            images = filter(os.path.isfile, glob.glob(xbmc.translatePath(image_directory_path) + "*"))
            images.sort(key=lambda x: os.path.getmtime(x), reverse=True)
            # self.log(', '.join(self.images))
            self.lastReloadTime = calendar.timegm(time.gmtime())
            self.log('total image files %s' % str(len(images)))

        return images





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