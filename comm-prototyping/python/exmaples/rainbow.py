#!/usr/bin/env python3
# NeoPixel library strandtest example
# Author: Tony DiCola (tony@tonydicola.com)
#
# Direct port of the Arduino NeoPixel library strandtest example.  Showcases
# various animations on a strip of NeoPixels.

import time
from neopixel import *
import argparse
import sys
import socket
import fcntl, os
import errno
from time import sleep
import signal


# LED strip configuration:
LED_COUNT      = 49      # Number of LED pixels.
LED_PIN        = 18      # GPIO pin connected to the pixels (18 uses PWM!).
#LED_PIN        = 10      # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 10      # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 255     # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL    = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53

SK6812_STRIP_RGBW =                       0x18100800
SK6812_STRIP_RBGW =                       0x18100008
SK6812_STRIP_GRBW =                       0x18081000
SK6812_STRIP_GBRW =                       0x18080010
SK6812_STRIP_BRGW =                       0x18001008
SK6812_STRIP_BGRW =                       0x18000810

scolor = SK6812_STRIP_GRBW
server = None

old_pix = 0

def signal_handler(sig, frame):
    print('You pressed Ctrl+C!')
    print("-" * 20)
    print("Shutting down...")
    server.close()
    colorWipe(strip, Color(0,0,0), 10) # clear lights regardless of -c flag
    os.remove("/tmp/python_unix_sockets_example")
    print("Done")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)


def init(socket_path):
    if os.path.exists(socket_path):
        os.remove(socket_path)
    print("Opening socket...")
    server = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
    server.bind(socket_path)
    fcntl.fcntl(server, fcntl.F_SETFL, os.O_NONBLOCK)
    return server

def get_data(server):
    try:
        datagram = server.recv(1024)
    except socket.error, e:
        err = e.args[0]
        if err == errno.EAGAIN or err == errno.EWOULDBLOCK:
            sleep(1)
            #print 'No data available'
            return 0,''
        else:
            # a "real" error occurred
            print e
            sys.exit(1)
    else:
        if not datagram:
            return -1, ''
        else:
            strback = datagram.decode('utf-8')
            #print(strback)
            if "DONE" == strback:
                return -1, ''
            return len(strback),strback

# Define functions which animate LEDs in various ways.
def colorWipe(strip, color, wait_ms=50):
    """Wipe color across display a pixel at a time."""
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color)
        strip.show()
        time.sleep(wait_ms/1000.0)

def wheel(pos):
    # print "wheel %s\n" % (pos),
    """Generate rainbow colors across 0-255 positions."""
    if pos < 85:
        return Color(pos * 3, 255 - pos * 3, 0)
    elif pos < 170:
        pos -= 85
        return Color(255 - pos * 3, 0, pos * 3)
    else:
        pos -= 170
        return Color(0, pos * 3, 255 - pos * 3)


def followball(rho, theta, photo, strip):
    tdeg = theta * 57.2958
    tdeg = tdeg%360
    tdeg = abs(tdeg)

    # print "rho %s degrees %s raw_theta %s photo %s\n" % (rho,tdeg,theta, photo),
    # sys.stdout.flush()

    # offset of rainbow
    wheel_deg = int(tdeg / 360 * 255)

    for i in range(0,LED_COUNT):
        pixel_offset = float(i)/LED_COUNT*255.0
        # print "%d wheel_deg %s degrees + pixel_offset %s \n" % (i, wheel_deg, pixel_offset),
        strip.setPixelColor(i, wheel((int(pixel_offset)+wheel_deg) & 255))
    strip.show()

# Main program logic follows:
if __name__ == '__main__':
    # Process arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--clear', action='store_true', help='clear the display on exit')
    args = parser.parse_args()

    # Create NeoPixel object with appropriate configuration.
    strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL) # , scolor !! not working
    # Intialize the library (must be called once before other functions).
    strip.begin()

    server = init('/tmp/python_unix_sockets_example')

    print ('Press Ctrl-C to quit.')
    if not args.clear:
        print('Use "-c" argument to clear LEDs on exit')

    try:
        colorWipe(strip, Color(0, 8, 0),50)  # Red wipe just to get started

        #
        #  Loop and get incoming data from plotter
        #
        while True:
            succode, strback = get_data(server)
            # if (succode == 0):
            #     print ('.'),
            #     sys.stdout.flush()
            if (succode > 0):
                pos = strback.rstrip().split(',')
                if (len(pos) == 4):
                    rho = float(pos[1])
                    theta = float(pos[2])
                    photo = float(pos[3])

                    followball(rho, theta, photo, strip)
            if succode < 0:
                break

    except KeyboardInterrupt:
        if args.clear:
            colorWipe(strip, Color(0,0,0), 10)
