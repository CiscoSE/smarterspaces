# petmorri@cisco.com
# meraki_analytics.py	-	this file provides the functionality for sending Meraki data to the AppDynamics API

import meraki_camera
import requests
import json
import time
import random
import gzip
import argparse

# For compatibility between python 2 and 3
try:
  import BytesIO as io
except ImportError:
  import io

# Replace these values with your credentials
appkey = None
collectorurl = "https://fra-iot-col.eum-appdynamics.com"

# Construct collector URL to send beacons to
sendBeaconUrl = collectorurl + '/eumcollector/iot/v1/application/' + appkey + '/beacons'

# Device Information on which the application is running
# Replace these values with your credentials
device_info = {
	'deviceId': '889',
	'deviceName': 'IKEA_Team_Meraki',
	'deviceType': 'IKEA_Team_Meraki'
  }

# Version Information of the application
version_info = {
	'hardwareVersion': '1.0',
	'firmwareVersion': '1.0',
	'softwareVersion': '1.0',
	'operatingSystemVersion': '1.0'
  }

# Create the beacon ready to send
def send_network_event_meraki(personCount,SnapURL):
  network_event = [{
	'timestamp': (int(time.time()) * 1000),
	'eventSummary': 'BulbState',
	'stringProperties': {
	  'snapshot': SnapURL
	},
	'longProperties': {
	   'personCount' : personCount
	}
  }]
  beacon = [{}]
  beacon[0]['deviceInfo'] = device_info
  beacon[0]['versionInfo'] = version_info
  beacon[0]['networkRequestEvents'] = network_event
  send_beacon(beacon)

# Send beacon to IoT Collector
def send_beacon(beacon):
  # Compress Payload
  out = io.BytesIO()
  with gzip.GzipFile(fileobj=out, mode='w') as f:
	json_str = json.dumps(beacon)
	json_bytes = json_str.encode('utf-8')
	f.write(json_bytes)

  r = requests.post(
		sendBeaconUrl,
		headers={
		  'Content-Type' : 'application/json',
		  'Accept' : 'application/json',
		  'Content-Encoding' : 'gzip'
		},
		data = out.getvalue()
	  )

# Main loop to update the analytics; default period is 60 seconds
while True:
	personCount = meraki_camera.getPeople()
	SnapURL = meraki_camera.getSnap()
	send_network_event_meraki(personCount,SnapURL)
	time.sleep(60)