# petmorri@cisco.com
# meraki_camera.py	-	this file provides the functionality for making calls to the Meraki Dashboard API

import requests
import json

base_url = 'https://api.meraki.com/api/v0'

# Replace these values with your credentials
api_key = None # Meraki Dashboard API key
serial = None # Meraki MV serial number
network = None # Meraki network ID

# HTTP headers
headers = {
	'Content-Type': 'application/json',
	'X-Cisco-Meraki-API-Key': api_key,
	'cache-control': 'no-cache'
}

# Utility function to issue a GET/POST request to Meraki Dashboard API
def __api_call(url, type):
	if(type == 'GET'):
		response = requests.get(url, headers=headers).json()
	elif(type == 'POST'):
		response = requests.post(url, headers=headers).json()
	else:
		print("Invalid HTTP request")
		response = None
	return response

# Return the number of people the camera can see (full view)
def getPeople():
	response = __api_call('{0}/devices/{1}/camera/analytics/live'.format(str(base_url), str(serial)), 'GET')
	return response['zones']['0']['person']

# Return the URL of the snapshot image at the current time
def getSnap():
	response = __api_call('{0}/networks/{1}/cameras/{2}/snapshot'.format(str(base_url), str(network), str(serial)), 'POST')
	return response['url']