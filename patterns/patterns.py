#!/usr/bin/env python3
# RGBW light patterns by Dennis Adams (dithermaster@gmail) for Sisyphus tables

from datetime import datetime
import math
from neopixel import *

# LED strip configuration:
LED_COUNT      = 99      # Number of LED pixels.
LED_PIN        = 18      # GPIO pin connected to the pixels (18 uses PWM!).
#LED_PIN        = 10      # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 10      # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 150     # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL    = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53
SK6812_STRIP_GRBW = 0x18081000  # Adafruit RGBW strip

TWO_PI = math.pi * 2.0

def static_rainbow(led_theta, day_ms):
    pos = int(256 * led_theta / TWO_PI)
    if pos < 85:
        return Color(pos * 3, 255 - pos * 3, 0)
    elif pos < 170:
        pos -= 85
        return Color(255 - pos * 3, 0, pos * 3)
    else:
        pos -= 170
        return Color(0, pos * 3, 255 - pos * 3)

def turning_rainbow(led_theta, day_ms):
    theta = led_theta + day_ms * TWO_PI / 1000
    pos = int(256 * theta / TWO_PI)
    if pos < 85:
        return Color(pos * 3, 255 - pos * 3, 0)
    elif pos < 170:
        pos -= 85
        return Color(255 - pos * 3, 0, pos * 3)
    else:
        pos -= 170
        return Color(0, pos * 3, 255 - pos * 3)

# sisbot simulator - replace with code that gets ball location from sisbot (I could not get that working, so I'm simulating it)
def sisbotSimulator():
    pattern = 2
    #ball_rho = 0.0
    #ball_theta = 0.0
    #speed
    #rotation
    #brightness = 1.0

    dt = datetime.now()
    day_ms = ((dt.hour * 60 + dt.minute) * 60 + dt.second) + dt.microsecond / 1000

    # get the pattern function
    switcher = {
        1: static_rainbow,
        2: turning_rainbow
    }
    func = switcher.get(pattern, lambda: Color(0, 0, 0))

    # set LED colors based on pattern function
    for i in range(strip.numPixels()):
        led_theta = TWO_PI * i / strip.numPixels()
        strip.setPixelColor(i, func(led_theta, day_ms))
    # send to strip
    strip.show()

# Main program logic follows:
if __name__ == '__main__':
    # Create NeoPixel object with configuration match 2' Sisyphus table (larger tables will need larger LED count)
    strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL, SK6812_STRIP_GRBW)
    strip.begin()

    try:
        while True:
            sisbotSimulator()

    except KeyboardInterrupt:
        # turn off LEDs on exit
        for i in range(strip.numPixels()):
            strip.setPixelColor(i, Color(0,0,0))
        strip.show()
