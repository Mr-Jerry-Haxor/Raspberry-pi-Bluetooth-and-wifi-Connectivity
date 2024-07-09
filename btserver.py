#!/usr/bin/env python3
# Desc: Bluetooth server application that uses RFCOMM sockets

import os
import sys
import time
import logging
import logging.config
import json
from bluetooth import *
import subprocess

def start_logging(default_path='configLogger.json', default_level=logging.INFO, env_key='LOG_CFG'):
    """Setup logging configuration"""
    path = default_path
    value = os.getenv(env_key, None)
    if value:
        path = value
    if os.path.exists(path):
        with open(path, 'rt') as f:
            config = json.load(f)
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)

class BLEServer:
    def __init__(self):
        self.server_socket = None
        self.client_socket = None
        self.service_name = "BluetoothServices"
        self.json_file = "text.json"
        self.uuid = "94f39d29-7d6d-437d-973b-fba39e49d4ee"
        self.logger = logging.getLogger('bleServerLogger')

    def setup_bluetooth_socket(self):
        self.server_socket = BluetoothSocket(RFCOMM)
        self.logger.info("Bluetooth server socket successfully created for RFCOMM service.")

    def bind_listen_bluetooth_socket(self):
        self.server_socket.bind(("", PORT_ANY))
        self.server_socket.listen(1)
        self.logger.info("Bluetooth server socket bind and listen setup successful.")

    def advertise_bluetooth_service(self):
        advertise_service(self.server_socket, self.service_name,
                          service_id=self.uuid,
                          service_classes=[self.uuid, SERIAL_PORT_CLASS],
                          profiles=[SERIAL_PORT_PROFILE])
        self.logger.info(f"{self.service_name} advertised successfully.")

    def accept_bluetooth_connection(self):
        self.client_socket, client_info = self.server_socket.accept()
        self.logger.info(f"Accepted bluetooth connection from {client_info}")
        self.send_data_to_client(f"Bluetooth connection Established")

    def receive_data(self):
        data = self.client_socket.recv(1024)
        if not data:
            return None
        return data

    def deserialize_data(self, data):
        if data:
            print(data)
            try:
                # Decode data from bytes to string before JSON deserialization
                data_str = data.decode('utf-8')
                data_obj = json.loads(data_str)
                self.logger.info("Data deserialized successfully.")
                return data_obj
            except json.JSONDecodeError:
                self.logger.error("Failed to deserialize data.", exc_info=True)
                return None
        else:
            self.logger.error("No data received to deserialize.")
            return None
        
    

    def write_to_json_file(self, data_obj):
        if data_obj:
            with open(self.json_file, 'w') as json_file:
                json.dump(data_obj, json_file, indent=4)
                self.logger.info(f"Data written successfully to {self.json_file}.")

    def close_sockets(self):
        if self.client_socket:
            self.client_socket.close()
        if self.server_socket:
            self.server_socket.close()
        self.logger.info("Bluetooth sockets closed successfully.")
    
    def send_data_to_client(self, message):
        if self.client_socket:
            try:
                # Convert the message to bytes and send
                self.client_socket.send(message.encode('utf-8'))
            except Exception as e:
                self.logger.error(f"Failed to send data to client: {e}", exc_info=True)

    def start(self):
        self.setup_bluetooth_socket()
        self.bind_listen_bluetooth_socket()
        self.advertise_bluetooth_service()
        self.accept_bluetooth_connection()

    def receive_process_data(self):
        data = self.receive_data()
        data_obj = self.deserialize_data(data)
        # Check if data contains ssid and password
        if data_obj and "ssid" in data_obj and "password" in data_obj:
            self.append_wifi_details_to_networkmanager(data_obj["ssid"], data_obj["password"])
        elif data_obj and "wifistatus" in data_obj:
            self.excute_cmd_and_return_data(
                """sudo nmcli dev wifi | awk '
BEGIN {print "SSID\t\t\t\t\tConnected Status"} 
NR==1 {next} 
$1 == "*" {print $3 "\t\t\t\t\tConnected"} 
$1 != "*" && $1 != "IN-USE" {print $2 "\t\t\t\t\tNot Connected"} 
$1 != "*" && $1 == "IN-USE" {print $3 "\t\t\t\t\tNot Connected"}'"""
                                            )
        elif data_obj and "cmd" in data_obj:
            self.excute_cmd_and_return_data(data_obj["cmd"])
        elif data_obj and "wifiscan" in data_obj:
            self.excute_cmd_and_return_data(
        """sudo nmcli dev wifi | awk '
BEGIN {print "wifiscan_data"} 
NR==1 {next} 
$1 == "*" {print $3 "| Connected"} 
$1 != "*" && $1 != "IN-USE" {print $2} 
$1 != "*" && $1 == "IN-USE" {print $3}'
        """
            )
        elif data_obj and "reboot" in data_obj:
            self.excute_cmd_and_return_data("sudo reboot")
        elif data_obj and "shutdown" in data_obj:
            self.excute_cmd_and_return_data("sudo shutdown -h now")
        elif data_obj and "test" in data_obj:
            self.logger.log(logging.INFO, "test connection succeeded")
            
    
    def excute_cmd_and_return_data(self, cmd):
        # send the output to the client
        try:
            output = subprocess.check_output(cmd, shell=True)
            self.send_data_to_client(output.decode('utf-8'))
        except subprocess.CalledProcessError as e:
            self.send_data_to_client(f"Failed to execute command: {e.stderr}")

    def append_wifi_details_to_networkmanager(self, ssid, password):
        try:
            # Construct the command with ssid and password
            command = f'sudo nmcli device wifi connect {ssid} password {password} ifname wlan0'
            # Execute the command
            result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            # Log the output
            #self.logger.info(f"Command output: {result.stdout}")
            self.send_data_to_client(f"Wi-Fi connected successfully to {ssid}.\nCommand output: {result.stdout}")
        except subprocess.CalledProcessError as e:
                    self.send_data_to_client(f"Failed to connect to Wi-Fi.\nCommand failed: {e.stderr}")


    def stop(self):
        self.close_sockets()

if __name__ == '__main__':
    while True:
        start_logging()
        ble_server = BLEServer()
        try:
            ble_server.start()
            while True:
                ble_server.receive_process_data()
        except KeyboardInterrupt:
            break
        finally:
            ble_server.stop()
