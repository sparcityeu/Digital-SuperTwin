from influxdb import InfluxDBClient
import subprocess
from subprocess import Popen, PIPE
import shlex
import time
import statistics
import supertwin
import utils
from copy import deepcopy

import paramiko

#import time
from timeit import default_timer as timer

repeat = 3
client = InfluxDBClient(host='localhost', port=8086)

def perform_triad(ssh, SuperTwin):

    stdin, stdout, stderr = ssh.exec_command("likwid-bench -t triad -w S0:100kB:1 -s 5")
    stdout = stdout.readlines()

    time = -1
    flops = -1
    for item in stdout:
        if(item.find("Time") != -1):
            time = item
        if(item.find("Number of Flops:") != -1):
            flops = item
    #cycles = float(flops.strip("Cycles:".strip("\n")))
    time = float(time.strip("Time:").strip("\n").strip(" sec"))
    flops = float(flops.strip("Number of Flops:".strip("\n")))
    
        
    return time, flops, stdout
    #return stdout
####    

####    
def perform_sum(ssh, SuperTwin):

    stdin, stdout, stderr = ssh.exec_command("likwid-bench -t triad -w S0:100kB:1")
    stdout = stdout.readlines()


    time = -1
    for item in stdout:
        if(item.find("Time") != -1):
            time = item
    time = float(time.strip("Time:").strip("\n").strip(" sec"))
    
    #return time
    return stdout
####    

####    
def perform_stream(ssh, SuperTwin):

    stdin, stdout, stderr = ssh.exec_command("likwid-bench -t triad -w S0:100kB:1")
    stdout = stdout.readlines()


    time = -1
    for item in stdout:
        if(item.find("Time") != -1):
            time = item
    time = float(time.strip("Time:").strip("\n").strip(" sec"))
    
    #return time
    return stdout
####    

####    
def perform_peakflops(ssh, SuperTwin):

    stdin, stdout, stderr = ssh.exec_command("likwid-bench -t triad -w S0:100kB:1")
    stdout = stdout.readlines()
    
    time = -1
    for item in stdout:
        if(item.find("Time") != -1):
            time = item
    time = float(time.strip("Time:").strip("\n").strip(" sec"))
    
    #return time
    return stdout
####    

####    
def perform_ddot(ssh, SuperTwin):

    stdin, stdout, stderr = ssh.exec_command("likwid-bench -t triad -w S0:100kB:1")
    stdout = stdout.readlines()
    
    time = -1
    flops = -1
    for item in stdout:
        if(item.find("Time") != -1):
            time = item
        if(item.find("Number of Flops:") != -1):
            flops = item
    time = float(time.strip("Time:").strip("\n").strip(" sec"))
    flops = float(flops.strip("Number of Flops:".strip("\n")))
    #return time
    return stdout
####    

####    
def perform_daxpy(ssh, SuperTwin):

    stdin, stdout, stderr = ssh.exec_command("likwid-bench -t triad -w S0:100kB:1 -s 45")
    stdout = stdout.readlines()
    
    time = -1
    for item in stdout:
        if(item.find("Time") != -1):
            time = item
    time = float(time.strip("Time:").strip("\n").strip(" sec"))
    
    #return time
    return stdout
####    

        
def decide_and_run(ssh, SuperTwin, bench):

    time = -1
    
    if(bench == "triad"):
        time, flops, stdout = perform_triad(ssh, SuperTwin)
    elif(bench == "sum"):
        time = perform_sum(ssh, SuperTwin)
    elif(bench == "stream"):
        time = perform_stream(ssh, SuperTwin)
    elif(bench == "peakflops"):
        time = perform_peakflops(ssh, SuperTwin)
    elif(bench == "ddot"):
        time = perform_ddot(ssh, SuperTwin)
    elif(bench == "daxpy"):
        time = perform_daxpy(ssh, SuperTwin)
    else:
        print("Weird benchmark, exiting,,\n eww:", bench, bench=="triad")
        exit(1)

    return time, flops, stdout


def one_run(SuperTwin, bench):

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SuperTwin.addr, username=SuperTwin.SSHuser, password=SuperTwin.SSHpass)

    times = []

    for i in range(repeat):
        time = decide_and_run(ssh, SuperTwin, bench)
        times.append(time)

    return times

def show_sum(metric):
    val = 0
    points = 0
    zero_points = 0
    ## get stddev of metric
    ## get values bigger than stddev
    client.switch_database("dolap_run")
    query = "select * from " + metric
    res = list(client.query(query))[0]
    #query = "select (_cpu0) from " + metric
    #print("res:", client.query(query))
    for item in res:
        val += item["_cpu0"]
        if(val != 0):
            points += 1
        else:
            zero_points += 1
    #print("metric:", metric, "val:", val)
    print("zero points:", zero_points)
    return val / points
    #return val

#def decide_and_run(SuperTwin, bench):
def one_run_sampled(SuperTwin, bench, config, db):

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SuperTwin.addr, username=SuperTwin.SSHuser, password=SuperTwin.SSHpass)

    
    client.drop_database(db)
    client.create_database(db)
    
    sampling_command = "pcp2influxdb " + config
    sampling_args = shlex.split(sampling_command)
    sampling_process = Popen(sampling_args)
    
    wall = timer()
    time, flops, stdout = decide_and_run(ssh, SuperTwin, bench)
    #time = decide_and_run(ssh, SuperTwin, bench)
    #times.append(time)
    sampling_process.kill()
    wall = timer() - wall
    print("Wall time:", wall, "Reported time:", time, "Ratio:", wall/time)
    ssh.close()

    for line in stdout:
        print(line)

    
        ##analyse here
    val = show_sum("perfevent_hwcounters_UNHALTED_CORE_CYCLES_value")
    val = show_sum("perfevent_hwcounters_UNHALTED_REFERENCE_CYCLES_value")
    val = show_sum("perfevent_hwcounters_INSTRUCTION_RETIRED_value")
    val = show_sum("perfevent_hwcounters_FP_ARITH_SCALAR_DOUBLE_value")
    #print("MFlops/s:", ((val / (1024*1024)) / time) )
    #print("Ratio:", flops / val)
    print("val:", val, "Ratio: ", flops / val)
    val = show_sum("perfevent_hwcounters_UOPS_ISSUED_ANY_value")
    val = show_sum("perfevent_hwcounters_MEM_UOPS_RETIRED_ALL_LOADS_value")
    val = show_sum("perfevent_hwcounters_MEM_UOPS_RETIRED_ALL_STORES_value")
    
    #return times 
    
    

def write_to_file(times, bench, interval, no_metrics):

    print("Writing file:", "--", times, "--", bench, "--", interval, "--", no_metrics)
    
    time_mean = statistics.mean(times)
    time_std = statistics.stdev(times)
    
    writer = open("dolap_cstress.csv", "a")
    line = "dolap," + str(interval) + "," + str(no_metrics) + "," + bench + "," + str(time_mean) + "," + str(time_std) + "," + "1" + "\n"
    writer.write(line)
    writer.close()

if __name__ == "__main__":

    
    my_superTwin = supertwin.SuperTwin("10.36.54.195")
    #benchs = ["triad", "sum", "stream", "peakflops", "ddot", "daxpy"]
    benchs = ["triad"]    
    
    for bench in benchs:
        print("##################" + bench + "##################")
        config = "-t 1 -c shortbench.conf :configured" 
        times = one_run_sampled(my_superTwin, bench, config, "dolap_run")
        print("##################" + bench + "##################")
                
