#!/usr/bin/env python3
#Imports python modules
import sys
import os
import shutil
import argparse
import subprocess
import time
import getpass
import configparser
#import zipfile #For upcoming auto-update feature
#import tarfile #For upcoming auto-update feature
try:
    import bluetooth
    from bluetooth import *
    import bluetooth._bluetooth as bt
except:
    print ("Cannot import the bluetooth modules!")
    print ("Please run install.sh!")
    sys.exit(1)
#Gets OS path for upcoming auto-update feature
dir_path = os.path.dirname(os.path.realpath(__file__))
print(dir_path)

#Detects python version
if (sys.version_info > (3, 0)):
    print("Python 3 has been detected you may continue\n")
else:
    sys.exit("Python 2 has been detected please run in Python3!")

#Things for imports
parser = argparse.ArgumentParser()
config = configparser.ConfigParser()
from distutils.spawn import find_executable

#Reads configuration file
config.read("config.ini")

#Variables
USER = getpass.getuser() #For the thank you message
GET_DEVICEADDR = 1 #For setup when no config is found
SELECT_ENV = 1 #For setup when no config is found

#Checks for a new version, i've tried to make it automatically install but due to many problems it had to be postponed
VERSION = config.get("VERSION", "version")
UPDATE = input("Would you like to check for an update? [Y/N]")
UPDATE = UPDATE.upper()
if UPDATE == "Y":
    print("Downloading Update.ini from ecloud...")
    process = subprocess.Popen(["wget", "-q", "-O", "Update.ini", "https://ecloud.zapto.org/index.php/s/AKeEkGxC2nww2KX/download"], shell=False, stdout=subprocess.PIPE)
    process.wait()
    print("Done!")
    config.read("Update.ini")
    NEWVERSION = config.get("NEWVERSION", "newversion")
    if NEWVERSION > VERSION:
        config.clear()
        print("New version found:", NEWVERSION)
    elif NEWVERSION < VERSION:
        config.clear()
        print("Version installed is higher than the version specified in update config")
    elif NEWVERSION == VERSION:
        config.clear()
        print("Latest version installed")
    else:
        config.clear()
        print("If you see this message then something has probably gone wrong :/")
elif UPDATE == "N":
    print("Not checking for updates!")
else:
    print("Unknown response")
config.read("config.ini")

#Loads the options from the config and loads them into a local variable
if config.has_option("DESKTOP", "env"):
    OPTION = config.get("DESKTOP", "env")
    print("Desktop Environment found in config, using the one specified")
    SELECT_ENV = 0
    ENV = config.get("DESKTOP", "env")
if config.has_option("DEVICEADDR", "deviceaddr"):
    OPTION = config.get("DEVICEADDR", "deviceaddr")
    print("Device Adress found in config, using the one specified \n")
    GET_DEVICEADDR = 0
    DEVICEADDR = config.get("DEVICEADDR", "deviceaddr")
AVAILDE = input("Would you like to see the available desktop environments? [Y/N]")
AVAILDE = AVAILDE.upper()
if AVAILDE == "Y":
        gnome_screensaver = {'GNOME': 'gnome-screensaver'}
        for gnome_env in gnome_screensaver:
            if find_executable(gnome_screensaver[gnome_env]):
                print("GNOME has been found")
            else:
                print("GNOME has not found")
        mate_screensaver = {'MATE': 'mate-screensaver-command'}
        for mate_env in mate_screensaver:
            if find_executable(mate_screensaver[mate_env]):
                print("MATE has been found")
            else:
                print("MATE has not been found")
        x_screensaver = {'XSCREENSAVER': 'xscreensaver'}
        for x_env in x_screensaver:
            if find_executable(x_screensaver[x_env]):
                print("XSCREENSAVER has been found")
            else:
                print("XSCREENSAVER has not been found")
        print("\n")
elif AVAILDE == "N":
    print("Not displaying the available desktop environments")
#Select Desktop Environment menu
if SELECT_ENV == 1:
    #Detects if these desktop evironments are available
    ENV = input("""Please Enter your Desktop Environment can be:
    "LOGINCTL" (Recommended) (Don't use sudo)
    "KDE" (Doesn"t work on older versions)
    "GNOME"
    "XSCREENSAVER"
    "MATE"
    "CINNAMON"
    """)
    ENV = ENV.upper()
    if ENV == "LOGINCTL":
        print(ENV,"has been selected")
    elif ENV == "KDE":
        print(ENV,"has been selected")
    elif ENV == "GNOME":
        print(ENV,"has been selected")
    elif ENV == "XSCREENSAVER":
        print(ENV,"has been selected")
    elif ENV == "MATE":
        print(ENV,"has been selected")
    elif ENV == "CINNAMON":
        print(ENV,"has been selected")
    else:
        sys.exit("Unidentified Environment exiting")
    config["DESKTOP"] = {"ENV": (ENV)}
    with open("config.ini", "w") as configfile:
        config.write(configfile)

elif SELECT_ENV == 0:
    print ("Config found using specified desktop environment")
    print (ENV)

DEBUG = input("Would you like to activate debug mode? [Y/N]")#Debug mode prints extra information of what"s going on
DEBUG = DEBUG.upper()
if DEBUG == "Y":
	print("DEBUG is active")
elif DEBUG == "N":
	print("DEBUG is not active")
else:
	sys.exit("Unknown option")

#Code containing thank you message and device detection
print ("Thank you for using Bluetooth-Unlock",VERSION ,USER ,"\n")
if GET_DEVICEADDR == 1:
    print ("Searching for nearby devices...\n")
    nearby = discover_devices(lookup_names = True)
    print (nearby,"\n")
    DEVICEADDR = input("Enter Bluetooth Adress of the device (e.g AA:BB:CC:DD:EE:FF): ")#Asks for bluetooth device address
    config["DEVICEADDR"] = {"DEVICEADDR": (DEVICEADDR)}
    with open("config.ini", "w") as configfile:
        config.write(configfile)
elif GET_DEVICEADDR == 0:
    print ("Device Address is", DEVICEADDR)
#Prints information
if DEBUG == "Y":
    print ("This is the sections found in config.ini")
    print (config.sections())
    print ("Desktop Environment is", ENV)
    print ("Device Address is",DEVICEADDR)
    print("Thank you to these contributors: jose1711, maaudrana")
    print("jose1711 has improved the code of this project")
    print("maaudrana is making a logo for this project")
    print("Thanks to all of them :)")

#Variables for Main code
CHECKINTERVAL = 3 # device pinged at this interval (seconds) when screen is unlocked
CHECKREPEAT = 2  # device must be unreachable this many times to lock
mode = "unlocked"

#Main code for Bluetooth-Unlock
if __name__ == "__main__":
    while True:
        tries = 0
        while tries < CHECKREPEAT:
            process = subprocess.Popen(["sudo", "/usr/bin/l2ping", DEVICEADDR, "-t", "1", "-c", "1"], shell=False, stdout=subprocess.PIPE)
            process.wait()
            if process.returncode == 0:
                print("ping OK")
                break
            print("ping response code: %d" % (process.returncode))
            time.sleep(1)
            tries = tries + 1

        if process.returncode == 0 and mode == "locked":
            mode = "unlocked"
            if ENV == "LOGINCTL":
                subprocess.Popen(["loginctl", "unlock-session"], shell=False, stdout=subprocess.PIPE)
            elif ENV == "KDE":
                subprocess.Popen(["loginctl", "unlock-session"], shell=False, stdout=subprocess.PIPE)
            elif ENV == "GNOME":
                subprocess.Popen(["gnome-screensaver-command", "-d"], shell=False, stdout=subprocess.PIPE)
            elif ENV == "XSCREENSAVER":
                subprocess.Popen(["pkill", "xscreensaver"], shell=False, stdout=subprocess.PIPE)
            elif ENV == "MATE":
                subprocess.Popen(["mate-screensaver-command", "-d"], shell=False, stdout=subprocess.PIPE)
            elif ENV == "CINNAMON":
                subprocess.Popen(["cinnamon-screensaver-command", "-d"], shell=False, stdout=subprocess.PIPE)

        if process.returncode == 1 and mode == "unlocked":
            mode = "locked"
            if ENV == "LOGINCTL":
                subprocess.Popen(["loginctl", "lock-session"], shell=False, stdout=subprocess.PIPE)
            elif ENV == "KDE":
                subprocess.Popen(["loginctl", "lock-session"], shell=False, stdout=subprocess.PIPE)
            elif ENV == "GNOME":
                subprocess.Popen(["gnome-screensaver-command", "-l"], shell=False, stdout=subprocess.PIPE)
            elif ENV == "XSCREENSAVER":
                subprocess.Popen(["xscreensaver-command", "-lock"], shell=False, stdout=subprocess.PIPE)
            elif ENV == "MATE":
                subprocess.Popen(["mate-screensaver-command", "-l"], shell=False, stdout=subprocess.PIPE)
            elif ENV == "CINNAMON":
                subprocess.Popen(["cinnamon-screensaver-command", "-l"], shell=False, stdout=subprocess.PIPE)

        if mode == "locked":
            time.sleep(1)
        else:
            time.sleep(CHECKINTERVAL)
