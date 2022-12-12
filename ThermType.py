import time
import os
import re
import board
import serial
import adafruit_thermal_printer
import termcolor

import textwrap as tr

from datetime import date
from datetime import datetime

now = datetime.now()

dt_string = now.strftime("%Y-%m-%d %H:%M:%S %z")

#ThermalPrinter = adafruit_thermal_printer.get_printer_class(2.69)
ThermalPrinter = adafruit_thermal_printer.get_printer_class(2.69)
RX = board.RX
TX = board.TX

uart = serial.Serial("/dev/serial0", baudrate=262148, timeout=3000)

printer = ThermalPrinter(uart, auto_warm_up=False)
printer.warm_up()
printer.feed(1)

termcolor.cprint("STARTUP: "+dt_string+"\n", 'cyan', attrs=["underline"])
printer.bold = True
printer.print("STARTUP: "+dt_string+"\n")

patrnONE = "EI3HIB" # My Call
patrnTWO = "Transmitting" # Only required if monitoring ALL.TXT
patrnTHREE = "@AREN" # AREN group
patrnFOUR = "RAYNET" # RAYNET group - I left out @ as there are multiple RAYNET groups using prefixes
patrnFIVE = "@R1EMCOR" # IARU Region 1 Emergency Co-ordination
patrnSIX = "@APRSIS" # APRS-IS monitoring
patrnSEVEN= "@ALLCALL" # ALLCALL group monitoring

termcolor.cprint("MONITORING: \n"+patrnONE+"\n"+patrnTHREE+"\n"+patrnFOUR+"\n"+patrnFIVE+"\n"+patrnSIX+"\n", 'white')
#printer.bold = True
printer.print("MONITORING: \n"+patrnONE+"\n"+patrnTHREE+"\n"+patrnFOUR+"\n"+patrnFIVE+"\n"+patrnSIX+"\n")

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
    
    # Use ALL.TXT to monitor outgoing transmissions
    #logfile = open("/home/pi/.local/share/JS8Call/ALL.TXT","r")
    logfile = open("/home/pi/.local/share/JS8Call/DIRECTED.TXT","r")
    loglines = follow(logfile)
    # iterate over the generator
   
    for line in loglines:
        
        # When looking at the ALL.TXT file I included a NOT check to 
        # change behaviour if I was transmitting.
        # This check is not required for DIRECTED.TXT
        # but is left in to make ALL.TXT monitoring easier.
        # Look at log - is it my callsign AND I am NOT transmitting?
        if re.search(patrnONE, line) and not re.search(patrnTWO, line):
            #printer.warm_up()
            printer.bold = True
            termcolor.cprint((tr.fill(line, width=32)), 'green')
            printer.underline = adafruit_thermal_printer.UNDERLINE_THICK
            printer.justify = adafruit_thermal_printer.JUSTIFY_LEFT
            printer.print("FAO EI3HIB")
            printer.underline = None
            printer.print(tr.fill(line, width=32))
            printer.feed(1)
        
        # Look at log - is it my callsign AND I AM transmitting?
        elif re.search(patrnONE, line) and re.search(patrnTWO, line):
            termcolor.cprint((tr.fill(line, width=32)), 'red')
            # Uncomment code below to print on transmit
            # This also requires that you monitor ALL.TXT and not DIRECTED.TXT
            # See lines 63 and 64.
            
            #printer.size = adafruit_thermal_printer.SIZE_SMALL
            #printer.inverse = True
            #printer.print(tr.fill(line, width=32))
            #printer.inverse = False
            #printer.feed(1)
        
        # Look at log - is it @AREN and I am NOT transmitting?
        elif re.search(patrnTHREE, line) and not re.search(patrnTWO, line):
            #printer.warm_up()
            printer.bold = True
            termcolor.cprint((tr.fill(line, width=32)), 'cyan', attrs=["blink"])
            printer.size = adafruit_thermal_printer.SIZE_MEDIUM
            printer.underline = adafruit_thermal_printer.UNDERLINE_THICK
            printer.justify = adafruit_thermal_printer.JUSTIFY_CENTER
            printer.print("@AREN")
            printer.underline = None
            printer.justify = adafruit_thermal_printer.JUSTIFY_LEFT
            printer.size = adafruit_thermal_printer.SIZE_SMALL
            printer.print(tr.fill(line, width=32))
            printer.feed(2)
            
        # Look at log - is it @RAYNET and I am NOT transmitting?
        elif re.search(patrnFOUR, line) and not re.search(patrnTWO, line):
            #printer.warm_up()
            printer.bold = True
            termcolor.cprint((tr.fill(line, width=25)), 'yellow', attrs=["blink"])
            printer.size = adafruit_thermal_printer.SIZE_MEDIUM
            printer.underline = adafruit_thermal_printer.UNDERLINE_THICK
            printer.justify = adafruit_thermal_printer.JUSTIFY_CENTER
            printer.print("RAYNET")
            printer.underline = None
            printer.justify = adafruit_thermal_printer.JUSTIFY_LEFT
            printer.size = adafruit_thermal_printer.SIZE_SMALL
            printer.print(tr.fill(line, width=32))
            printer.feed(2)
            
        # Look at log - is it @R1EMCOR and I am NOT transmitting?
        elif re.search(patrnFIVE, line) and not re.search(patrnTWO, line):
            #printer.warm_up()
            printer.bold = True
            termcolor.cprint((tr.fill(line, width=25)), 'magenta', attrs=["blink"])
            printer.size = adafruit_thermal_printer.SIZE_MEDIUM
            printer.underline = adafruit_thermal_printer.UNDERLINE_THICK
            printer.justify = adafruit_thermal_printer.JUSTIFY_CENTER
            printer.print("@R1EMCOR")
            printer.underline = None
            printer.justify = adafruit_thermal_printer.JUSTIFY_LEFT
            printer.size = adafruit_thermal_printer.SIZE_SMALL
            printer.print(tr.fill(line, width=32))
            printer.feed(2)

        # Look at log - is it @APRSIS and I am NOT transmitting?
        elif re.search(patrnSIX, line) and not re.search(patrnTWO, line):
            #printer.warm_up()
            printer.bold = True
            termcolor.cprint((tr.fill(line, width=20)), 'magenta')
            printer.size = adafruit_thermal_printer.SIZE_SMALL
            printer.underline = adafruit_thermal_printer.UNDERLINE_THIN
            printer.print("@APRSIS")
            printer.underline = None
            printer.print(tr.fill(line, width=32))
            printer.feed(2)
            
        #Look at log - is it @ALLCALL and I am NOT transmitting?
        elif re.search(patrnSEVEN, line) and not re.search(patrnTWO, line):
            #printer.warm_up()
            #printer.bold = True
            termcolor.cprint((tr.fill(line, width=20)), 'blue')
            #printer.size = adafruit_thermal_printer.SIZE_SMALL
            #printer.underline = adafruit_thermal_printer.UNDERLINE_THIN
            #printer.print("@ALLCALL")
            #printer.underline = None
            #printer.print(tr.fill(line, width=32))
            #printer.feed(2)
