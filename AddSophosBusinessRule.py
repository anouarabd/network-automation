## This script calls Sophos XG XML API
## This script allows you to create Sophos business application rule by entering only : public IP & private IP & service & policy name
## Script will check if objects already exist and will show you objects' names, otherwise it will automatically create them and ask you to choose the name
## Protected server's zone is automatically detected by checking subinterfaces IP
## Anouarabd

import sys
import requests
import ipaddress
import argparse
from getpass import getpass
import xml.etree.ElementTree as ElementTree
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning) ## Do not display self-signed certificate warning

## Shared data

username= input("Firewall username :  ")
password = getpass("Password : ")
login="""<Request><Login><Username>"""+username+"""</Username><Password passwordform="plain">""" + password + """</Password></Login>"""
url = 'https://192.168.1.254:4443/webconsole/APIController?reqxml='


## Reading private & public IP && policy name
private_ip = input("Protected server IP address : ")
private_ip=str(ipaddress.ip_address(private_ip))
public_ip = input ("Public IP : ")
public_ip=str(ipaddress.ip_address(public_ip))
policy_name=input("Business application rule name : ")

## Reading services' list

x = [str(x) for x in input("List of service, separate using a whitespace : ").split()]
services=''
for test in range(len(x)):
    service="""<Service>""" + x[test].strip().upper() + """</Service>"""
    services +=service
## Check zone of Private IP ; all protected servers are directly connected and their gateways are subinterfaces in FW

GetVlanObjects="""<Get><VLAN></VLAN></Get></Request>"""
GetVlanResponse = requests.get(url+login+GetVlanObjects, verify = False).content
root = ElementTree.fromstring(GetVlanResponse)
if ipaddress.ip_address(private_ip) in ipaddress.ip_network('192.168.58.0/24'): ## Exceptional case ; forcing it manually
    detected_zone = "MGMT"
for data in root.findall('VLAN'):
      IPAddress = data.find('IPAddress').text
      tmp=IPAddress.split('.')
      interface_subnet=tmp[0]+"." +tmp[1]+"."+tmp[2]+"."+"0/24"
      zone = data.find('Zone').text
      if ipaddress.ip_address(private_ip) in ipaddress.ip_network(interface_subnet):
          detected_zone=zone
print("This server belongs to  " + detected_zone + " zone")

## Looking for private host object name/existence

GetPrivateHostObject="""<Get><IPHost><Filter><key name="IPAddress" criteria="like">""" + private_ip + """</key></Filter></IPHost></Get></Request>"""
GetPrivateHostResponse = requests.get(url+login+GetPrivateHostObject, verify = False).content
root = ElementTree.fromstring(GetPrivateHostResponse)
#print(GetPrivateHostResponse)

## If private object exists captures its name, if not ask for the new name

private_host_existence = 'Name' in str(GetPrivateHostResponse)
if private_host_existence:
      host_private_name = root.find('IPHost').find('Name').text
      print("Host object with IP " + private_ip + " is already existing under the name "+ host_private_name)
      #print(private_host_existence)
if not private_host_existence:
      host_private_name= input("No host with " + private_ip + " already exists, choose the name of object : ")
      AddPrivateHostXML = """<Set operation="add"><IPHost><Name>""" + host_private_name + """</Name><IPFamily>IPv4</IPFamily><HostType>IP</HostType><IPAddress>""" + private_ip + """</IPAddress></IPHost></Set></Request>"""
      AddPrivateHostRequest = requests.post(url + login + AddPrivateHostXML, verify=False).content
      #print (AddPrivateHostRequest)

## Looking for public host object name/existence

GetPublicHostObject="""<Get><IPHost><Filter><key name="IPAddress" criteria="like">""" + public_ip + """</key></Filter></IPHost></Get></Request>"""
GetPublicHostResponse = requests.get(url+login+GetPublicHostObject, verify = False).content
root = ElementTree.fromstring(GetPublicHostResponse)
#print(GetPublicHostResponse)

## If public object exists captures its name, if not ask for the new name

public_host_existence = 'Name' in str(GetPublicHostResponse)
if public_host_existence:
      host_public_name = root.find('IPHost').find('Name').text
      print("Host object with IP " + public_ip + " is already existing under the name "+ host_public_name)
if not public_host_existence:
      host_public_name= input("No host with " + public_ip + " already exists, choose the name of object : ")
      AddPublicHostXML = """<Set operation="add"><IPHost><Name>""" + host_public_name + """</Name><IPFamily>IPv4</IPFamily><HostType>IP</HostType><IPAddress>""" + public_ip + """</IPAddress></IPHost></Set></Request>"""
      AddPublicHostRequest = requests.post(url + login + AddPublicHostXML, verify=False).content
      #print(AddPublicHostRequest)

AddDNATXML ="""<Set operation="add"><SecurityPolicy><Name>""" + policy_name + """</Name><Description/><IPFamily>IPv4</IPFamily><Status>Enable</Status><Position>After</Position><PolicyType>NonHTTPBased</PolicyType><After><Name>PUBLICATION_ABF_NOUVEAU_SITEWEB</Name></After><NonHTTPBasedPolicy><SourceZones><Zone>WAN</Zone></SourceZones><HostedAddress>"""+ host_public_name +"""</HostedAddress><ScanSMTP>Disable</ScanSMTP><ScanSMTPS>Disable</ScanSMTPS><ProtectedZone>""" + detected_zone.upper() +"""</ProtectedZone><ProtectedServer>"""+ host_private_name + """</ProtectedServer><MappedPort/><RewriteSourceAddress>Disable</RewriteSourceAddress><OutboundAddress/><ReflexiveRule>No</ReflexiveRule></NonHTTPBasedPolicy><LogTraffic>Disable</LogTraffic><MatchIdentity>Disable</MatchIdentity><IntrusionPrevention>None</IntrusionPrevention><TrafficShappingPolicy>None</TrafficShappingPolicy><SourceSecurityHeartbeat>Disable</SourceSecurityHeartbeat><MinimumSourceHBPermitted>No Restriction</MinimumSourceHBPermitted><DestSecurityHeartbeat>Disable</DestSecurityHeartbeat><MinimumDestinationHBPermitted>No Restriction</MinimumDestinationHBPermitted><Services>"""+services+"""</Services></SecurityPolicy></Set></Request>"""
AddDNATRequest = requests.post(url + login + AddDNATXML, verify=False).content
success = 'applied successfully' in str(AddDNATRequest)
if success:
    print('\n' + policy_name " rule was added successfully")
else:
    print(AddDNATRequest)
