## This script collects configuration & hardware data and saves them into one file
## Anouarabd

from netmiko import ConnectHandler
from getpass import getpass
from datetime import date

## Username & customer & password prompts

user = input("Username : ")
pwd = getpass('Password : ')
customer = input("Customer : ")

## Get the date

today = date.today()
today=today.strftime("%b-%d-%Y")

## Getting devices' list from a text file , syntax per line is   " hostname:IP "

with open('devices_file.txt') as f:
    devices_list = f.read().splitlines()

    for devices in devices_list:
        tmp = devices.split(':') ## file includes devicename:ipaddress
        ip_address_of_device = tmp[1]
        hostname_of_device = tmp[0]
        print('Connecting to ' + hostname_of_device)
        ios_device = {
            'device_type': 'cisco_ios',
            'ip': ip_address_of_device,
            'username': user,
            'password': pwd
        }
        net_connect = ConnectHandler(**ios_device)

        ## Data collect namefile
        data_collect_filename = customer + "_" + hostname_of_device + "_" + today
        dest_path = 'C:\\Users\\anouarabd\\Desktop\\' + data_collect_filename
        dest_config = open (dest_path,"w")

        ## Backup show run configuration

        out = net_connect.send_command('show run')
        dest_config.write(' *** SHOW RUNNING-CONFIG ***' + ('\n' * 3) + out + ('\n' * 3))
        print(out)

        ## Backup show version

        out = net_connect.send_command('show version')
        dest_config.write(' *** SHOW VERSION ***' + ('\n' * 3) + out + ('\n' * 3))
        print(out)

        ## Backup show inventory

        out = net_connect.send_command('show inventory')
        dest.write(' *** SHOW INVENTORY ***' + ('\n' * 3) + out)
        print(out)

        ## Close file

        dest_config.close()