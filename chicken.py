#!/usr/bin/python

# Control program for chicken coop door 

##################################################################################
# MIT License
# 
# Copyright (c) 2018 Jason Shaw
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# 
##################################################################################
#
#
# Updated 9/7/18
#	- Added offsets to allow open/close triggering to be adjusted by X minutes
#	see the -O and -C options
#	- Fixed bug with serviceDay calculation

import ephem
import datetime
import time
import logging
import os.path
import os
import RPi.GPIO as GPIO
import argparse


def setupLogging(name):
	# To Do: move format, file name, etc to a logging.ini file 
	# include time, function name, level, and message
	formatter = logging.Formatter(fmt='%(asctime)s %(levelname)-8s %(funcName)-15s %(message)s',datefmt='%b %d %H:%M:%S')
	handler = logging.FileHandler('/var/log/chicken.log')
	handler.setFormatter(formatter)
	logger = logging.getLogger(name)
	logger.setLevel(logging.INFO)
	if (args.debug): 	# if -d passed in,change logging level from INFO to DEBUG
		logger.setLevel(logging.DEBUG)
	logger.addHandler(handler)

	return logger


def getTimes(sun):
	# calculate previous and next sunrise and sunset times
	r1 = home.previous_rising(sun)
	r2 = home.next_rising(sun)
	s1 = home.previous_setting(sun)
	s2 = home.next_setting(sun)

	pSunrise_base = ephem.Date(ephem.localtime(r1))
	nSunrise_base = ephem.Date(ephem.localtime(r2))
	pSunset_base = ephem.Date(ephem.localtime(s1))
	nSunset_base = ephem.Date(ephem.localtime(s2))
	# 9/7 - updated dates to include offset
	pSunrise = ephem.Date(ephem.localtime(ephem.Date(r1 - o_offset * ephem.minute)))
	nSunrise = ephem.Date(ephem.localtime(ephem.Date(r2 - o_offset * ephem.minute)))
	pSunset = ephem.Date(ephem.localtime(ephem.Date(s1 + c_offset * ephem.minute)))
	nSunset = ephem.Date(ephem.localtime(ephem.Date(s2 + c_offset * ephem.minute)))
	tNow = ephem.Date(ephem.localtime(home.date))

	# debug
	logger.debug("pSunrise_base  %s", pSunrise_base)
	logger.debug("pSunset_base  %s", pSunset_base)
	logger.debug("nSunrise_base  %s", nSunrise_base)
	logger.debug("nSunset_base  %s", nSunset_base)
	logger.debug("pSunrise  %s", pSunrise)
	logger.debug("pSunset  %s", pSunset)
	logger.debug("nSunrise  %s", nSunrise)
	logger.debug("nSunset  %s", nSunset)
	logger.debug("tNow  %s", tNow)

	return tNow, pSunrise, pSunset, nSunrise, nSunset

def getAction(verb):
# figure out whether we should do anything or if it has already been done
	# marker for state files, valid from sunrise to sunrise
	#serviceDay = str(pSunrise.tuple()[3]) + "-" + str(pSunrise.tuple()[2])
	serviceDay = str(pSunrise.tuple()[1]) + "-" + str(pSunrise.tuple()[2])
	logger.debug("serviceDay is %s",serviceDay)

	# state files we store the MM-DD we last did action so we
	# don't constantly do it (i.e. close a relay every 5 min)
	if (verb == "open"):
		p1='/tmp/.openChicken'
		p2='/tmp/.closeChicken'
	elif(verb == "close"):
		p2='/tmp/.openChicken'
		p1='/tmp/.closeChicken'
	else:
		return 0
		
	if (os.path.isfile(p1)):
		with open(p1,"r") as f:
			prevRun = f.read().rstrip()
			f.close()
			if (prevRun == serviceDay):
				# if we already did this action serviceDay, don't do it again
				logger.info("NO ACTION: prevRun %s ==  serviceDay %s, verb %s", prevRun, serviceDay, verb)
				return 0
			else:
				# the file has an old date in it so we do the action just in case the program
				# bailed earlier
				logger.info("ACTION: prevRun %s != serviceDay %s, %s door", prevRun, serviceDay, verb)
				f = open(p1,"w")
				f.write(serviceDay)
	else:
		# the state file is not present, so assume we have not done
		# action and need to do it
		logger.info("ACTION: %s state file not found, %s door", verb, verb)
		f = open(p1,"w")
		f.write(serviceDay)

	# remove opposite state file so that when the opposite action is tried later
	# we hit the block of code directly above and do the action
	if (os.path.isfile(p2)):
		try:
			os.remove(p2)
		except OSError:
			logger.info("could not remove %s", p2)
	
	return verb

def setPins(operation,runtime):
# set the pins to the right value based on the action
	# pin numbering scheme and setup
	GPIO.setmode(GPIO.BCM) # Broadcom pin-numbering scheme
	GPIO.setup(closePin, GPIO.OUT) # PWM pin set as output
	GPIO.setup(openPin, GPIO.OUT) # PWM pin set as output

        if operation == 'close':
                closePinState = GPIO.HIGH
                openPinState = GPIO.LOW
        elif operation == 'open':
                closePinState = GPIO.LOW
                openPinState = GPIO.HIGH

	# write the pins
        GPIO.output(closePin, closePinState)
        GPIO.output(openPin, openPinState)

	# wait for the motor
        time.sleep(runtime)

	# cleanup and reset pins
        GPIO.cleanup() 


###############################################################
#### MAIN PROGRAM #####
###############################################################
# take in args
parser = argparse.ArgumentParser(description='Automated chicken door controller')
parser.add_argument('-l','--latitude', help='latitude of your coop')
parser.add_argument('-g','--longitude', help='longitude of your coop')
parser.add_argument('-e','--elevation', type=float, help='elevation in meters of your coop')
parser.add_argument('-o','--openpin', type=int, help='gpio pin for open')
parser.add_argument('-c','--closepin', type=int, help='gpio pin for close')
parser.add_argument('-t','--runtime', type=int, help='runtime for actuator')
parser.add_argument('-d','--debug', action='store_true', help='enable debugging logging')
parser.add_argument('-C','--c_offset', type=int, default=0, help='sunset offset - minutes after sunset to run') # added 9/4/18
parser.add_argument('-O','--o_offset', type=int, default=0, help='sunrise offset - minutes before sunrise to run') # added 9/y/18
args = parser.parse_args()

# prime logging
logger = setupLogging('chicken-logger')


#  pyephem setup
home = ephem.Observer()

# set up some defaults, you can change these or pass them in as args
home.lat = '0.0'	# latitude
home.lon = '0.0'	# longitude
home.elevation = 0.0  	# elevation in meters, must be a float
closePin = 23 		# physical pin 16
openPin = 24 		# physical pin 18
# Seconds to run the motor for. Be careful if your motor
# does not have built in limit switches to turn it off at the end
# of the stroke.
runtime = 45

# change defaults based on args, if provided
if (args.latitude): 
	home.lat = args.latitude
if (args.longitude): 
	home.lon = args.longitude
if (args.elevation): 
	home.elevation = args.elevation
if (args.closepin): 
	closePin = args.closepin
if (args.openpin): 
	openPin = args.openpin
if (args.runtime): 
	runtime = args.runtime

c_offset = args.c_offset
o_offset = args.o_offset

sun = ephem.Sun()

# get times for now, next/prev sunrise, and next/prev sunset 
(tNow, pSunrise, pSunset, nSunrise, nSunset) = getTimes(sun)

if ((tNow >= pSunrise and tNow < nSunset) and (pSunrise.tuple()[2] == nSunset.tuple()[2])):
	# It is between sunrise (minus offset) and sunset AND pSunrise and nSunset are in the same day, the door should be open.
	# The day compare (tuple()[2]) is required since nSunset turns into tomorrow right at sunset, so this always
	# evaluated true otherwise. Ugly, maybe find a better way to do this later.
	logger.debug("tNow > pSunrise and tNow < nSunset, door should be open")
	if(getAction("open")):
		logger.debug("Opening door..")	
 		setPins("open", runtime)
		
elif (tNow >= pSunset and tNow < nSunrise):
	# js7558 (9/4/18): changed this to pSunset from pSunset to allow extra min after sunset
	# it is the middle of the night, the door should be closed
	logger.debug("tNow > pSunset and tNow < nSunrise, door should be closed")
	if(getAction("close")):
		logger.debug("Closing Door...")	
		setPins("close", runtime)

