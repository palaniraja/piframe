# PiFrame - Custom Digital Photo frame setup for RaspberryPi


## Hardware

  * [Raspberry Pi 2 - Model B](https://www.raspberrypi.org/products/raspberry-pi-2-model-b/)
  * [Waveshare 7 inch IPS LCD](https://www.waveshare.com/wiki/7inch_LCD_for_Pi)

## OS, Services, scripts and packages

  * Raspbian Lite
  * Shared Google Drive with images - (pre-resized to 1024x600 to match display)
  * Kodi - 17.6
  * [Node script](/node-ngdrive) - to downlaod latest files from Google Drive in a cron job
  * [Bash scripts](/bash-scripts) - To handle auto shutdown Raspberry in a cron
  * [Kodi Screensaver addon](kodi-addon) - To display the images downloaded via node script


## TODO

  * Install script to do the following
    * Download/clone the project
    * Install kodi, logger, node
    * Add node to PATH
    * Ask the user to place their privatekey.json in node script folder
    * Update node index.js with the path
    * Setup cron job
    * Inform the user 
        * Path to screensaver.ngdrive.piframe.zip for installation
        * Path for the image download folder _node-script/files_ to setup addon


