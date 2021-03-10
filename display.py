#!/usr/bin/env python3

import argparse
import textwrap

from PIL import Image, ImageDraw, ImageFont

import busio
import adafruit_ssd1306
from board import SCL, SDA


class Display:
    def __init__(self):
        self.oled = adafruit_ssd1306.SSD1306_I2C(128, 64, busio.I2C(SCL, SDA))

        self.font_large = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 14)
        self.font_small = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 9)

        self.image = Image.new('1', (self.oled.width, self.oled.height))
        self.draw = ImageDraw.Draw(self.image)

    def write_lines(self, lines):
        self.draw.rectangle((0, 0, self.oled.width, self.oled.height), outline=0, fill=0)

        if lines:
            self.draw.text((2, -2), lines[0], font=self.font_large, fill=255)

            i = 0
            if len(lines) > 1:
                for t in lines[1:]:
                    try:
                        t = textwrap.wrap(t, width=24) 
                    except AttributeError:
                        t = []
                    for s in t:
                        self.draw.text((0, 16 + 8*i), s, font=self.font_small, fill=255)
                        if s:
                            i += 1

        self.oled.image(self.image)
        self.oled.show()

    def dim(self):
        self.oled.contrast(1)

    def bright(self):
        self.oled.contrast(255)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Display text on the front panel OLED.')
    parser.add_argument('text', metavar='TITLE', nargs='+', help='Text to display. Title followed by lines of body.')
    parser.add_argument('--dim', action='store_true', help='Dim the display.')
    args = parser.parse_args()

    d = Display()
    if args.dim:
        d.dim()
    d.write_lines(args.text)
