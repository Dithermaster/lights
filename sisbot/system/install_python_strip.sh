#
#  Install script to run the python DMA light strip controller on a PI
#
#  https://tutorials-raspberrypi.com/connect-control-raspberry-pi-ws2812-rgb-led-strips/
#
# The sed command on line 13 has not been tested yet
#
sudo apt-get update
sudo apt-get install python-dev
sudo cat > /etc/modprobe.d/snd-blacklist.conf
  blacklist snd_bcm2835

sudo sed -i 's/dtparam/#dtparam/g' /boot/config.txt
#sudo vi /boot/config.txt
  #dtparam=audio=on
git clone https://github.com/jgarff/rpi_ws281x
cd rpi_ws281x
sudo apt-get install scons
sudo scons

sudo apt-get install swig
cd python
wget https://pypi.python.org/packages/source/s/setuptools/setuptools-5.7.zip
sudo python ./setup.py build
sudo python ./setup.py install
sudo PYTHONPATH=".:build/lib.linux-armv7l-2.7" python examples/strandtest.py

