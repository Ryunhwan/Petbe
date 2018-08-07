# Petbe

The project Petbe is tracking Pet's location in home using 3 Raspi(Beacon signal scanner). A Beacon attach with users pet, 3 scanner track it.

## Contents

* Main
* Sub1
* Sub2

The file is executed on Raspberry Pi.

## Hardware Spec
* Raspberry Pi 3 model B+
* BLE dongle (attached with Raspi, model is not matter)
* Beacon [B4 BeaFon](http://global.11st.co.kr/product/SellerProductDetail.tmall?method=getSellerProductDetail&prdNo=1732219552#) (But the model is not matter)

## Configuration

[**1. Scanning System Install**](http://www.switchdoc.com/2014/08/ibeacon-raspberry-pi-scanner-python/)
```sh
sudo apt-get update && sudo apt-get upgrade
sudo apt-get install libusb-dev
sudo apt-get install libdbus-1-dev
sudo apt-get install libglib2.0-dev --fix-missing
sudo apt-get install libudev-dev
sudo apt-get install libical-dev
sudo apt-get install libreadline-dev
sudo apt-get install libdbus-glib-1-dev
sudo mkdir bluez
cd bluez
sudo wget www.kernel.org/pub/linux/bluetooth/bluez-5.19.tar.gz
sudo gunzip bluez-5.19.tar.gz
sudo tar xvf bluez-5.19.tar
cd bluez-5.19
sudo ./configure --disable-systemd
sudo make
sudo make install
sudo apt-get install python-bluez
sudo shutdown -r now
```

**2. Mount Dongle**

First, insert a dongle on Raspi any USB port
```
lsusb                         Check dongle connect
hciconfig                     Check dongle port number(Maybe inner Bluetooth is hci0, new dongle is hci1) 
```

Swap two port number. if you skip, you'll get an error in code 
```
sudo hciconfig hci0 down      Connect down Inner Bluetooth
sudo reboot                   Save and reboot
```

**3. AutoRun**

Follow it if you want the code autorun when raspi is rebooted
```
sudo nano ~/.config/lxsession/LXDE-pi/autostart
@sudo /usr/bin/python /home/pi/iBeacon-Scanner-/testblescan.py    add it below
```
save the file use `control + x`(Nano editor save key)
```
sudo chmod +x /home/pi/iBeacon-Scanner-/testblescan.py            add execute permission
```
