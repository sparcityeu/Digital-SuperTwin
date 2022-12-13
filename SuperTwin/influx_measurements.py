from influxdb import InfluxDBClient
from subprocess import Popen, PIPE
import shlex

#pcp2influxdb -t 0.1 -J 1 -c pcp_dolap_overhead_checker.conf :configured
#conf_file = ""
#sampling_command = "pcp2influxdb -t 1 -c " + conf_file + " :configured"

def one_run(client, interval, metric):

    ##try except: insert some datapoints if no response
    before = list(client.query('SELECT "_cpu0" from ' + metric))[0]
    before = len(before)
    
    #sampling_command = "pcp2influxdb -t " + interval + " -c pcp_dolap_overhead_checker.conf :configured"
    sampling_command = "pcp2influxdb -t " + interval + " -c pcp_dolap_overhead_checker.conf :configured"
    sampling_args = shlex.split(sampling_command)
    sampling_process = Popen(sampling_args)
    
    wait_command = "sleep 10"
    wait_args = shlex.split(wait_command)
    wait_process = Popen(wait_args)
    wait_process.wait()
    
    sampling_process.kill()

    after = list(client.query('SELECT "_cpu0" from ' + metric))[0]
    after = len(after)

    expected = (1 / float(interval)) * 10
    got = after - before
    print("interval:", interval, "expected:", expected, "got:", got, "ratio:", got/expected)

if __name__ == "__main__":

    client = InfluxDBClient(host='localhost', port=8086)
    client.switch_database("dolap2")
    #res = client.query("SELECT SUM(mem_use) FROM (SELECT *,mem_use::INTEGER FROM mem_use GROUP BY count FILL(1))")
    #print("res:", res)
    #res = client.query("SELECT * from mem_use")
    #print("res:", len(list(res)[0]))
    #l_res = list(res)[0]

    one_run(client, "1")
    one_run(client, "0.5")
    one_run(client, "0.25")
    one_run(client, "0.125")
    one_run(client, "0.1")
    one_run(client, "0.0625")
    one_run(client, "0.01")
    one_run(client, "0.0025")
    one_run(client, "0.001")
    one_run(client, "0.0001")
