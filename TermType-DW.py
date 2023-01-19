import time
import os
import re
import atexit
import signal
import geopy.distance
import math
import textwrap as tr
import pandas as pd
import numpy as np

from datetime import datetime
from io import StringIO

now = datetime.now()

dt_string = now.strftime("%Y-%m-%d %H:%M:%S %z")

print("STARTUP: "+dt_string+"\n")

homeLOC = (53.2306, -6.6531)

print("MONITORING: APRS\n")

def handler(signum, frame):
    res = input("Ctrl-c was pressed. Do you really want to exit? y/n ")
    if res == 'y':
        time.sleep(1)
        print("SHUTDOWN: "+dt_string+"\n")
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
	
	def has_gps_data(rCall,rHeard,aprsDATA):
		print("Has GPS: "+aprsDATA)
		print("Call:\t"+rCall)
		print("Heard:\t"+rHeard)
	
	def no_gps_data(rCall,rHeard,aprsDATA):
		print("No GPS: "+aprsDATA)
		print("Call:\t"+rCall)
		print("Heard:\t"+rHeard)
	
	for line in loglines:
		
		csvTime = StringIO(line)
		csvCall = StringIO(line)
		csvHeard = StringIO(line)
		csvLat = StringIO(line)
		csvLng = StringIO(line)
		csvCom = StringIO(line)

		#Direwolf logging columns [0-21]
		#	      [2]    [3]                                        [10]    [11]                                                                          [21]
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
			
		# This checks to see if there is position data - if not, we bypass the distance and bearing calculations.
		if(np.isnan(othLOC).any()):
			aprsDATA = (""+str(rTime)+" "+str(rCall)+" "+rCom+"")
			no_gps_data(rCall, rHeard, aprsDATA)
		
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
			aprsDATA = (""+str(rTime)+" "+str(rCall)+" Lat/Long: "+str(othLOC)+" DX: "+str(dx)+"km Az:"+str(brngTWO)+" "+rCom+"")
			has_gps_data(rCall, rHeard, aprsDATA)
