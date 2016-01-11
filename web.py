#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Web interface for controlling the Dampness Hunter.

Flask-based webapp.

By: Yoan Tournade <yoan@ytotech.com>
Copyright (c) 2015 Yoan Tournade
"""
from flask import Flask, render_template, jsonify
from app import strategy, run, stop
import threading

web = Flask(__name__)

@web.route("/")
def index():
    return render_template('index.html')

@web.route("/on", methods=['POST'])
def on():
    return '', 204

@web.route("/off", methods=['POST'])
def off():
    return '', 204

@web.route("/readings", methods=['GET'])
def get_readings():
    return jsonify(temperature=strategy.temperature,
        humidity=strategy.humidity)

@web.route("/settings", methods=['GET'])
def get_settings():
    return ''

@web.route("/settings", methods=['POST'])
def set_settings():
    return '', 204

if __name__ == "__main__":
    threading.Thread(target=run).start()
    try:
        web.run(host='0.0.0.0', port=80)
    finally:
        stop()
