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

##Can use the same architecture for creating mpi benchmarks
def generate_stream_bench_sh(SuperTwin):

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
    print("STREAM Benchmark thread set:", thread_set)

    base = "/tmp/dt_probing/benchmarks/STREAM/"
    
    lines = ["#!/bin/bash \n\n\n",
             "source /opt/intel/oneapi/setvars.sh \n",
             "make -C " + base + " \n\n"
             "KMP_AFFINITY=granularity=fine,compact,1,0 \n\n"]
    
    modifiers["environment"].append("KMP_AFFINITY=granularity=fine,compact,1,0")
    
    for thread in thread_set:

        if str(thread) not in modifiers.keys():
            modifiers[str(thread)] = []
        
        line1 = "export OMP_NUM_THREADS=" + str(thread) + " \n"
        line2 = ""
        if(thread == 1):
            line2 = "likwid-pin -c N:" + str(thread - 1) + " " + base + "./stream.omp.AVX512.80M.20x.icc &>> " + base + "STREAM_res/t" + str(thread) + ".txt \n\n"
        else:
            line2 = "likwid-pin -c N:0-" + str(thread - 1) + " " + base + "./stream.omp.AVX512.80M.20x.icc &>> " + base + "STREAM_res/t" + str(thread) + ".txt \n\n"

        modifiers[str(thread)].append("export OMP_NUM_THREADS=" + str(thread))
        modifiers[str(thread)].append("likwid-pin -c N:0-" + str(thread - 1))
        

        lines.append(line1)
        lines.append(line2)
        

    writer = open("probing/benchmarks/STREAM/gen_bench.sh", "w+")
    for line in lines:
        writer.write(line)
    writer.close()

    print("STREAM benchmark script generated..")

    return modifiers


def execute_stream_bench(SuperTwin):

    ##This will be common together with hpcg ?
    path = detect_utils.cmd("pwd")[1].strip("\n")
    print("path:", path)
    path += "/probing/benchmarks/STREAM"
    print("path:", path)
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SuperTwin.addr, username = SuperTwin.SSHuser, password = SuperTwin.SSHpass)
    
    scp = SCPClient(ssh.get_transport())

    try:
        scp.put(path, recursive=True, remote_path="/tmp/dt_probing/benchmarks/")
        remote_probe.run_sudo_command(ssh, SuperTwin.SSHpass, SuperTwin.name, "sudo rm -r /tmp/dt_probing/benchmarks/*")
        scp.put(path, recursive=True, remote_path="/tmp/dt_probing/benchmarks/")
    except:
        remote_probe.run_command(ssh, SuperTwin.name, "mkdir /tmp/dt_probing/benchmarks/")
        scp.put(path, recursive=True, remote_path="/tmp/dt_probing/benchmarks/")
        remote_probe.run_sudo_command(ssh, SuperTwin.SSHpass, SuperTwin.name, "sudo rm -r /tmp/dt_probing/benchmarks/*")
        scp.put(path, recursive=True, remote_path="/tmp/dt_probing/benchmarks/")
        
    remote_probe.run_command(ssh, SuperTwin.name, "mkdir /tmp/dt_probing/benchmarks/STREAM/STREAM_res/")
    remote_probe.run_sudo_command(ssh, SuperTwin.SSHpass, SuperTwin.name, "sh /tmp/dt_probing/benchmarks/STREAM/gen_bench.sh")
    scp.get(recursive=True, remote_path = "/tmp/dt_probing/benchmarks/STREAM/STREAM_res", local_path = "probing/benchmarks/")
    


def parse_one_stream_res(res_mt_scale, one_res):

    thread = one_res.split("/t")[1]
    thread = int(thread.split(".")[0])
    #print("file:", one_res, "threads:", thread)

    reader = open(one_res, "r")
    lines = reader.readlines()
    reader.close()

    run_max = 0.0
    for line in lines:
        if(line.find("Copy") != -1 or
           line.find("Scale") != -1 or
           line.find("Add") != -1 or
           line.find("Triad") != -1):

            fields = line.split(" ")
            fields = [x for x in fields if x != ""]
            fields = [x.strip(":") for x in fields]
            res = float(fields[1])
            #print("file:", one_res, "field:", fields[0], "res:", res)
            
            res_mt_scale[fields[0]][str(thread)] = res
            if(res > run_max):
                run_max = res

    res_mt_scale["Max_Thr"][str(thread)] = run_max
    
    return res_mt_scale
    
def parse_stream_bench(SuperTwin):

    res_base = "probing/benchmarks/STREAM_res/"
    files = glob.glob(res_base + "*.txt")

    res_mt_scale = {}
    res_mt_scale["Copy"] = {}
    res_mt_scale["Scale"] = {}
    res_mt_scale["Add"] = {}
    res_mt_scale["Triad"] = {}
    res_mt_scale["Max_Thr"] = {}

    for _file in files:
        res_mt_scale = parse_one_stream_res(res_mt_scale, _file)

    max_global = 0
    for key in res_mt_scale["Max_Thr"]:
        if res_mt_scale["Max_Thr"][key] > max_global:
            max_global = res_mt_scale["Max_Thr"][key]

    res_mt_scale["Max_Glob"] = max_global
    
    return res_mt_scale
