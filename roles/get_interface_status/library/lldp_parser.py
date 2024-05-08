import os
import re
import socket
import sys
import time
import pandas as pd
import json
# from pprint import pprint

"""
This script parses the "show lldp entry" outputs and creates a json output:
  -> Command output:
    CALAX04-DC1AS-02A# show lldp entry 
    Capability codes:
    (R) Router, (B) Bridge, (T) Telephone, (C) DOCSIS Cable Device
    (W) WLAN Access Point, (P) Repeater, (S) Station, (O) Other
    Device ID            Local Intf      Hold-time  Capability  Port ID  

    Chassis id: 0024.98e8.1ed9
    Port id: Eth7/18
    Local Port id: mgmt0
    Port Description: CALAX04-DC1AS-02A_mgmt0
    System Name: DC-DIST7-1.paramount.com
    System Description: Cisco NX-OS(tm) n7000, Software (n7000-s1-dk9), Version 6.2(10), RELEASE SOFTWARE Copyright (c) 2002-2013 by Cisco Systems, Inc. Compiled 10/9/2014 12:00:00
    Time remaining: 108 seconds
    System Capabilities: B, R
    Enabled Capabilities: B, R
    Management Address: 0024.98e8.1ed9
    Management Address IPV6: not advertised
    Vlan ID: 500     


    Chassis id: c89c.1dd4.3b7c
    Port id: Eth3/1
    Local Port id: Eth1/5
    Port Description: CALAX04-DC1AS-02A
    System Name: DC-DIST7-1.paramount.com
    System Description: Cisco NX-OS(tm) n7000, Software (n7000-s1-dk9), Version 6.2(10), RELEASE SOFTWARE Copyright (c) 2002-2013 by Cisco Systems, Inc. Compiled 10/9/2014 12:00:00
    Time remaining: 98 seconds
    System Capabilities: B, R
    Enabled Capabilities: B, R
    Management Address: c89c.1dd4.3b7c
    Management Address IPV6: not advertised
    Vlan ID: 1     

    ...
    ----------------------------------------
    
  -> First step to get structured data:
    {
      "CALAX04-DC1AS-02A": {
        local_port_id: "mgmt0",
        remote_chassis_id: "0024.98e8.1ed9",
        remote_port_id: "Eth7/18",
        remote_port_description: "CALAX04-DC1AS-02A_mgmt0",
        remote_system_name: "DC-DIST7-1.paramount.com",
        remote_system_description: "Cisco NX-OS(tm) n7000, Software (n7000-s1-dk9), Version 6.2(10), RELEASE SOFTWARE Copyright (c) 2002-2013 by Cisco Systems, Inc. Compiled 10/9/2014 12:00:00",
        remote_system_capabilities: "B, R",
        remote_enabled_capabilities: "B, R",
        remote_mgmt_address: "0024.98e8.1ed9",
        remote_mgmt_address_ipv6: "not advertised",
        remote_vlan_id: "500",
      },
      ...
    }
  
  -> The next step is to get a JSON Output:
    [
        {

        },
        {
            ...
        }
    ]
  -> lldp output fields are mapped to the JSON output as follows:
     ...      
"""

### raw_output contains the show lldp entry output from one network devices!

def parser_lldp_output(output_raw):
    local_device = ''
    # net_link = {}
    loop_flag = False
    # Convert the raw output into a list of lines
    output_lines = output_raw.split('\n')
    
    print(f'output_lines is: {output_lines}')

    # Remove empty lines from the list
    output_lines = [i for i in output_lines if i]

    for line in output_lines:
    
        line = line.replace('\\x05','')
        line = line.replace('\u0006','')
        line = line.replace('�','')

        # if ('#' in line) and ('lldp' in line):
        #     # Parse a line containing the device hostname
        #     # where the show lldp entry command was issued
        #     (local_device, junk) = line.split('#')
        #     local_device = local_device.strip().strip('\ufeff\ufeff')
    

        ### Interface names are being abbreviated in the LLDP outputs.
        ### Need to replace a short interface name with the full interface name.
        ### A dictionary is used to map the short interface names to the full interface names.
        
        interface_map = {
            'Eth': 'Ethernet',
            'Po': 'Port-channel',
            'Vlan': 'Vlan',
            'Lo': 'Loopback',
            'Tu': 'Tunnel',
            'Fa': 'FastEthernet',
            'Gig': 'GigabitEthernet',
            'Gi': 'GigabitEthernet',
            'Ten': 'TenGigabitEthernet',
            'Te': 'TenGigabitEthernet',
            'Twe': 'TwentyFiveGigE',
            'For': 'FortyGigabitEthernet',
            'Fo': 'FortyGigabitEthernet',
            'Hun': ' HundredGigE',
            'Hu': ' HundredGigE'
        }

        ### Local_device is taken from STDIN passing as a parameter by Ansible in this case.
        local_device = device_hostname

        if 'Chassis id:' in line:
            loop_flag = True
            flag_append = False

            """
            # Example of key-value pairs to be parsed from the raw output
            local_port_id: "mgmt0",
            remote_chassis_id: "0024.98e8.1ed9",
            remote_port_id: "Eth7/18",
            remote_port_description: "CALAX04-DC1AS-02A_mgmt0",
            remote_system_name: "DC-DIST7-1.paramount.com",
            remote_system_description: "Cisco NX-OS(tm) n7000, Software (n7000-s1-dk9), Version 6.2(10), RELEASE SOFTWARE Copyright (c) 2002-2013 by Cisco Systems, Inc. Compiled 10/9/2014 12:00:00",
            remote_system_capabilities: "B, R",
            remote_enabled_capabilities: "B, R",
            remote_mgmt_address: "0024.98e8.1ed9",
            remote_mgmt_address_ipv6: "not advertised",
            remote_vlan_id: "500",
            """


            ### Reset net_link and define the order of keys in the dictionary
            net_link = {
                'local_device': '',
                'local_port_id': '',
                'remote_chassis_id': '',
                'remote_port_id': '',
                'remote_port_description': '',
                'remote_system_name': '',
                'remote_system_description': '',
                'remote_system_capabilities': '',
                'remote_enabled_capabilities': '',
                'remote_mgmt_address': '',
                'remote_mgmt_address_ipv6': '',
                'remote_vlan_id': ''
            }
            net_link['local_device'] = local_device

        ### Use loop_flag to populate lldp data of one link between the following lines:
        ### - the start line contains 'Chassis id:'
        ### - the end line contains "Vlan ID:"
        if loop_flag:
            if 'Chassis id:' in line:
                (junk, remote_chassis_id) = line.split('Chassis id:')
                remote_chassis_id = remote_chassis_id.strip()

                ### There might be a MAC address as Chassis ID so it's better to not remove the dots
                # if '.' in remote_chassis_id:
                #     (remote_chassis_id, junk) = re.split('\..*', remote_chassis_id)

                # if '(' in remote_chassis_id:
                #     (remote_chassis_id, junk) = re.split('\(', remote_chassis_id)
                
                net_link['remote_chassis_id'] = remote_chassis_id
                continue

            # if 'Port id:' in line:
            #     (junk, remote_port_id) = line.split('Port id:')
            #     remote_port_id = remote_port_id.strip()
            #     net_link['remote_port_id'] = remote_port_id
            #     continue

            if line.startswith('Port id:'):
                (junk, remote_port_id) = line.split('Port id:')
                remote_port_id = remote_port_id.strip()
                net_link['remote_port_id'] = remote_port_id
                continue

            if 'Local Port id:' in line:
                (junk, local_port_id) = line.split('Local Port id:')
                local_port_id = local_port_id.strip()
                net_link['local_port_id'] = local_port_id

                for k,v in interface_map.items():
                    if k in local_port_id:
                        local_port_id = local_port_id.replace(k,v)
                        net_link['local_port_id'] = local_port_id
                        continue

                continue
            
            ### It will require to develop a separate script to parse IOS-XE outputs
            # if 'Local Intf:' in line:
            #     (junk, local_port_id) = line.split('Local Intf:')
            #     local_port_id = local_port_id.strip()
            #     net_link['local_port_id'] = local_port_id

            #     for k,v in interface_map.items():
            #         if k in local_port_id:
            #             local_port_id = local_port_id.replace(k,v)
            #             net_link['local_port_id'] = local_port_id
            #             continue

            #     continue

            if 'Port Description:' in line:
                (junk, remote_port_description) = line.split('Port Description:')
                remote_port_description = remote_port_description.strip()
                net_link['remote_port_description'] = remote_port_description
                continue

            if 'System Name:' in line:
                (junk, remote_system_name) = line.split('System Name:')
                remote_system_name = remote_system_name.strip()
                net_link['remote_system_name'] = remote_system_name
                continue

            if 'System Description:' in line:
                (junk, remote_system_description) = line.split('System Description: ')
                # remote_system_description = remote_system_description.strip()
                net_link['remote_system_description'] = remote_system_description
                continue

            if 'System Capabilities:' in line:
                (junk, remote_system_capabilities) = line.split('System Capabilities:')
                remote_system_capabilities = remote_system_capabilities.strip()
                net_link['remote_system_capabilities'] = remote_system_capabilities
                continue

            if 'Enabled Capabilities:' in line:
                (junk, remote_enabled_capabilities) = line.split('Enabled Capabilities:')
                remote_enabled_capabilities = remote_enabled_capabilities.strip()
                net_link['remote_enabled_capabilities'] = remote_enabled_capabilities
                continue

            if 'Management Address:' in line:
                (junk, remote_mgmt_address) = line.split('Management Address:')
                remote_mgmt_address = remote_mgmt_address.strip()
                net_link['remote_mgmt_address'] = remote_mgmt_address
                continue

            if 'Management Address IPV6:' in line:
                (junk, remote_mgmt_address_ipv6) = line.split('Management Address IPV6:')
                remote_mgmt_address_ipv6 = remote_mgmt_address_ipv6.strip()
                net_link['remote_mgmt_address_ipv6'] = remote_mgmt_address_ipv6
                continue

            if 'Vlan ID:' in line:
                (junk, remote_vlan_id) = line.split('Vlan ID:')
                remote_vlan_id = remote_vlan_id.strip()
                net_link['remote_vlan_id'] = remote_vlan_id
                flag_append = True

            ### Append collected lldp data of one link to the parsed output
            if flag_append: 
                ALL_LLDP_DATA_PARSED.append(net_link)
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
    #     with open(os.path.join(path,filename), 'r') as f:
    #         output_raw = f.read()
    #     parser_lldp_output(output_raw)

    ### The folder is being created by Ansible playbook
    # os.makedirs(path, exist_ok=True)
    
    with open(input_data) as f:
        output_raw = f.read()
    
    ### Old NXOS verisons have '\u0005' and '\u0006' characters in the output
    ### As a result, the output is not being parsed correctly.
    ### To fix this issue, the characters are being removed from the output as follows:
    if output_raw.startswith('"['):
        output_raw = json.loads(output_raw)
        output_raw = output_raw.strip('"[').strip(']"')
        output_raw = output_raw.replace('\\n','\n')
        output_raw = output_raw.replace('\\x05','')
        output_raw = output_raw.replace('\\x06','')
    # output_raw = str(output_raw_list[0])
    # output_raw

    print(f'output_raw is: {output_raw}')
    print(f'output_raw type is: {type(output_raw)}')
    # os._exit(1)

    parser_lldp_output(output_raw)

    ### Converting the output_rows list to a dictionay format
    ### to use it as a data frame to merge with lldp LLDP outputs
    ### by separate python sripts

    output_dict = { device_hostname: [] }

    for row in ALL_LLDP_DATA_PARSED:
        # for k, v in row.items():
        output_dict[device_hostname].append({
            # "local_device": row["local_device"],
            "local_port_id": row["local_port_id"],
            "remote_chassis_id": row["remote_chassis_id"],
            "remote_port_id": row["remote_port_id"],
            "remote_port_description": row["remote_port_description"],
            "remote_system_name": row["remote_system_name"],
            "remote_system_description": row["remote_system_description"],
            "remote_system_capabilities": row["remote_system_capabilities"],
            "remote_enabled_capabilities": row["remote_enabled_capabilities"],
            "remote_mgmt_address": row["remote_mgmt_address"],
            "remote_mgmt_address_ipv6": row["remote_mgmt_address_ipv6"],
            "remote_vlan_id": row["remote_vlan_id"]
        })

    save2json(output_dict, output_dict2json)

    ### Create Pandas DataFrame from the ALL_LLDP_DATA_PARSED list
    ### To save the parsed lldp data to an excel file
    pd.DataFrame(ALL_LLDP_DATA_PARSED).to_excel(output_excel)

    ### Save parsed lldp data as a JSON file
    DATA2JSON = {"links": ALL_LLDP_DATA_PARSED}
    save2json(DATA2JSON,output_json)

if __name__ == "__main__":
    stdin_read = sys.stdin.readlines()
    input_vars = stdin_read[0].rstrip('\n')
    input_folder,device_hostname = input_vars.split(',') 
     
    # # Debugging  
    # input_folder = "2024-05-07_21-45"
    # device_hostname = "DC-ACS5-2"

    input_data = "../../../outputs/" + input_folder + "/command_outputs/" + device_hostname + "_show_lldp_entry.txt"

    path_output_dir = os.path.join("../../../outputs/",input_folder,"script_outputs")
    output_json = path_output_dir + "/json/" + device_hostname + "_lldp_list.json"
    output_dict2json = path_output_dir + "/json/" + device_hostname + "_lldp_dict.json"
    output_csv = path_output_dir + "/csv" + device_hostname + "_lldp_list.csv"
    output_excel = path_output_dir + "/excel/" + device_hostname + "_lldp_list.xlsx"

    ALL_LLDP_DATA_PARSED = []

    main(path_output_dir)