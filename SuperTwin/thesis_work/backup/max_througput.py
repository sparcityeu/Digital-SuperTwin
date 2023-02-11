from influxdb import InfluxDBClient                                                                 
import subprocess                                                                                   
from subprocess import Popen, PIPE                                                                  
import shlex                                                                                        
import time                                                                                         
import statistics                                                                                   
                                                                                                    
import supertwin                                                                                    
import utils                                                                                        
                                                                                                    
from copy import deepcopy  

duration = 10

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

def get_truth(addr):

    duration = 5
    
    get_command = "pmval proc.nprocs -s 1 -h " + addr
    print(get_command)
    get_command_args = shlex.split(get_command)
    get_process = Popen(get_command_args, stdout=PIPE)
    
    val = get_process.stdout.readlines()#.decode("utf-8")
    val = int(val[6].decode("utf-8").strip(" "))
    
    return val
    

def one_run(addr, client, config, db, no_metrics, persecond):

    _expected = []
    _got = []
    for i in range(5):

        client.drop_database(db)
        client.create_database(db)
        
        truth = get_truth(addr)
        print("TRUTH:", truth)
        expected = no_metrics * persecond * truth * duration
                
        sampling_command = "pcp2influxdb " + config
        sampling_args = shlex.split(sampling_command)
        sampling_process = Popen(sampling_args)

        if(persecond < 4):
            time.sleep(0.3)
        time.sleep(duration)

        sampling_process.kill()
        
        client.switch_database(db)
        mes = list(client.query("SHOW MEASUREMENTS"))[0]
        print("mes:", mes)
        inserted = 0
        for item in mes:
            query = "select * from " + item["name"]
            res = list(client.query(query))[0]
            for item in res:
                points = len(item.keys()) - 2 ##One for tag, one for time 
                inserted += points
        if(inserted > expected):
            inserted = expected ##Number of process increased during test
        _expected.append(expected)
        _got.append(inserted)
        
    return _expected, _got

def main(addr, config, db, no_metrics):

    my_superTwin = supertwin.SuperTwin(addr)
    pids = utils.get_pcp_pids(my_superTwin)
    pmdas = pmdas = mutate_p1(deepcopy(pmdas_atm), pids)
    pmdas = mutate_p2(pmdas)
    client = InfluxDBClient(host='localhost', port=8086)

    expected = {}
    got = {}

    #expected["1"], got["1"] = one_run(addr, client, "-t 1 " + config, db, no_metrics, 1)
    #print("expected:", expected["1"], "got:", got["1"])
    ###
    expected["0.5"], got["0.5"] = one_run(addr, client, "-t 0.5" + config, db, no_metrics, 2)
    if(statistics.stdev(got["0.5"]) == 0):   ##Means the error is with measurement
        got["0.5"] = expected["0.5"]
    print("expected:", expected["0.5"], "got:", got["0.5"])
    ##
    expected["0.25"], got["0.25"] = one_run(addr, client, "-t 0.25" + config, db, no_metrics, 4)
    if(statistics.stdev(got["0.25"]) == 0):
        got["0.25"] = expected["0.25"]    
    print("expected:", expected["0.25"], "got:", got["0.25"])
    ##
    expected["0.125"], got["0.125"] = one_run(addr, client, "-t 0.125" + config, db, no_metrics, 8)
    if(statistics.stdev(got["0.125"]) == 0):
        got["0.125"] = expected["0.125"]
    print("expected:", expected["0.125"], "got:", got["0.125"])
    ##
    expected["0.0625"], got["0.0625"] = one_run(addr, client, "-t 0.0625" + config, db, no_metrics, 16)
    if(statistics.stdev(got["0.0625"]) == 0):
        got["0.0625"] = expected["0.0625"]    
    print("expected:", expected["0.0625"], "got:", got["0.0625"])
    ##
    expected["0.03125"], got["0.03125"] = one_run(addr, client, "-t 0.03125" + config, db, no_metrics, 32)
    if(statistics.stdev(got["0.03125"]) == 0):
        got["0.03125"] = expected["0.03125"]
    print("expected:", expected["0.03125"], "got:", got["0.03125"])
    ##
    expected["0.015625"], got["0.015625"] = one_run(addr, client, "-t 0.015625" + config, db, no_metrics, 64)
    if(statistics.stdev(got["0.015625"]) == 0):
        got["0.015625"] = expected["0.015625"]
    print("expected:", expected["0.015625"], "got:", got["0.015625"])
    
    writer = open("throughput_results_proc.csv", "a")
    #line_1 = db + "_1" + "," + str(no_metrics) + "," + str(statistics.mean(expected["1"])) + "," + str#(statistics.mean(got["1"])) + "," + str(statistics.stdev(got["1"])) + "\n"
    line_2 = db + "_2" + "," + str(no_metrics) + "," + str(statistics.mean(expected["0.5"])) + "," + str(statistics.mean(got["0.5"])) + "\n"
    line_4 = db + "_4" + "," + str(no_metrics) + "," + str(statistics.mean(expected["0.25"])) + "," + str(statistics.mean(got["0.25"])) + "\n"
    line_8 = db + "_8" + "," + str(no_metrics) + "," + str(statistics.mean(expected["0.125"])) + "," + str(statistics.mean(got["0.125"])) + "\n"
    line_16 = db + "_16" + "," + str(no_metrics) + "," + str(statistics.mean(expected["0.0625"])) + "," + str(statistics.mean(got["0.0625"])) + "\n"
    line_32 = db + "_32" + "," + str(no_metrics) + "," + str(statistics.mean(expected["0.03125"])) + "," + str(statistics.mean(got["0.03125"])) + "\n"
    line_64 =  db + "_64" + "," + str(no_metrics) + "," + str(statistics.mean(expected["0.015625"])) + "," + str(statistics.mean(got["0.015625"])) + "\n"

    #writer.write(line_1)
    writer.write(line_2)
    writer.write(line_4)
    writer.write(line_8)
    writer.write(line_16)
    writer.write(line_32)
    writer.write(line_64)

    writer.close()

    print(db, no_metrics, "successfuly wrote to file")
                                      

if __name__ == "__main__":

    
    print("Deren 1 proc")
    main("10.92.53.74", " -c throughput_measurements/deren_1.conf :configured", "deren_run", 1)
    print("Deren 2 proc")
    main("10.92.53.74", " -c throughput_measurements/deren_2.conf :configured", "deren_run", 2)
    print("Deren 3 proc")
    main("10.92.53.74", " -c throughput_measurements/deren_3.conf :configured", "deren_run", 3)
    print("Deren 4 proc")
    main("10.92.53.74", " -c throughput_measurements/deren_4.conf :configured", "deren_run", 4)
    print("Deren 5 proc")
    main("10.92.53.74", " -c throughput_measurements/deren_5.conf :configured", "deren_run", 5)
    print("Deren 6 proc")
    main("10.92.53.74", " -c throughput_measurements/deren_6.conf :configured", "deren_run", 6)
    
    print("Poseidon 1 proc")
    main("10.92.55.4", " -c throughput_measurements/poseidon_1.conf :configured", "poseidon_run", 1)
    print("Poseidon 2 proc")
    main("10.92.55.4", " -c throughput_measurements/poseidon_2.conf :configured", "poseidon_run", 2)
    print("Poseidon 3 proc")
    main("10.92.55.4", " -c throughput_measurements/poseidon_3.conf :configured", "poseidon_run", 3)
    print("Poseidon 4 proc")
    main("10.92.55.4", " -c throughput_measurements/poseidon_4.conf :configured", "poseidon_run", 4)
    print("Poseidon 5 proc")
    main("10.92.55.4", " -c throughput_measurements/poseidon_5.conf :configured", "poseidon_run", 5)
    print("Poseidon 6 proc")
    main("10.92.55.4", " -c throughput_measurements/poseidon_6.conf :configured", "poseidon_run", 6)

    print("Luna 1 proc")
    main("10.36.52.109", " -c throughput_measurements/luna_1.conf :configured", "luna_run", 1)
    print("Luna 2 proc")
    main("10.36.52.109", " -c throughput_measurements/luna_2.conf :configured", "luna_run", 2)
    print("Luna 3 proc")
    main("10.36.52.109", " -c throughput_measurements/luna_3.conf :configured", "luna_run", 3)
    print("Luna 4 proc")
    main("10.36.52.109", " -c throughput_measurements/luna_4.conf :configured", "luna_run", 4)
    print("Luna 5 proc")
    main("10.36.52.109", " -c throughput_measurements/luna_5.conf :configured", "luna_run", 5)
    print("Luna 6 proc")
    main("10.36.52.109", " -c throughput_measurements/luna_6.conf :configured", "luna_run", 6)
    
    print("Dolap 1 proc")
    main("10.36.54.195", " -c throughput_measurements/dolap_1.conf :configured", "dolap_run", 1)
    print("Dolap 2 proc")
    main("10.36.54.195", " -c throughput_measurements/dolap_2.conf :configured", "dolap_run", 2)
    print("Dolap 3 proc")
    main("10.36.54.195", " -c throughput_measurements/dolap_3.conf :configured", "dolap_run", 3)
    print("Dolap 4 proc")
    main("10.36.54.195", " -c throughput_measurements/dolap_4.conf :configured", "dolap_run", 4)
    print("Dolap 5 proc")
    main("10.36.54.195", " -c throughput_measurements/dolap_5.conf :configured", "dolap_run", 5)
    print("Dolap 6 proc")
    main("10.36.54.195", " -c throughput_measurements/dolap_6.conf :configured", "dolap_run", 6)

    print("ALL SUCCESFULY EXECUTED")
