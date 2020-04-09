## This script allows you to configure a VLAN list from a CSV file
## anouarabd

from netmiko import ConnectHandler
from getpass import getpass
import csv

# Username & Password prompts

user = input("Username : ")
pwd = getpass('Password : ')

## Opening file including IPs

with open('devices_file') as f:
    devices_list = f.read().splitlines()

## Opening VLAN list CSV file with ";" as delimiter

with open('vlans_list.csv', 'r' ) as v:
    reader = csv.reader(v, delimiter=';')
    next(reader)
    list = dict()

## Converting data into a dictionary

    for row in reader:
        list [row[0]] = row [1]
        
## Connecting to devices and configuring VLAN

    for devices in devices_list:
        print('Connecting to switch with IP ' + devices)
        ip_address_of_device = devices
        ios_device = {
            'device_type': 'cisco_ios',
            'ip': ip_address_of_device,
            'username': user,
            'password': pwd
        }
        net_connect = ConnectHandler(**ios_device)
        for k , v in list.items():
         cfg_commands = "vlan " + str(k).strip() , "name " + str(v).strip()
         output = net_connect.send_config_set(cfg_commands)
         print(output)