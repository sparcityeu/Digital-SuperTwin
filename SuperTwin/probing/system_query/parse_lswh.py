import json
import detect_utils
import pprint

#from collections.abc import MutableMapping
import collections

recurse = 0

def find_field_recursive(top_dict, _class, _description, found):
    
    print("id:", top_dict["id"])
    
    if("description" not in top_dict):
        top_dict["description"] = "EMPTY"
    
    condition = (top_dict["class"] == _class) and (top_dict["description"] == _description)
            
    if(condition):

        print("Found!")
        pprint.pprint(top_dict)
        found.append(top_dict)
    
    
    elif("children" in top_dict and not condition):
        for i in range(len(top_dict["children"])):
            find_field_recursive(top_dict["children"][i], _class, _description, found)
            
            
        
def find_field(top_dict, _class, _description, found):

    return find_field_recursive(top_dict, _class, _description, found)
        


def parse_lshw():
    
    out = detect_utils.cmd('lshw -json')[1]

    out = json.loads(out)[0]
    #pprint.pprint(out)
    
    system = {}

    #This is ok since system is always the top level dict
    system['uuid'] = out['configuration']['uuid']


    ##Parse system-motherboard info
    system["system"] = {}
    system["system"]["motherboard"] = {}

    found = []
    find_field(out, "bus", "Motherboard", found)

    td = found[0] ##Since there is one motherboard, assume one dict will return
    system["system"]["motherboard"]["name"] = td["product"]
    system["system"]["motherboard"]["vendor"] = td["vendor"]
    
    
    ##Parse bios info
    system["firmware"] = {}
    system["firmware"]["bios"] = {}
    
    found = []
    find_field(out, "memory", "BIOS", found)

    td = found[0] ##Since there is one BIOS, assume one dict will return
    system["firmware"]["bios"]["version"] = td["version"]
    system["firmware"]["bios"]["date"] = td["date"]
    system["firmware"]["bios"]["vendor"] = td["vendor"]


    ##Parse memory info
    system["memory"] = {}
    system["memory"]["total"] = {}

    found = []
    find_field(out, "memory", "System Memory", found)
    td = found[0] ##System memory is top dictionary and banks are it's children
    system["memory"]["total"]["size"] = td["size"]
    system["memory"]["total"]["units"] = td["units"]
    system["memory"]["total"]["banks"] = 0 ##Increment as filled slots found
    
    system["memory"]["banks"] = {}
    
    for i in range(len(td["children"])):
        this_bank = td["children"][i]
        
        if(this_bank["description"].find("empty") == -1): ##if the slot is filled
            system["memory"]["total"]["banks"] += 1
            system["memory"]["banks"][this_bank["id"]] = {}
            system["memory"]["banks"][this_bank["id"]]["size"] = this_bank["size"]
            system["memory"]["banks"][this_bank["id"]]["slot"] = this_bank["slot"]
            system["memory"]["banks"][this_bank["id"]]["clock"] = this_bank["clock"]
            system["memory"]["banks"][this_bank["id"]]["description"] = this_bank["description"]
            system["memory"]["banks"][this_bank["id"]]["vendor"] = this_bank["vendor"]
            system["memory"]["banks"][this_bank["id"]]["model"] = this_bank["product"]


    ##Parse network info
    system["network"] = {}
    found = []
    find_field(out, "network", "Ethernet interface", found)
    find_field(out, "network", "Wireless interface", found)

    for network in found:
        key = network["logicalname"] ## a name
        conf = network["configuration"] ## a dict
        
        system["network"][key] = {}
        if("ip" in conf):
            system["network"][key]["ipv4"] = conf["ip"]
        if("speed" in conf):
            system["network"][key]["speed"] = conf["speed"]

        system["network"][key]["link"] = conf["link"]

        if("firmware" in conf):
            system["network"][key]["firmware"] = conf["firmware"]
            system["network"][key]["serial"] = network["serial"]
            system["network"][key]["businfo"] = network["businfo"]
            system["network"][key]["vendor"] = network["vendor"]
            system["network"][key]["model"] = network["product"]
        


    ##Parse disk info
    system["disk"] = {}
    found = []
    find_field(out, "disk", "ATA Disk", found)
    find_field(out, "storage", "NVMe device", found)

    system["disk"]["logical"] = {}
    system["disk"]["logical"]["count"] = len(found)

    ##TO DO: Add other disk types as encountered
    for f_disk in found:
        if(f_disk["description"].find("NVMe") != -1):
            name = f_disk["children"][0]["logicalname"].strip("/dev/")
            system["disk"][name] = {}
            system["disk"][name]["model"] = f_disk["product"]
            system["disk"][name]["size"] = f_disk["children"][0]["size"]
            system["disk"][name]["units"] = f_disk["children"][0]["units"]
        else:
            name = f_disk["logicalname"].strip("/dev/")
            system["disk"][name] = {}
            system["disk"][name]["model"] = f_disk["product"]
            system["disk"][name]["size"] = f_disk["size"]
            system["disk"][name]["units"] = f_disk["units"]


    ##Parse CPU info
    system["cpu"] = {}

    #find_field(out, "processor", "CPU", found)
    #print("Found:", found)
    

    pprint.pprint(system)

if __name__ == "__main__":

    parse_lshw()
