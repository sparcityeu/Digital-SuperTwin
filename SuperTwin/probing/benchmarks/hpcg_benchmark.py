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
import pprint


def set_hpcg_parameters(HPCG_PARAM):

    nx = HPCG_PARAM["nx"]
    ny = HPCG_PARAM["ny"]
    nz = HPCG_PARAM["nz"]
    time = HPCG_PARAM["time"]
    
    reader = open("probing/benchmarks/hpcg/bin/hpcg.dat", "r")
    lines = reader.readlines()
    reader.close()
    
    lines[2] = str(nx) + " " + str(ny) + " " + str(nz) + "\n"
    lines[3] = str(time) + "\n"

    writer = open("probing/benchmarks/hpcg/bin/hpcg.dat", "w")
    for line in lines:
        writer.write(line)
    writer.close()

    
def generate_hpcg_bench_sh(SuperTwin, HPCG_PARAM):

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
    print("HPCG Benchmark thread set:", thread_set)

    top_base = "/tmp/dt_probing/benchmarks/hpcg/"
    sub_base = "/tmp/dt_probing/benchmarks/hpcg/bin/"

    lines = ["#!/bin/bash \n\n\n",
             "make -C " + top_base + " arch=GCC_OMP \n",
             "cd " + sub_base + " \n"]


    set_hpcg_parameters(HPCG_PARAM)

    for thread in thread_set:

        if str(thread) not in modifiers.keys():
            modifiers[str(thread)] = []
        
        line1 = "export OMP_NUM_THREADS=" + str(thread) + " \n"
        line2 = ""
        if(thread == 1):
            line2 = "likwid-pin -c N:" + str(thread - 1) + " ./xhpcg" + " \n"
        else:
            line2 = "likwid-pin -c N:0-" + str(thread - 1) + " ./xhpcg" + " \n"

        modifiers[str(thread)].append("export OMP_NUM_THREADS=" + str(thread))
        modifiers[str(thread)].append("likwid-pin -c N:0-" + str(thread - 1))
        

        lines.append(line1)
        lines.append(line2)

    writer = open("probing/benchmarks/hpcg/bin/gen_bench.sh", "w+")
    for line in lines:
        writer.write(line)
    writer.close()

    print("HPCG benchmark script, with params",
          "nx:", HPCG_PARAM["nx"],
          "ny:", HPCG_PARAM["ny"],
          "nz:", HPCG_PARAM["nz"],
          "time:", HPCG_PARAM["time"], "is generated..")

    #pprint.pprint(modifiers)
    
    return modifiers


def execute_hpcg_bench(SuperTwin):

    path = detect_utils.cmd("pwd")[1].strip("\n")
    path += "/probing/benchmarks/hpcg"

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SuperTwin.addr, username = SuperTwin.SSHuser, password = SuperTwin.SSHpass)
    
    scp = SCPClient(ssh.get_transport())
    try:
        scp.put(path, recursive=True, remote_path="/tmp/dt_probing/benchmarks/")
    except:
        remote_probe.run_command(ssh, SuperTwin.name, "mkdir /tmp/dt_probing/benchmarks/")
        scp.put(path, recursive=True, remote_path="/tmp/dt_probing/benchmarks/")
        
    #remote_probe.run_command(ssh, SuperTwin.name, "mkdir /tmp/dt_probing/benchmarks/STREAM/STREAM_res/")
    remote_probe.run_sudo_command(ssh, SuperTwin.SSHpass, SuperTwin.name, "sh /tmp/dt_probing/benchmarks/hpcg/bin/gen_bench.sh")
    scp.get(recursive=True, remote_path = "/tmp/dt_probing/benchmarks/hpcg/bin", local_path = "probing/benchmarks/")
    detect_utils.cmd("mv probing/benchmarks/bin probing/benchmarks/HPCG_res")

def parse_one_res(res, _file):

    reader = open(_file, "r")
    lines = reader.readlines()
    reader.close()

    thread = -1
    
    for line in lines:
        if(line.find("Machine Summary::Threads per processes") != -1):
            thread = str(line.strip("\n").split("=")[1])
        if(line.find("GFLOP/s Summary::Raw DDOT") != -1):
            gfps = float(line.strip("\n").split("=")[1])
            res["ddot"][thread] = gfps
        if(line.find("GFLOP/s Summary::Raw WAXPBY") != -1):
            gfps = float(line.strip("\n").split("=")[1])
            res["waxpby"][thread] = gfps
        if(line.find("GFLOP/s Summary::Raw SpMV") != -1):
            gfps = float(line.strip("\n").split("=")[1])
            res["spmv"][thread] = gfps
        if(line.find("Global Problem Dimensions::Global nx") != -1):
            nx = int(line.strip("\n").split("=")[1])
            if(nx != res["parameters"]["nx"] and res["parameters"]["nx"] > 0):
                print("WARNING: HPCG parameters are not consistent within thread set..")
            else:
                res["parameters"]["nx"] = nx
        if(line.find("Global Problem Dimensions::Global ny") != -1):
            ny = int(line.strip("\n").split("=")[1])
            if(ny != res["parameters"]["ny"] and res["parameters"]["ny"] > 0):
                print("WARNING: HPCG parameters are not consistent within thread set..")
            else:
                res["parameters"]["ny"] = ny
        if(line.find("Global Problem Dimensions::Global nz") != -1):
            nz = int(line.strip("\n").split("=")[1])
            if(nx != res["parameters"]["nz"] and res["parameters"]["nz"] > 0):
                print("WARNING: HPCG parameters are not consistent within thread set..")
            else:
                res["parameters"]["nz"] = nz
            

    return res


def parse_hpcg_bench(SuperTwin):

    res_base = "probing/benchmarks/HPCG_res/"
    _files = glob.glob(res_base + "HPCG-Benchmark*")

    hpcg_res = {}
    hpcg_res["spmv"] = {}
    hpcg_res["ddot"] = {}
    hpcg_res["waxpby"] = {}
    hpcg_res["parameters"] = {}
    hpcg_res["parameters"]["nx"] = -1
    hpcg_res["parameters"]["ny"] = -1
    hpcg_res["parameters"]["nz"] = -1
    

    for _file in _files:
        hpcg_res = parse_one_res(hpcg_res, _file)

    hpcg_res["Max_Glob"] = {}
    spmv_max = 0.0
    ddot_max = 0.0
    waxpby_max = 0.0
    
    for key in hpcg_res["spmv"]:
        if(hpcg_res["spmv"][key] > spmv_max):
            spmv_max = hpcg_res["spmv"][key]

    for key in hpcg_res["ddot"]:
        if(hpcg_res["ddot"][key] > spmv_max):
            ddot_max = hpcg_res["ddot"][key]

    for key in hpcg_res["waxpby"]:
        if(hpcg_res["waxpby"][key] > spmv_max):
            waxpby_max = hpcg_res["waxpby"][key]

    hpcg_res["Max_Glob"]["spmv"] = spmv_max
    hpcg_res["Max_Glob"]["ddot"] = ddot_max
    hpcg_res["Max_Glob"]["waxpby"] = waxpby_max
    
    #pprint.pprint(hpcg_res)

    return hpcg_res


if __name__ == "__main__":

    
    parse()
