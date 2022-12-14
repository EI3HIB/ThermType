import time
import os
import re
import board
import serial
import adafruit_thermal_printer
import termcolor
import pygame
import RPi.GPIO as GPIO
import atexit
import signal

import textwrap as tr

from datetime import datetime
from configparser import ConfigParser
from multiprocessing import Process

config_object = ConfigParser()
config_object.read("config.ini")

GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.OUT) # Green LED
GPIO.setup(22, GPIO.OUT) # Amber LED
GPIO.setup(23, GPIO.OUT) # Red LED

GPIO.output(17, True)      

now = datetime.now()

dt_string = now.strftime("%Y-%m-%d %H:%M:%S %z")

ThermalPrinter = adafruit_thermal_printer.get_printer_class(2.69)
RX = board.RX
TX = board.TX

printerconfig = config_object["PRINTERCONFIG"]
paddress = (printerconfig["address"]) 
pbaudrate = (printerconfig["baudrate"]) 
ptimeout = int((printerconfig['timeout']))

uart = serial.Serial(paddress, baudrate=pbaudrate, timeout=ptimeout)

printer = ThermalPrinter(uart, auto_warm_up=False)
printer.warm_up()
printer.feed(1)

termcolor.cprint("STARTUP: "+dt_string+"\n", 'cyan', attrs=["underline"])
printer.print("STARTUP: "+dt_string+"\n")

useroptions = config_object["USEROPTIONS"]

callsign = (useroptions["callsign"]) # My Call
groupONE = (useroptions["groupone"]) 
groupTWO = (useroptions["grouptwo"]) 
groupTHREE = (useroptions["groupthree"]) 
groupFOUR = (useroptions["groupfour"]) 
groupFIVE = (useroptions["groupfive"])
filterONE = (useroptions["filterone"])

termcolor.cprint("MONITORING: \n"+callsign+"\n"+groupONE+"\n"+groupTWO+"\n"+groupTHREE+"\n"+groupFOUR+"\n", 'white')
printer.print("MONITORING: \n"+callsign+"\n"+groupONE+"\n"+groupTWO+"\n"+groupTHREE+"\n"+groupFOUR+"\n")

def handler(signum, frame):
    res = input("Ctrl-c was pressed. Do you really want to exit? y/n ")
    if res == 'y':
        GPIO.output(17, False)
        time.sleep(1)
        exit(1)

signal.signal(signal.SIGINT, handler)

#def amber_led():
#    GPIO.output(22, True)
#    time.sleep(2)
#    GPIO.output(22, False)

def amber_led():
    for i in range(5):
        GPIO.output(22, True)
        time.sleep(0.5)
        GPIO.output(22, False)
        time.sleep(0.5)

def red_led():
    for i in range(20):
        GPIO.output(23, True)
        time.sleep(0.5)
        GPIO.output(23, False)
        time.sleep(0.5)
        
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
    
   
    def use_printer_ordinary(addressedTo):
        printer.underline = adafruit_thermal_printer.UNDERLINE_THICK
        printer.justify = adafruit_thermal_printer.JUSTIFY_LEFT
        printer.print(addressedTo)
        printer.underline = None
        printer.print(tr.fill(line, width=32))
        printer.feed(2)
        
    def use_printer_priority(groupName):
        printer.size = adafruit_thermal_printer.SIZE_MEDIUM
        printer.justify = adafruit_thermal_printer.JUSTIFY_CENTER
        printer.inverse = True
        printer.print(groupName)
        printer.inverse = False
        printer.justify = adafruit_thermal_printer.JUSTIFY_LEFT
        printer.size = adafruit_thermal_printer.SIZE_SMALL
        printer.print(tr.fill(line, width=32))
        printer.feed(2)
   
    # Iterate over the generator
    for line in loglines:
        # Is it my callsign AND NOT a HB response?    
        if re.search(callsign, line) and not re.search(filterONE, line):
            termcolor.cprint((tr.fill(line, width=128)), 'green', attrs=["blink"])
            addressedTo = callsign
            use_printer_ordinary(addressedTo)
            red_led()
            alarm_tone()
            confidence_tone()

        # If it's a HB response to me - output to terminal, don't send to printer.    
        elif re.search(callsign, line) and re.search(filterONE, line):
            termcolor.cprint((tr.fill(line, width=128)), 'green')
            red_led()

        # Is it @AREN?
        elif re.search(groupONE, line):
            termcolor.cprint((tr.fill(line, width=128)), 'cyan', attrs=["blink"])
            groupName = groupONE
            use_printer_priority(groupName)
            red_led()
            alarm_tone()
            confidence_tone()

        # Is it at RAYNET?
        elif re.search(groupTWO, line):
            termcolor.cprint((tr.fill(line, width=128)), 'yellow', attrs=["blink"])
            groupName = groupTWO
            use_printer_priority(groupName)
            red_led()
            alarm_tone()
            confidence_tone()
            
        # Is it @R1EMCOR?
        elif re.search(groupTHREE, line):
            termcolor.cprint((tr.fill(line, width=128)), 'magenta', attrs=["blink"])
            groupName = groupTHREE
            use_printer_priority(groupName)
            red_led()
            alarm_tone()
            confidence_tone()

        # Is it @APRSIS?
        elif re.search(groupFOUR, line):
            termcolor.cprint((tr.fill(line, width=128)), 'white')
            # Uncomment below to enable printing, sounds etc
            #addressedTo = groupFOUR
            #use_printer_ordinary(addressedTo)
            amber_led()
            #message_tone()
            #confidence_tone()
            
        # Is it @ALLCALL?
        elif re.search(groupFIVE, line):
            termcolor.cprint((tr.fill(line, width=128)), 'white')
            red_led()
            # Uncomment below to enable sounds for @ALLCALL
            #message_tone()
            #confidence_tone()

        # Amber led illuminates when a non priority message is decoded amd written to DIRECTED.TXT
        # For testing - uncomment lines below to send everything to terminal/printer/speaker
        else:
            amber_led()
            #use_printer_ordinary(addressedTo)
            #termcolor.cprint((tr.fill(line, width=128)), 'blue')
            #addressedTo = "TESTING"
            #p1 = Process(use_printer_ordinary(addressedTo))
            #p1.start()
            #p2 = Process(termcolor.cprint((tr.fill(line, width=128)), 'blue'))
            #p2.start()
            #p3 = Process(amber_led())
            #p3.start()
            #p4 = Process(message_tone())
            #p4.start()
            #confidence_tone()

