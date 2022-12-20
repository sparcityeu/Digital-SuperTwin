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

AIs = {'triad': 0.0625,
       'sum': 0.125,
       'stream': 0.833,
       'peakflops': 2.0,
       'ddot': 0.125,
       'daxpy': 0.833}


accuracy_set = ["perfevent_hwcounters_UNHALTED_REFERENCE_CYCLES_value",
                "perfevent_hwcounters_INSTRUCTION_RETIRED_value",
                "perfevent_hwcounters_FP_ARITH_SCALAR_DOUBLE_value",
                "perfevent_hwcounters_UOPS_RETIRED_ANY_value",
                "perfevent_hwcounters_MEM_UOPS_RETIRED_ALL_LOADS_value",
                "perfevent_hwcounters_MEM_UOPS_RETIRED_ALL_STORES_value"]


def parse_likwid_bench(stdout):

    time = -1
    flops = -1
    cycles = -1
    mflops_s = -1
    mbyte_s = -1
    databytes = -1
    instructions = -1
    uops = -1
    for item in stdout:
        if(item.find("Time") != -1):
            time = item
        if(item.find("Number of Flops:") != -1):
            flops = item
        if(item.find("Cycles:") != -1):
            cycles = item
        if(item.find("MFlops/s") != -1):
            mflops_s = item
        if(item.find("Data volume") != -1):
            databytes = item
        if(item.find("MByte/s") != -1):
            mbyte_s = item
        if(item.find("Instructions") != -1):
            instructions = item
        if(item.find("UOPs") != -1):
            uops = item

    cycles = float(cycles.strip("Cycles:".strip("\n")))
    time = float(time.strip("Time:").strip("\n").strip(" sec"))
    flops = float(flops.strip("Number of Flops:".strip("\n")))
    mflops_s = float(mflops_s.strip("MFlops/s:").strip("\n"))
    databytes = float(databytes.strip("Data volume (Byte):").strip("\n"))
    mbytes_s = float(mbyte_s.strip("MByte/s:").strip("\n"))
    instructions = float(instructions.strip("Instructions:").strip("\n"))
    uops = float(uops.strip("UOPs:").strip("\n"))
            
    return cycles, time, flops, mflops_s, databytes, mbytes_s, instructions, uops


def perform_triad(ssh, SuperTwin):

    stdin, stdout, stderr = ssh.exec_command("likwid-bench -t triad -w S0:100kB:1 -s 2")
    stdout = stdout.readlines()

    cycles, time, flops, mflops_s, databytes, mbytes_s, instructions, uops = parse_likwid_bench(stdout)
    
    return time, cycles, flops, mflops_s, databytes, mbytes_s, instructions, uops, stdout
####    

####    
def perform_sum(ssh, SuperTwin):

    stdin, stdout, stderr = ssh.exec_command("likwid-bench -t sum -w S0:100kB:1 -s 2")
    stdout = stdout.readlines()

    cycles, time, flops, mflops_s, databytes, mbytes_s, instructions, uops = parse_likwid_bench(stdout)
    
    return time, cycles, flops, mflops_s, databytes, mbytes_s, instructions, uops, stdout
    
####    

####    
def perform_stream(ssh, SuperTwin):

    stdin, stdout, stderr = ssh.exec_command("likwid-bench -t stream -w S0:100kB:1")
    stdout = stdout.readlines()

    cycles, time, flops, mflops_s, databytes, mbytes_s, instructions, uops = parse_likwid_bench(stdout)
    
    return time, cycles, flops, mflops_s, databytes, mbytes_s, instructions, uops, stdout
    
####    

####    
def perform_peakflops(ssh, SuperTwin):

    stdin, stdout, stderr = ssh.exec_command("likwid-bench -t peakflops -w S0:100kB:1")
    stdout = stdout.readlines()

    cycles, time, flops, mflops_s, databytes, mbytes_s, instructions, uops = parse_likwid_bench(stdout)
    
    return time, cycles, flops, mflops_s, databytes, mbytes_s, instructions, uops, stdout
    
####    

####    
def perform_ddot(ssh, SuperTwin):

    stdin, stdout, stderr = ssh.exec_command("likwid-bench -t ddot -w S0:100kB:1")
    stdout = stdout.readlines()

    cycles, time, flops, mflops_s, databytes, mbytes_s, instructions, uops = parse_likwid_bench(stdout)
    
    return time, cycles, flops, mflops_s, databytes, mbytes_s, instructions, uops, stdout
    
####    

####    
def perform_daxpy(ssh, SuperTwin):

    stdin, stdout, stderr = ssh.exec_command("likwid-bench -t daxpy -w S0:100kB:1 -s 2")
    stdout = stdout.readlines()

    cycles, time, flops, mflops_s, databytes, mbytes_s, instructions, uops = parse_likwid_bench(stdout)
    
    return time, cycles, flops, mflops_s, databytes, mbytes_s, instructions, uops, stdout
    
####    

#time, cycles, flops, mflops_s, mbytes_s, instructions, uops
def decide_and_run(ssh, SuperTwin, bench):

    time = -1
    
    if(bench == "triad"):
        time, cycles, flops, mflops_s, databytes, mbytes_s, instructions, uops, stdout = perform_triad(ssh, SuperTwin)
    elif(bench == "sum"):
        time, cycles, flops, mflops_s, databytes, mbytes_s, instructions, uops, stdout = perform_sum(ssh, SuperTwin)
    elif(bench == "stream"):
        time, cycles, flops, mflops_s, databytes, mbytes_s, instructions, uops, stdout = perform_stream(ssh, SuperTwin)
    elif(bench == "peakflops"):
        time, cycles, flops, mflops_s, databytes, mbytes_s, instructions, uops, stdout = perform_peakflops(ssh, SuperTwin)
    elif(bench == "ddot"):
        time, cycles, flops, mflops_s, databytes, mbytes_s, instructions, uops, stdout = perform_ddot(ssh, SuperTwin)
    elif(bench == "daxpy"):
        time, cycles, flops, mflops_s, databytes, mbytes_s, instructions, uops, stdout = perform_daxpy(ssh, SuperTwin)
    else:
        print("Weird benchmark, exiting,,\n eww:", bench)
        exit(1)
        
    return time, cycles, flops, mflops_s, databytes, mbytes_s, instructions, uops, stdout


def one_run(SuperTwin, bench):

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SuperTwin.addr, username=SuperTwin.SSHuser, password=SuperTwin.SSHpass)

    times = []

    for i in range(repeat):
        time, cycles, flops, mflops_s, databytes, mbytes_s, instructions, uops, stdout = decide_and_run(ssh, SuperTwin, bench)
        times.append(time)

    return time, cycles, flops, mflops_s, databytes, mbytes_s, instructions, uops, stdout

def get_sum(metric):
    val = 1
    points = 0
    zero_points = 0
    ## get stddev of metric
    ## get values bigger than stddev

    client.switch_database("dolap_run")
    query = "select _cpu0 from " + metric
    res = list(client.query(query))[0]
    _stdev = "select stddev(_cpu0) from " + metric
    _stdev_res = list(client.query(_stdev))[0][0]['stddev']
    #print("_stdev_res:", _stdev_res)
    for item in res:
        if(item["_cpu0"] > _stdev_res):
            val += item["_cpu0"]
            points += 1
        else:
            zero_points += 1
            
    #print("points:", points)
    return val, points, zero_points



#time, cycles, flops, mflops_s, mbytes_s, instructions, uops
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
    time, cycles, flops, mflops_s, databytes, mbytes_s, instructions, uops, stdout = decide_and_run(ssh, SuperTwin, bench)
    sampling_process.kill()
    wall = timer() - wall
    #print("Wall time:", wall, "Reported time:", time, "Ratio:", wall/time)
    ssh.close()

    #for line in stdout:
        #print(line)

            
    ##analyse here
    #unhalted_core, p, zp = get_sum("perfevent_hwcounters_UNHALTED_CORE_CYCLES_value")
    unhalted_ref, p, zp = get_sum("perfevent_hwcounters_UNHALTED_REFERENCE_CYCLES_value")
    inst_retired, p, zp = get_sum("perfevent_hwcounters_INSTRUCTION_RETIRED_value")
    fp_arith_scalar_d, p, zp = get_sum("perfevent_hwcounters_FP_ARITH_SCALAR_DOUBLE_value")
    uops_retired_any, p, zp = get_sum("perfevent_hwcounters_UOPS_RETIRED_ANY_value")
    mem_uops_all_loads, p, zp = get_sum("perfevent_hwcounters_MEM_UOPS_RETIRED_ALL_LOADS_value")
    mem_uops_all_stores, p, zp = get_sum("perfevent_hwcounters_MEM_UOPS_RETIRED_ALL_STORES_value")
    #return times

    #make these lines modular, and then, profit! While writing to csv, absent values are -1
    print("fp_arith_scalar:", fp_arith_scalar_d)
    print("####RATIOS####")
    print("Wall / Time:", (time/wall) )
    #print("Cycles / Unhalted Core:", ((unhalted_core/p)*time) / (cycles) )
    print("Cycles / Unhalted Ref:", ((unhalted_ref/p)*time) / (cycles) )
    print("Instructions / Inst_Retired:", ((inst_retired/p)*time) / (instructions) )
    print("Uops / uops_issued_any:", ((uops_retired_any/p)*time)/uops )
    print("No flops / fp_arith_scalar:", ((fp_arith_scalar_d/p)*time) / flops )
    print("Mflop/s / fp_arith_scalar/p:", (mflops_s/(fp_arith_scalar_d/((p)*1000000))))
    print("All mem:", ((((mem_uops_all_loads + mem_uops_all_stores)/p)*time)*8) / (databytes))
    print("AI:", (fp_arith_scalar_d/(mem_uops_all_loads + mem_uops_all_stores))/8)
    #print("p:", p, "zp:", zp)

    #print("No flops:", flops, "MFlop/s:", mflops_s, "Time:", time, "Mflops/s*time:", mflops_s*time*1000000, "this:", (fp_arith_scalar_d/p)*time, ((fp_arith_scalar_d/p)*time)/flops)

    
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
    benchs = ["triad", "sum", "stream", "peakflops", "ddot", "daxpy"]
    #benchs = ["triad"]    
    
    for bench in benchs:
        print("##################" + bench + "##################")
        #config = "-t 1 -c shortbench.conf :configured"
        config = "-t 1 -c dolap_shortbench_1.conf :configured"
        ##no_metrics, interval
        baseline = one_run(my_superTwin, bench)
        one_run_sampled(my_superTwin, bench, config, "dolap_run", "1", "1")
        print("##################" + bench + "##################")
                
