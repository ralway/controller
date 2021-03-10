#!/usr/bin/env python3

import gpiozero
from time import sleep
from subprocess import run, PIPE
from socket import socket, timeout, AF_INET, SOCK_STREAM

from display import Display

STOPPED = 0
STARTING = 1
INITIALISING = 2
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

display = Display()

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
                state = INITIALISING
        except ConnectionRefusedError:
            state = STARTING
    except ValueError:
        state = STOPPED

    if state == STARTING:
        led.color = AMBER
        delay = 1 / 4 #Hz
        state_text = 'JMRI Starting'
    elif state == INITIALISING:
        led.color = YELLOW
        delay = 1 / 6 #Hz
        state_text = 'Initialising'
    elif state == RUNNING:
        led.color = GREEN
        delay = 5
        state_text = 'JMRI Running'
    elif state == STOPPED:
        led.color = RED
        delay = 1 / 2 #Hz
        state_text = 'JMRI Stopped'
    elif state == ERROR:
        led.color = PURPLE
        delay = 1 / 8 #Hz
        state_text = 'Error'
    else:
        led.color = PURPLE
        delay = 1 / 16 #Hz
        state_text = 'Unknown Error'

    session_log = []
    try:
        with open('/home/pi/.jmri/log/session.log') as f:
            session_log = f.readlines()
    except FileNotFoundError:
        pass

    if session_log:
        session_head = [ l for l in session_log if 'ERROR' in l ]
        if session_head:
            session_head = session_head[0]

        session_tail = session_log[-1]

        log_line = session_tail
        if state in (STOPPED, ERROR):
            log_line = session_head

        display.write_lines([state_text, log_line[62:]])

    sleep(delay)

    if state == RUNNING:
        delay = 0.02

    led.color = BLACK
    sleep(delay)
