#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Web interface for controlling the Dampness Hunter.

Flask-based webapp.

By: Yoan Tournade <yoan@ytotech.com>
Copyright (c) 2015 Yoan Tournade
"""
from flask import Flask
from app import strategy, run, stop
import threading

web = Flask(__name__)

@web.route("/")
def index():
    return "Hello World!"

if __name__ == "__main__":
	threading.Thread(target=run).start()
	try:
		web.run(host='0.0.0.0')
	finally:
		stop()
