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
                "perfevent_hwcounters_UOPS_RETIRED_SLOTS_value",
                "perfevent_hwcounters_MEM_INST_RETIRED_ALL_LOADS_value",
                "perfevent_hwcounters_MEM_INST_RETIRED_ALL_STORES_value"]


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

    stdin, stdout, stderr = ssh.exec_command("likwid-bench -t triad -w S0:100kB:1 -s 20")
    stdout = stdout.readlines()

    cycles, time, flops, mflops_s, databytes, mbytes_s, instructions, uops = parse_likwid_bench(stdout)
    
    return time, cycles, flops, mflops_s, databytes, mbytes_s, instructions, uops, stdout
####    

####    
def perform_sum(ssh, SuperTwin):

    stdin, stdout, stderr = ssh.exec_command("likwid-bench -t sum -w S0:100kB:1 -s 20")
    stdout = stdout.readlines()

    cycles, time, flops, mflops_s, databytes, mbytes_s, instructions, uops = parse_likwid_bench(stdout)
    
    return time, cycles, flops, mflops_s, databytes, mbytes_s, instructions, uops, stdout
    
####    

####    
def perform_stream(ssh, SuperTwin):

    stdin, stdout, stderr = ssh.exec_command("likwid-bench -t stream -w S0:100kB:1 -s 20")
    stdout = stdout.readlines()

    cycles, time, flops, mflops_s, databytes, mbytes_s, instructions, uops = parse_likwid_bench(stdout)
    
    return time, cycles, flops, mflops_s, databytes, mbytes_s, instructions, uops, stdout
    
####    

####    
def perform_peakflops(ssh, SuperTwin):

    stdin, stdout, stderr = ssh.exec_command("likwid-bench -t peakflops -w S0:100kB:1 -s 20")
    stdout = stdout.readlines()

    cycles, time, flops, mflops_s, databytes, mbytes_s, instructions, uops = parse_likwid_bench(stdout)
    
    return time, cycles, flops, mflops_s, databytes, mbytes_s, instructions, uops, stdout
    
####    

####    
def perform_ddot(ssh, SuperTwin):

    stdin, stdout, stderr = ssh.exec_command("likwid-bench -t ddot -w S0:100kB:1 -s 20")
    stdout = stdout.readlines()

    cycles, time, flops, mflops_s, databytes, mbytes_s, instructions, uops = parse_likwid_bench(stdout)
    
    return time, cycles, flops, mflops_s, databytes, mbytes_s, instructions, uops, stdout
    
####    

####    
def perform_daxpy(ssh, SuperTwin):

    stdin, stdout, stderr = ssh.exec_command("likwid-bench -t daxpy -w S0:100kB:1 -s 20")
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

    client.switch_database("poseidon_run")
    query = "select _cpu0 from " + metric
    print("query:", query)
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

########
def write_accuracy_to_file(db, bench, metric, no_metrics, frequency, accuracy):

    print("no_metrics:", no_metrics)
    print("")
    line = db + "," + bench + "," + metric + "," + str(no_metrics) + "," + str(frequency) + "," + str(accuracy) + "," + "1" + "\n"
    
    writer = open("poseidon_cstress_accuracy.csv", "a")
    writer.write(line)
    writer.close()
    print("Wrote line - ", line)
########

########
def write_overhead_to_file(db, bench, no_metrics, frequency, overhead):

    line = db + "," + bench + "," + str(no_metrics) + "," + str(frequency) + "," + str(overhead) + "," + "1" + "\n"

    writer = open("poseidon_cstress_overhead.csv", "a")
    writer.write(line)
    writer.close()
    print("Wrote line - ", line)
#######

#time, cycles, flops, mflops_s, mbytes_s, instructions, uops
def one_run_sampled(SuperTwin, bench, config, db, baseline, no_metrics, frequency):

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SuperTwin.addr, username=SuperTwin.SSHuser, password=SuperTwin.SSHpass)

    fp_arith_inst_list = [-1] * repeat
    unhalted_ref_list = [-1] * repeat
    inst_retired_list = [-1] * repeat
    fp_arith_scalar_d_list = [-1] * repeat
    uops_retired_any_list  = [-1] * repeat
    unhalted_refs = [-1] * repeat
    unhalted_refs = [-1] * repeat

    l1_bw_list = [-1] * repeat
    ai_list = [-1] * repeat
    ai_err_list = [-1] * repeat
    overhead_list = []
    
    for i in range(repeat):
        
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
        
        unhalted_ref = -1
        inst_retired = -1
        fp_arith_scalar_d = -1
        uops_retired_any = -1
        mem_uops_all_loads = -1
        mem_uops_all_stores = -1
        ai = -1
        ai_err = -1

        client.switch_database(db)
        involved_dlist = list(client.query("SHOW MEASUREMENTS"))[0]
        involved = []

        for item in involved_dlist:
            involved.append(item['name'])
    
        if("perfevent_hwcounters_UNHALTED_REFERENCE_CYCLES_value" in involved):
            unhalted_ref, p, zp = get_sum("perfevent_hwcounters_UNHALTED_REFERENCE_CYCLES_value")
        if("perfevent_hwcounters_INSTRUCTION_RETIRED_value" in involved):
            inst_retired, p, zp = get_sum("perfevent_hwcounters_INSTRUCTION_RETIRED_value")
        if("perfevent_hwcounters_UOPS_EXECUTED_CORE_value" in involved):
            uops_retired_any, p, zp = get_sum("perfevent_hwcounters_UOPS_EXECUTED_CORE_value")
        if("perfevent_hwcounters_MEM_INST_RETIRED_ALL_LOADS_value" in involved):
            mem_uops_all_loads, p, zp = get_sum("perfevent_hwcounters_MEM_INST_RETIRED_ALL_LOADS_value")
        if("perfevent_hwcounters_MEM_INST_RETIRED_ALL_STORES_value" in involved):
            mem_uops_all_stores, p, zp = get_sum("perfevent_hwcounters_MEM_INST_RETIRED_ALL_STORES_value")

        fp_arith_scalar_d, p, zp = get_sum("perfevent_hwcounters_FP_ARITH_SCALAR_DOUBLE_value") ##This is always on
        fp_arith_scalar_err = (((fp_arith_scalar_d/p)*time) - flops) / flops
        fp_arith_inst_list[i] = fp_arith_scalar_err

        if(unhalted_ref != -1):
            unhalted_ref_err = (((unhalted_ref/p)*time) - cycles)/ cycles
            unhalted_ref_list[i] = unhalted_ref_err
        if(inst_retired != -1):
            inst_retired_err = (((inst_retired/p)*time) - instructions) / instructions
            inst_retired_list[i] = inst_retired_err
        if(uops_retired_any != -1):
            uops_retired_any_err = (((uops_retired_any/p)*time) - uops) / uops
            uops_retired_any_list[i] = uops_retired_any_err
        if(mem_uops_all_loads != -1 and mem_uops_all_stores != -1):
            l1_bw_err = (((((mem_uops_all_loads + mem_uops_all_stores)/p)*time)*8) - databytes) / databytes
            ai_itself = ((fp_arith_scalar_d/(mem_uops_all_loads + mem_uops_all_stores))/8)
            ai_err = (((fp_arith_scalar_d/(mem_uops_all_loads + mem_uops_all_stores))/8)) - AIs[bench] / AIs[bench]
            ##
            l1_bw_list[i] = l1_bw_err
            ai_list[i] = ai_itself
        ##append to own list
        ##if not -1 write line
        ##for AI, if all 3 is here
    
        #make these lines modular, and then, profit! While writing to csv, absent values are -1
        print("fp_arith_scalar:", fp_arith_scalar_d)
        print("####RATIOS####")
        print("Wall / Time:", (time/wall) )
        #print("Cycles / Unhalted Core:", ((unhalted_core/p)*time) / (cycles) )
        print("Cycles / Unhalted Ref:", ((unhalted_ref/p)*time) / (cycles) )
        print("Instructions / Inst_Retired:", ((inst_retired/p)*time) / (instructions) )
        print("Uops / uops_retired_any:", ((uops_retired_any/p)*time)/uops )
        print("No flops / fp_arith_scalar:", ((fp_arith_scalar_d/p)*time) / flops )
        print("Mflop/s / fp_arith_scalar/p:", (mflops_s/(fp_arith_scalar_d/((p)*1000000))))
        print("All mem:", ((((mem_uops_all_loads + mem_uops_all_stores)/p)*time)*8) / (databytes))
        print("AI:", (fp_arith_scalar_d/(mem_uops_all_loads + mem_uops_all_stores))/8)

        print("fp?:", fp_arith_inst_list)
        print(unhalted_ref_list)
        print(inst_retired_list)
        print(uops_retired_any_list)
        print(l1_bw_list)
        print(ai_list)
        print(ai_err)

        print("overhead:", time/baseline)
        overhead_list.append(time/baseline)
        
    
    ssh.close()

    write_accuracy_to_file(db, bench, "fp_arith_scalar_double_err", no_metrics, frequency, statistics.mean(fp_arith_inst_list))
    if(-1 not in unhalted_ref_list):
        write_accuracy_to_file(db, bench, "unhalted_reference_cycles_err", no_metrics, frequency, statistics.mean(unhalted_ref_list))
    if(-1 not in inst_retired_list):
        write_accuracy_to_file(db, bench, "instruction_retired_err", no_metrics, frequency, statistics.mean(inst_retired_list))
    if(-1 not in uops_retired_any_list):
        write_accuracy_to_file(db, bench, "uops_retired_any_err", no_metrics, frequency, statistics.mean(uops_retired_any_list))
    if(-1 not in l1_bw_list):
        write_accuracy_to_file(db, bench, "l1_bw", no_metrics, frequency, statistics.mean(l1_bw_list))
    if(-1 not in ai_list):
        write_accuracy_to_file(db, bench, "ai", no_metrics, frequency, statistics.mean(ai_list))
    if(ai_err != -1):
        write_accuracy_to_file(db, bench, "ai_err", no_metrics, frequency, ai_err)
        
    #def write_overhead_to_file(db, bench, no_metrics, frequency, overhead):
    write_overhead_to_file(db, bench, no_metrics, frequency, statistics.mean(overhead_list))
        

def write_to_file(times, bench, interval, no_metrics):

    print("Writing file:", "--", times, "--", bench, "--", interval, "--", no_metrics)
    
    time_mean = statistics.mean(times)
    time_std = statistics.stdev(times)
    
    writer = open("poseidon_cstress.csv", "a")
    line = "poseidon," + str(interval) + "," + str(no_metrics) + "," + bench + "," + str(time_mean) + "," + str(time_std) + "," + "1" + "\n"
    writer.write(line)
    writer.close()






if __name__ == "__main__":
    
    my_superTwin = supertwin.SuperTwin("10.92.55.4")
    name = my_superTwin.name
    benchs = ["triad", "sum", "stream", "peakflops", "ddot", "daxpy"]

    #sizes = [1,4,8,12,16,20,24]
    sizes = [8,12,16,24]

    my_superTwin.reconfigure_observation_events_parameterized("twentyfour_perfevent.txt")
    
    for size in sizes:
        for bench in benchs:
            print("##################" + bench + "##################")
            baseline = one_run(my_superTwin, bench)[0] ##time
            
            mtr = size
            str_mtr = str(mtr)
            
            config = "-t 1 -c cstress_configs/" + name + "_" + str_mtr + ".conf :configured"
            one_run_sampled(my_superTwin, bench, config, "poseidon_run", baseline, mtr, 1)
            print("##################" + bench + "##################")
            
            config = "-t 0.5 -c cstress_configs/" + name + "_" + str_mtr + ".conf :configured"
            one_run_sampled(my_superTwin, bench, config, "poseidon_run", baseline, mtr, 2)
            print("##################" + bench + "##################")
            
            config = "-t 0.25 -c cstress_configs/" + name + "_" + str_mtr + ".conf :configured"
            one_run_sampled(my_superTwin, bench, config, "poseidon_run", baseline, mtr, 4)
            print("##################" + bench + "##################")
            
            config = "-t 0.125 -c cstress_configs/" + name + "_" + str_mtr + ".conf :configured"
            one_run_sampled(my_superTwin, bench, config, "poseidon_run", baseline, mtr, 8)
            print("##################" + bench + "##################")
            
            config = "-t 0.0625 -c cstress_configs/" + name + "_" + str_mtr + ".conf :configured"
            one_run_sampled(my_superTwin, bench, config, "poseidon_run", baseline, mtr, 16)
            print("##################" + bench + "##################")
        
            '''
            config = "-t 0.03125 -c cstress_configs/poseidon_" + str_mtr + ".conf :configured"
            one_run_sampled(my_superTwin, bench, config, "poseidon_run", baseline, mtr, 32)
            print("##################" + bench + "##################")
            
            config = "-t 0.015625 -c cstress_configs/poseidon_" + str_mtr + ".conf :configured"
            one_run_sampled(my_superTwin, bench, config, "poseidon_run", baseline, mtr, 64)
            print("##################" + bench + "##################")
            
            config = "-t 0.0078125 -c cstress_configs/poseidon_" + str_mtr + ".conf :configured"
            one_run_sampled(my_superTwin, bench, config, "poseidon_run", baseline, mtr, 128)
            print("##################" + bench + "##################")
            
            config = "-t 0.00390625 -c cstress_configs/poseidon_" + str_mtr + ".conf :configured"
            one_run_sampled(my_superTwin, bench, config, "poseidon_run", baseline, mtr, 256)
            print("##################" + bench + "##################")
            '''
                

                

