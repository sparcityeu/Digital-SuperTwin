import sys
sys.path.append("probing")
sys.path.append("probing/benchmarks")
sys.path.append("observation")
sys.path.append("twin_description")
sys.path.append("sampling")

import utils
import remote_probe
import detect_utils
import generate_dt
import sampling
import stream_benchmark
import uuid

#from influxdb import InfluxDBClient
#import pymongo
#from pymongo import MongoClient

from bson.objectid import ObjectId
from bson.json_util import dumps
from bson.json_util import loads

import datetime
import json


def get_twin_description(hostProbFile):

    with open(hostProbFile, "r") as j:
        _sys_dict = json.loads(j.read())

    _twin = generate_dt.main(_sys_dict)
    return _twin


def insert_twin_description(_twin, supertwin):

    date = datetime.datetime.now()
    date = date.strftime("%d-%m-%Y")

    hostname = supertwin.name
    CONNECTION_STRING = supertwin.mongodb_addr
    
    mongodb = utils.get_mongo_database(hostname, CONNECTION_STRING)
    collection = mongodb["twin"]
    
    metadata = {
        "id": supertwin._id,
        "hostname": supertwin.name,
        "date": date,
        "twin_description": _twin,
        "influxdb_name": supertwin.influxdb_name,
        "influxdb_tag": supertwin.monitor_tag,
        "monitor_pid": supertwin.monitor_pid,
        "prob_file": supertwin.prob_file,
        "system_dashboard": "to be added",
        "monitoring_dashboard": "to be added"}

    result = collection.insert_one(metadata)
    twin_id = str(result.inserted_id)

    return twin_id

            
class SuperTwin:

    def __init__(self):
        self.addr = input("Address of the remote system: ")
        exist, twin_id, collection_id = utils.check_state(self.addr)
        if(not exist or exist):
        
            self._id = str(uuid.uuid4())
            print("Creating a new digital twin with id:", self._id)
        
            #self.name, self.prob_file = remote_probe.main(self.addr)
            
            ##Debug
            self.name = "dolap"
            self.prob_file = "probing_dolap.json"
            ##Debug
        
            self.influxdb_name = self.name + "_main"
            self.mongodb_addr, self.influxdb_addr, self.grafana_addr, self.grafana_token = utils.read_env()
            utils.get_influx_database(self.influxdb_addr, self.influxdb_name)
            self.monitor_metrics = utils.read_monitor_metrics() ##These are the continuously sampled metrics
            self.monitor_tag = "_monitor"
            self.monitor_pid = sampling.main(self.name, self.addr, self.influxdb_name, self.monitor_tag, self.monitor_metrics)
            #self.benchmarks = perform_benchmarks()
            self.mongodb_id = insert_twin_description(get_twin_description(self.prob_file),
                                                            self)
        
            print("Collection id:", self.mongodb_id)
            utils.update_state(self.addr, self._id, self.mongodb_id)
            self.resurrect_and_clear_monitors() ##If there is any zombie monitor sampler
            self.add_stream_benchmark()

        else:

            print("A digital twin with")
            print("--twin_id:", twin_id)
            print("--collection_id:", collection_id)
            print("--monitor_pid:", monitor_pid)
            print("Is already exists")

            
    def resurrect_and_clear_monitors(self):

        out = detect_utils.output_lines("ps aux | grep pcp2influxdb")

        for line in out: ##Accesses are emprical
            if(line.find("/usr/bin/pcp2influxdb") != -1):
                fields = line.split(" ")
                pid = -1
                state = None
                conf_file = None
                try:
                    pid = int(fields[5])
                    state = fields[17]
                    conf_file = int(fields[30])
                except:
                    pid = int(fields[5])
                    
                #print("pid:", pid, "state:", state, "conf_file:", conf_file)
                if(pid != self.monitor_pid):
                    print("Killing zombie monitoring sampler with pid:", pid)
                    detect_utils.cmd("sudo kill " + str(pid))



    def update_twin_document__new_monitor_pid(self):
        
        db = utils.get_mongo_database(self.name, self.mongodb_addr)["twin"]
        print("Killing existed monitor sampler with pid:", self.monitor_pid)
        detect_utils.cmd("sudo kill " + str(self.monitor_pid))
        new_pid = sampling.main(self.name, self.addr, self.influxdb_name, self.monitor_tag, self.monitor_metrics)
        print("New sampler pid: ", new_pid)
        to_new = loads(dumps(db.find({"_id": ObjectId(self.mongodb_id)})))[0]
        #print(to_new)
        to_new["monitor_pid"] = new_pid        
        db.replace_one({"_id": ObjectId(self.mongodb_id)}, to_new)
        self.monitor_pid = new_pid


    def add_stream_benchmark(self):

        stream_benchmark.generate_stream_bench_sh(self)

        
    def generate_system_dashboard(self):
        x = 1
        
    def generate_observation_dashboard_type1(self):
        x = 1
        
    #def generate_observation_dashboard_type2():
    #def generate_inescid_dashboard_type1():
    #def generate_inescid_dashboard_type2():

    def reconfigure_perf(self):
        x = 1
        
    def update_state(self): ##Add yourself to the state file
        x = 1
        
    def read_monitor_metrics(self):
        x = 1
        
    def observation(self):
        x = 1
                

if __name__ == "__main__":

    myTwin = SuperTwin()
    #myTwin.update_twin_document__new_monitor_pid()





















