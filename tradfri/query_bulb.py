# petmorri@cisco.com
# change_bulb.py	-	this file provides the functionality for pulling the status of the bulb to send to AppD

import sys
import os
import uuid
import argparse
import threading
import time
import requests
import json
import random
import gzip
import argparse
from pytradfri import Gateway
from pytradfri.api.libcoap_api import APIFactory
from pytradfri.error import PytradfriError
from pytradfri.util import load_json, save_json
folder = os.path.dirname(os.path.abspath(__file__))  # noqa
sys.path.insert(0, os.path.normpath("%s/.." % folder))  # noqa

# For compatibility between python 2 and 3
try:
	import BytesIO as io
except ImportError:
	import io

appkey = "EC-AAB-FPB"
collectorurl = "https://fra-iot-col.eum-appdynamics.com"

# Construct collector url to send beacons to
sendBeaconUrl = collectorurl + '/eumcollector/iot/v1/application/' + appkey + '/beacons'

# Device Information on which the application is running
device_info = {
		'deviceId': '888',
		'deviceName': 'IKEA_Tradfri_LED',
		'deviceType': 'IKEA_Tradfri_LED'
	}

# Version Information of the application
version_info = {
		'hardwareVersion': '1.0',
		'firmwareVersion': '1.0',
		'softwareVersion': '1.0',
		'operatingSystemVersion': '1.0'
	}


CONFIG_FILE = 'tradfri_standalone_psk.conf'


parser = argparse.ArgumentParser()
parser.add_argument('host', metavar='IP', type=str,
										help='IP Address of your Tradfri gateway')
parser.add_argument('-K', '--key', dest='key', required=False,
										help='Security code found on your Tradfri gateway')
parser.add_argument('-S','--state', dest='set_state',required=False)
args = parser.parse_args()

if args.host not in load_json(CONFIG_FILE) and args.key is None:
		print("Please provide the 'Security Code' on the back of your "
					"Tradfri gateway:", end=" ")
		key = input().strip()
		if len(key) != 16:
				raise PytradfriError("Invalid 'Security Code' provided.")
		else:
				args.key = key


def init():
		conf = load_json(CONFIG_FILE)

		try:
				identity = conf[args.host].get('identity')
				psk = conf[args.host].get('key')
				api_factory = APIFactory(host=args.host, psk_id=identity, psk=psk)
		except KeyError:
				identity = uuid.uuid4().hex
				api_factory = APIFactory(host=args.host, psk_id=identity)

				try:
						psk = api_factory.generate_psk(args.key)
						print('Generated PSK: ', psk)

						conf[args.host] = {'identity': identity,
															 'key': psk}
						save_json(CONFIG_FILE, conf)
				except AttributeError:
						raise PytradfriError("Please provide the 'Security Code' on the "
																 "back of your Tradfri gateway using the "
																 "-K flag.")

		api = api_factory.request

		gateway = Gateway()

		devices_command = gateway.get_devices()
		devices_commands = api(devices_command)
		devices = api(devices_commands)

		lights = [dev for dev in devices if dev.has_light_control]
		return lights,api

def set_light(lights,api,myvalue):
		my_command = lights[0].light_control.set_dimmer(myvalue)
		api(my_command)

#------------------------------------------------------------------------------------------
def send_network_event(bulbstate):
	#print ("Network Event")
	network_event = [{
		'timestamp' : (int(time.time()) * 1000),
		'eventSummary' : 'Bulb Intensity',
		'longProperties' : {
			'intensity' : bulbstate
		}
	}]
	beacon = [{}]
	beacon[0]['deviceInfo'] = device_info
	beacon[0]['versionInfo'] = version_info
	beacon[0]['networkRequestEvents'] = network_event

	#print("send network event for url: {}".format(network_event[0]['url']))
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

while True:
		lights, api = init()
		on_off = (lights[0].light_control.lights[0].state)
		dim_state = (lights[0].light_control.lights[0].dimmer)
		if on_off:
				perc_dim_state = int(dim_state/254*100)
				if dim_state <3 and dim_state > 1:
						perc_dim_state = 1
				elif dim_state < 2:
						perc_dim_state = 0
		else:
				perc_dim_state=0
		component = "48173"
		metricPath = "IKEA|Tradfri|LED|Alie_Room|intensity"
		intensity = perc_dim_state
		send_network_event(perc_dim_state)
		time.sleep(60)