#!/Users/timkinv0815/Documents/venv3106/bin/env python3

import json
import xmltodict
import xml.etree.ElementTree as ET
import pandas as pd
import sys
import os



# xmlparse = ET.parse(input_xml)
# xmlroot = xmlparse.getroot()
def main():
        
    os.makedirs(path_output_dir, exist_ok=True)

    with open(input_xml) as f:
        data_dict = xmltodict.parse(f.read())
        json_data = json.dumps(data_dict)

    with open(output_json, "w") as f:
        f.write(json_data)

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
        type = i["type"]


        if "name" in i.keys():
            name = i["name"]
        else:
            name = "--"

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

    # output_header = ["Hostname", "Port", "Name", "Status", "Vlan", "Duplex", "Speed", "Type"]
    # df = pd.DataFrame(output_rows, columns=output_header)
    df = pd.DataFrame(output_rows)
    df.index += 1

    df.to_csv(output_csv)
    df.to_excel(output_excel)

if __name__ == "__main__":
    stdin_read = sys.stdin.readlines()
    input_vars = stdin_read[0].rstrip('\n')
    print(input_vars)
    input_folder,device_hostname = input_vars.split(',')
    input_xml = "../../../outputs/" + input_folder + "/command_outputs/" + device_hostname + "_show_interface_status.xml"
    output_dir = "../../../outputs/" + input_folder + "/xml2csv_outputs/"
    output_json = output_dir + device_hostname + ".json"
    output_csv = output_dir + device_hostname + ".csv"
    output_excel = output_dir + device_hostname + ".xlsx"
    output_rows = []
    list_if = []
    path_output_dir = os.path.join("../../../outputs/",input_folder,"xml2csv_outputs")
    main()

