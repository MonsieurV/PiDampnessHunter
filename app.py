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

TARGET_HUMIDITY = 35
TARGET_TEMPERATURE = 20

pifacedigital = pifacedigitalio.PiFaceDigital()

try:
	while 1:
		humidity, temperature = Adafruit_DHT.read_retry(Adafruit_DHT.DHT22, 4)
		if humidity is None or temperature is None:
			continue
		print('Temperature: {0:0.1f}°C -- Humidity: {1:0.1f}%'.format(
			temperature, humidity))
		if temperature < TARGET_TEMPERATURE or humidity > TARGET_HUMIDITY:
			# Turn on the heater.
			pifacedigital.relays[1].turn_on()
		else:
			pifacedigital.relays[1].turn_off()
		time.sleep(10)
finally:
	# Turn off the heater.
	pifacedigital.relays[1].turn_off()
