import time
import os
import re
import termcolor
import atexit
import signal
import geopy.distance
import math
import textwrap as tr
import pandas as pd
import numpy as np

from datetime import datetime
from io import StringIO
from escpos import USBConnection
from escpos.impl.elgin import ElginRM22

now = datetime.now()

dt_string = now.strftime("%Y-%m-%d %H:%M:%S %z")

conn = USBConnection.create('28e9:0289,interface=0,ep_out=3,ep_in=0')
printer = ElginRM22(conn)
printer.init()

termcolor.cprint("STARTUP: "+dt_string+"\n", 'cyan', attrs=["underline"])
printer.text("STARTUP: "+dt_string+"\n")

myCall = "EI3HIB" # My Call
repeaterList= ['EI2LLP','EI2MLP']
homeLOC = (53.2306, -6.6531)

termcolor.cprint("MONITORING: APRS\n", 'white')
#printer.text("MONITORING: APRS\n")

def handler(signum, frame):
    res = input("Ctrl-c was pressed. Do you really want to exit? y/n ")
    if res == 'y':
        time.sleep(1)
        #printer.text("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXX\n")
        printer.text("SHUTDOWN: "+dt_string+"\n")
        #printer.text("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXX\n")
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
	
	logfile = open('/home/pi/aprslog.txt', "r", encoding="ascii", errors="ignore")
	loglines = follow(logfile)
	
	def has_pos_data(rCall,rHeard, aprsDATA):
		if rCall == rHeard and not any(substring in rCall for substring in repeaterList): # Am I Hearing the Station Directly - and is it not a known repeater?
			termcolor.cprint(aprsDATA, 'green')
			printer.set_text_size(1,1)
			printer.justify_center()
			printer.text(rCall)
			printer.justify_left()
			printer.set_text_size(0,0)
			printer.text(tr.fill(aprsDATA, width=32))
		else:
			termcolor.cprint(aprsDATA, 'white')
	
	def no_pos_data(rCall,rHeard, aprsDATA):
		if rCall == rHeard and not any(substring in rCall for substring in repeaterList): # Am I Hearing the Station Directly - and is it not a known repeater?
			termcolor.cprint(aprsDATA, 'yellow')
		else:
			termcolor.cprint(aprsDATA, "white")
	
	for line in loglines:

		csvTime = StringIO(line)
		csvCall = StringIO(line)
		csvHeard = StringIO(line)
		csvLat = StringIO(line)
		csvLng = StringIO(line)
		csvCom = StringIO(line)

		#Direwolf logging columns [0-21]
		#	      [2]    [3]    [4]                                [10]    [11]                                                                          [21]
		#chan,utime,isotime,source,heard,level,error,dti,name,symbol,latitude,longitude,speed,course,altitude,frequency,offset,tone,system,status,telemetry,comment
		
		qTime = pd.read_csv(csvTime, sep=",", usecols =[2], header = None) 
		rTime = qTime.to_string(index=False, header=False)
			
		qCall = pd.read_csv(csvCall, sep=",", usecols =[3], header = None) 
		rCall = qCall.to_string(index=False, header=False)
		
		qHeard = pd.read_csv(csvHeard, sep=",", usecols =[4], header = None) 
		rHeard = qHeard.to_string(index=False, header=False)
			
		qLat = pd.read_csv(csvLat, sep=",", usecols =[10], header = None) 
		rLat = float(qLat.to_string(index=False, header=False))
		
		qLng = pd.read_csv(csvLng, sep=",", usecols =[11], header = None) 
		rLng = float(qLng.to_string(index=False, header=False))
			
		qCom = pd.read_csv(csvCom, sep=",", usecols =[21], header = None) 
		rCom = qCom.to_string(index=False, header=False)
		
		othLOC = np.array([rLat, rLng])
			
		# This checks to see if there is position data - if not, we bypass the distance and bearing calculations
		if(np.isnan(othLOC).any()):
			if rCom == "NaN":
				pass
			else:
				aprsDATA = (""+str(rTime)+" "+str(rCall)+" "+rCom+"")
				no_pos_data(rCall, rHeard, aprsDATA)
		
		# If it does have position data - we attempt to work out their distance and bearing from our location
		else:
			dLon = (rLng - homeLOC[1])
			x = math.cos(math.radians(rLat)) * math.sin(math.radians(dLon))
			y = math.cos(math.radians(homeLOC[0])) * math.sin(math.radians(rLat)) - math.sin(math.radians(homeLOC[0])) * math.cos(math.radians(rLat)) * math.cos(math.radians(dLon))
			brngONE = np.arctan2(x,y)
			brngONE = round(np.degrees(brngONE),2)
			brngTWO = 0						
				
			if brngONE > 0:
			    brngTWO = brngONE

			elif brngONE == 0:
			    brngTWO = 0

			else:
			    deg = 360
			    brngTWO = deg + brngONE
							
			dx = round(geopy.distance.geodesic(homeLOC, othLOC).km, 2)
			
			if rCom == "NaN":
				aprsDATA = (""+str(rTime)+" "+str(rCall)+" Lat/Long: "+str(othLOC)+" DX: "+str(dx)+"km Az:"+str(brngTWO))
				has_pos_data(rCall, rHeard, aprsDATA)
			else:
				aprsDATA = (""+str(rTime)+" "+str(rCall)+" Lat/Long: "+str(othLOC)+" DX: "+str(dx)+"km Az:"+str(brngTWO)+" "+rCom+"")
				has_pos_data(rCall, rHeard, aprsDATA)
