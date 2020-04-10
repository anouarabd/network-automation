## This script gets all interfaces configuration by running "show running-config | section interfaces Gi " and adds your personal configuration
## for interfaces which are assigned to a particular vlan
## it can be used to configure dot1x for a specific users' vlan (dot1x configuration per interface should be available in "commands_file.txt" file)
## script saves the original configuration and the new generated one in two separate files
## Anouarabd

from netmiko import ConnectHandler
from getpass import getpass
from ciscoconfparse import CiscoConfParse

# Prompts username, password, existing users' vlan to enable dot1x on

user = input("Username : ")
pwd = getpass('Password : ')
vlan = input("Users vlan : ")

## Getting devices' list from a text file ; IP Address per line

with open('devices_file.txt') as f:
    devices_list = f.read().splitlines()

## Reading new interfaces' commands from file

with open('commands_file.txt') as c:
    commands_list = c.read().splitlines()

## Connecting to device and importing existing interfaces' configuration

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
        net_connect.enable()

        out = net_connect.send_command('show run | sec interface Gi')

        ## save the original configuration for each device and overwrite file with every execution

        original_config_filename = "old_config" + "_" + ip_address_of_device
        original_config = open (original_config_filename,"a")
        original_config.seek(0)
        original_config.truncate()
        original_config.write(out)
        original_config.close()
        parse = CiscoConfParse(original_config_filename)

        # Add required configuration under interface configuration (reading new commands from file)

        for intf in parse.find_objects(r'^interface.+?thernet'):
            is_access_vlan_users = intf.has_child_with(r'switchport access vlan ' + str(vlan))
            if is_access_vlan_users:
                for cmd in commands_list:
                    intf.append_to_family(" " + str(cmd))

         ## save the new configuration in file

        new_config_filename = "new_config" + "_" + ip_address_of_device
        parse.save_as(new_config_filename)

         ## delete unnecessary lines 'Building configuration' 'size' ..

        lines = open(new_config_filename).readlines()
        open(new_config_filename,'w').writelines(lines[3:-1])

        ## open the new configuration file and push it to device

        with open(new_config_filename) as n:
            cfg_commands = n.read().splitlines()
            output = net_connect.send_config_set(cfg_commands)
            net_connect.disconnect()
            print(output)
