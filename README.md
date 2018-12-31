# lights


cd /home/pi
git clone git@github.com:joelxxx/lights.git


Follow directions in 
~/lights/sisbot/system/install_python_strip.sh


Plug in the lights as shown in the photo
test the default lights program 
cd /home/pi/rpi_ws281x/python
sudo python examples/strandtest.py

If that works, start up the python program to listen on datagram socket for ball positions.

cp ~/lights/comm-prototyping/python/exmaples/baller.py examples

(you will need to modify the code for the number of leds in your strip)
(line 20 in baller.py  LED_COUNT      = 44      # Number of LED pixels. )
sudo python examples/baller.py


----- Setup the sisbot to send position information over the dgram socket
cd /home/pi/sisbot-server/sisbot
cp ~/lights/sisbot/* .

cd ../sisproxy
sudo rm /var/log/sisyphus/*
sudo ./restart.sh &


After the table gets running you should see ball positions priting out from the python program, and the lights changing position and color as Theta and Rho change.




