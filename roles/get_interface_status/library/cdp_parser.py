import os
import re
import socket
import sys
import time
import pandas as pd
import json
# from pprint import pprint

"""
This script parses the "show cdp entry all|*" outputs and creates a json output:
  -> Command output:
    HCS-METRO-01# show cdp entry all
    ...
    ----------------------------------------
    Device ID:MOB-METRO-02(JPG2025002Q)
    System Name:MOB-METRO-02
    Interface address(es):
        IPv4 Address: 172.26.67.253
    Platform: N77-C7702, Capabilities: Router Switch Supports-STP-Dispute 
    Interface: Ethernet1/24/4, Port ID (outgoing port): Ethernet1/7/1
    Holdtime: 160 sec

    Version:
    Cisco Nexus Operating System (NX-OS) Software, Version 7.3(5)D1(1)

    Advertisement Version: 2
    Duplex: full
    ----------------------------------------
    
  -> First step to get structured data:
    {
      "HCS-METRO-01": {
        remote_device: "MOB-METRO-02",
        mgmt_ip: "172.26.67.253",
        platform: "N77-C7702",
        capabilities: "Router Switch Supports-STP-Dispute",
        local_int: "Ethernet1/24/4",
        remote_int: "Ethernet1/7/1",
        version: "Cisco Nexus Operating System (NX-OS) Software, Version 7.3(5)D1(1)"
      },
      ...
    }
  
  -> The next step is to get a JSON Output:
    [
        {
            local_device: "HCS-METRO-01",
            remote_device: "MOB-METRO-02",
            mgmt_ip: "172.26.67.253",
            platform: "N77-C7702"
            local_int: "Ethernet1/24/4"
            remote_int: "Ethernet1/7/1"
            version: "Cisco Nexus Operating System (NX-OS) Software, Version 7.3(5)D1(1)"
        },
        {
            ...
        }
    ]
  -> CDP output fields are mapped to the JSON output as follows:
            remote_device: "System Name:",
            mgmt_ip: "IPv4 Address:",
            platform: "Platform:"
            local_int: "Interface:"
            remote_int: "Port ID (outgoing port):"
            version: "Version:" <-- insert the next line after "Version:"         
"""

### raw_output contains the show cdp entry all|* output from one network devices!

def parser_cdp_output(output_raw):
  local_device = ''
  # net_link = {}
  loop_flag = False
  # Convert the raw output into a list of lines
  output_lines = output_raw.split('\n')
  
  # Remove empty lines from the list
  output_lines = [i for i in output_lines if i]

  for line in output_lines:
  # for i in range(len(output_lines)):
  #   line = output_lines[i]

    if ('#' in line) and ('cdp' in line):
      # Parse a line containing the device hostname
      # where the show cdp entry command was issued
      (local_device, junk) = line.split('#')
      local_device = local_device.strip().strip('\ufeff\ufeff')

    if '------------------' in line:
      loop_flag = True
      flag_append = False

      ### Reset net_link and define the order of keys in the dictionary
      net_link = {
        'local_device': '',
        'local_int': '',
        'remote_device': '',
        'remote_int': '',
        'remote_platform': '',
        'remote_capabilities': '',
        'remote_ip_cdp': ''
      }
      net_link['local_device'] = local_device
      remote_device = ''

    ### Use loop_flag to populate cdp data of one link between the following lines:
    ### - the start line contains '------------------'
    ### - the end line contains "Holdtime:"
    if loop_flag:
      if 'Device ID:' in line:
        (junk, remote_device) = line.split('Device ID:')
        remote_device = remote_device.strip()

        if '.' in remote_device:
          (remote_device, junk) = re.split('\..*', remote_device)

        if '(' in remote_device:
          (remote_device, junk) = re.split('\(', remote_device)
        
        net_link['remote_device'] = remote_device

      if ('IPv4 Address:' in line) or ('IP address:' in line) or ('IPv4 address:' in line):
        (junk, remote_ip) = line.split(':')
        remote_ip = remote_ip.strip()
        net_link['remote_ip_cdp'] = remote_ip

      if 'Platform:' in line:
        (platform, capabilities) = line.split(',')
        (junk, platform) = re.split('Platform: ', platform)
        platform = platform.strip('cisco ')
        (junk, capabilities) = re.split('Capabilities: ', capabilities)
        net_link['remote_platform'] = platform
        net_link['remote_capabilities'] = capabilities

      if ('Interface:' in line) and ('Port ID' in line):
        (local_int, remote_int) = line.split(',')
        (junk, local_int) = re.split('Interface: ', local_int)
        (junk, remote_int) = re.split('.*: ', remote_int)
        net_link['local_int'] = local_int
        net_link['remote_int'] = remote_int
        flag_append = True

      ### Need to parse IOS-XR outputs in another way:
      if ('Interface:' in line) and ('Port ID' not in line):
        (junk, local_int) = re.split('Interface: ', line)
        net_link['local_int'] = local_int

      if ('Interface:' not in line) and ('Port ID' in line):
        (junk, remote_int) = re.split('Port ID.*: ', line)
        net_link['remote_int'] = remote_int
        flag_append = True

      ### Append collected cdp data of one link to the parsed output
      if flag_append:
        ALL_CDP_DATA_PARSED.append(net_link)
        flag_append = False
        loop_flag = False
      
      continue

def save2json(data,filename):
  json_data = json.dumps(data, indent=2)
  with open(filename, 'w') as f:
      f.write(json_data)

def main(path):
  
  # dirname = os.path.dirname(__file__)
  # path = os.path.join(dirname, path)
  # for filename in os.listdir(path):
  #   with open(os.path.join(path,filename), 'r') as f:
  #     output_raw = f.read()
  #   parser_cdp_output(output_raw)

  os.makedirs(path_output_dir, exist_ok=True)
  
  with open(input_data) as f:
    output_raw = f.read()

  parser_cdp_output(output_raw)

  ### Create Pandas DataFrame from the ALL_CDP_DATA_PARSED list
  ### To save the parsed cdp data to an excel file
  pd.DataFrame(ALL_CDP_DATA_PARSED).to_excel(output_excel)

  ### Save parsed CDP data as a JSON file
  DATA2JSON = {"links": ALL_CDP_DATA_PARSED}
  save2json(DATA2JSON,output_json)

if __name__ == "__main__":
  stdin_read = sys.stdin.readlines()
  input_vars = stdin_read[0].rstrip('\n')
  input_folder,device_hostname = input_vars.split(',')  

  input_data = "../../../outputs/" + input_folder + "/command_outputs/" + device_hostname + "_show_cdp_entry.txt"

  path_output_dir = os.path.join("../../../outputs/",input_folder,"cdp_parser_outputs")
  output_json = path_output_dir + "/" + device_hostname + ".json"
  output_dict2json = path_output_dir + "/" + device_hostname + "_dict.json"
  output_csv = path_output_dir + "/" + device_hostname + ".csv"
  output_excel = path_output_dir + "/" + device_hostname + ".xlsx"

  ALL_CDP_DATA_PARSED = []

  main(path_output_dir)