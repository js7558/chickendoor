# chickendoor
Raspberry Pi based chicken coop automated door control program. 

# Features:
- Uses python ephem to calculate sunrise and sunset based on latitude, longitude, and elevation of your chicken coop. This automatically adjusts as the year goes on and doesn't rely on using an API to obtain these data (i.e. works if your internet connection is down).  
- Sets GPIO pins on Raspberry Pi using RPi.GPIO to set output pins on Rasberry Pi to drive a 2 channel relay
- Tries to determine of the program has already opened or closed the door and avoids unnecessary triggering of the relays if it can confirm this (uses files placed in /tmp to try to figure that out).
- NEW FEATURE 9/2018:  Offsets using the -O and -C options allow an opening X minutes before sunrise and Y minutes after sunset, respectively.  Helpful if your chickens get up too early and make a bunch of noise or stragglers/younger birds come to the roost too late.  Each offset can be up to 90 minutes.  

# My Setup:
I have a 12" linear actuator controlling a small swinging door on my chicken coop.  The actuator has limit switches at the end of travel in either direction, which is important because it means I simply have to keep pins on the Pi open longer than it takes to open/close the door .  The actuator was obtained from a large, Seattle based online retailer. I am using a raspberry pi 1 with a 2 channel relay module that can be driven by 3.3V from the Pi's GPIO pins.  I directly connect 2 of the GPIO pins from the Pi (openpin and closepin) to the relay module:  One to the "open" relay and one to the "close" relay.   The relay also gets +5V power and GND from pins on the Pi.  +12V at the NC side of each relay, GND at the NO side of each relay, and leads for my linear actuator connected to the middle ports on the relays (black to relay #1, red to relay #2).    The door being fairly small at 14" x 18" and lightweight, I'm pulling about 0.2A @ 12V when the door runs.   I put a video of the hardware and it closing at sunset at https://www.youtube.com/watch?v=bQoSN8a1NS8.

# How to Use:
1) Install ephem and RPi.GPIO (the other stuff should hopefully already be there, but check imports)
2) Figure out the latitude, longitude, and elevation and elevation (meters) of your chicken coop.  Mine in Seattle are something like
      47.62, -122.33, and 34.0 respectively.
3) Schedule chicken.py to run in cron on a reasonable interval. I run mine every 5 minutes:
    
    0,5,10,15,20,25,30,35,40,45,50,55 * * * * /home/pi/chicken/chicken.py  -g -122.33 -l 47.62 -e 34.0 -o 24 -c 23 -O 30 -C 30 -d
4) Watch the log file in /var/log/chicken.log for a while to make sure it is doing what you want. Once you're happy you can remove -d from           above to turn off debug logging.

# Help:

root@lizard:/home/pi/chicken# ./chicken.py --help
usage: chicken.py [-h] [-l LATITUDE] [-g LONGITUDE] [-e ELEVATION]
                  [-o OPENPIN] [-c CLOSEPIN] [-t RUNTIME] [-d]
                  [-C {0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88,89}]
                  [-O {0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88,89}]

Automated chicken door controller

optional arguments:
  -h, --help            show this help message and exit
  -l LATITUDE, --latitude LATITUDE
                        latitude of your coop
  -g LONGITUDE, --longitude LONGITUDE
                        longitude of your coop
  -e ELEVATION, --elevation ELEVATION
                        elevation in meters of your coop
  -o OPENPIN, --openpin OPENPIN
                        gpio pin for open
  -c CLOSEPIN, --closepin CLOSEPIN
                        gpio pin for close
  -t RUNTIME, --runtime RUNTIME
                        runtime for actuator
  -d, --debug           enable debugging logging
  -C {0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88,89}, --c_offset {0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88,89}
                        sunset offset - minutes after sunset to run
  -O {0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88,89}, --o_offset {0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88,89}
                        sunrise offset - minutes before sunrise to run


# Caveats/Considerations:
- I use mine on a door that swings on normal hinges, but there isn't any reason you couldn't use this for a door that moves in a single plane.  There are a lot of door designs online like this where it goes up/down vs. swinging on hinges.
- It is key to have limit switches on the ends of travel for your motor/actuator mechanism.  This program uses a fairly simple approach of just leaving the relays energized longer than it takes to open or close the door.  You could do something more elaborate like reading a switch to shut it off if you want to get more fancy.
- Good idea to mount your Pi and relay modules in a dust proof enclosure in your coop.  I epoxied some mounting plates for the Pi and relay module inside of mine and got some cable glands to keep the entry points for cables sealed up. 
