from netmiko import ConnectHandler
from getpass import getpass
from datetime import date


with open('commands_file') as f:
    commands_list = f.read().splitlines()

#Commands here in Script instead of reading from file:

##commands_list = ['vlan 2, 'name VLAN_Anouar']

## Get the date

today = date.today()
today=today.strftime("%b-%d-%Y")

user = input("Username : ")
pwd = getpass('Password : ')
customer = input("Customer : ")

## Failed devices file

failed_devices_filename = customer + " Failed Devices "  + today ## Failed devices filename includes customer name and current date
dest_path = 'C:\\Users\\a.abdallah\\Desktop\\' + failed_devices_filename ## failed devices list will be written on Desktop
failed_devices_file = open (dest_path,"a") ## Create a new file


with open('devices_file') as f:
    devices_list = f.read().splitlines()

for devices in devices_list:
   try:
    print ('Connecting to ' + devices)
    ip_address_of_device = devices
    ios_device = {
        'device_type': 'cisco_ios',
        'ip': ip_address_of_device,
        'username': user,
        'password': pwd
    }

    net_connect = ConnectHandler(**ios_device)
    output = net_connect.send_config_set(commands_list)

    #print (output) ## enable if commands syntax check is needed ; commands differ from one device to another
    
    print('Configuration has been applied successfuly to ' + devices) 
   except:
        print('Connection to ' + devices + ' device has failed')
 
## Add failed device to file

        failed_devices_file.write(devices + ('\n'))
        failed_devices_file = open (dest_path,"a+") ## a+ mode to add devices into file and not delete
        pass

failed_devices_file.close()
