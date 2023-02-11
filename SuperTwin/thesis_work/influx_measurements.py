from influxdb import InfluxDBClient
from subprocess import Popen, PIPE
import shlex
import time
import statistics

#pcp2influxdb -t 0.1 -J 1 -c pcp_dolap_overhead_checker.conf :configured
#conf_file = ""
#sampling_command = "pcp2influxdb -t 1 -c " + conf_file + " :configured"

def quick_insert(client, sampler_config):

    sampling_command = "pcp2influxdb -t " + "0.1" + sampler_config
    sampling_args = shlex.split(sampling_command)
    sampling_process = Popen(sampling_args)
    
    time.sleep(3)
    
    sampling_process.kill()
    
    
def one_run(client, interval, metric, field, sampler_config, duration):

    gots = []
    runs = []
    
    for i in range(2):
        ##try except: insert some datapoints if no response
        query_string = 'SELECT ' + '"' + field + '"' +' from ' + metric
        print("query_string:", query_string)
        before = []
        try:
            before = list(client.query(query_string))[0]
        except:
            quick_insert(client, sampler_config)
            before = list(client.query(query_string))[0]
        #print("before:", before)    
        before = len(before)
            
        #sampling_command = "pcp2influxdb -t " + interval + " -c pcp_dolap_overhead_checker.conf :configured"
        print("Interval:", interval)
        sampling_command = "pcp2influxdb -t " + interval + sampler_config
        sampling_args = shlex.split(sampling_command)
        sampling_process = Popen(sampling_args)
        
        time.sleep(duration)
        
        sampling_process.kill()
        
        after = list(client.query(query_string))[0]
        after = len(after)
        
        expected = (1 / float(interval)) * duration
        got = after - before
        #print("interval:", interval, "expected:", expected, "got:", got, "ratio:", got/expected)
        gots.append(got/duration) ##Datapoints inserted per second
        runs.append(got/expected)

    return runs, gots
    
if __name__ == "__main__":

    client = InfluxDBClient(host='localhost', port=8086)
    client.switch_database("dolap2")
    #res = client.query("SELECT SUM(mem_use) FROM (SELECT *,mem_use::INTEGER FROM mem_use GROUP BY count FILL(1))")
    #print("res:", res)
    #res = client.query("SELECT * from mem_use")
    #print("res:", len(list(res)[0]))
    #l_res = list(res)[0]

    sampler_config = " -c pcp_dolap_monitor.conf :configured"
    metric = "hinv_cpu_clock"
    field = "_cpu0"

    duration = 10
    
    #sampler_config = " -c pcp_dolap_overhead_checker.conf :configured"
    #metric = "proc_psinfo_age"
    #field = "_750317__usr_lib_pcp_bin_pmcd"

    _runs = {}
    _gots = {}
    
    #_runs["1"], _gots["1"] = one_run(client, "1", metric, field, sampler_config, duration)
    #_runs["0.5"], _gots["0.5"] = one_run(client, "0.5", metric, field, sampler_config, duration)
    #_runs["0.25"], _gots["0.25"] = one_run(client, "0.25", metric, field, sampler_config, duration)
    _runs["0.125"], _gots["0.125"] = one_run(client, "0.125" , metric, field, sampler_config, duration)
    print("runs:", _runs, "gots:", _gots)
    _runs["0.0625"], _gots["0.0625"] = one_run(client, "0.0625" , metric, field, sampler_config, duration)
    _runs["0.03125"], _gots["0.03125"] = one_run(client, "0.03125" , metric, field, sampler_config, duration)
        
    _runs["0.1"], _gots["0.1"] = one_run(client, "0.1" , metric, field, sampler_config, duration)
    _runs["0.01"], _gots["0.01"] = one_run(client, "0.01", metric, field, sampler_config, duration)
    _runs["0.001"], _gots["0.001"] = one_run(client, "0.001" , metric, field, sampler_config, duration)
    _runs["0.0001"], _gots["0.0001"] = one_run(client, "0.0001" , metric, field, sampler_config, duration)

    writer = open("dolap_first.txt", "w+")
    for key in _runs:
        got = _runs[key]
        writer.write("#############################" + "\n")
        writer.write("interval:" + str(key) + "\n")
        writer.write("mean:" + str(statistics.mean(got)) + "\n")
        writer.write("min:" +  str(min(got)) + "\n")
        writer.write("max:" + str(max(got)) + "\n")
        writer.write("std:" + str(statistics.stdev(got)) + "\n")
        writer.write("data point per second:" + str(statistics.mean(_gots[key])) + "\n")
        writer.write("#############################" + "\n")
        
    
    for key in _runs:
        got = _runs[key]
        print("#############################")
        print("interval:", key)
        print("mean:", statistics.mean(got))
        print("min:", min(got))
        print("max:", max(got))
        print("std:", statistics.stdev(got))
        print("data point per second", statistics.mean(_gots[key]))
        print("#############################")

    
        
        
