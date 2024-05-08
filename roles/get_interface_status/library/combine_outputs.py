import json
import pandas as pd
import sys
import os


def json2dict(input_file):
    with open(input_file) as f:
        data = json.load(f)
    return data

def save2json(data,filename):
  json_data = json.dumps(data, indent=2)
  with open(filename, 'w') as f:
      f.write(json_data)

def main():
    input_if_dict = {}
    input_cdp_dict = {}
    input_lldp_dict = {}

    temp_dict = {}
    # combined_dict = {}
    combined_list = []

    # flag_if_dict = False
    flag_cdp_input = False
    flag_lldp_input = False

    if os.path.isfile(if_dict_json):
        input_if_dict = json2dict(if_dict_json)

    if os.path.isfile(cdp_dict_json):
        input_cdp_dict = json2dict(cdp_dict_json)

    if os.path.isfile(lldp_dict_json):
        input_lldp_dict = json2dict(lldp_dict_json)

    if not input_if_dict:
        print("No interface status data found")
        sys.exit(1)


    ### Initial check-up
    if not len(input_if_dict) == 0:
        
        if device_hostname in input_if_dict.keys():
            temp_dict = input_if_dict[device_hostname]
            
            ### Add empty lists for CDP and LLDP data
            for k in temp_dict.keys():
                temp_dict[k]['cdp_output'] = []
                temp_dict[k]['lldp_output'] = []

            if device_hostname in input_cdp_dict.keys():
                input_cdp_list = input_cdp_dict[device_hostname]
                flag_cdp_input = True

            if device_hostname in input_lldp_dict.keys():
                input_lldp_list = input_lldp_dict[device_hostname]
                flag_lldp_input = True

    ### Add CDP data to interface data
    ### We assume that all 'local_int' values are present in 'temp_dict'
    if flag_cdp_input:
        for item in input_cdp_list:
            temp_dict[item['local_int']]['cdp_output'].append(item)
    
    ### Add LLDP data to interface data
    if flag_lldp_input:
        for item in input_lldp_list:
            temp_dict[item['local_port_id']]['lldp_output'].append(item)

    # combined_dict = {device_hostname: temp_dict}

    for k,v in temp_dict.items():
        if (len(v['cdp_output']) == 0) and (len(v['lldp_output']) == 0):
            combined_list.append({
                "Hostname": device_hostname,
                "Port": k,
                "Name": v['Name'],
                "Status": v['Status'],
                "Vlan": v['Vlan'],
                "Duplex": v['Duplex'],
                "Speed": v['Speed'],
                "Type": v['Type'],
                "CDP_local_int": "--",
                "CDP_remote_device": "--",
                "CDP_remote_int": "--",
                "CDP_remote_platform": "--",
                "CDP_remote_capabilities": "--",
                "CDP_remote_ip": "--",
                "LLDP_local_port_id": "--",
                "LLDP_remote_chassis_id": "--",
                "LLDP_remote_port_id": "--",
                "LLDP_remote_port_description": "--",
                "LLDP_remote_system_name": "--",
                "LLDP_remote_system_description": "--",
                "LLDP_remote_system_capabilities": "--",
                "LLDP_remote_system_address": "--",
                "LLDP_remote_vlan_id": "--"
            })
        
        if (len(v['cdp_output']) > 0) and (len(v['lldp_output']) == 0):
            for item in v['cdp_output']:
                combined_list.append({
                    "Hostname": device_hostname,
                    "Port": k,
                    "Name": v['Name'],
                    "Status": v['Status'],
                    "Vlan": v['Vlan'],
                    "Duplex": v['Duplex'],
                    "Speed": v['Speed'],
                    "Type": v['Type'],
                    "CDP_local_int": item['local_int'],
                    "CDP_remote_device": item['remote_device'],
                    "CDP_remote_int": item['remote_int'],
                    "CDP_remote_platform": item['remote_platform'],
                    "CDP_remote_capabilities": item['remote_capabilities'],
                    "CDP_remote_ip": item['remote_ip_cdp'],
                    "LLDP_local_port_id": "--",
                    "LLDP_remote_chassis_id": "--",
                    "LLDP_remote_port_id": "--",
                    "LLDP_remote_port_description": "--",
                    "LLDP_remote_system_name": "--",
                    "LLDP_remote_system_description": "--",
                    "LLDP_remote_system_capabilities": "--",
                    "LLDP_remote_system_address": "--",
                    "LLDP_remote_vlan_id": "--"
                })
        
        if (len(v['cdp_output']) == 0) and (len(v['lldp_output']) > 0):
            for item in v['lldp_output']:
                combined_list.append({
                    "Hostname": device_hostname,
                    "Port": k,
                    "Name": v['Name'],
                    "Status": v['Status'],
                    "Vlan": v['Vlan'],
                    "Duplex": v['Duplex'],
                    "Speed": v['Speed'],
                    "Type": v['Type'],
                    "CDP_local_int": "--",
                    "CDP_remote_device": "--",
                    "CDP_remote_int": "--",
                    "CDP_remote_platform": "--",
                    "CDP_remote_capabilities": "--",
                    "CDP_remote_ip": "--",
                    "LLDP_local_port_id": item['local_port_id'],
                    "LLDP_remote_chassis_id": item['remote_chassis_id'],
                    "LLDP_remote_port_id": item['remote_port_id'],
                    "LLDP_remote_port_description": item['remote_port_description'],
                    "LLDP_remote_system_name": item['remote_system_name'],
                    "LLDP_remote_system_description": item['remote_system_description'],
                    "LLDP_remote_system_capabilities": item['remote_system_capabilities'],
                    "LLDP_remote_system_address": item['remote_mgmt_address'],
                    "LLDP_remote_vlan_id": item['remote_vlan_id']
                })
        
        if (len(v['cdp_output']) > 0) and (len(v['lldp_output']) > 0):
            if len(v['cdp_output']) == len(v['lldp_output']):
                for i in range(len(v['cdp_output'])):
                    combined_list.append({
                        "Hostname": device_hostname,
                        "Port": k,
                        "Name": v['Name'],
                        "Status": v['Status'],
                        "Vlan": v['Vlan'],
                        "Duplex": v['Duplex'],
                        "Speed": v['Speed'],
                        "Type": v['Type'],
                        "CDP_local_int": v['cdp_output'][i]['local_int'],
                        "CDP_remote_device": v['cdp_output'][i]['remote_device'],
                        "CDP_remote_int": v['cdp_output'][i]['remote_int'],
                        "CDP_remote_platform": v['cdp_output'][i]['remote_platform'],
                        "CDP_remote_capabilities": v['cdp_output'][i]['remote_capabilities'],
                        "CDP_remote_ip": v['cdp_output'][i]['remote_ip_cdp'],
                        "LLDP_local_port_id": v['lldp_output'][i]['local_port_id'],
                        "LLDP_remote_chassis_id": v['lldp_output'][i]['remote_chassis_id'],
                        "LLDP_remote_port_id": v['lldp_output'][i]['remote_port_id'],
                        "LLDP_remote_port_description": v['lldp_output'][i]['remote_port_description'],
                        "LLDP_remote_system_name": v['lldp_output'][i]['remote_system_name'],
                        "LLDP_remote_system_description": v['lldp_output'][i]['remote_system_description'],
                        "LLDP_remote_system_capabilities": v['lldp_output'][i]['remote_system_capabilities'],
                        "LLDP_remote_system_address": v['lldp_output'][i]['remote_mgmt_address'],
                        "LLDP_remote_vlan_id": v['lldp_output'][i]['remote_vlan_id']
                    })

                if len(v['cdp_output']) > len(v['lldp_output']):
                    for i in range(len(v['cdp_output'])):
                        if i < len(v['lldp_output']):
                            combined_list.append({
                                "Hostname": device_hostname,
                                "Port": k,
                                "Name": v['Name'],
                                "Status": v['Status'],
                                "Vlan": v['Vlan'],
                                "Duplex": v['Duplex'],
                                "Speed": v['Speed'],
                                "Type": v['Type'],
                                "CDP_local_int": v['cdp_output'][i]['local_int'],
                                "CDP_remote_device": v['cdp_output'][i]['remote_device'],
                                "CDP_remote_int": v['cdp_output'][i]['remote_int'],
                                "CDP_remote_platform": v['cdp_output'][i]['remote_platform'],
                                "CDP_remote_capabilities": v['cdp_output'][i]['remote_capabilities'],
                                "CDP_remote_ip": v['cdp_output'][i]['remote_ip_cdp'],
                                "LLDP_local_port_id": v['lldp_output'][i]['local_port_id'],
                                "LLDP_remote_chassis_id": v['lldp_output'][i]['remote_chassis_id'],
                                "LLDP_remote_port_id": v['lldp_output'][i]['remote_port_id'],
                                "LLDP_remote_port_description": v['lldp_output'][i]['remote_port_description'],
                                "LLDP_remote_system_name": v['lldp_output'][i]['remote_system_name'],
                                "LLDP_remote_system_description": v['lldp_output'][i]['remote_system_description'],
                                "LLDP_remote_system_capabilities": v['lldp_output'][i]['remote_system_capabilities'],
                                "LLDP_remote_system_address": v['lldp_output'][i]['remote_mgmt_address'],
                                "LLDP_remote_vlan_id": v['lldp_output'][i]['remote_vlan_id']
                            })
                        if i >= len(v['lldp_output']):
                            combined_list.append({
                                "Hostname": device_hostname,
                                "Port": k,
                                "Name": v['Name'],
                                "Status": v['Status'],
                                "Vlan": v['Vlan'],
                                "Duplex": v['Duplex'],
                                "Speed": v['Speed'],
                                "Type": v['Type'],
                                "CDP_local_int": v['cdp_output'][i]['local_int'],
                                "CDP_remote_device": v['cdp_output'][i]['remote_device'],
                                "CDP_remote_int": v['cdp_output'][i]['remote_int'],
                                "CDP_remote_platform": v['cdp_output'][i]['remote_platform'],
                                "CDP_remote_capabilities": v['cdp_output'][i]['remote_capabilities'],
                                "CDP_remote_ip": v['cdp_output'][i]['remote_ip_cdp'],
                                "LLDP_local_port_id": "--",
                                "LLDP_remote_chassis_id": "--",
                                "LLDP_remote_port_id": "--",
                                "LLDP_remote_port_description": "--",
                                "LLDP_remote_system_name": "--",
                                "LLDP_remote_system_description": "--",
                                "LLDP_remote_system_capabilities": "--",
                                "LLDP_remote_system_address": "--",
                                "LLDP_remote_vlan_id": "--"
                            })
                
                if len(v['cdp_output']) < len(v['lldp_output']):
                    for i in range(len(v['lldp_output'])):
                        if i < len(v['cdp_output']):
                            combined_list.append({
                                "Hostname": device_hostname,
                                "Port": k,
                                "Name": v['Name'],
                                "Status": v['Status'],
                                "Vlan": v['Vlan'],
                                "Duplex": v['Duplex'],
                                "Speed": v['Speed'],
                                "Type": v['Type'],
                                "CDP_local_int": v['cdp_output'][i]['local_int'],
                                "CDP_remote_device": v['cdp_output'][i]['remote_device'],
                                "CDP_remote_int": v['cdp_output'][i]['remote_int'],
                                "CDP_remote_platform": v['cdp_output'][i]['remote_platform'],
                                "CDP_remote_capabilities": v['cdp_output'][i]['remote_capabilities'],
                                "CDP_remote_ip": v['cdp_output'][i]['remote_ip_cdp'],
                                "LLDP_local_port_id": v['lldp_output'][i]['local_port_id'],
                                "LLDP_remote_chassis_id": v['lldp_output'][i]['remote_chassis_id'],
                                "LLDP_remote_port_id": v['lldp_output'][i]['remote_port_id'],
                                "LLDP_remote_port_description": v['lldp_output'][i]['remote_port_description'],
                                "LLDP_remote_system_name": v['lldp_output'][i]['remote_system_name'],
                                "LLDP_remote_system_description": v['lldp_output'][i]['remote_system_description'],
                                "LLDP_remote_system_capabilities": v['lldp_output'][i]['remote_system_capabilities'],
                                "LLDP_remote_system_address": v['lldp_output'][i]['remote_mgmt_address'],
                                "LLDP_remote_vlan_id": v['lldp_output'][i]['remote_vlan_id']
                            })

                        if i >= len(v['cdp_output']):
                            combined_list.append({
                                "Hostname": device_hostname,
                                "Port": k,
                                "Name": v['Name'],
                                "Status": v['Status'],
                                "Vlan": v['Vlan'],
                                "Duplex": v['Duplex'],
                                "Speed": v['Speed'],
                                "Type": v['Type'],
                                "CDP_local_int": "--",
                                "CDP_remote_device": "--",
                                "CDP_remote_int": "--",
                                "CDP_remote_platform": "--",
                                "CDP_remote_capabilities": "--",
                                "CDP_remote_ip": "--",
                                "LLDP_local_port_id": v['lldp_output'][i]['local_port_id'],
                                "LLDP_remote_chassis_id": v['lldp_output'][i]['remote_chassis_id'],
                                "LLDP_remote_port_id": v['lldp_output'][i]['remote_port_id'],
                                "LLDP_remote_port_description": v['lldp_output'][i]['remote_port_description'],
                                "LLDP_remote_system_name": v['lldp_output'][i]['remote_system_name'],
                                "LLDP_remote_system_description": v['lldp_output'][i]['remote_system_description'],
                                "LLDP_remote_system_capabilities": v['lldp_output'][i]['remote_system_capabilities'],
                                "LLDP_remote_system_address": v['lldp_output'][i]['remote_mgmt_address'],
                                "LLDP_remote_vlan_id": v['lldp_output'][i]['remote_vlan_id']
                            })
                            

        # combined_list.append({
        #     "Hostname": device_hostname,
        #     "Port": k,
        #     "Name": v['Name'],
        #     "Status": v['Status'],
        #     "Vlan": v['Vlan'],
        #     "Duplex": v['Duplex'],
        #     "Speed": v['Speed'],
        #     "Type": v['Type'],
        #     "CDP": v['cdp_output'],
        #     "LLDP": v['lldp_output']
        # })

    df = pd.DataFrame(data=combined_list)
    df.index += 1

    df.to_csv(output_csv)
    df.to_excel(output_excel)
    df.to_json(output_json, orient="records", indent=2)


if __name__ == "__main__":
    stdin_read = sys.stdin.readlines()
    input_vars = stdin_read[0].rstrip('\n')
    input_folder,device_hostname = input_vars.split(',')

    ### Input files:
    if_dict_json = "../../../outputs/" + input_folder + "/script_outputs/json/" + device_hostname + "_ifstatus_dict.json"
    cdp_dict_json = "../../../outputs/" + input_folder + "/script_outputs/json/" + device_hostname + "_cdp_dict.json"
    lldp_dict_json = "../../../outputs/" + input_folder + "/script_outputs/json/" + device_hostname + "_lldp_dict.json"

    path_output_dir = os.path.join("../../../outputs/",input_folder,"script_outputs")
    output_json = path_output_dir + "/json/" + device_hostname + "_combined.json"
    # output_dict2json = path_output_dir + "/json/" + device_hostname + "_ifstatus_dict.json"
    output_csv = path_output_dir + "/csv/" + device_hostname + "_combined.csv"
    output_excel = path_output_dir + "/excel/" + device_hostname + "_combined.xlsx"

    # output_rows = []
    # list_if = []

    main()