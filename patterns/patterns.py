#!/usr/bin/env python3
# RGBW light patterns by Dennis Adams (dithermaster@gmail) for Sisyphus tables

import math
import time
from datetime import datetime
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

def RGBW(r, g, b):
    w = min(r, g, b)
    return Color(r-w, g-w, b-w, w)

def Perceptual_to_RGBW(r, g, b):
    # squares perceptual value to make it linear, converts to 0-255 integer
    return RGBW(int(round(r*r*255.0)), int(round(g*g*255.0)), int(round(b*b*255.0)))

def rainbow_sat(led_theta, ball_rho, ball_theta, day_ms, rotation):
    theta = led_theta + rotation
    pos = int(256 * theta / TWO_PI) & 255
    if pos < 85:
        return RGBW(pos * 3, 255 - pos * 3, 0)
    elif pos < 170:
        pos -= 85
        return RGBW(255 - pos * 3, 0, pos * 3)
    else:
        pos -= 170
        return RGBW(0, pos * 3, 255 - pos * 3)

def rainbow_pastel(led_theta, ball_rho, ball_theta, day_ms, rotation):
    theta = led_theta + rotation
    offset = TWO_PI / 3.0
    r = int(round((math.sin(theta) + 1.0) / 2.0 * 255.0))
    g = int(round((math.sin(theta+offset) + 1.0) / 2.0 * 255.0))
    b = int(round((math.sin(theta+2*offset) + 1.0) / 2.0 * 255.0))
    return RGBW(r, g, b)

def color_waves(led_theta, ball_rho, ball_theta, day_ms, rotation):
    movement = TWO_PI * day_ms / 60000
    theta = led_theta + rotation + movement
    r = (math.sin(theta * 1559 / 1000) + 1.0) / 2.0
    g = (math.sin(theta * 1193 / 1000) + 1.0) / 2.0
    b = (math.sin(theta * 2161 / 1000) + 1.0) / 2.0
    return Perceptual_to_RGBW(r, g, b)

def ball_spotlight(led_theta, ball_rho, ball_theta, day_ms, rotation):
    led_theta = led_theta - math.floor(led_theta / TWO_PI) * TWO_PI # make 0 .. TWO_PI
    ball_theta = ball_theta - math.floor(ball_theta / TWO_PI) * TWO_PI # make 0 .. TWO_PI
    angle_diff = abs(ball_theta - led_theta)
    w = max(min(10*((1.0-ball_rho) * (TWO_PI / 2.0) - (angle_diff - TWO_PI/50)), max(ball_rho,0.3)), 0.0)
    return Perceptual_to_RGBW(w, w, w)

# sisbot simulator - replace with code that gets ball location from sisbot (I could not get that working, so I'm simulating it)
def sisbotSimulator():
    pattern = 4
    dt = datetime.now()
    day_ms = ((dt.hour * 60 + dt.minute) * 60 + dt.second) * 1000 + dt.microsecond / 1000
    speed = 5 # 0=stopped, 1=slow (1 minute per rotation), 60=fast (1 second per rotation)
    rotation = TWO_PI * day_ms * speed / 60000
    ball_rho = (math.sin(TWO_PI * day_ms * 2 / 60000) + 1.0) / 2.0
    ball_theta = 0.0
    #brightness = 1.0

    # get the pattern function
    switcher = {
        1: rainbow_sat,
        2: rainbow_pastel,
        3: color_waves,
        4: ball_spotlight
    }
    func = switcher.get(pattern, lambda: RGBW(0, 0, 0))

    # set LED colors based on pattern function
    for i in range(strip.numPixels()):
        led_theta = TWO_PI * i / strip.numPixels()
        strip.setPixelColor(i, func(led_theta, ball_rho, ball_theta, day_ms, rotation))
    # send to strip
    strip.show()
    # limit update speed (no faster than this, but likely slower due to math and strip update)
    time.sleep(1.0/60)


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
            strip.setPixelColor(i, RGBW(0,0,0))
        strip.show()
