# Petbe

The project Petbe is tracking Pet's location in home using 3 Raspi(Beacon signal scanner). A Beacon attach on pet, 3 scanner track it.

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

**2. Mount BLE Dongle**

First, insert a dongle on Raspi any USB port
```
lsusb                             Check dongle connect
hciconfig                         Check dongle port number(maybe inner Bluetooth is hci0, dongle is hci1)
```

Swap two port number. if you skip, you'll get an error in code 
```
sudo hciconfig hci0 down           Connect down inner Bluetooth
sudo reboot                        Save and reboot
```

**3. AutoRun**

Follow it if you want the code autorun when raspi is rebooted
```
sudo nano ~/.config/lxsession/LXDE-pi/autostart                   open autostart script
@sudo /usr/bin/python /home/pi/iBeacon-Scanner-/testblescan.py    add it below
```
And save the file use `control + x`(Nano editor save key)
```
sudo chmod +x /home/pi/iBeacon-Scanner-/testblescan.py            add execute permission
```

**4. Static IP Address Setting**

Raspies are have to connected with one router, so I set a static IP adress for each Raspi.

Main(server): `192.168.1.150`, Sub1 is `192.168.1.151`, and Sub2 is `192.168.1.152`
```
sudo nano /etc/dhcpcd.conf                open setting script
netstat -nr                               check the router address
```
And setting like below
```
interface wlan0
static ip_address=192.168.x.xxx/24        static address you want
static routers=192.168.x.x                the address of 'netstat -nr'
static domain_name_servers=192.168.x.x    same with above
```
And save the file use `control + x`(Nano editor save key)
```
sudo reboot                                Save and reboot
```
