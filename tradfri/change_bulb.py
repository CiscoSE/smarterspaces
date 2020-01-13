# petmorri@cisco.com
# change_bulb.py	-	this file provides the functionality for changing the status of the bulb based on data pulled from AppD

import sys
import os
import uuid
import argparse
import requests
import time
from pytradfri import Gateway
from pytradfri.api.libcoap_api import APIFactory
from pytradfri.error import PytradfriError
from pytradfri.util import load_json, save_json
folder = os.path.dirname(os.path.abspath(__file__))  # noqa
sys.path.insert(0, os.path.normpath("%s/.." % folder))  # noqa

CONFIG_FILE = 'tradfri_standalone_psk.conf'

# Parse Tradfri credentials
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
if args.set_state is not None:
    set_state = args.set_state

# Make a call to the AppDynamics API to get the current value of people in the room
def query_appd_metric():
    params=(('metric-path', 'Analytics|Cisco_Meraki_Camera average person count'),
    ('time-range-type', 'BEFORE_NOW'),
    ('duration-in-mins', '1'),
    ('output', 'json')
    )
    response = requests.get('https://hackathon-emea.saas.appdynamics.com/controller/rest/applications/AppDynamics%20Analytics-145/metric-data', params=params, auth=('USER', 'PASS'))
    pers_count_appd = response.json()[0]['metricValues'][0]['current']
    return pers_count_appd

# Get lights, api objects
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

def set_light(lights, api, myvalue):
    my_command = lights[0].light_control.set_dimmer(myvalue)
    api(my_command)

lights, api = init()
on_off = (lights[0].light_control.lights[0].state)
dim_state = (lights[0].light_control.lights[0].dimmer)

# Loop and decide whether to dim the bulb, etc.
while True:
    pers_count_appd = query_appd_metric()
    if pers_count_appd > 0 and not on_off:
        lights, api = init()
        set_light(lights, api, 128)
        last_state = 128
        on_off = True
    elif pers_count_appd == 0 and on_off:
        lights, api = init()
        set_light(lights, api, 0)
        on_off = False
    time.sleep(10)
