from influxdb import InfluxDBClient
import subprocess
from subprocess import Popen, PIPE
import shlex
import time
import statistics

import supertwin
import utils

from copy import deepcopy

def mutate_p2(pmdas):
    #print("pmdas:", pmdas)
    for key in pmdas:
        pmdas[key] = pmdas[key].replace(" ", "_")
        pmdas[key] = pmdas[key].replace("/", "_")
        pmdas[key] = "_" + pmdas[key]
    return pmdas

def mutate_p1(pmdas, pids):
    #print("pmdas:", pmdas, "pids:", pids)
    for key in pmdas:
        pmdas[key] = pmdas[key].replace("XXXXXX", pids[key])
        
    return pmdas
    
    
    
##pmdas atm
pmdas_atm = {#'pmproxy': "XXXXXX /usr/lib/pcp/bin/pmproxy",
             'pmie': "XXXXXX /usr/bin/pmie",
             'pmcd': "XXXXXX /usr/lib/pcp/bin/pmcd",
             'pmdaproc': "XXXXXX /var/lib/pcp/pmdas/proc/pmdaproc",
             'pmdalinux': "XXXXXX /var/lib/pcp/pmdas/linux/pmdalinux",
             'pmdaperfevent': "XXXXXX /var/lib/pcp/pmdas/perfevent/pmdaperfevent"
}

def quick_insert(client, sampler_config):

    sampling_command = "pcp2influxdb -t " + "0.1" + sampler_config
    sampling_args = shlex.split(sampling_command)
    sampling_process = Popen(sampling_args)
    
    time.sleep(3)
    
    sampling_process.kill()
    
    
def one_run(client, interval, metric, field, sampler_config, duration):

    runs = []    
    for i in range(5):
        ##try except: insert some datapoints if no response
        print("Interval:", interval)
        sampling_command = "pcp2influxdb -t " + interval + sampler_config
        sampling_args = shlex.split(sampling_command)
        sampling_process = Popen(sampling_args)
        
        time.sleep(duration)
        
        sampling_process.kill()
        
        query_string = 'SELECT ' + '"' + field + '"' +' from ' + metric
        #print("query_string:", query_string)
        response = list(client.query(query_string))[0]

        _sum = 0
        for item in response:
            _sum += item[field]
        _sum /= len(response)
        runs.append(_sum)
        print("Mean CPU usage of pmdaproc:", _sum) 
        
    
    return runs

def sample(interval, sampler_config, duration):
    print("trying once more")

    print("Interval:", interval)
    sampling_command = "pcp2influxdb -t " + interval + sampler_config
    sampling_args = shlex.split(sampling_command)
    sampling_process = Popen(sampling_args)
    
    time.sleep(duration)

    
def one_run_two_returns(client, interval, metric1, metric2, fields, sampler_config, duration, name):
    
    client.drop_database(name + "_run")   ##Reset database
    client.create_database(name + "_run")
    client.switch_database(name + "_run")

    cpu_overheads = {}
    mem_overheads = {}
    cpu_responses = {}
    mem_responses = {}
    io_overheads = {}
    io_responses = {}
    net_traffic = {}
    
    for key in fields:
        cpu_overheads[key] = []
        mem_overheads[key] = []
        cpu_responses[key] = []
        mem_responses[key] = []
        io_overheads[key] = []
        io_responses[key] = []
    net_traffic["all"] = []
            
    for i in range(5):
        ##try except: insert some datapoints if no response
        print("Interval:", interval)
        sampling_command = "pcp2influxdb -t " + interval + sampler_config
        sampling_args = shlex.split(sampling_command)
        sampling_process = Popen(sampling_args)
        
        time.sleep(duration)

        '''
        netwatch_command = "ifstat -i enp4s0"
        netwatch_args = shlex.split(netwatch_command)
        netwatch_process = Popen(netwatch_args,stdin=PIPE, stdout=PIPE)
        t_end = time.time() + duration
        while time.time() < t_end:
            val = netwatch_process.stdout.readline().decode("utf-8")
            if(val.find("KB") == -1 and val.find("enp") == -1):
                val = val.split(" ")
                val = [x for x in val if x != ""]
                net_traffic[key].append(float(val[0]))
            
        netwatch_process.kill()
        '''
        sampling_process.kill()

                        
        for key in fields:
            cpu_query = 'SELECT ' + '"' + fields[key] + '"' +' from ' + metric1
            mem_query = 'SELECT ' + '"' + fields[key] + '"' +' from ' + metric2
            io_query = 'SELECT ' + '"' + fields[key] + '"' +' from ' + "proc_io_total_bytes"
            #print("cpu_query:", cpu_query)
            #print("mem_query:", mem_query)
            #print("io_query:", io_query)
            #print("key:", key)
            #print("q:", client.query(cpu_query))
            #print("w:", client.query(mem_query))
            try:
                cpu_responses[key] = list(client.query(cpu_query))[0]
                mem_responses[key] = list(client.query(mem_query))[0]
                io_responses[key] = list(client.query(io_query))[0]
            except:
                sample(interval, sampler_config, duration)
                cpu_responses[key] = list(client.query(cpu_query))[0]
                mem_responses[key] = list(client.query(mem_query))[0]
                io_responses[key] = list(client.query(io_query))[0]

                
                
        ##This or that
        net_query = 'SELECT * from network_out'
        net_response = list(client.query(net_query))[0]
        #print("net_response:", net_response)
        _sum0 = 0
        for item in net_response:
            _sum0 += item["value"]
        _sum0 /= len(net_response)
        net_traffic["all"].append(_sum0)

        
        for key in fields:
            _sum1 = 0
            for item in cpu_responses[key]:
                #print("item:", item)
                #print("fields[key]:", fields[key])
                _sum1 += item[fields[key]]
            _sum1 /= len(cpu_responses[key])
            cpu_overheads[key].append(_sum1)

            _sum2 = 0
            for item in mem_responses[key]:
                #print("item:", item)
                #print("fields[key]:", fields[key])
                _sum2 += item[fields[key]]
            _sum2 /= len(mem_responses[key])
            mem_overheads[key].append(_sum2)

            _sum3 = 0
            for item in mem_responses[key]:
                #print("item:", item)
                #print("fields[key]:", fields[key])
                _sum3 += item[fields[key]]
            _sum3 /= len(io_responses[key])
            _sum3 /= 1024 ##convert to kbs as others
            io_overheads[key].append(_sum3)
        
            #print("Mean CPU usage of",field, _sum1)
            #print("Mean MEMORY usage of",field, _sum2) 
            
    return cpu_overheads, mem_overheads, io_overheads, net_traffic
    
def bw():

    netwatch_command = "ifstat -i enp4s0"
    netwatch_args = shlex.split(netwatch_command)
    netwatch_process = Popen(netwatch_args,stdin=PIPE, stdout=PIPE)
    t_end = time.time() + 5
    while time.time() < t_end:
        #output = netwatch_process.communicate()[0]
        val = netwatch_process.stdout.readline().decode("utf-8")
        if(val.find("KB") == -1 and val.find("enp") == -1):
            val = val.split(" ")
            val = [x for x in val if x != ""]
            #print("val:", float(val[0]))
    netwatch_process.kill()
        
    exit(1)

def reassign_pids(SuperTwin):
    
    pids = utils.get_pcp_pids(SuperTwin)
    pmdas = mutate_p1(deepcopy(pmdas_atm), pids)
    pmdas = mutate_p2(pmdas)

    return pmdas
    
def main(addr, config, name, run_name, alias):
    
    my_superTwin = supertwin.SuperTwin(addr)
    pids = utils.get_pcp_pids(my_superTwin)
    
    pmdas = mutate_p1(deepcopy(pmdas_atm), pids)
    pmdas = mutate_p2(pmdas)
    
    client = InfluxDBClient(host='localhost', port=8086)

    
    sampler_config = config
    metric1 = "cpu_use"
    metric2 = "mem_use"
    fields = pmdas

    duration = 20
    
    _runs = {}
    _gots = {}
    _ios = {}
    _nets = {}

    
    #my_superTwin.reconfigure_observation_events_parameterized("poseidon10_perfevent.txt")
    
    fields = reassign_pids(my_superTwin)
    _runs["1"], _gots["1"], _ios["1"], _nets["1"] = one_run_two_returns(client, "1", metric1, metric2, fields, sampler_config, duration, name)
    #my_superTwin.reconfigure_observation_events_parameterized("dolap10_perfevent.txt")
    fields = reassign_pids(my_superTwin)
    _runs["0.5"], _gots["0.5"], _ios["0.5"], _nets["0.5"] = one_run_two_returns(client, "0.5", metric1, metric2, fields, sampler_config, duration, name)
    #my_superTwin.reconfigure_observation_events_parameterized("dolap10_perfevent.txt")
    fields = reassign_pids(my_superTwin)
    _runs["0.25"], _gots["0.25"], _ios["0.25"], _nets["0.25"] = one_run_two_returns(client, "0.25", metric1, metric2, fields, sampler_config, duration, name)
    #my_superTwin.reconfigure_observation_events_parameterized("dolap10_perfevent.txt")
    fields = reassign_pids(my_superTwin)
    _runs["0.125"], _gots["0.125"], _ios["0.125"], _nets["0.125"] = one_run_two_returns(client, "0.125" , metric1, metric2, fields, sampler_config, duration, name)
    #my_superTwin.reconfigure_observation_events_parameterized("dolap10_perfevent.txt")
    fields = reassign_pids(my_superTwin)
    _runs["0.0625"], _gots["0.0625"], _ios["0.0625"], _nets["0.0625"] = one_run_two_returns(client, "0.0625" , metric1, metric2, fields, sampler_config, duration, name)
    #my_superTwin.reconfigure_observation_events_parameterized("dolap10_perfevent.txt")

    fields = reassign_pids(my_superTwin)
    _runs["0.03125"], _gots["0.03125"], _ios["0.03125"], _nets["0.03125"] = one_run_two_returns(client, "0.03125" , metric1, metric2, fields, sampler_config, duration, name)


    ##datapoints
    client.switch_database("poseidon_run") ##PROBLEM
    mes = list(client.query("SHOW MEASUREMENTS"))[0]
    total_datapoints = 0
    print("mes:", mes)
    for item in mes:
        datapoints = len(list(client.query("SELECT last(*) FROM " + item["name"]))[0][0].keys())
        print(item["name"], ":", datapoints)
        total_datapoints += datapoints
    ##
    total_datapoints = str(total_datapoints)
    print("Total datapoints:", total_datapoints)
    

    writer = open("poseidon_results" + ".csv", "a")
    for key in _runs:
        cpuo = _runs[key]
        memo = _gots[key]
        neto = _nets[key]
        io = _ios[key]
        interval = key
        #print("cpuo:", cpuo, "memo:", memo, "key:", key)
        for comp in cpuo:
            #print("interval:", key, "comp:", comp, "")            
            comp = comp
            cpu_use_mean = str(statistics.mean(cpuo[comp]))
            cpu_use_min = str(min(cpuo[comp]))
            cpu_use_max = str(max(cpuo[comp]))
            cpu_use_std = str(statistics.stdev(cpuo[comp]))

            mem_use_mean = str(statistics.mean(memo[comp]))
            mem_use_min = str(min(memo[comp]))
            mem_use_max = str(max(memo[comp]))
            mem_use_std = str(statistics.stdev(cpuo[comp]))

            io_use_mean = str(statistics.mean(io[comp]))
            io_use_min = str(min(io[comp]))
            io_use_max = str(max(io[comp]))
            io_use_std = str(statistics.stdev(io[comp]))
            
            line = alias + "," + interval + "," + comp + "," + cpu_use_mean + "," + cpu_use_min + "," + cpu_use_max + "," + cpu_use_std + "," + mem_use_mean + "," + mem_use_min + "," + mem_use_max + "," + mem_use_std + "," + io_use_mean + "," + io_use_min + "," + io_use_max + "," + io_use_std + "," + "-1" + "," + "-1" + "," + "-1" + "," + "-1" + "," + "-1"+"\n" 
            writer.write(line)

        net_use_mean = str(statistics.mean(neto["all"]))
        net_use_min = str(min(neto["all"]))
        net_use_max = str(max(neto["all"]))
        net_use_std = str(statistics.stdev(neto["all"]))

        line = alias + "," + interval + "," + "network" + "," + "-1" + "," + "-1" + "," + "-1" + "," + "-1" + "," + "-1" + "," + "-1" + "," + "-1" + "," + "-1" + "," + "-1" + "," + "-1" + "," + "-1" + "," + "-1" + "," + net_use_mean + "," + net_use_min + "," + net_use_max + "," + net_use_std + "," + "-1" +"\n"
        writer.write(line)

        line = alias + "," + interval + "," + "datapoints" + "," + "-1" + "," + "-1" + "," + "-1" + "," + "-1" + "," + "-1" + "," + "-1" + "," + "-1" + "," + "-1" + "," + "-1" + "," + "-1" + "," + "-1" + "," + "-1" + "," + "-1" + "," + "-1" + "," + "-1" + "," + "-1" + "," + total_datapoints +"\n"
        writer.write(line)
    
    writer.close()
    print("Succesfully wrote", alias, "results")
    '''
    for key in _runs:
        run = _runs[key]
        print("#############################")
        print("interval:", key)
        print("mean:", statistics.mean(run))
        print("min:", min(run))
        print("max:", max(run))
        print("std:", statistics.stdev(run))
        print("memory", statistics.mean(_gots[key]))
        print("#############################")
    '''
    
        
if __name__ == "__main__":
    
    print("With 10 metrics")
    main("10.92.55.4", " -c new_overhead_configs/poseidon_10.conf :configured", "poseidon", "try0", "poseidon10")
    print("With 20 metrics")
    main("10.92.55.4", " -c new_overhead_configs/poseidon_20.conf :configured", "poseidon", "try0", "poseidon20")
    print("With 30 metrics")
    main("10.92.55.4", " -c new_overhead_configs/poseidon_30.conf :configured", "poseidon", "try0", "poseidon30")
    print("With 40 metrics")
    main("10.92.55.4", " -c new_overhead_configs/poseidon_40.conf :configured", "poseidon", "try0", "poseidon40")
    print("With 50 metrics")
    main("10.92.55.4", " -c new_overhead_configs/poseidon_50.conf :configured", "poseidon", "try0", "poseidon50")
    print("#########################################################################################")
    print("SUCCESFULLY FINISHED!")
    print("#########################################################################################")
    
