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

# TODO Conceive a smarter algorithm that use 'target' values,
# not raw thresholds.
THRESHOLD_HUMIDITY = 48
THRESHOLD_TEMPERATURE = 18.5
MAX_TEMPERATURE = 21.5
TICK = 10
# As a multiple of TICK.
MIN_DURATION = 3

class HeatStrategy:
	def __init__(self):
		self.min_duration_counter = 3

	def heat(self, temperature, humidity):
		if self.min_duration_counter > 0:
			return self.continue_heating()
		if temperature > THRESHOLD_TEMPERATURE and humidity < THRESHOLD_HUMIDITY:
			return stop_heating()
		if temperature > MAX_TEMPERATURE:
			return self.stop_heating()
		# TODO Check the current duration of heating: if the heater has been working
		# more than MAX_DURATION, make a pause during PAUSE_DURATION.
		return True

	def stop_heating(self):
		self.min_duration_counter = MIN_DURATION
		return False

	def continue_heating(self):
		self.min_duration_counter = self.min_duration_counter - 1
		return True

pifacedigital = pifacedigitalio.PiFaceDigital()
strategy = HeatStrategy()

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
		if strategy.heat(temperature, humidity):
			# Turn on the heater.
			pifacedigital.relays[1].turn_on()
		else:
			pifacedigital.relays[1].turn_off()
		time.sleep(TICK)
finally:
	# Turn off the heater.
	pifacedigital.relays[1].turn_off()
