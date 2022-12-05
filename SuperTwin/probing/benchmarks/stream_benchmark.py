import sys
sys.path.append("../")
sys.path.append("../../")
sys.path.append("../../observation")
sys.path.append("../../sampling")

import utils
import remote_probe
import detect_utils
import observation
import sampling
from bson.objectid import ObjectId

import paramiko
from scp import SCPClient

import glob

def vector_flags(max_vector):

    if(max_vector == "avx"):
        return ["-xAVX"]
    elif(max_vector == "avx2"):
        return ["-xCORE-AVX2"]
    elif(max_vector == "avx512"):
        return ["-xCORE-AVX512", "-qopt-zmm-usage=high"]
    else:
        return []

##Can use the same architecture for creating mpi benchmarks
##Note that benchmarks are copied alongside with probing framework beforehand calling
##this function
def generate_stream_bench_sh(SuperTwin):

    modifiers = {}
    modifiers["environment"] = {}
    
    td = utils.get_twin_description(SuperTwin)
    mt_info = utils.get_multithreading_info(td)
    
    
    no_sockets = mt_info["no_sockets"]
    no_cores_per_socket = mt_info["no_cores_per_socket"]
    no_threads_per_socket = mt_info["no_threads_per_socket"]
    total_cores = mt_info["total_cores"]
    total_threads = mt_info["total_threads"]
    vector = utils.get_biggest_vector_inst(td)
    print("My vector:", vector)
    if(vector == None): ##No vector instructions, so compile with plain gcc
        vector = "gcc"

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

    ##Two possiblities, numa will have two different versions for number of threads that span
    ##multiple numa domains

    is_numa = utils.is_numa_td(td)
    stream_compiler_flags = ["-O3", "-DNTIMES=100", "-DOFFSET=0", "-DSTREAM_TYPE=double",
                             "-DSTREAM_ARRAY_SIZE=268435456", "-Wall", "-mcmodel=medium",
                             "-qopenmp", "-shared-intel", "-qopt-streaming-stores always"]
    
    stream_compiler_flags += vector_flags(vector)
    modifiers["environment"]["flags"] = stream_compiler_flags

    base = "/tmp/dt_probing/benchmarks/STREAM"
    make_lines = ["#!/bin/bash \n\n\n",
                  "source /opt/intel/oneapi/setvars.sh \n",
                  "make -C " + base + " " + "stream_" + vector + "\n\n",
                  "mkdir /tmp/dt_probing/benchmarks/STREAM_RES \n"]
    
    writer = open("probing/benchmarks/compile_stream_bench.sh", "w+")
    for line in make_lines:
        writer.write(line)
    writer.close()
    maker = "bash /tmp/dt_probing/benchmarks/compile_stream_bench.sh"
    runs = {}
    for thread in thread_set:
        if(thread == 1):
            thr_name = "t_" + str(thread)
            exec_name = "./stream_" + vector
            runs[thr_name] = "likwid-pin -c N:0 ./stream_" + vector + " &>> " + thr_name + ".txt"
            try:
                modifiers[thr_name].append("likwid-pin -c N:0")
            except:
                modifiers[thr_name] = []
                modifiers[thr_name].append("likwid-pin -c N:0")
        else:
            thr_name = "t_" + str(thread) ##For normal
            exec_name = "./stream_" + vector
            runs[thr_name] = "likwid-pin -c N:0-" + str(thread-1) + " ./stream_" + vector + " &>> " + thr_name + ".txt"
            try:
                modifiers[thr_name].append("likwid-pin -c N:0-" + str(thread-1))
            except:
                modifiers[thr_name] = []
                modifiers[thr_name].append("likwid-pin -c N:0" + str(thread-1))
        if(is_numa and thread != 1):                               
            thr_name_numa = "t_" + str(thread) + "_numa" #For socket binding
            per_socket = int(thread / 2)
            #print("per_socket:", per_socket)
            exec_name = "./stream_" + vector
            ##Hardcoded for 2 nodes for now
            runs[thr_name_numa] = "likwid-pin -c S0:0-" + str(per_socket - 1) + "@S1:0-" + str(per_socket - 1)+ " ./stream_" + vector + " &>> " + thr_name_numa + ".txt"
            
            try:
                modifiers[thr_name_numa].append("likwid-pin -c S0:0- " + str(per_socket - 1) + "@S1:0-" + str(per_socket - 1))
            except:
                modifiers[thr_name_numa] = []
                modifiers[thr_name_numa].append("likwid-pin -c S0:0- " + str(per_socket - 1) + "@S1:0-" + str(per_socket - 1))
                        

    for key in runs:
        writer = open(SuperTwin.name + "_STREAM_" + key + ".sh", "w+")
        writer.write("#!/bin/bash" + "\n")
        writer.write("source /opt/intel/oneapi/setvars.sh" + "\n")
        writer.write("cd /tmp/dt_probing/benchmarks/STREAM \n")
        writer.write(runs[key] + "\n")
        writer.close()
        
    print("STREAM benchmark run scripts generated..")

    return modifiers, maker, runs


def compile_stream_bench(SuperTwin, maker):

    ##This will be common together with hpcg ?
    path = detect_utils.cmd("pwd")[1].strip("\n")
    print("path:", path)
    path += "/probing/benchmarks/STREAM"
    print("path:", path)
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SuperTwin.addr, username = SuperTwin.SSHuser, password = SuperTwin.SSHpass)
    
    scp = SCPClient(ssh.get_transport())

    ##Copy benchmark framework if there is problem
    try:
        scp.put(path, recursive=True, remote_path="/tmp/dt_probing/benchmarks/")
        remote_probe.run_sudo_command(ssh, SuperTwin.SSHpass, SuperTwin.name, "sudo rm -r /tmp/dt_probing/benchmarks/*")
        scp.put(path, recursive=True, remote_path="/tmp/dt_probing/benchmarks/")
    except:
        remote_probe.run_command(ssh, SuperTwin.name, "mkdir /tmp/dt_probing/benchmarks/")
        scp.put(path, recursive=True, remote_path="/tmp/dt_probing/benchmarks/")
        remote_probe.run_sudo_command(ssh, SuperTwin.SSHpass, SuperTwin.name, "sudo rm -r /tmp/dt_probing/benchmarks/*")
        scp.put(path, recursive=True, remote_path="/tmp/dt_probing/benchmarks/")

    scp.put("probing/benchmarks/compile_stream_bench.sh", remote_path="/tmp/dt_probing/benchmarks/")
    remote_probe.run_sudo_command(ssh, SuperTwin.SSHpass, SuperTwin.name, maker)


##I need some functions like
##utils.copy_file_to_remote()
##utils.copy_folder_to_remote()

def copy_file_to_remote(SuperTwin, f_name, remote_path="tmp/dt_files/"):

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SuperTwin.addr, username = SuperTwin.SSHuser, password = SuperTwin.SSHpass)
    scp = SCPClient(ssh.get_transport())

    try:
        scp.put(f_name, remote_path=remote_path)
    except:
        remote_probe.run_command(ssh, SuperTwin.name, "mkdir /tmp/dt_files/")
        scp.put(f_name, remote_path=remote_path)
    
def execute_stream_runs(SuperTwin, runs):
    
    for key in runs:
        script_name = SuperTwin.name + "_STREAM_" + key + ".sh"
        #copy_file_to_remote(SuperTwin, script_name)
        time, uid = observation.observe_script_wrap(SuperTwin, script_name)
        print("Observation", uid, "is completed in", time, "seconds")

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
        
    remote_probe.run_command(ssh, SuperTwin.name, "mkdir /tmp/dt_probing/benchmarks/STREAM/STREAM_res_" + SuperTwin.name)
    remote_probe.run_sudo_command(ssh, SuperTwin.SSHpass, SuperTwin.name, "sh /tmp/dt_probing/benchmarks/STREAM/gen_bench.sh")
    scp.get(recursive=True, remote_path = "/tmp/dt_probing/benchmarks/STREAM/STREAM_res_" + SuperTwin.name, local_path = "probing/benchmarks/")
    


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

    res_base = "probing/benchmarks/STREAM_res_" + SuperTwin.name
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
