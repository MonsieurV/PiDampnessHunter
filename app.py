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
import json
import datetime

CONF_FILE = 'conf.json'

def loadConfigurationFromFile(strategy):
    with open(CONF_FILE, 'r') as f:
        strategy.conf = json.load(f)

def saveConfigurationToFile(strategy):
    with open(CONF_FILE, 'w') as f:
        json.dump(strategy.conf, f)

class HeatStrategy:
    def __init__(self, configuration):
        """ Initiliaze.
        configuration -- A dict with:
        - threshold_humidity;
        - threshold_temperature;
        - max_temperature;
        - tick -- In seconds;
        - min_duration -- As a multiple of tick;
        - history_length."""
        self.conf = configuration
        self.on = True
        self.duration_counter = None
        self.temperature = None
        self.humidity = None
        self.history = []

    def set(self, temperature, humidity):
        self.temperature = temperature
        if self.temperature:
            self.temperature = round(self.temperature, 2)
        self.humidity = humidity
        if self.humidity:
            self.humidity = round(self.humidity, 2)
        self.history.append({
            'timestamp': datetime.datetime.now(),
            'humidity': humidity,
            'temperature': temperature
            })
        while len(self.history) > self.conf['history_length']:
            del self.history[0]

    def heat(self):
        if not self.on:
            return self._stop_heating()
        if self.duration_counter is not None \
                and self.duration_counter < self.conf['min_duration']:
            return self._start_heating()
        if self.temperature > self.conf['threshold_temperature'] \
                and self.humidity < self.conf['threshold_humidity']:
            return self._stop_heating()
        if self.temperature > self.conf['max_temperature']:
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
        self.reset()
        return False

    def start(self):
        self.on = True

    def stop(self):
        self.on = False

    def reset(self):
        self.duration_counter = None

pifacedigital = pifacedigitalio.PiFaceDigital()
strategy = HeatStrategy(None)
# Load conf from file.
loadConfigurationFromFile(strategy)
irqQueue = queue.Queue()

def quit_gracefully(*args):
    pifacedigital.relays[1].turn_off()
    exit(0)
signal.signal(signal.SIGINT, quit_gracefully)

def update():
    irqQueue.put('UPDATE')
    saveConfigurationToFile(strategy)

def stop():
    irqQueue.put('STOP')

def run():
    try:
        while 1:
            try:
                if irqQueue.get(True, strategy.conf['tick']) == 'STOP':
                    quit_gracefully()
                strategy.reset()
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
