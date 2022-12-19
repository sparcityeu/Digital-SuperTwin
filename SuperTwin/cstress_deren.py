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

repeat = 2
client = InfluxDBClient(host='localhost', port=8086)

def perform_triad(ssh, SuperTwin):

    stdin, stdout, stderr = ssh.exec_command("likwid-bench -t triad -w S0:1MB:1 -s 1")
    stdout = stdout.readlines()


    time = -1
    for item in stdout:
        if(item.find("Time") != -1):
            time = item
    time = float(time.strip("Time:").strip("\n").strip(" sec"))
    
    return time
####    

####    
def perform_sum(ssh, SuperTwin):

    stdin, stdout, stderr = ssh.exec_command("likwid-bench -t triad -w S0:1MB:1 -s 1")
    stdout = stdout.readlines()


    time = -1
    for item in stdout:
        if(item.find("Time") != -1):
            time = item
    time = float(time.strip("Time:").strip("\n").strip(" sec"))
    
    return time
####    

####    
def perform_stream(ssh, SuperTwin):

    stdin, stdout, stderr = ssh.exec_command("likwid-bench -t triad -w S0:1MB:1 -s 1")
    stdout = stdout.readlines()


    time = -1
    for item in stdout:
        if(item.find("Time") != -1):
            time = item
    time = float(time.strip("Time:").strip("\n").strip(" sec"))
    
    return time
####    

####    
def perform_peakflops(ssh, SuperTwin):

    stdin, stdout, stderr = ssh.exec_command("likwid-bench -t triad -w S0:1MB:1 -s 1")
    stdout = stdout.readlines()
    
    time = -1
    for item in stdout:
        if(item.find("Time") != -1):
            time = item
    time = float(time.strip("Time:").strip("\n").strip(" sec"))
    
    return time
####    

####    
def perform_ddot(ssh, SuperTwin):

    stdin, stdout, stderr = ssh.exec_command("likwid-bench -t triad -w S0:1MB:1 -s 1")
    stdout = stdout.readlines()
    
    time = -1
    for item in stdout:
        if(item.find("Time") != -1):
            time = item
    time = float(time.strip("Time:").strip("\n").strip(" sec"))
    
    return time
####    

####    
def perform_daxpy(ssh, SuperTwin):

    stdin, stdout, stderr = ssh.exec_command("likwid-bench -t triad -w S0:1MB:1 -s 1")
    stdout = stdout.readlines()
    
    time = -1
    for item in stdout:
        if(item.find("Time") != -1):
            time = item
    time = float(time.strip("Time:").strip("\n").strip(" sec"))
    
    return time
####    

        
def decide_and_run(ssh, SuperTwin, bench):

    time = -1
    
    if(bench == "triad"):
        time = perform_triad(ssh, SuperTwin)
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

    return time


def one_run(SuperTwin, bench):

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SuperTwin.addr, username=SuperTwin.SSHuser, password=SuperTwin.SSHpass)

    times = []

    for i in range(repeat):
        time = decide_and_run(ssh, SuperTwin, bench)
        times.append(time)

    return times

#def decide_and_run(SuperTwin, bench):
def one_run_sampled(SuperTwin, bench, config, db):

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SuperTwin.addr, username=SuperTwin.SSHuser, password=SuperTwin.SSHpass)

    for i in range(repeat):
    
        client.drop_database(db)
        client.create_database(db)
        
        sampling_command = "pcp2influxdb " + config
        sampling_args = shlex.split(sampling_command)
        sampling_process = Popen(sampling_args)

        times = []
        
        for i in range(5):
            time = decide_and_run(ssh, SuperTwin, bench)
            times.append(time)
        sampling_process.kill()


    ssh.close()

    return times 
    
    

def write_to_file(times, bench, interval, no_metrics):

    print("Writing file:", "--", times, "--", bench, "--", interval, "--", no_metrics)
    
    time_mean = statistics.mean(times)
    time_std = statistics.stdev(times)
    
    writer = open("deren_cstress.csv", "a")
    line = "deren," + str(interval) + "," + str(no_metrics) + "," + bench + "," + str(time_mean) + "," + str(time_std) + "," + "1" + "\n"
    writer.write(line)
    writer.close()

if __name__ == "__main__":

    
    my_superTwin = supertwin.SuperTwin("10.92.53.74")

    intervals = ["1", "0.5", "0.25", "0.125", "0.0625"]
    metrics = [" -c cstress/deren_1.conf",
               " -c cstress/deren_8.conf",
               " -c cstress/deren_16.conf",
               " -c cstress/deren_24.conf"]
               
    benchs = ["triad", "sum", "stream", "peakflops", "ddot", "daxpy"]

    '''
    times = one_run(my_superTwin, "triad")
    write_to_file(times, "triad", -1, -1)
    times = one_run(my_superTwin, "sum")
    write_to_file(times, "sum", -1, -1)
    times = one_run(my_superTwin, "stream")
    write_to_file(times, "stream", -1, -1)
    times = one_run(my_superTwin, "peakflops")
    write_to_file(times, "peakflops", -1, -1)
    times = one_run(my_superTwin, "ddot")
    write_to_file(times, "ddot", -1, -1)
    times = one_run(my_superTwin, "daxpy")
    write_to_file(times, "daxpy", -1, -1)
    '''
    
    for interval in intervals:
        for metric in metrics:
            for bench in benchs:
                config = "-t " + interval + metric + " :configured" ##
                print("config:", config)
                times = one_run_sampled(my_superTwin, bench, config, "deren_run")
                print("times:", times, " config:", config)
                write_to_file(times, bench, interval, metric)

    '''
    ##f = 1
    times = one_run(my_superTwin, "triad", "-t 1 -c cstress/deren_1.conf")
    
    times = one_run(my_superTwin, "sum", "-t 1 -c cstress/deren_1.conf")
    write_to_file(times, "sum", "1", "1"):
    times = one_run(my_superTwin, "stream", "-t 1 -c cstress/deren_1.conf")
    write_to_file(times, "stream", "1", "1"):
    times = one_run(my_superTwin, "peakflops", "-t 1 -c cstress/deren_1.conf")
    write_to_file(times, "peakflops", "1", "1"):
    times = one_run(my_superTwin, "ddot", "-t 1 -c cstress/deren_1.conf")
    write_to_file(times, "ddot", "1", "1"):
    times = one_run(my_superTwin, "daxpy", "-t 1 -c cstress/deren_1.conf")
    write_to_file(times, "daxpy", "1", "1"):

    #f = 2
    times = one_run(my_superTwin, "triad", "-t 0.5 -c cstress/deren_1.conf")
    write_to_file(times, "triad", "0.5", "1"):
    times = one_run(my_superTwin, "sum", "-t 0.5 -c cstress/deren_1.conf")
    write_to_file(times, "sum", "0.5", "1"):
    times = one_run(my_superTwin, "stream", "-t 0.5 -c cstress/deren_1.conf")
    write_to_file(times, "stream", "0.5", "1"):
    times = one_run(my_superTwin, "peakflops", "-t 0.5 -c cstress/deren_1.conf")
    write_to_file(times, "peakflops", "0.5", "1"):
    times = one_run(my_superTwin, "ddot", "-t 0.5 -c cstress/deren_1.conf")
    write_to_file(times, "ddot", "0.5", "1"):
    times = one_run(my_superTwin, "daxpy", "-t 0.5 -c cstress/deren_1.conf")
    write_to_file(times, "daxpy", "0.5", "1"):

    #f = 4
    times = one_run(my_superTwin, "triad", "-t 0.25 -c cstress/deren_1.conf")
    write_to_file(times, "triad", "0.25", "1"):
    times = one_run(my_superTwin, "sum", "-t 0.25 -c cstress/deren_1.conf")
    write_to_file(times, "sum", "0.25", "1"):
    times = one_run(my_superTwin, "stream", "-t 0.25 -c cstress/deren_1.conf")
    write_to_file(times, "stream", "0.25", "1"):
    times = one_run(my_superTwin, "peakflops", "-t 0.25 -c cstress/deren_1.conf")
    write_to_file(times, "peakflops", "0.25", "0.1"):
    times = one_run(my_superTwin, "ddot", "-t 0.25 -c cstress/deren_1.conf")
    write_to_file(times, "ddot", "0.25", "1"):
    times = one_run(my_superTwin, "daxpy", "-t 0.25 -c cstress/deren_1.conf")
    write_to_file(times, "daxpy", "0.25", "1"):

    #f = 8
    times = one_run(my_superTwin, "triad", "-t 0.125 -c cstress/deren_1.conf")
    write_to_file(times, "triad", "0.125", "1"):
    times = one_run(my_superTwin, "sum", "-t 0.125 -c cstress/deren_1.conf")
    write_to_file(times, "sum", "0.125", "1"):
    times = one_run(my_superTwin, "stream", "-t 0.125 -c cstress/deren_1.conf")
    write_to_file(times, "stream", "0.125", "1"):
    times = one_run(my_superTwin, "peakflops", "-t 0.125 -c cstress/deren_1.conf")
    write_to_file(times, "peakflops", "0.125", "1"):
    times = one_run(my_superTwin, "ddot", "-t 0.125 -c cstress/deren_1.conf")
    write_to_file(times, "ddot", "0.125", "1"):
    times = one_run(my_superTwin, "daxpy", "-t 0.125 -c cstress/deren_1.conf")
    write_to_file(times, "daxpy", "0.125", "1"):

    #f = 16
    times = one_run(my_superTwin, "triad", "-t 0.0625 -c cstress/deren_1.conf")
    write_to_file(times, "triad", "0.0625", "1"):
    times = one_run(my_superTwin, "sum", "-t 0.0625 -c cstress/deren_1.conf")
    write_to_file(times, "sum", "0.0625", "1"):
    times = one_run(my_superTwin, "stream", "-t 0.0625 -c cstress/deren_1.conf")
    write_to_file(times, "stream", "0.0625", "1"):
    times = one_run(my_superTwin, "peakflops", "-t 0.025 -c cstress/deren_1.conf")
    write_to_file(times, "peakflops", "0.0625", "1"):
    times = one_run(my_superTwin, "ddot", "-t 0.0625 -c cstress/deren_1.conf")
    write_to_file(times, "ddot", "0.0625", "1"):
    times = one_run(my_superTwin, "daxpy", "-t 0.0625 -c cstress/deren_1.conf")
    write_to_file(times, "daxpy", "0.0625", "1"):

    
    one_run(my_superTwin, "sum")
    one_run(my_superTwin, "stream")
    one_run(my_superTwin, "peakflops")
    one_run(my_superTwin, "ddot")
    one_run(my_superTwin, "daxpy")
    '''
    
    
