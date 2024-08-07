# Raspberry-pi-Bluetooth-and-wifi-Connectivity

This project is developed to make the Raspberry Pi Bluetooth to auto connect with any devices and  control wifi connectivity

# Pre-quisites

## Bluetooth power on and make it discoverable 

```
sudo rfkill unblock bluetooth
```
Modify Discoverable Timeout 
```
sudo nano /etc/bluetooth/main.conf
```
uncomment and set value "DiscoverableTimeout = 0" 
and save and close the file by pressing CTRL + X, then Y to confirm the changes, and Enter to exit.



next 


Create a new service file
```
sudo nano /etc/systemd/system/bluetooth-setup.service
```
paste the below script , save and close the file by pressing CTRL + X, then Y to confirm the changes, and Enter to exit.
```
[Unit]
Description=Bluetooth Setup Service
After=bluetooth.service

[Service]
Type=oneshot
ExecStartPre=/bin/sleep 5
ExecStart=/bin/sh -c '/usr/bin/bluetoothctl power on && /usr/bin/bluetoothctl pairable on && /usr/bin/bluetoothctl discoverable on'
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
```
run below commands
```
sudo chmod 644 /etc/systemd/system/bluetooth-setup.service

sudo systemctl daemon-reload

sudo systemctl enable bluetooth-setup.service
```
Reboot the Raspberry pi
```
sudo reboot
```


Turn on Bluetooth  on boot
```
sudo systemctl start bluetooth

sudo systemctl enable bluetooth
```

This python-script uses Bluez, Linux's Bluetooth protocol stack, we'll be using PyBluez, a Python API for accessing the bluetooth resources using the bluez protocol.

Installation

```
sudo apt-get install python3-pip python3-dev ipython3

sudo apt-get install bluetooth libbluetooth-dev

sudo apt-get install blueman

sudo apt-get install python3-bluez

sudo apt-get install bluez-tools

```


## Edit bluetooth config file

You need to run the Bluetooth daemon in 'compatibility' mode. Edit /lib/systemd/system/bluetooth.service and add '-C' after 'ExecStart=/usr/libexec/bluetooth/bluetoothd'. like this "ExecStart=/usr/libexec/bluetooth/bluetoothd -C" and now  Reboot Raspberry Pi. 

```
sudo nano /lib/systemd/system/bluetooth.service
```
save and close the file by pressing CTRL + X, then Y to confirm the changes, and Enter to exit.

Reboot the Raspberry pi
```
sudo reboot
```
After reboot run the following command.
```
sudo sdptool add SP
```

Reset adaptor
```
sudo hciconfig -a hci0 reset
```

## Bluetooth SERVER code

```
git clone https://github.com/Mr-Jerry-Haxor/Raspberry-pi-Bluetooth-and-wifi-Connectivity.git

cd Raspberry-pi-Bluetooth-and-wifi-Connectivity

sudo cp btserver.py /opt/btserver.py

sudo mkdir -p /var/log/btserver

sudo touch /var/log/btserver/btserver.log

sudo chmod -R 777 /var/log/btserver

```

## Create the Service File

Create a systemd service file using a text editor. This file will define how your service should behave.

```
sudo nano /etc/systemd/system/btserver.service
```

Paste the following content into the file

```
[Unit]
Description=Custom Bluetooth Service
After=network.target

[Service]
Type=simple
ExecStartPre=/bin/mkdir -p /var/log/btserver
ExecStart=sudo /usr/bin/python3 /opt/btserver.py > /var/log/btserver/btserver.log 2>&1
Restart=always
RestartSec=3
User=root   
Group=root  

[Install]
WantedBy=multi-user.target
```

Ensure that your Python script /opt/btserver.py has execute permissions. You can set it with:

```
sudo chmod +x /opt/btserver.py
```

Reload systemd and Start the Service
After creating the service file, reload systemd to read the new service file and start the service:

```
sudo systemctl daemon-reload

sudo systemctl start btserver
```

Enable the Service to Start on Boot

```
sudo systemctl enable btserver
```

Check the Status
You can check the status of your service to ensure it's running without errors:

```
sudo systemctl status btserver
```

# To make Raspberry pi bluetooth to Auto connect

## created a another service file

```
sudo nano /usr/lib/systemd/system/bt-agent.service
```

paste all the below code in that file

```
[Unit]
Description=Bluetooth Auth Agent
After=bluetooth.service
PartOf=bluetooth.service

[Service]
Type=simple
ExecStartPre=/bin/sleep 30
ExecStart=/usr/bin/bt-agent -c DisplayOnly -p /opt/pin
Restart=always
RestartSec=3
User=root
[Install]
WantedBy=bluetooth.target
```

Once you've added details, save and close the file by pressing CTRL + X, then Y to confirm the changes, and Enter to exit.

create another file

```
sudo nano /opt/pin
```

paste below code into the file, save and close the file by pressing CTRL + X, then Y to confirm the changes, and Enter to exit.

```
* *
```

created a service that would start after reboot

```
sudo systemctl start bt-agent
```

```
sudo systemctl enable bt-agent
```

now check the status

```
sudo systemctl status bt-agent
```

if it is working or not, if it shows "active" then it's working , if it shows "failed" then it is  not working
if it is failed run

```
sudo systemctl daemon-reload
```

```
sudo systemctl restart bt-agent
```
Reboot the Raspberry pi
```
sudo reboot
```

### Now Try to connect to the bluetooth of raspberry , it will connect automatically Through the below APP

[Raspberry PI controller APP](https://github.com/Mr-Jerry-Haxor/Raspberry-pi-Bluetooth-and-wifi-Connectivity/releases/download/Raspberry-pi-controller-APP-v1/Raspberry.Pi.controller.v1.apk)

OR
Check realease for latest APK file . 

https://github.com/Mr-Jerry-Haxor/Raspberry-pi-Bluetooth-and-wifi-Connectivity/releases

NOTE: 
Before using the App , open Bluetooth of your mobile and connect with the Raspberry pi bluetooth.
USE 2.4GHz wifi band in mobile hotspot, while connecting to mobile hotspot.
