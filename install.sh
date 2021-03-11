#!/bin/bash

sudo cp ./systemd/jmri_monitor.service ./systemd/jmri.service /etc/systemd/system
sudo systemctl daemon-reload
sudo systemctl enable jmri_monitor.service jmri.service

sudo cp ./udev/99-usb-serial.rules /etc/udev/rules.d/

mkdir -p /home/pi/bin
cp ./src/display.py ./src/status_monitor.py /home/pi/bin
