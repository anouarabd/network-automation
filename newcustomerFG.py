## This script allows you to create VDOM for new customer, configure WAN Interface (enhanced MAC, bridged to another WAN interface) and add a default route
## This script calls jinja2 template file
from netmiko import ConnectHandler
from getpass import getpass
from jinja2 import Environment, FileSystemLoader
import ipaddress



user = input("Username : ")
pwd = getpass('Password : ')
customer_name=input("Customer : ")
public_ip = input ("Public IP : ")
public_ip=str(ipaddress.ip_address(public_ip))

file_loader = FileSystemLoader('.')
env = Environment(loader=file_loader)
new_vdom_template = env.get_template('new_vdom.j2')
config = new_vdom_template.render(vdom_name=customer_name.upper(),ip_address=public_ip)

fortios_device = {
            'device_type': 'fortinet',
            'ip': '192.168.1.1',
            'port': '2658',
            'username': user,
            'password': pwd
        }
net_connect = ConnectHandler(**fortios_device)
output = net_connect.send_command_timing(config,delay_factor=1)
print(config)