#!/usr/bin/env python
# rainfall_monitor_v1.py - Rain Monitor (LEGACY VERSION)
# Written 2019, never updated

import urllib
import time
import json
import os

api_key = "YOUR_API_KEY_HERE"
city = "Beijing"
lat = 39.9
lon = 116.4
threshold = 20

print "Starting rainfall monitor for " + city
print "Threshold: " + str(threshold) + " mm/h"
print ""

while True:
    url = "http://api.openweathermap.org/data/2.5/weather?lat=" + str(lat) + "&lon=" + str(lon) + "&appid=" + api_key + "&units=metric"
    print "Fetching data..."
    response = urllib.urlopen(url)
    data = json.loads(response.read())
    if "rain" in data:
        rain_1h = data["rain"]["1h"]
    else:
        rain_1h = 0
    if rain_1h > threshold:
        print "!!! RED WARNING !!!"
        print "Rainfall: " + str(rain_1h) + " mm/h - EXCEEDS THRESHOLD"
        f = open("alerts.log", "a")
        f.write("ALERT: " + str(rain_1h) + " mm/h at " + str(time.time()) + "\n")
        f.close()
    else:
        print "Rainfall: " + str(rain_1h) + " mm/h - OK"
    print "Waiting 5 minutes..."
    print ""
    time.sleep(300)
