# Raspberry-pi-Bluetooth-and-wifi-Connectivity
This project is developed to make the Raspberry Pi Bluetooth to auto connect with any devices and  control wifi connectivity 


# Pre-quisites
This python-script uses Bluez, Linux's Bluetooth protocol stack, we'll be using PyBluez, a Python API for accessing the bluetooth resources using the bluez protocol.

Installation
```
sudo apt-get install python3-pip python3-dev ipython3

sudo apt-get install bluetooth libbluetooth-dev

sudo apt-get install bluez-utils blueman

sudo apt install snapd

sudo snap install bluez

sudo apt-get install python3-bluez

sudo pip install pybluez
```

# Edit bluetooth config file 
You need to run the Bluetooth daemon in 'compatibility' mode. Edit /lib/systemd/system/bluetooth.service and add '-C' after ' <other_data>/bluetoothd'. Reboot.

```
sudo nano /lib/systemd/system/bluetooth.service
```
```
sudo sdptool add SP
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
# Create the Service File
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

## To make it auto connect

# created a new file
```
sudo nano /usr/lib/systemd/system/bt-agent
```
# paste all the below code in that file

```
[Unit]
Description=Bluetooth Auth Agent
After=bluetooth.service
PartOf=bluetooth.service

[Service]
Type=simple
ExecStart=/usr/bin/bt-agent -c DisplayOnly -p /opt/pin
Restart=always
RestartSec=3
User=root
[Install]
WantedBy=bluetooth.target
```
Once you've added details, save and close the file by pressing CTRL + X, then Y to confirm the changes, and Enter to exit.


# create another fiele
```
sudo nano /opt/pin
```

# paste below code
```
* *
```
# created a service that would start after reboot
```
sudo systemctl start bt-agent
```
```
sudo systemctl enable bt-agent
```

# now check the status
```
sudo systemctl status bt-agent
```
# if it is working or not, if it shows "active" then it's working , if it shows "failed" then it is  not working 
# if it is failed run 
```
sudo systemctl daemon-reload
```
```
sudo systemctl restart bt-agent
```

## now Try to connect to the bluetooth of raspberry , it will connect automatically.
