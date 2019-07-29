#!/bin/bash

apt-get install python-pymysql python-serial -y

python -m pip install --upgrade pip setuptools wheel
pip install Adafruit-SSD1306
pip install -r data/lib.txt
