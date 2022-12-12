import time
import os
import re
import termcolor

import textwrap as tr

from datetime import date
from datetime import datetime

now = datetime.now()

dt_string = now.strftime("%Y-%m-%d %H:%M:%S %z")

termcolor.cprint("STARTUP: "+dt_string+"\n", 'cyan', attrs=["underline"])

patrnONE = "EI3HIB" # My Call
patrnTWO = "Transmitting" # Only required if monitoring ALL.TXT
patrnTHREE = "@AREN" # AREN group
patrnFOUR = "RAYNET" # RAYNET group - I left out @ as there are multiple RAYNET groups - some with prefix and/or suffix
patrnFIVE = "@R1EMCOR" # IARU Region 1 Emergency Co-ordination
patrnSIX = "@APRSIS" # APRS-IS monitoring
patrnSEVEN = "@ALLCALL" # ALLCALL group monitoring
patrnEIGHT = "HEARTBEAT SNR" # For filtering HB responses

termcolor.cprint("MONITORING: \n"+patrnONE+"\n"+patrnTHREE+"\n"+patrnFOUR+"\n"+patrnFIVE+"\n"+patrnSIX+"\n", 'white')

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
    
    logfile = open("/home/pi/.local/share/JS8Call/DIRECTED.TXT","r")
    loglines = follow(logfile)
    # iterate over the generator
   
    for line in loglines:        
      
        # Look at log - is it my callsign AND NOT a HB response?    
        if re.search(patrnONE, line) and not re.search(patrnEIGHT, line):
            termcolor.cprint((tr.fill(line, width=128)), 'green', attrs=["blink"])

        # Look at log - is it my callsign AND a HB response?      
        elif re.search(patrnONE, line) and re.search(patrnEIGHT, line):
            termcolor.cprint((tr.fill(line, width=128)), 'green')      
      
        # Look at log - is it @AREN?
        elif re.search(patrnTHREE, line)
            termcolor.cprint((tr.fill(line, width=128)), 'cyan', attrs=["blink"])
            
        # Look at log - is it @RAYNET
        elif re.search(patrnFOUR, line)
            termcolor.cprint((tr.fill(line, width=128)), 'yellow', attrs=["blink"])
            
        # Look at log - is it @R1EMCOR
        elif re.search(patrnFIVE, line)
            termcolor.cprint((tr.fill(line, width=128)), 'magenta', attrs=["blink"])

        # Look at log - is it @APRSIS
        elif re.search(patrnSIX, line)
            termcolor.cprint((tr.fill(line, width=128)), 'white')
            
        #Look at log - is it @ALLCALL
        elif re.search(patrnSEVEN, line)
            termcolor.cprint((tr.fill(line, width=128)), 'white')

