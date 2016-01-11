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
try:
    import Queue as queue
except ImportError:
    import queue


# TODO Conceive a smarter algorithm that use 'target' values,
# not raw thresholds.
THRESHOLD_HUMIDITY = 50
THRESHOLD_TEMPERATURE = 18.5
MAX_TEMPERATURE = 21.5
# In seconds.
TICK = 10
# As a multiple of TICK.
MIN_DURATION = 3

class HeatStrategy:
    def __init__(self):
        self.on = True
        self.duration_counter = None
        self.temperature = None
        self.humidity = None

    def set(self, temperature, humidity):
        self.temperature = temperature
        if self.temperature:
            self.temperature = round(self.temperature, 2)
        self.humidity = humidity
        if self.humidity:
            self.humidity = round(self.humidity, 2)

    def heat(self):
        if not self.on:
            return self._stop_heating()
        if self.duration_counter is not None and self.duration_counter < MIN_DURATION:
            return self._start_heating()
        if self.temperature > THRESHOLD_TEMPERATURE \
                and self.humidity < THRESHOLD_HUMIDITY:
            return self._stop_heating()
        if self.temperature > MAX_TEMPERATURE:
            return self._stop_heating()
        # TODO Check the current duration of heating: if the heater has been working
        # more than MAX_DURATION, make a pause during PAUSE_DURATION.
        return self._start_heating()

    def _start_heating(self):
        if self.duration_counter is None:
            self.duration_counter = 0
        else:
            self.duration_counter = self.duration_counter + 1
        return True

    def _stop_heating(self):
        self.duration_counter = None
        return False

    def start(self):
        self.on = True

    def stop(self):
        self.on = False

pifacedigital = pifacedigitalio.PiFaceDigital()
strategy = HeatStrategy()

def quit_gracefully(*args):
    pifacedigital.relays[1].turn_off()
    exit(0)

irqQueue = queue.Queue()

def stop():
    irqQueue.put('STOP')

signal.signal(signal.SIGINT, quit_gracefully)

def run():
    try:
        while 1:
            try:
                if irqQueue.get(True, TICK) == 'STOP':
                    quit_gracefully()
            except queue.Empty:
                pass
            humidity, temperature = Adafruit_DHT.read_retry(Adafruit_DHT.DHT22, 4)
            strategy.set(temperature, humidity)
            if humidity is None or temperature is None:
                continue
            print('Temperature: {0:0.1f}°C -- Humidity: {1:0.1f}%'.format(
                temperature, humidity))
            if strategy.heat():
                # Turn on the heater.
                pifacedigital.relays[1].turn_on()
            else:
                pifacedigital.relays[1].turn_off()
    finally:
        # Turn off the heater.
        pifacedigital.relays[1].turn_off()

if __name__ == "__main__":
    run()
