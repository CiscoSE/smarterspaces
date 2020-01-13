# Integrating Meraki, AppDynamics and IKEA Tradfri for Smarter Spaces
This project is the result of the IKEA team's submission for the AppDynamics Hackathon 2019. The purpose of the project is to push data about the status of a room (number of people, light intensity, etc.) to AppDynamics, and subsequently using the analytics provided by AppD to control IoT devices such as the IKEA Tradfri smart lights.

This project was developed by:
- Peter Morris (Cisco); [petmorri@cisco.com]
- Tom Mcauliffe (Cisco)
- Isi Ramirez (AppDynamics)
- Stefan Hemeier (IKEA)

*N.B. - this project was developed in less than 48 hours as a proof-of-concept, and as such is not regularly maintained.*

## Installation

This project makes use of the `requests` Python library;

```
pip install requests
```

Additionally, it requires the installation of the [https://github.com/ggravlingen/pytradfri](IKEA Tradfri API);

```
git clone https://github.com/ggravlingen/pytradfri
```

>It is recommended that you create a virtual environment for installing dependencies.

## Usage

This PoC demonstrates how AppDynamics can be used collect and analyse data fron IoT devices, and subsequently control them. In this example, an IKEA Tradfri bulb is dimmed or lit based on the average number of people seen by a Meraki MV camera over the last 5 minutes.

A number of variables will need to be substituted with your own credentials:

* `meraki_camera.py`
  * api key
  * serial
  * network
* `meraki_analytics.py`
  * appkey
  * deviceID
  * deviceName
  * deviceType
* `change_bulb.py`, `query_bulb.py`
  * USER
  * PASS


---

## Contact
Please email [petmorri@cisco.com](Peter) if you discover any bugs / errors.