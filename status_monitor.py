#!/usr/bin/env python3

import signal

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


def get_log_line(first_error=False):
    session_log = []
    try:
        with open('/home/pi/.jmri/log/session.log') as f:
            session_log = f.readlines()
    except FileNotFoundError:
        return 'Session log not found.'

    # Remove lines which are parts of stack traces
    session_log = [ l for l in session_log if not l.startswith('    ') ]

    if session_log:
        session_error = [ l for l in session_log if 'ERROR' in l ][0]
        session_tail = session_log[-1]

        if first_error:
            return session_error[62:]

        return session_tail[62:]

    return 'Session log empty.'


SIG_LUT = list(range(1, 64))
SIG_LUT[2] = 'Monitor interrupted by Keyboard.'
SIG_LUT[15] = 'The system is shutting down.'

RUN = True

def signal_handler(i, _):
    global RUN
    display.write_lines(['Please Wait', SIG_LUT[i]])
    RUN = False

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)


while RUN:
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


    log_line = '…'
    if state != STARTING:
        log_line = get_log_line(state == ERROR)
    display.write_lines([state_text, log_line])

    sleep(delay)

    if state == RUNNING:
        delay = 0.02

    led.color = BLACK
    sleep(delay)
