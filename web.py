#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Web interface for controlling the Dampness Hunter.

Flask-based webapp.

By: Yoan Tournade <yoan@ytotech.com>
Copyright (c) 2015 Yoan Tournade
"""
from flask import Flask, render_template, jsonify, request
from app import strategy, run, stop, update
import threading

web = Flask(__name__)

@web.route("/")
def index():
    return render_template('index.html', on=strategy.on)

@web.route("/on", methods=['POST'])
def on():
    strategy.start()
    update()
    return '', 204

@web.route("/off", methods=['POST'])
def off():
    strategy.stop()
    update()
    return '', 204

@web.route("/readings", methods=['GET'])
def get_readings():
    return jsonify(temperature=strategy.temperature,
        humidity=strategy.humidity)

@web.route("/settings", methods=['GET'])
def get_settings():
    return jsonify(on=strategy.on,
        threshold_humidity=strategy.THRESHOLD_HUMIDITY,
        threshold_temperature=strategy.THRESHOLD_TEMPERATURE,
        max_temperature=strategy.MAX_TEMPERATURE)

@web.route("/settings", methods=['PATCH'])
def set_settings():
    if request.json['threshold_humidity']:
        strategy.THRESHOLD_HUMIDITY = request.json['threshold_humidity']
    if request.json['threshold_temperature']:
        strategy.THRESHOLD_TEMPERATURE = request.json['threshold_temperature']
    if request.json['max_temperature']:
        strategy.MAX_TEMPERATURE = request.json['max_temperature']
    update()
    return '', 204

if __name__ == "__main__":
    threading.Thread(target=run).start()
    try:
        web.run(host='0.0.0.0', port=80)
    finally:
        stop()
