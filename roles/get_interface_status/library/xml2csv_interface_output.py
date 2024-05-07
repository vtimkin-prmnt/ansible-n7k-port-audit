#!/Users/timkinv0815/Documents/venv3106/bin/env python3

import json
import xmltodict
import xml.etree.ElementTree as ET
import pandas as pd
import sys
import os


# xmlparse = ET.parse(input_xml)
# xmlroot = xmlparse.getroot()

def save2json(data,filename):
  json_data = json.dumps(data, indent=2)
  with open(filename, 'w') as f:
      f.write(json_data)

def main():
        
    os.makedirs(path_output_dir, exist_ok=True)

    with open(input_xml) as f:
        data_dict = xmltodict.parse(f.read())
        # json_data = json.dumps(data_dict)

    # with open(output_json, "w") as f:
    #     f.write(json_data)

    # list_temp = data_dict["nf:rpc-reply"]["nf:data"]["show"]["interface"]["status"].values()

    temp_dict = data_dict["nf:rpc-reply"]["nf:data"]
    flag = True
    while flag:
        for k,v in temp_dict.items():
            if "ROW_interface" in v:
                list_if = v["ROW_interface"]
                flag = False
            else:
                temp_dict = v

    for i in list_if:
        port = i["interface"]
        status = i["state"]
        vlan = i["vlan"]
        duplex = i["duplex"]
        speed = i["speed"]

        if "name" in i.keys():
            name = i["name"]
        else:
            name = "--"

        if "type" in i.keys():
            type = i["type"]
        else:
            type = "--"

        output_rows.append({
            "Hostname": device_hostname,
            "Port": port,
            "Name": name,
            "Status": status,
            "Vlan": vlan,
            "Duplex": duplex,
            "Speed": speed,
            "Type": type
        })

    ### Converting the output_rows list to a dictionay format
    ### to use it as a data frame to merge with CDP LLDP outputs
    ### by separate pythons

    # define a structure of the dictionary

    output_dict = { device_hostname: {} }

    for row in output_rows:
        # for k, v in row.items():
        output_dict[device_hostname][row["Port"]]= {
            # "Port": row["Port"],
            "Name": row["Name"],
            "Status": row["Status"],
            "Vlan": row["Vlan"],
            "Duplex": row["Duplex"],
            "Speed": row["Speed"],
            "Type": row["Type"]
        }

    save2json(output_dict, output_dict2json)


    # output_header = ["Hostname", "Port", "Name", "Status", "Vlan", "Duplex", "Speed", "Type"]
    # df = pd.DataFrame(output_rows, columns=output_header)
    df = pd.DataFrame(output_rows)
    df.index += 1

    df.to_csv(output_csv)
    df.to_excel(output_excel)
    df.to_json(output_json, orient="records", indent=2)

if __name__ == "__main__":
    stdin_read = sys.stdin.readlines()
    input_vars = stdin_read[0].rstrip('\n')
    input_folder,device_hostname = input_vars.split(',')

    input_xml = "../../../outputs/" + input_folder + "/command_outputs/" + device_hostname + "_show_interface_status.xml"

    path_output_dir = os.path.join("../../../outputs/",input_folder,"xml2csv_interface_outputs")
    output_json = path_output_dir + "/" + device_hostname + ".json"
    output_dict2json = path_output_dir + "/" + device_hostname + "_dict.json"
    output_csv = path_output_dir + "/" + device_hostname + ".csv"
    output_excel = path_output_dir + "/" + device_hostname + ".xlsx"

    output_rows = []
    list_if = []

    main()