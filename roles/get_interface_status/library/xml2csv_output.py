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

    df = pd.DataFrame(output_rows, columns=output_header)
    df.index += 1

    df.to_csv(output_csv)
    df.to_excel(output_excel)


if __name__ == "__main__":
    # input_xml = "./input/xml_file.xml"
    input_vars = sys.stdin.readlines()
    # input_vars = json.loads(stdin_vars)
    # print(input_vars)
    # input_folder = input_vars["input_folder"]
    # device_hostname = input_vars["hostname"]
    print(input_vars)
    input_folder,device_hostname = input_vars.split(',')
    input_xml = "./outputs/" + input_folder + "/command_outputs/" + device_hostname + "_show_interface_status.xml"
    output_dir = "./outputs/" + input_folder + "/xml2csv_outputs/"
    output_json = output_dir + device_hostname + ".json"
    output_csv = output_dir + device_hostname + ".csv"
    output_excel = output_dir + device_hostname + ".xlsx"
    output_header = ["Hostname", "Port", "Name", "Status", "Vlan", "Duplex", "Speed", "Type"]
    output_rows = []
    list_if = []

    path_output_dir = os.path.join("./outputs/",input_folder,"xml2csv_outputs")

    # device_hostname = str(sys.argv[2])
    # input_xml = "./outputs/" + str(sys.argv[1]) + "/command_outputs/" + str(sys.argv[2]) + "_show_interface_status.xml"
    # output_dir = "./outputs/" + str(sys.argv[1]) + "/xml2csv_outputs/"
    # output_json = output_dir + str(sys.argv[2]) + ".json"
    # output_csv = output_dir + str(sys.argv[2]) + ".csv"
    # output_excel = output_dir + str(sys.argv[2]) + ".xlsx"
    # output_header = ["Hostname", "Port", "Name", "Status", "Vlan", "Duplex", "Speed", "Type"]
    # output_rows = []
    # list_if = []

    # DIRNAME = os.path.dirname(__file__)
    # OG_FOLDER_INPUT = os.path.join(DIRNAME, './object-groups-to-merge/input')
    # OG_FOLDER_OUTPUT = os.path.join(DIRNAME, './object-groups-to-merge/output/merged-list.txt')
    # OG_FOLDER_FORMATTED_OUTPUT = os.path.join(DIRNAME, './object-groups-to-merge/output/merged-list-ipformatted.txt')
    main()

