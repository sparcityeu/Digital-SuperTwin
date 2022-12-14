from influxdb import InfluxDBClient
import subprocess
from subprocess import Popen, PIPE
import shlex
import time
import statistics

import supertwin
import utils

def mutate_p2(pmdas):

    for key in pmdas:
        pmdas[key] = pmdas[key].replace(" ", "_")
        pmdas[key] = pmdas[key].replace("/", "_")
        pmdas[key] = "_" + pmdas[key]
    return pmdas

def mutate_p1(pmdas, pids):

    for key in pmdas:
        pmdas[key] = pmdas[key].replace("XXXXXX", pids[key])
        
    return pmdas
    
    
    
##pmdas atm
pmdas_atm = {'pmproxy': "XXXXXX /usr/lib/pcp/bin/pmproxy",
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
    for i in range(3):
        ##try except: insert some datapoints if no response
        print("Interval:", interval)
        sampling_command = "pcp2influxdb -t " + interval + sampler_config
        sampling_args = shlex.split(sampling_command)
        sampling_process = Popen(sampling_args)
        
        time.sleep(duration)
        
        sampling_process.kill()
        
        query_string = 'SELECT ' + '"' + field + '"' +' from ' + metric
        print("query_string:", query_string)
        response = list(client.query(query_string))[0]

        _sum = 0
        for item in response:
            _sum += item[field]
        _sum /= len(response)
        runs.append(_sum)
        print("Mean CPU usage of pmdaproc:", _sum) 
        
    
    return runs

def one_run_two_returns(client, interval, metric1, metric2, fields, sampler_config, duration, name):

    client.drop_database(name + "_run")   ##Reset database
    client.create_database(name + "_run")
    client.switch_database(name + "_run")

    cpu_overheads = {}
    mem_overheads = {}
    cpu_responses = {}
    mem_responses = {}
    
    for key in fields:
        cpu_overheads[key] = []
        mem_overheads[key] = []
        cpu_responses[key] = []
        mem_responses[key] = []
            
    for i in range(3):
        ##try except: insert some datapoints if no response
        print("Interval:", interval)
        sampling_command = "pcp2influxdb -t " + interval + sampler_config
        sampling_args = shlex.split(sampling_command)
        sampling_process = Popen(sampling_args)
        
        time.sleep(duration)
        
        sampling_process.kill()

                        
        for key in fields:
            cpu_query = 'SELECT ' + '"' + fields[key] + '"' +' from ' + metric1
            mem_query = 'SELECT ' + '"' + fields[key] + '"' +' from ' + metric2
            #print("cpu_query:", cpu_query)
            #print("mem_query:", mem_query)
            #print("key:", key)
            #print("q:", client.query(cpu_query))
            #print("w:", client.query(mem_query))
            cpu_responses[key] = list(client.query(cpu_query))[0]
            mem_responses[key] = list(client.query(mem_query))[0]
            
                
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
        
            #print("Mean CPU usage of",field, _sum1)
            #print("Mean MEMORY usage of",field, _sum2) 
            
    return cpu_overheads, mem_overheads
    
def bw():
    print("wtf")
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
            print("val:", float(val[0]))
    netwatch_process.kill()
        
    exit(1)

def main(addr, config, name, run_name, alias):
    print("wtf1")
    bw()
    print("wtf2")
    my_superTwin = supertwin.SuperTwin(addr)
    pids = utils.get_pcp_pids(my_superTwin)
    
    pmdas = mutate_p1(pmdas_atm, pids)
    pmdas = mutate_p2(pmdas)
    
    
    client = InfluxDBClient(host='localhost', port=8086)
        
    sampler_config = config
    metric1 = "cpu_use"
    metric2 = "mem_use"
    fields = pmdas

    duration = 5
    
    _runs = {}
    _gots = {}

    
    #_runs["1"], _gots["1"] = one_run_two_returns(client, "1", metric1, metric2, fields, sampler_config, duration, name)
    #_runs["0.5"], _gots["0.5"] = one_run_two_returns(client, "0.5", metric1, metric2, fields, sampler_config, duration, name)
    #_runs["0.25"], _gots["0.25"] = one_run_two_returns(client, "0.25", metric1, metric2, fields, sampler_config, duration, name)
    #_runs["0.125"], _gots["0.125"] = one_run_two_returns(client, "0.125" , metric1, metric2, fields, sampler_config, duration, name)
    #_runs["0.0625"], _gots["0.0625"] = one_run_two_returns(client, "0.0625" , metric1, metric2, fields, sampler_config, duration, name)
    _runs["0.03125"], _gots["0.03125"] = one_run_two_returns(client, "0.03125" , metric1, metric2, fields, sampler_config, duration, name)
            

    writer = open("dolap_results" + ".csv", "a")
    for key in _runs:
        cpuo = _runs[key]
        memo = _gots[key]
        #print("cpuo:", cpuo, "memo:", memo, "key:", key)
        for comp in cpuo:
            print("interval:", key, "comp:", comp, "")
            interval = key
            comp = comp
            cpu_use_mean = str(statistics.mean(cpuo[comp]))
            cpu_use_min = str(min(cpuo[comp]))
            cpu_use_max = str(max(cpuo[comp]))
            cpu_use_std = str(statistics.stdev(cpuo[comp]))

            mem_use_mean = str(statistics.mean(memo[comp]))
            mem_use_min = str(min(memo[comp]))
            mem_use_max = str(max(memo[comp]))
            mem_use_std = str(statistics.stdev(cpuo[comp]))
            print("cpu_use_mean:", cpu_use_mean)
            line = alias + "," + interval + "," + comp + "," + cpu_use_mean + "," + cpu_use_min + "," + cpu_use_max + "," + cpu_use_std + "," + mem_use_mean + "," + mem_use_min + "," + mem_use_max + "," + mem_use_std + "\n"
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

    
    #main("10.36.54.195", " -c overhead_configs/dolap_10.conf :configured", "dolap", "try0", "dolap10")
    #main("10.36.54.195", " -c overhead_configs/dolap_20.conf :configured", "dolap", "try0", "dolap20")
    main("10.36.54.195", " -c overhead_configs/dolap_30.conf :configured", "dolap", "try0", "dolap30")
    main("10.36.54.195", " -c overhead_configs/dolap_40.conf :configured", "dolap", "try0", "dolap40")
    main("10.36.54.195", " -c overhead_configs/dolap_50.conf :configured", "dolap", "try0", "dolap50")
    main("10.36.54.195", " -c overhead_configs/dolap_100.conf :configured", "dolap", "try0", "dolap100")
    
