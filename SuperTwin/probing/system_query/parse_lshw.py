import json
import detect_utils
import pprint

#from collections.abc import MutableMapping
import collections

def generate_hardware_dict(to_gen, info_list):

    for item in info_list:
                
        try:
            to_gen[item[0]]
        except:
            to_gen[item[0]] = {}
        try:
            to_gen[item[0]][item[1]]
        except:
            to_gen[item[0]][item[1]] = {}
        try:
            to_gen[item[0]][item[1]][item[2]]
        except:
            to_gen[item[0]][item[1]][item[2]] = {}
        

    for item in info_list:
        to_gen[item[0]][item[1]][item[2]] = item[3]

    return to_gen



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
    try:
        out = json.loads(out)[0]
    except:
        out = json.loads(out)
    
    system = {"uuid":out.get('configuration',{}).get('uuid',None)}
    
    parse_motherboard_info(out,system)
    parse_bios_info(out,system)
    parse_memory_info(out,system)
    parse_network_info(out,system)
    parse_disk_info(out,system)
    generate_hardware_dict(system, get_cpus() + get_kernel_info())
    
    pprint.pprint(system)
    return system

def parse_motherboard_info(out,system):
    system["system"] = {}
    system["system"]["motherboard"] = {}

    found = []
    find_field(out, "bus", "Motherboard", found)
    
    if(len(found) > 0):
        td = found[0] ##Since there is one motherboard, assume one dict will return
        system["system"]["motherboard"]["name"] = td.get("product","")    
        system["system"]["motherboard"]["vendor"] = td.get("vendor","")    
    
def parse_bios_info(out,system):
    system["firmware"] = {}
    system["firmware"]["bios"] = {}
    
    found = []
    find_field(out, "memory", "BIOS", found)

    if(len(found) > 0):
        td = found[0] ##Since there is one BIOS, assume one dict will return
        system["firmware"]["bios"]["version"] = td.get("version","")
        system["firmware"]["bios"]["date"] = td.get("date","")
        system["firmware"]["bios"]["vendor"] = td.get("vendor","")

def parse_memory_info(out,system):
    system["memory"] = {}
    system["memory"]["total"] = {}

    found = []
    find_field(out, "memory", "System Memory", found)
    
    if(len(found) > 0):
        td = found[0] ##System memory is top dictionary and banks are it's children
        system["memory"]["total"]["size"] = td.get("size","")
        system["memory"]["total"]["units"] = td.get("units","")
        system["memory"]["total"]["banks"] = 0 ##Increment as filled slots found
        system["memory"]["banks"] = {}
    
        if "children" in td:
            for i in range(len(td["children"])):
                this_bank = td["children"][i]
                if(this_bank["description"].find("empty") == -1): ##if the slot is filled
                    system["memory"]["total"]["banks"] += 1
                    system["memory"]["banks"][this_bank["id"]] = {}
                    system["memory"]["banks"][this_bank["id"]] ["size"] = this_bank.get("size","")
                    system["memory"]["banks"][this_bank["id"]] ["slot"] = this_bank.get("slot","")
                    system["memory"]["banks"][this_bank["id"]] ["clock"] = this_bank.get("clock","")
                    system["memory"]["banks"][this_bank["id"]] ["description"] = this_bank.get("description","")
                    system["memory"]["banks"][this_bank["id"]] ["vendor"] = this_bank.get("vendor","")
                    system["memory"]["banks"][this_bank["id"]] ["model"] = this_bank.get("product","")

def parse_network_info(out,system):
    system["network"] = {}
    found = []
    find_field(out, "network", "Ethernet interface", found)
    find_field(out, "network", "Wireless interface", found)

    if(len(found) > 0):
        for network in found:
            key = network.get("logicalname","") ## a name
            conf = network.get("configuration","") ## a dict
            
            system["network"][key] = {}
            if("ip" in conf):
                system["network"][key]["ipv4"] = conf["ip"]
            if("speed" in conf):
                system["network"][key]["speed"] = conf["speed"]
    
            system["network"][key]["link"] = conf["link"]
    
            if("firmware" in conf):
                system["network"][key]["firmware"] = conf.get("firmware","")
                system["network"][key]["serial"] = network.get("serial","")
                system["network"][key]["businfo"] = network.get("businfo","")
                system["network"][key]["vendor"] = network.get("vendor","")
                system["network"][key]["model"] = network.get("product","")
            
def parse_disk_info(out,system):
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
            system["disk"][name]["model"] = f_disk.get("product","")
            system["disk"][name]["size"] = f_disk.get("children",[{}])[0].get("size","")
            system["disk"][name]["units"] = f_disk.get("children",[{}])[0].get("units","")
        else:
            name = f_disk["logicalname"].strip("/dev/")
            system["disk"][name] = {}
            system["disk"][name]["model"] = f_disk.get("product","")
            system["disk"][name]["size"] = f_disk.get("size","")
            system["disk"][name]["units"] = f_disk.get("units","")


def get_cpus():
    hw_lst = []
    detect_utils.get_cpus(hw_lst)
    return hw_lst

def get_kernel_info():
    hw_lst = []
    osvendor_cmd = detect_utils.output_lines("lsb_release -is")
    for line in osvendor_cmd:
        hw_lst.append(('system', 'os', 'vendor', line.rstrip('\n').strip()))

    osinfo_cmd = detect_utils.output_lines("lsb_release -ds | tr -d '\"'")
    for line in osinfo_cmd:
        hw_lst.append(('system', 'os', 'version', line.rstrip('\n').strip()))

    uname_cmd = detect_utils.output_lines("uname -r")
    for line in uname_cmd:
        hw_lst.append(('system', 'kernel', 'version',
                       line.rstrip('\n').strip()))

    arch_cmd = detect_utils.output_lines("uname -i")
    for line in arch_cmd:
        hw_lst.append(('system', 'kernel', 'arch', line.rstrip('\n').strip()))

    cmdline_cmd = detect_utils.output_lines("cat /proc/cmdline")
    for line in cmdline_cmd:
        hw_lst.append(('system', 'kernel', 'cmdline',
                       line.rstrip('\n').strip()))
    return hw_lst

    
if __name__ == "__main__":
    parse_lshw()
