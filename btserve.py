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

    def receive_data(self):
        data = self.client_socket.recv(1024)
        if not data:
            return None
        return data

    def deserialize_data(self, data):
        if data:
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
        self.write_to_json_file(data_obj)
        # Check if data contains ssid and password
        if data_obj and "ssid" in data_obj and "password" in data_obj:
            self.append_wifi_details_to_wpa_supplicant(data_obj["ssid"], data_obj["password"])
            self.reconfigure_wifi_interface()
        elif data_obj and "cmd" in data_obj:
            self.excute_cmd_and_return_data(data_obj["cmd"])
    
    def excute_cmd_and_return_data(self, cmd):
        # send the output to the client
        try:
            output = subprocess.check_output(cmd, shell=True)
            self.send_data_to_client(output.decode('utf-8'))
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to execute command: {e}", exc_info=True)
            self.send_data_to_client(f"Failed to execute command: {e}")

    def append_wifi_details_to_wpa_supplicant(self, ssid, password):
        wifi_config = f'\nnetwork={{ ssid="{ssid}" psk="{password}"}}\n'
        with open("/etc/wpa_supplicant/wpa_supplicant.conf", "a") as file:
            file.write(wifi_config)
        self.logger.info("Wi-Fi details appended to wpa_supplicant.conf.")
        self.send_data_to_client("Wi-Fi details appended to wpa_supplicant.conf successfully.")

    def reconfigure_wifi_interface(self):
        try:
            # subprocess.run(["sudo", "wpa_cli", "-i", "wlan0", "reconfigure"], check=True)
            subprocess.run(["sudo", "systemctl", "restart", "wpa_supplicant"], check=True)
            self.logger.info("Wi-Fi interface reconfigured successfully.")
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to reconfigure Wi-Fi interface: {e}")

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
