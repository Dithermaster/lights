# lights

Engineering prototype for streaming ball positions (rho, theta) from sisbot plotter across a unix domain datagram socket to a python light contolling program.   The python program needs to use the DMA on the PI, one of the items below show the steps to reconfigure the PI to support use of DMA.  The python is built on https://github.com/jgarff/rpi_ws281x


## setup the lights programs

* cd /home/pi
* git clone git@github.com:joelxxx/lights.git
* Follow directions in  ~/lights/sisbot/system/install_python_strip.sh
* Plug in the lights as shown in the photo
* test the default lights program 
* cd /home/pi/rpi_ws281x/python
* sudo python examples/strandtest.py

### If that works, start up the python program to listen on datagram socket for ball positions.

* cd /home/pi/rpi_ws281x/python
* cp ~/lights/comm-prototyping/python/exmaples/baller.py examples
* modify line 20 in baller.py  LED_COUNT      = 44 for your #leds
* sudo python examples/baller.py


## Setup & restart sisbot to send position information over the dgram socket
* cd /home/pi/sisbot-server/sisbot
* cp ~/lights/sisbot/* .
* cd ../sisproxy
* sudo rm /var/log/sisyphus/*
* sudo ./restart.sh &


After the table gets running you should see ball positions priting out from the python program, and the lights changing position and color as Theta and Rho change.




