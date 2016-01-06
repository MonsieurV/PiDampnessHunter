#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Control a room dampness with a Raspberry Pi, a DHT-22 sensor
and an electric heater.

Switch a relay to which is connected an electric heater
following the temperature and humidity level measured
by the DHT-22 sensor.

This is a very prototype.

By: Yoan Tournade <yoan@ytotech.com>
Copyright (c) 2015 Yoan Tournade
"""
import Adafruit_DHT
import pifacedigitalio
import time
import signal

# TODO Conceive a smarter algorithm a use 'target' values,
# not row thresholds.
THRESHOLD_HUMIDITY = 50
THRESHOLD_TEMPERATURE = 19
MAX_TEMPERATURE = 22

pifacedigital = pifacedigitalio.PiFaceDigital()

def heat(temperature, humidity):
	if temperature > THRESHOLD_TEMPERATURE and humidity < THRESHOLD_HUMIDITY:
		return False
	if temperature > MAX_TEMPERATURE:
		return False
	# TODO Check the current duration of heating: if the heater has been working
	# more than MAX_DURATION, make a pause during PAUSE_DURATION.
	return True

def quit_gracefully(*args):
    pifacedigital.relays[1].turn_off()
    exit(0)

signal.signal(signal.SIGINT, quit_gracefully)
try:
	while 1:
		humidity, temperature = Adafruit_DHT.read_retry(Adafruit_DHT.DHT22, 4)
		if humidity is None or temperature is None:
			continue
		print('Temperature: {0:0.1f}°C -- Humidity: {1:0.1f}%'.format(
			temperature, humidity))
		if heat(temperature, humidity):
			# Turn on the heater.
			pifacedigital.relays[1].turn_on()
		else:
			pifacedigital.relays[1].turn_off()
		time.sleep(10)
finally:
	# Turn off the heater.
	pifacedigital.relays[1].turn_off()
