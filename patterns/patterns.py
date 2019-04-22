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

PI = math.pi
TWO_PI = math.pi * 2.0

# utility functions

def RGBW(r, g, b, user_r, user_g, user_b, blend):
    r_int = int(round(blend * user_r + (1.0 - blend) * r))
    g_int = int(round(blend * user_g + (1.0 - blend) * g))
    b_int = int(round(blend * user_b + (1.0 - blend) * b))
    w = min(r_int, g_int, b_int)
    return Color(r_int-w, g_int-w, b_int-w, w)

def Perceptual_to_RGBW(r, g, b, user_r, user_g, user_b, blend):
    # squares perceptual value to make it linear, converts to 0-255 integer
    return RGBW(r*r*255.0, g*g*255.0, b*b*255.0, user_r, user_g, user_b, blend)

def min_angle(angle1, angle2):
    angle1 = angle1 - math.floor(angle1 / TWO_PI) * TWO_PI # make 0 .. TWO_PI
    angle2 = angle2 - math.floor(angle2 / TWO_PI) * TWO_PI # make 0 .. TWO_PI
    angle_diff = abs(angle2 - angle1)
    if (angle_diff > PI):
        angle_diff -= TWO_PI
    return abs(angle_diff)

# patterns below

def rainbow_sat(led_theta, ball_rho, ball_theta, day_ms, rotation, speed, user_r, user_g, user_b, blend):
    theta = led_theta + rotation
    pos = int(256 * theta / TWO_PI) & 255
    if pos < 85:
        return RGBW(pos * 3, 255 - pos * 3, 0, user_r, user_g, user_b, blend)
    elif pos < 170:
        pos -= 85
        return RGBW(255 - pos * 3, 0, pos * 3, user_r, user_g, user_b, blend)
    else:
        pos -= 170
        return RGBW(0, pos * 3, 255 - pos * 3, user_r, user_g, user_b, blend)

def rainbow_pastel(led_theta, ball_rho, ball_theta, day_ms, rotation, speed, user_r, user_g, user_b, blend):
    theta = led_theta + rotation
    offset = TWO_PI / 3.0
    r = int(round((math.sin(theta) + 1.0) / 2.0 * 255.0))
    g = int(round((math.sin(theta+offset) + 1.0) / 2.0 * 255.0))
    b = int(round((math.sin(theta+2*offset) + 1.0) / 2.0 * 255.0))
    return RGBW(r, g, b, user_r, user_g, user_b, blend)

def color_waves(led_theta, ball_rho, ball_theta, day_ms, rotation, speed, user_r, user_g, user_b, blend):
    movement = TWO_PI * day_ms / 60000
    theta = led_theta + rotation + movement
    r = (math.sin(theta * 1559 / 1000) + 1.0) / 2.0
    g = (math.sin(theta * 1193 / 1000) + 1.0) / 2.0
    b = (math.sin(theta * 2161 / 1000) + 1.0) / 2.0
    return Perceptual_to_RGBW(r, g, b, user_r, user_g, user_b, blend)

def ball_spotlight(led_theta, ball_rho, ball_theta, day_ms, rotation, speed, user_r, user_g, user_b, blend):
    angle_diff = min_angle(ball_theta, led_theta)
    ball_rho_adjusted = math.sqrt(ball_rho) # keep narrow more than wide
    w = max(min(10*((1.0-ball_rho_adjusted) * PI - (angle_diff - TWO_PI/50)), max(ball_rho,0.3)), 0.0)
    return Perceptual_to_RGBW(w, w, w, user_r, user_g, user_b, blend)

# sisbot simulator - replace with code that gets ball location from sisbot (I could not get that working, so I'm simulating it)
def sisbotSimulator():
    # user parameters
    pattern = 3 # this would be set by the user (they would have a set of named patterns to pick from)
    speed = 1 # this would be set by the users and sets rotation speed of patterns (0=stopped, 1=slow; 1 minute per rotation, 60=fast; 1 second per rotation
    brightness = 1.0 # this would be set by user (currently not implemented)
    user_r = 255 # user chosen int RGB color, passed to patterns; typically used with blend to mix in final output
    user_g = 0
    user_b = 0
    blend = 0.0 # blend amount, 0.0 (pattern only) to 1.0 (full solid color)

    # calculated parmeters
    dt = datetime.now()
    day_ms = ((dt.hour * 60 + dt.minute) * 60 + dt.second) * 1000 + dt.microsecond / 1000
    rotation = TWO_PI * day_ms * speed / 60000
    # move ball in rho
    #ball_rho = (math.sin(TWO_PI * day_ms * 2 / 60000) + 1.0) / 2.0
    #ball_theta = 0.0
    # move ball in theta
    ball_rho = 1.0
    ball_theta = TWO_PI * day_ms * 2 / 60000

    # get the pattern function
    switcher = {
        1: rainbow_sat,
        2: rainbow_pastel,
        3: color_waves,
        4: ball_spotlight
    }
    func = switcher.get(pattern, lambda: RGBW(0, 0, 0, 0, 0, 0, 0))

    # set LED colors based on pattern function
    for i in range(strip.numPixels()):
        led_theta = TWO_PI * i / strip.numPixels()
        strip.setPixelColor(i, func(led_theta, ball_rho, ball_theta, day_ms, rotation, speed, user_r, user_g, user_b, blend))

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
            strip.setPixelColor(i, RGBW(0,0,0, 0,0,0,0))
        strip.show()
