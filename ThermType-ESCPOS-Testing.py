import time
import os
import re
import termcolor
import pygame
import atexit
import signal

from escpos import USBConnection
from escpos.impl.elgin import ElginRM22

import textwrap as tr

from datetime import datetime

now = datetime.now()

dt_string = now.strftime("%Y-%m-%d %H:%M:%S %z")

conn = USBConnection.create('28e9:0289,interface=0,ep_out=3,ep_in=0')
printer = ElginRM22(conn)
printer.init()
printer.text('Hello World!')

termcolor.cprint("STARTUP: "+dt_string+"\n", 'cyan', attrs=["underline"])
printer.text("STARTUP: "+dt_string+"\n")

callsign = "EI3HIB" # My Call
groupONE = "@AREN" # AREN group
groupTWO = "RAYNET" # RAYNET group - I left out @ as there are RAYNET groups using prefixes
groupTHREE = "@R1EMCOR" # IARU Region 1 Emergency Co-ordination
groupFOUR = "@APRSIS" # APRS-IS monitoring
groupFIVE = "@ALLCALL" # ALLCALL group monitoring
filterONE = "HEARTBEAT" # For filtering HB responses

termcolor.cprint("MONITORING: \n"+callsign+"\n"+groupONE+"\n"+groupTWO+"\n"+groupTHREE+"\n"+groupFOUR+"\n", 'white')
printer.text("MONITORING: \n"+callsign+"\n"+groupONE+"\n"+groupTWO+"\n"+groupTHREE+"\n"+groupFOUR+"\n")

def handler(signum, frame):
    res = input("Ctrl-c was pressed. Do you really want to exit? y/n ")
    if res == 'y':
        time.sleep(1)
        printer.text("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXX\n")
        printer.text("SHUTDOWN: "+dt_string+"\n")
        printer.text("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXX\n")
        termcolor.cprint("SHUTDOWN: "+dt_string+"\n", 'red', attrs=["underline"])
        exit(1)

signal.signal(signal.SIGINT, handler)
     

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
    
    logfile = open("/home/daithi/.local/share/JS8Call/DIRECTED.TXT","r", encoding="ascii", errors="ignore")
    loglines = follow(logfile)
    # iterate over the generator
   
    def use_printer_ordinary(addressedTo):
        printer.text(addressedTo)
        printer.text(tr.fill(line, width=32))
        
    def use_printer_priority(groupName):
        printer.text(groupName)
        printer.text(tr.fill(line, width=32))
   
    for line in loglines:
        # Is it my callsign AND NOT a HB response?    
        if re.search(callsign, line) and not re.search(filterONE, line):
            termcolor.cprint((tr.fill(line, width=128)), 'green', attrs=["blink"])
            addressTo = callsign
            use_printer_ordinary(addressedTo)

        # If it's a HB response to me - output to terminal, don't send to printer.    
        elif re.search(callsign, line) and re.search(filterONE, line):
            termcolor.cprint((tr.fill(line, width=128)), 'green')

        # Is it @AREN?
        elif re.search(groupONE, line):
            termcolor.cprint((tr.fill(line, width=128)), 'cyan', attrs=["blink"])
            groupName = groupONE
            use_printer_priority(groupName)

        # Is it at RAYNET?
        elif re.search(groupTWO, line):
            termcolor.cprint((tr.fill(line, width=128)), 'yellow', attrs=["blink"])
            groupName = groupTWO
            use_printer_priority(groupName)
            
        # Is it @R1EMCOR?
        elif re.search(groupTHREE, line):
            termcolor.cprint((tr.fill(line, width=128)), 'magenta', attrs=["blink"])
            groupName = groupTHREE
            use_printer_priority(groupName)

        # Is it @APRSIS?
        elif re.search(groupFOUR, line):
            termcolor.cprint((tr.fill(line, width=128)), 'white')
            addressedTo = groupFOUR
            use_printer_ordinary(addressedTo)
            
        # Is it @ALLCALL?
        elif re.search(groupFIVE, line):
            termcolor.cprint((tr.fill(line, width=128)), 'white')
            # Uncomment below to send @ALLCALL messages to printer
            #addressedTo = groupFIVE
            #use_printer_ordinary(addressedTo) 

        # For testing - uncomment lines below to send everything to printer
        else:
            addressedTo = "Testing"
            use_printer_ordinary(addressedTo)
            termcolor.cprint((tr.fill(line, width=128)), 'blue')
