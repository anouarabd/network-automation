## This script allows you to configure interfaces with their corresponding Vlans by getting details (interface number,mode,vlan list, description) from a CSV file
## a CSV example is available in this repository
## Anouarabd
 
from netmiko import ConnectHandler
from getpass import getpass
import csv

user = input("Username : ")
pwd = getpass('Password : ')

## Getting devices' list from a text file ; IP Address per line

with open('devices_file') as f:
    devices_list = f.read().splitlines()

## Opening VLAN assignment file ; includes ports and corresponding vlans

with open('vlan_assignment.csv', 'r' ) as v:
    reader = csv.reader(v, delimiter=';')
    next(reader)

    for devices in devices_list:
        print('Connecting to switch ' + devices)
        ip_address_of_device = devices
        ios_device = {
            'device_type': 'cisco_ios',
            'ip': ip_address_of_device,
            'username': user,
            'password': pwd
        }
        net_connect = ConnectHandler(**ios_device)
        for line in reader:
         line = list(line)

         ## Check if port is port is Access or Trunk and make suitable config

         if 'TRUNK' == str(line[1]).upper():
               cfg_commands = "interface Gi0/" + line[0], "switchport mode trunk", "switchport trunk allowed vlan " + line[2], "description " + line[3]
               output = net_connect.send_config_set(cfg_commands)
               print(output)
         if 'ACCESS' == str(line[1]).upper():
               cfg_commands = "interface Gi0/" + line [0], "switchport mode access" , "switchport access vlan " + line [2], "description " + line [3]
               output = net_connect.send_config_set(cfg_commands)
               print(output)

