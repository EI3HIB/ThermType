import time
import os
import re
import termcolor
import pygame
import atexit
import signal

import textwrap as tr

from datetime import datetime
from configparser import ConfigParser

config_object = ConfigParser()
config_object.read("config.ini")

now = datetime.now()

dt_string = now.strftime("%Y-%m-%d %H:%M:%S %z")

termcolor.cprint("STARTUP: "+dt_string+"\n", 'cyan', attrs=["underline"])

useroptions = config_object["USEROPTIONS"]

callsign = (useroptions["callsign"]) # My Call
groupONE = (useroptions["groupONE"]) 
groupTWO = (useroptions["groupTWO"]) 
groupTHREE = (useroptions["groupTHREE"]) 
groupFOUR = (useroptions["groupFOUR"]) 
groupFIVE = (useroptions["groupFIVE"])
filterONE = (useroptions["filterONE"])

termcolor.cprint("MONITORING: \n"+callsign+"\n"+groupONE+"\n"+groupTWO+"\n"+groupTHREE+"\n"+groupFOUR+"\n", 'white')

def handler(signum, frame):
    res = input("Ctrl-c was pressed. Do you really want to exit? y/n ")
    if res == 'y':
        time.sleep(1)
        exit(1)

signal.signal(signal.SIGINT, handler)

       
def confidence_tone():
    pygame.mixer.init()
    pygame.mixer.music.load("/home/pi/radio/confidencetick.wav")
    pygame.mixer.music.play(-1)
        
def message_tone():
    pygame.mixer.init()
    pygame.mixer.music.load("/home/pi/radio/message.wav")
    pygame.mixer.music.play()
    pygame.time.wait(10000)
        
def alarm_tone():
    pygame.mixer.init()
    pygame.mixer.music.load("/home/pi/radio/alarm.wav")
    pygame.mixer.music.play()
    pygame.time.wait(10000)   
        
confidence_tone()


def follow(thefile):
    '''generator function that yields new lines in a file
    '''

    # seek the end of the file
    thefile.seek(0, os.SEEK_END)
    
    # start infinite loop
    while True:

        # read last line of file
        line = thefile.readline()
        # sleep if file hasn't been updated
        if not line:
            time.sleep(0.1)
            continue

        yield line
        
if __name__ == '__main__':
    
    logfile = open("/home/pi/.local/share/JS8Call/DIRECTED.TXT","r", encoding="ascii", errors="ignore")
    loglines = follow(logfile)
    # iterate over the generator
   
   
    for line in loglines:
        # Is it my callsign AND NOT a HB response?    
        if re.search(callsign, line) and not re.search(filterONE, line):
            termcolor.cprint((tr.fill(line, width=128)), 'green', attrs=["blink"])
            addressTo = callsign
            alarm_tone()
            confidence_tone()

        # If it's a HB response to me - output to terminal, don't send to printer.    
        elif re.search(callsign, line) and re.search(filterONE, line):
            termcolor.cprint((tr.fill(line, width=128)), 'green')

        # Is it @AREN?
        elif re.search(groupONE, line):
            termcolor.cprint((tr.fill(line, width=128)), 'cyan', attrs=["blink"])
            groupName = groupONE
            alarm_tone()
            confidence_tone()

        # Is it at RAYNET?
        elif re.search(groupTWO, line):
            termcolor.cprint((tr.fill(line, width=128)), 'yellow', attrs=["blink"])
            groupName = groupTWO
            alarm_tone()
            confidence_tone()
            
        # Is it @R1EMCOR?
        elif re.search(groupTHREE, line):
            termcolor.cprint((tr.fill(line, width=128)), 'magenta', attrs=["blink"])
            groupName = groupTHREE
            alarm_tone()
            confidence_tone()

        # Is it @APRSIS?
        elif re.search(groupFOUR, line):
            termcolor.cprint((tr.fill(line, width=128)), 'white')
            addressedTo = groupFOUR
            message_tone()
            confidence_tone()
            
        # Is it @ALLCALL?
        elif re.search(groupFIVE, line):
            termcolor.cprint((tr.fill(line, width=128)), 'white')
            # Uncomment below to enable sounds for @ALLCALL
            #message_tone()
            #confidence_tone()

        # For testing - uncomment lines below to send everything to terminal/speaker
        #else:
            #termcolor.cprint((tr.fill(line, width=128)), 'blue')
            #message_tone()
            #confidence_tone()
