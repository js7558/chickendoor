# chickendoor
Raspberry Pi based chicken coop automated door control program. 

Features:
- Uses python ephem to calculate sunrise and sunset based on latitude, longitude, and elevation of your chicken coop. This automatically adjusts as the year goes on and doesn't rely on using an API to obtain these data (i.e. works if your internet connection is down).  
- Sets GPIO pins on Raspberry Pi using RPi.GPIO to set output pins on Rasberry Pi to drive a 2 channel relay
- Tries to determine of the program has already opened or closed the door and avoids unnecessary triggering of the relays if it can confirm this (uses files placed in /tmp to try to figure that out).

My Setup:
I have a 12" linear actuator controlling a small swinging door on my chicken coop.  The actuator has limit switches at the end of travel in either direction, which is important because it means I simply have to keep pins on the Pi open longer than it takes to open/close the door .  The actuator was obtained from a large, Seattle based online retailer. I am using a raspberry pi 1 with a 2 channel relay module that can be driven by 3.3V from the Pi's GPIO pins.  I directly connect 2 of the GPIO pins from the Pi (openpin and closepin) to the relay module:  One to the "open" relay and one to the "close" relay.   The relay also gets +5V power and GND from pins on the Pi.  +12V at the NC side of each relay, GND at the NO side of each relay, and leads for my linear actuator connected to the middle ports on the relays (black to relay #1, red to relay #2).    The door being fairly small at 14" x 18" and lightweight, I'm pulling about 0.2A @ 12V when the door runs.  

How to Use:
1) Install ephem and RPi.GPIO (the other stuff should hopefully already be there, but check imports)
2) Figure out the latitude, longitude, and elevation and elevation (meters) of your chicken coop.  Mine in Seattle are something like
      47.6062, -122.3321, and 34.0 respectively.
3) Schedule chicken.py to run in cron on a reasonable interval. I run mine every 5 minutes:
    0,5,10,15,20,25,30,35,40,45,50,55 * * * * /home/pi/chicken/chicken.py -d -g -122.3321 -l 47.6062 -e 34.0 -o 24 -c 23
4) Watch the log file in /var/log/chicken.log for a while to make sure it is doing what you want. Once you're happy you can remove -d from           above to turn off debug logging.

Help:
root@lizard:/home/pi/chicken# ./chicken.py --help
usage: chicken.py [-h] [-l LATITUDE] [-g LONGITUDE] [-e ELEVATION]
                  [-o OPENPIN] [-c CLOSEPIN] [-t RUNTIME] [-d]

Automated chicken door controller

optional arguments:
  -h, --help            show this help message and exit
  -l LATITUDE, --latitude LATITUDE
                        latitude of your coop
  -g LONGITUDE, --longitude LONGITUDE
                        longitude of your coop
  -e ELEVATION, --elevation ELEVATION
                        elevation of your coop
  -o OPENPIN, --openpin OPENPIN
                        gpio pin for open
  -c CLOSEPIN, --closepin CLOSEPIN
                        gpio pin for close
  -t RUNTIME, --runtime RUNTIME
                        runtime for actuator
  -d, --debug           enable debugging logging

Caveats/Considerations:
- I use mine on a door that swings on normal hinges, but there isn't any reason you couldn't use this for a door that moves in a single plane.  There are a lot of door designs online like this where it goes up/down vs. swinging on hinges.
- It is key to have limit switches on the ends of travel for your motor/actuator mechanism.  This program uses a fairly simple approach of just leaving the relays open longer than it takes to open or close the door.  You could do something more elaborate like reading a switch to shut it off if you want to get more fancy.
- Good idea to mount your Pi and relay modules in a dust proof enclosure in your coop.  I epoxied some mounting plates for the Pi and relay module inside of mine and got some cable glands to keep the entry points for cables sealed up. 
