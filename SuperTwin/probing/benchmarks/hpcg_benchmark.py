import subprocess
import sys
sys.path.append("../")
sys.path.append("../../")
sys.path.append("../../observation")
sys.path.append("../../sampling")

import observation
import sampling

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

    td = utils.get_twin_description(SuperTwin)

    mt_info = utils.get_multithreading_info(td)

    no_sockets = mt_info["no_sockets"]
    no_cores_per_socket = mt_info["no_cores_per_socket"]
    no_threads_per_socket = mt_info["no_threads_per_socket"]
    total_cores = mt_info["total_cores"]
    total_threads = mt_info["total_threads"]
    is_numa = utils.is_numa_td(td)

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

    msr = utils.get_msr_td(td)
    vector = utils.get_biggest_vector_inst(td)

    vecmsr = ""
    if(msr == "skx"):
        vecmsr = "skx"
    if(vector == "avx512" or vector == "avx2"):
        vecmsr = "avx2"
    else:
        vecmsr = "avx"
    
    set_hpcg_parameters(HPCG_PARAM)

    '''
    make_lines = ["#!/bin/bash \n\n\n",
                  "source /opt/intel/oneapi/setvars.sh \n",
                  "mkdir /tmp/dt_probing/benchmarks/HPCG_RES_" + SuperTwin.name + "\n"]

    writer = open("probing/benchmarks/prepare_hpcg.sh", "w+")
    for line in make_lines:
        writer.write(line)
    writer.close()
    maker = "bash /tmp/dt_probing/benchmarks/compile_hpcg_bench.sh"
    '''
    runs = {}

    for thread in thread_set:
        print("modifiers:", modifiers)
        thr_name = "t_" + str(thread)
        modif_key = str(thread)
        if(thread == 1):
            runs[thr_name] = "likwid-pin -c N:0 ./xhpcg_" + vecmsr
            try:
                modifiers[modif_key].append("likwid-pin -c N:0")
            except:
                modifiers[modif_key] = []
                modifiers[modif_key].append("likwid-pin -c N:0")
        else:
            if(is_numa):
                per_socket = int(thread / 2)
                per_socket_string = "S0:" + str(per_socket - 1) + "@" + "S1:" + str(per_socket - 1)
                affinity = utils.prepare_st_likwid_pin(per_socket_string)
                affinity = "likwid-pin -q -c " + affinity
                runs[thr_name] = affinity + " ./xhpcg_" + vecmsr
                try:
                    modifiers[modif_key].append(pin_and_thread)
                except:
                    modifiers[modif_key] = []
                    modifiers[modif_key].append(pin_and_thread)
            else:
                affinity = "likwid-pin -c N:0-" + str(thread - 1) + " ./xhpcg_" + vecmsr
                runs[thr_name] = affinity
                try:
                    modifiers[modif_key].append(affinity.split(" ./xhpcg")[0])
                except:
                    modifiers[modif_key] = []
                    modifiers[modif_key].append(affinity.split(" ./xhpcg")[0])

                
    for key in runs:
        writer = open(SuperTwin.name + "_HPCG_" + key + ".sh", "w+") 
        writer.write("#!/bin/bash" + "\n")
        writer.write("source /opt/intel/oneapi/setvars.sh \n")
        writer.write("cd /tmp/dt_probing/benchmarks/mkl_hpcg \n")
        writer.write(runs[key] + "\n")

    print("HPCG benchmark run scripts generated")

    print("modifiers here:", modifiers)
    return modifiers, runs

    
##deprecated
def generate_hpcg_bench_deprecated_sh(SuperTwin, HPCG_PARAM):

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
    path += "/probing/benchmarks/mkl_hpcg"

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


def copy_remote_files_to_local(SuperTwin):

    path = detect_utils.cmd("pwd")[1].strip("\n")
    print("path:", path)
    
    subprocess.call(["rm", "-r", path + "/probing/benchmarks/HPCG_RES_" + SuperTwin.name])
    subprocess.call(["mkdir", path + "/probing/benchmarks/HPCG_RES_" + SuperTwin.name])
        
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SuperTwin.addr, username = SuperTwin.SSHuser, password = SuperTwin.SSHpass)

    scp = SCPClient(ssh.get_transport())
    
    base_path = "/tmp/dt_probing/benchmarks/mkl_hpcg"
    list_path = "/tmp/dt_probing/benchmarks/mkl_hpcg/"+ "*-*.txt"
    local_path = "/probing/benchmarks/HPCG_RES_" + SuperTwin.name
    stdin, stdout, stderr = ssh.exec_command("ls " + list_path)
    print("that fuck:", "ls " + list_path)
    result = stdout.read().split()

    #print("FUCKING result:", result)
    for per_result in result:
        per_result = per_result.decode("utf-8")
        print("getting ", per_result, "to", local_path)
        scp.get(remote_path = per_result, local_path = path + local_path)
        
    scp.close()
    ssh.close()


def copy_binary_files_to_remote(SuperTwin):

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SuperTwin.addr, username = SuperTwin.SSHuser, password = SuperTwin.SSHpass)

    scp = SCPClient(ssh.get_transport())

    path = detect_utils.cmd("pwd")[1].strip("\n")
    path += "/probing/benchmarks/mkl_hpcg"

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


def copy_script_files_to_remote(SuperTwin):

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SuperTwin.addr, username = SuperTwin.SSHuser, password = SuperTwin.SSHpass)

    scp = SCPClient(ssh.get_transport())

    _filter = SuperTwin.name + "_HPCG*"
    _files = detect_utils.cmd("ls " + _filter)[1].strip("\n").split()

    for _file in _files:
        #path = detect_utils.cmd("pwd")[1].strip("\n") + "/" + _file
        scp.put(_file, remote_path = "/tmp/dt_files")
        print("putting file:", _file)

def get_benchmark_observation_fields(td, script):

    reader = open(script, "r")
    lines = reader.readlines()
    command = lines[3].strip("\n")
    affinity = command.split("./")[0].strip(" ")
    threads = utils.resolve_likwid_pin(td, affinity)
    thread_count = len(threads)
    observation = {}
    observation["command"] = command
    observation["affinity"] = affinity
    observation["thread_count"] = thread_count
    observation["threads"] = threads

    return observation
    
def execute_hpcg_runs(SuperTwin, runs):

    
    td = utils.get_twin_description(SuperTwin)
    
    copy_binary_files_to_remote(SuperTwin)
    copy_script_files_to_remote(SuperTwin)
    
    
    for key in runs:
        script_name = SuperTwin.name + "_HPCG_" + key + ".sh"
        time, uid = observation.observe_script_wrap(SuperTwin, script_name)
        observation_dict = {}
        print("Observation", uid, "is completed in", time, "seconds")
        observation_dict = get_benchmark_observation_fields(td, script_name)
        observation_dict["name"] = "HPCG_" + key
        observation_dict["duration"] = time
        observation_dict["uid"] = uid
        observation_dict["metrics"] = {}
        observation_dict["metrics"]["software"] = []
        observation_dict["metrics"]["hardware"] = []

        for metric in SuperTwin.monitor_metrics:
            if(metric.find("RAPL") == -1):
                observation_dict["metrics"]["software"].append(metric)
        for metric in SuperTwin.observation_metrics:
            observation_dict["metrics"]["hardware"].append(metric)
        SuperTwin.update_twin_document__add_observation(observation_dict)
    
    copy_remote_files_to_local(SuperTwin)

##deprecated
def parse_hpcg_bench(SuperTwin):

    path = detect_utils.cmd("pwd")[1].strip("\n")
    print("path:", path)
    res_base = path + "/probing/benchmarks/HPCG_RES_" + SuperTwin.name
    print("res base:", res_base)
    _files = glob.glob(res_base + "/*.txt")

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
