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
        humidity=strategy.humidity, heating=strategy.heating)

@web.route("/readings/history", methods=['GET'])
def get_readings_history():
    return jsonify({ 'history': strategy.history })

@web.route("/settings", methods=['GET'])
def get_settings():
    return jsonify(on=strategy.on,
        threshold_humidity=strategy.conf['threshold_humidity'],
        threshold_temperature=strategy.conf['threshold_temperature'],
        max_temperature=strategy.conf['max_temperature'],
        history_length=strategy.conf['history_length'])

@web.route("/settings", methods=['PATCH'])
def set_settings():
    if request.json['threshold_humidity']:
        strategy.conf['threshold_humidity'] = request.json['threshold_humidity']
    if request.json['threshold_temperature']:
        strategy.conf['threshold_temperature'] = request.json['threshold_temperature']
    if request.json['max_temperature']:
        strategy.conf['max_temperature'] = request.json['max_temperature']
    if request.json['history_length']:
        strategy.conf['history_length'] = request.json['history_length']
    update()
    return '', 204

if __name__ == "__main__":
    threading.Thread(target=run).start()
    try:
        web.run(host='0.0.0.0', port=80)
    finally:
        stop()
