#!/usr/bin/env python3

import gpiozero
from time import sleep
from subprocess import run, PIPE
from socket import socket, timeout, AF_INET, SOCK_STREAM

STOPPED = 0
STARTING = 1
CONNECTING = 2
RUNNING = 3
ERROR = 4

RED = (1, 0, 0)
AMBER = (1, 0.1, 0)
YELLOW = (1, 0.24, 0)
GREEN = (0, 1, 0)
BLUE = (0, 0, 1)
PURPLE = (1, 0, 1)

BLACK = (0, 0, 0)


led = gpiozero.RGBLED(22, 27, 17)

state = STOPPED
delay = 1 / 5 #Hz


while True:
    r = run(['pgrep', '-f', 'jmri.jar'], stdout=PIPE)
    try:
        int(r.stdout)
        state = ERROR
        try:
            s = socket(AF_INET, SOCK_STREAM)
            s.settimeout(0.25)
            try:
                s.connect(('localhost', 12090))
                s.recv(1, 2048)
                state = STARTING
                chunk = None
                while s and chunk != b'':
                    chunk = s.recv(2048, 2048)
                    if b'PW12080' in chunk:
                        s.send(b'Q\n')
                        state = RUNNING
                        break
                s.close()
            except timeout:
                state = CONNECTING
        except ConnectionRefusedError:
            state = STARTING
    except ValueError:
        state = STOPPED

    if state == STARTING:
        led.color = AMBER
        delay = 1 / 4 #Hz
    elif state == CONNECTING:
        led.color = YELLOW
        delay = 1 / 6 #Hz
    elif state == RUNNING:
        led.color = GREEN
        delay = 5
    elif state == STOPPED:
        led.color = RED
        delay = 1 / 2 #Hz
    elif state == ERROR:
        led.color = PURPLE
        delay = 1 / 8 #Hz
    else:
        led.color = PURPLE
        delay = 1 / 16 #Hz

    #print(state, delay)
    sleep(delay)

    if state == RUNNING:
        delay = 0.02

    led.color = BLACK
    sleep(delay)
