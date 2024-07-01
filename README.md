# Raspberry-pi-Bluetooth-and-wifi-Connectivity
This project is developed to make the Raspberry Pi Bluetooth to auto connect with any devices and  control wifi connectivity 


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
User=root
[Install]
WantedBy=bluetooth.target
```
# save it and exit :  Ctrl + x and Y


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
