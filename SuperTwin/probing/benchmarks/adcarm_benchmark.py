import sys
sys.path.append("../")
sys.path.append("../../")

import utils
import remote_probe
import detect_utils

from bson.objectid import ObjectId

import paramiko
from scp import SCPClient

import glob


def get_fields(data):

    nominal_frequency = "" ##We are looking at name for this because this is nominal frequency
    l1_cache = ""
    l2_cache = ""
    l3_cache = ""

    for key in data.keys():

        if(key.find("socket") != -1):
            contents = data[key]["contents"]

            for content in contents:
                
                if(content["name"] == "model"):
                    string = content["description"]
                    nominal_frequency = str(float(string.split("@")[1].strip("GHz").strip("")))

        if(key.find("L1D") != -1):
            contents = data[key]["contents"]

            for content in contents:

                if(content["name"] == "size"):
                    l1_cache = content["description"].strip(" kB")


        if(key.find("L2") != -1):
            contents = data[key]["contents"]

            for content in contents:

                if(content["name"] == "size"):
                    l2_cache = int(content["description"].strip(" MB"))
                    l2_cache *= 1024
                    l2_cache = str(l2_cache)

        if(key.find("L3") != -1):
            contents = data[key]["contents"]

            for content in contents:

                if(content["name"] == "size"):
                    l3_cache = float(content["description"].strip(" MB")) 
                    l3_cache *= 1024
                    l3_cache = str(int(l3_cache)) ##It wont be a problem since multiplication is have to be an integer
                    

    return nominal_frequency, l1_cache, l2_cache, l3_cache
                    

def generate_adcarm_config(SuperTwin):

    db = utils.get_mongo_database(SuperTwin.name, SuperTwin.mongodb_addr)["twin"]
    data = db.find_one({'_id': ObjectId(SuperTwin.mongodb_id)})["twin_description"]

    nominal_frequency, l1_cache, l2_cache, l3_cache = get_fields(data)

    base = "probing/benchmarks/adCARM/config/"
    config_name = SuperTwin.name + "_gen.conf"
    local_path_and_name = "config/" + config_name
    

    writer = open(base + config_name, "w+")
    writer.write("name=" + SuperTwin.name + "\n")
    writer.write("nominal_frequency=" + nominal_frequency + "\n")
    writer.write("l1_cache=" + l1_cache + "\n")
    writer.write("l2_cache=" + l2_cache + "\n")
    writer.write("l3_cache=" + l3_cache + "\n")
    writer.close()

    print("CARM config generated..")
    
    return local_path_and_name
    
    

def generate_adcarm_bench_sh(SuperTwin, adcarm_config):

    modifiers = {}
    modifiers["environment"] = []

    db = utils.get_mongo_database(SuperTwin.name, SuperTwin.mongodb_addr)["twin"]
    data = db.find_one({'_id': ObjectId(SuperTwin.mongodb_id)})["twin_description"]

    mt_info = utils.get_multithreading_info(data)
    
    no_sockets = mt_info["no_sockets"]
    no_cores_per_socket = mt_info["no_cores_per_socket"]
    no_threads_per_socket = mt_info["no_threads_per_socket"]
    total_cores = mt_info["total_cores"]
    total_threads = mt_info["total_threads"]


    thread_set = []
    thr = 1
    while(thr < total_threads):
        thread_set.append(thr)
        thr = thr * 2

    if no_cores_per_socket not in thread_set:
        thread_set.append(no_cores_per_socket)

    if no_threads_per_socket not in thread_set:
        thread_set.append(no_threads_per_socket)

    if total_cores not in thread_set:
        thread_set.append(total_cores)

    if total_threads not in thread_set:
        thread_set.append(total_threads)

    thread_set = list(sorted(thread_set))
    print("ADCARM Benchmark thread set:", thread_set)

    base = "/tmp/dt_probing/benchmarks/adCARM/"

    lines = ["#!/bin/bash \n\n\n", "cd " + base + "\n\n\n"]

    ##for debug purposes
    ##thread_set = [1, 88]

    for thread in thread_set:

        if str(thread) not in modifiers.keys():
            modifiers[str(thread)] = []

        if(thread <= no_cores_per_socket):
            line = "python3 " + "run.py " + " " + adcarm_config + " -t " + str(thread) + " \n\n"
            lines.append(line)
        elif(thread > no_cores_per_socket  and thread <= no_threads_per_socket):
            line = "python3 " + "run.py " + " " + adcarm_config + " -t " + str(thread) + " \n\n"
            lines.append(line) ##As it is
            modifiers[str(thread)].append([]) ##There is a list of lists whose goes with same thread different setting

            line = "python3 " + "run.py " + " " + adcarm_config + " -t " + str(thread) + " --interleaved "+" \n\n"
            lines.append(line) ##As it is with interleave
            modifiers[str(thread)].append(["--interleaved"]) ##There is a list of lists whose goes with same thread different setting
            
            binding = "likwid-pin|-q|-c|S0:0-"+str(thread-1)
            binding_list = binding.split("|")
            binding_pretty = ""
            for item in binding_list:
                binding_pretty += item
                binding_pretty += " "
            line = "python3 " + "run_binded.py " + " " + adcarm_config + " -t " + str(thread) + " -b " + "'" + binding + "'" + " \n\n" ##Binded without interleave
            lines.append(line)
            modifiers[str(thread)].append([binding_pretty])

            line = "python3 " + "run_binded.py " + " " + adcarm_config + " -t " + str(thread) + " -b " + "'" +binding + "'" + " --interleaved"+" \n\n" ##Binded with interleave
            lines.append(line)
            modifiers[str(thread)].append([binding_pretty, "--interleaved"])

            
        elif(thread > no_cores_per_socket  and thread > no_threads_per_socket):
            line = "python3 " + "run.py " + " " + adcarm_config + " -t " + str(thread) + " \n\n"
            lines.append(line) ##As it is
            modifiers[str(thread)].append([]) ##There is a list of lists whose goes with same thread different setting

            if(thread <= no_threads_per_socket):
                line = "python3 " + "run.py " + " " + adcarm_config + " -t " + str(thread) + " --interleaved "+" \n\n"
                lines.append(line) ##As it is with interleave
                modifiers[str(thread)].append(["--interleaved"]) ##There is a list of lists whose goes with same thread different setting
            
            binding = "likwid-pin|-q|-c|S0:0-"+ str(int((thread/2)) - 1) + "@" + "S1:0-"+ str(int(thread/2) - 1)
            binding_list = binding.split("|")
            binding_pretty = ""
            for item in binding_list:
                binding_pretty += item
                binding_pretty += " "
            line = "python3 " + "run_binded.py " + " " + adcarm_config + " -t " + str(thread) + " -b " + "'" + binding + "'" + " \n\n" ##Binded without interleave
            lines.append(line)
            modifiers[str(thread)].append([binding_pretty])

            if(thread <= no_threads_per_socket):
                line = "python3 " + "run_binded.py " + " " + adcarm_config + " -t " + str(thread) + " -b " + "'" + binding + "'" +" --interleaved"+" \n\n" ##Binded with interleave
                lines.append(line)
                modifiers[str(thread)].append([binding_pretty, "--interleaved"])
        
           
    writer = open("probing/benchmarks/adCARM/gen_bench.sh", "w+")
    for line in lines:
        writer.write(line)
    writer.close()

    print("adCARM benchmark script generated..")

    return modifiers

        
            
def execute_adcarm_bench(SuperTwin):

    
    path = detect_utils.cmd("pwd")[1].strip("\n")
    path += "/probing/benchmarks/adCARM"

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SuperTwin.addr, username = SuperTwin.SSHuser, password = SuperTwin.SSHpass)

    scp = SCPClient(ssh.get_transport())
    '''
    try:
        scp.put(path, recursive=True, remote_path="/tmp/dt_probing/benchmarks/")
        remote_probe.run_sudo_command(ssh, SuperTwin.SSHpass, SuperTwin.name, "sudo rm -r /tmp/dt_probing/benchmarks/*")
        scp.put(path, recursive=True, remote_path="/tmp/dt_probing/benchmarks/")
    except:
        remote_probe.run_command(ssh, SuperTwin.name, "mkdir /tmp/dt_probing/benchmarks/")
        scp.put(path, recursive=True, remote_path="/tmp/dt_probing/benchmarks/")
        remote_probe.run_sudo_command(ssh, SuperTwin.SSHpass, SuperTwin.name, "sudo rm -r /tmp/dt_probing/benchmarks/*")
        scp.put(path, recursive=True, remote_path="/tmp/dt_probing/benchmarks/")
        

    remote_probe.run_sudo_command(ssh, SuperTwin.SSHpass, SuperTwin.name, "sh /tmp/dt_probing/benchmarks/adCARM/gen_bench.sh")
    '''
    scp.get(recursive=True, remote_path = "/tmp/dt_probing/benchmarks/adCARM/Results", local_path = "probing/benchmarks/")

    try:
        detect_utils.cmd("mv probing/benchmarks/Results probing/benchmarks/adCARM_RES") ##On local
    except:
        detect_utils.cmd("rm -r probing/benchmarks/adCARM_RES") ##On local
        detect_utils.cmd("mv probing/benchmarks/Results probing/benchmarks/adCARM_RES") ##On local


def pretty_binding(ugly_binding):

    pretty_binding = ""

    fields = ugly_binding.split("|")

    for item in fields:
        pretty_binding += item
        pretty_binding += " "

    pretty_binding = pretty_binding[:-1]
    return pretty_binding
    

def parse_one_file(adcarm_res, fname):

    fields = fname.strip(".out").split("__")
    #print("fields:", fields)

    fields_keep = []
    for i in range(1, len(fields)):
        sep = fields[i].split("_")
        fields_keep.append(sep)

    thread = fields_keep[5][1]
    this_run_dict = {}
    
    for item in fields_keep:
        if(item[0] != "threads"):
            if(item[0] == "binding"):
                item[1] = pretty_binding(item[1])
            if(item[1] != '0' or item[1] != '1'):
                try:
                    this_run_dict[item[0]] = int(item[1])
                except:
                    this_run_dict[item[0]] = item[1]
            else:
                this_run_dict[item[0]] = bool(int(item[1]))
        
    reader = open(fname, "r")
    lines = reader.readlines()
    reader.close()

    for line in lines:
        fields = line.strip("\n").split(":")
        this_run_dict[fields[0]] = float(fields[1])

    adcarm_res["threads"][thread].append(this_run_dict)
    
    return adcarm_res


def get_threads(files):

    threads = []
    
    for item in files:
        fields = item.split("__")
        thread = fields[6].split("_")[1]
        if thread not in threads:
            threads.append(thread)
            
    return threads


def parse_adcarm_bench():

    adcarm_base = "probing/benchmarks/adCARM_RES/"

    files = glob.glob(adcarm_base + "*.out")
            
    adcarm_res = {}
    adcarm_res["threads"] = {}
    
    threads = get_threads(files)

    for thread in threads:
        adcarm_res["threads"][thread] = []
    
    for fname in files:
        adcarm_res = parse_one_file(adcarm_res, fname)
        

    return adcarm_res
