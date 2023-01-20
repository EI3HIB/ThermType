import json
import pandas as pd
import requests
import time

import collections

from datetime import datetime

now = datetime.now()
dt_string = now.strftime("%Y-%m-%d")
print(dt_string)

lat = 0.00 # Your Latitude
lng = 0.00 # Your Longitude 

someKey = "YOUR-KEY-HERE" # Register on N2YO to get your free API key
satIds = ['39084','40697','42063', '49260','39634'] # This includes active Sentinel and LandSat satellites

days = 1 # Day(s) of passes from now
ele = 30 # Minimum elevation of the pass

size = len(satIds) # To work out how many separate satellites we have to iterate through

data = []
df1 = pd.DataFrame(data,columns=['SAT','START','EL','SDir','EDir'])

    
h = 0
while h < size:
    response = requests.get("https://api.n2yo.com/rest/v1/satellite/radiopasses/"+str(satIds[h])+"/"+str(lat)+"/"+str(lng)+"/0/"+str(days)+"/"+str(ele)+"/&apiKey="+str(someKey))
    jsonResponse = response.json()

    satName = jsonResponse['info']['satname'] # Get the satellite name from the JSON
    passCount = jsonResponse['info']['passescount'] # Get the number of passes for that satellite from the JSON

    i = 0
    while i < passCount: # While i is less than the number of passes, iterate through the details of each pass
        startUnix = jsonResponse['passes'][i]['startUTC']
        maxEl = jsonResponse['passes'][i]['maxEl']
        startDir = jsonResponse['passes'][i]['startAzCompass']
        endDir = jsonResponse['passes'][i]['endAzCompass']
        startUTC = datetime.utcfromtimestamp(startUnix).strftime("%a %H:%M")
        
        data = pd.DataFrame({'SAT':satName,'START':[startUTC],'EL':maxEl,'SDir':startDir,'EDir':endDir})
        df1 = pd.concat([df1, data])

        i += 1
            
    h += 1


blankIndex=[''] * len(df1)
df1.index=blankIndex
print(df1.sort_values(by=['START']))


