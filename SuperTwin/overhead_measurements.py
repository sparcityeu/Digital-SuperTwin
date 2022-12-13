from influxdb import InfluxDBClient
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

def one_run_two_returns(client, interval, metric1, metric2, fields, sampler_config, duration):

    client.drop_database("dolap_run")   ##Reset database
    client.create_database("dolap_run")
    client.switch_database("dolap_run")

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
            print("cpu_query:", cpu_query)
            print("mem_query:", mem_query)
            cpu_responses[key] = list(client.query(cpu_query))[0]
            mem_responses[key] = list(client.query(mem_query))[0]

        for key in fields:
            _sum1 = 0
            for item in cpu_responses[key]:
                print("item:", item)
                print("fields[key]:", fields[key])
                _sum1 += item[fields[key]]
            _sum1 /= len(cpu_responses[key])
            cpu_overheads[key].append(_sum1)

            _sum2 = 0
            for item in mem_responses[key]:
                print("item:", item)
                print("fields[key]:", fields[key])
                _sum2 += item[fields[key]]
            _sum2 /= len(mem_responses[key])
            mem_overheads[key].append(_sum2)
        
            #print("Mean CPU usage of",field, _sum1)
            #print("Mean MEMORY usage of",field, _sum2) 
            
    return cpu_overheads, mem_overheads
    
if __name__ == "__main__":

    my_superTwin = supertwin.SuperTwin("10.36.54.195")
    pids = utils.get_pcp_pids(my_superTwin)
    
    pmdas = mutate_p1(pmdas_atm, pids)
    pmdas = mutate_p2(pmdas)
    
    
    client = InfluxDBClient(host='localhost', port=8086)
    
    sampler_config = " -c overhead_configs/dolap_10.conf :configured"
    metric1 = "cpu_use"
    metric2 = "mem_use"
    fields = pmdas

    duration = 10
    
    #sampler_config = " -c pcp_dolap_overhead_checker.conf :configured"
    #metric = "proc_psinfo_age"
    #field = "_750317__usr_lib_pcp_bin_pmcd"

    _runs = {}
    _gots = {}

    
    _runs["1"], _gots["1"] = one_run_two_returns(client, "1", metric1, metric2, fields, sampler_config, duration)
    _runs["0.5"], _gots["0.5"] = one_run_two_returns(client, "0.5", metric1, metric2, fields, sampler_config, duration)
    _runs["0.25"], _gots["0.25"] = one_run_two_returns(client, "0.25", metric1, metric2, fields, sampler_config, duration)
    _runs["0.125"], _gots["0.125"] = one_run_two_returns(client, "0.125" , metric1, metric2, fields, sampler_config, duration)
    _runs["0.0625"], _gots["0.0625"] = one_run_two_returns(client, "0.0625" , metric1, metric2, fields, sampler_config, duration)
    _runs["0.03125"], _gots["0.03125"] = one_run_two_returns(client, "0.03125" , metric1, metric2, fields, sampler_config, duration)
            

    writer = open("dolap_first.txt", "w+")
    for key in _runs:
        run = _runs[key]
        writer.write("#############################" + "\n")
        writer.write("interval:" + str(key) + "\n")
        writer.write("mean:" + str(statistics.mean(run)) + "\n")
        writer.write("min:" +  str(min(run)) + "\n")
        writer.write("max:" + str(max(run)) + "\n")
        writer.write("std:" + str(statistics.stdev(run)) + "\n")
        writer.write("memory:" + str(statistics.mean(_gots[key])) + "\n")
        writer.write("#############################" + "\n")
        
    
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

    
        
        
