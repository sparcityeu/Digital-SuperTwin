import sys
sys.path.append("probing")
sys.path.append("probing/benchmarks")
sys.path.append("observation")
sys.path.append("twin_description")
sys.path.append("sampling")
sys.path.append("dashboards")

import utils
import remote_probe
import detect_utils
import generate_dt
import sampling
import stream_benchmark
import hpcg_benchmark
import roofline_dashboard

import uuid

#from influxdb import InfluxDBClient
#import pymongo
#from pymongo import MongoClient

from bson.objectid import ObjectId
from bson.json_util import dumps
from bson.json_util import loads

import datetime
import json

##HPCG benchmark parameters are set to be separate from classes, so hpcg is repeatable and easily mutable
HPCG_PARAM = {}
HPCG_PARAM["nx"] = 104
HPCG_PARAM["ny"] = 104
HPCG_PARAM["nz"] = 104
HPCG_PARAM["time"] = 60

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
        "roofline_dashboard": "to be added",
        "monitoring_dashboard": "to be added"}

    result = collection.insert_one(metadata)
    twin_id = str(result.inserted_id)

    return twin_id

            
class SuperTwin:

    def __init__(self):
        #self.addr = input("Address of the remote system: ")
        self.addr = "10.36.54.195"
        exist, twin_id, collection_id = utils.check_state(self.addr)
        if(not exist or exist):
        
            self._id = str(uuid.uuid4())
            print("Creating a new digital twin with id:", self._id)
        
            #self.name, self.prob_file, self.SSHuser, self.SSHpass = remote_probe.main(self.addr)
            
            ##Debug
            self.name = "dolap"
            self.prob_file = "probing_dolap.json"
            self.SSHuser = "ftasyaran"
            self.SSHpass = "kemaliye"
            ##Debug
        
            self.influxdb_name = self.name + "_main"
            self.mongodb_addr, self.influxdb_addr, self.grafana_addr, self.grafana_token = utils.read_env()
            utils.get_influx_database(self.influxdb_addr, self.influxdb_name)
            self.monitor_metrics = utils.read_monitor_metrics() ##These are the continuously sampled metrics
            self.monitor_tag = "_monitor"
            self.monitor_pid = sampling.main(self.name, self.addr, self.influxdb_name, self.monitor_tag, self.monitor_metrics)
            self.mongodb_id = insert_twin_description(get_twin_description(self.prob_file),
                                                            self)
        
            print("Collection id:", self.mongodb_id)
            utils.update_state(self.addr, self._id, self.mongodb_id)
            self.resurrect_and_clear_monitors() ##If there is any zombie monitor sampler
            
            ##benchmark members
            self.benchmarks = 0
            self.benchmark_results = 0
            self.add_stream_benchmark()
            self.add_hpcg_benchmark(HPCG_PARAM) ##One can change HPCG_PARAM and call this function repeatedly as wanted
            self.generate_roofline_dashboard()

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
                fields = [x for x in fields if x != ""]
                pid = None
                state = None
                conf_file = None
                try:
                    pid = int(fields[1])
                    state = fields[7]
                    conf_file = fields[15]
                except:
                    continue
                                    
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


    def prepare_stream_content(self, stream_modifiers, stream_res):

        benchmark_id = str(self.benchmarks)
        benchmark_result_id = self.benchmark_results ##Note that benchmark_id is str but this one is int, since we will keep incrementing this one

        id_base = "dtmi:dt:" + self.name + ":"
        
        content = {}
        content["@id"] = id_base + "benchmark:B" + benchmark_id + ";1"
        content["@type"] = "benchmark"
        content["@date"] = datetime.datetime.now().strftime("%d-%m-%Y")
        content["@name"] = "STREAM"
        content["@environment"] = stream_modifiers['environment']
        
        content["@mvres"] = stream_res["Max_Glob"]
        content["@mvres_name"] = "Global Max"
        content["@mvres_unit"] = "MB/s"
        
        content["@contents"] = []
        
        for _field_key in stream_res:
            try: ##Field key is a thread
                for _thread_key in stream_res[_field_key]: 
                    _dict = {}
                    _dict["@id"] = id_base + "benchmark_res:B" + str(benchmark_result_id) + ";1"
                    _dict["@type"] = "benchmark result"
                    _dict["@field"] = _field_key
                    _dict["@threads"] = int(_thread_key)
                    _dict["@modifier"] = stream_modifiers[_thread_key]
                    _dict["@result"] = stream_res[_field_key][_thread_key]
                    _dict["@unit"] = "MB/s" #We know that beforehand

                    content["@contents"].append(_dict)
                    benchmark_result_id += 1
            except: ##Field key is a global or local max
                continue

        self.benchmarks += 1
        self.benchmark_results = benchmark_result_id

        return content

    
    def prepare_hpcg_content(self, hpcg_modifiers, hpcg_res):

        benchmark_id = str(self.benchmarks)
        benchmark_result_id = self.benchmark_results ##Note that benchmark_id is str but this one is int, since we will keep incrementing this one

        id_base = "dtmi:dt:" + self.name + ":"
        
        content = {}
        content["@id"] = id_base + "benchmark:B" + benchmark_id + ";1"
        content["@type"] = "benchmark"
        content["@date"] = datetime.datetime.now().strftime("%d-%m-%Y")
        content["@name"] = "HPCG"
        content["@environment"] = hpcg_modifiers['environment']
        content["@parameters"] = hpcg_res["parameters"] 
        
        content["@mvres"] = hpcg_res["Max_Glob"] 
        content["@mvres_name"] = "Global Max"
        content["@mvres_unit"] = "GFlop/s"
        
        content["@contents"] = []
        
        for _field_key in hpcg_res:
            if(_field_key == "spmv" or _field_key == "ddot" or _field_key == "waxpby"):
                for _thread_key in hpcg_res[_field_key]: 
                    _dict = {}
                    _dict["@id"] = id_base + "benchmark_res:B" + str(benchmark_result_id) + ";1"
                    _dict["@type"] = "benchmark result"
                    _dict["@field"] = _field_key
                    _dict["@threads"] = int(_thread_key)
                    _dict["@modifier"] = hpcg_modifiers[_thread_key]
                    _dict["@result"] = hpcg_res[_field_key][_thread_key]
                    _dict["@unit"] = "GFlop/s" #We know that beforehand

                    content["@contents"].append(_dict)
                    benchmark_result_id += 1
            else: ##Field key is a global or local max or parameter
                continue

        self.benchmarks += 1
        self.benchmark_results = benchmark_result_id

        return content

        
        
    def update_twin_document__add_stream_benchmark(self, stream_modifiers, stream_res):

        db = utils.get_mongo_database(self.name, self.mongodb_addr)["twin"]
        meta_with_twin = loads(dumps(db.find({"_id": ObjectId(self.mongodb_id)})))[0]
        new_twin = meta_with_twin["twin_description"]

        for key in new_twin:
            if(key.find("system") != -1): ##Get the system interface and add the benchmarks
                content = self.prepare_stream_content(stream_modifiers, stream_res)
                new_twin[key]["contents"].append(content)

        meta_with_twin["twin_description"] = new_twin
        db.replace_one({"_id": ObjectId(self.mongodb_id)}, meta_with_twin)
        print("STREAM benchmark result added to Digital Twin")
        
        
    def add_stream_benchmark(self):
        
        stream_modifiers = stream_benchmark.generate_stream_bench_sh(self)
        #stream_benchmark.execute_stream_bench(self)
        stream_res = stream_benchmark.parse_stream_bench(self)

        ##debug##
        #with open("stream_modifiers.json", "w") as outfile:
            #json.dump(modifiers, outfile)

        #with open("stream_res.json", "w") as outfile:
            #json.dump(stream_res, outfile)

        #with open("stream_modifiers.json", "r") as j:
            #stream_modifiers = json.loads(j.read())

        #with open("stream_res.json", "r") as j:
            #stream_res = json.loads(j.read())

        #print("modifiers:", stream_modifiers)
        #print("stream_res", stream_res)
        ##debug##

        self.update_twin_document__add_stream_benchmark(stream_modifiers, stream_res)
        

    def update_twin_document__add_hpcg_benchmark(self, hpcg_modifiers, hpcg_res):

        db = utils.get_mongo_database(self.name, self.mongodb_addr)["twin"]
        meta_with_twin = loads(dumps(db.find({"_id": ObjectId(self.mongodb_id)})))[0]
        new_twin = meta_with_twin["twin_description"]

        for key in new_twin:
            if(key.find("system") != -1): ##Get the system interface and add the benchmarks
                content = self.prepare_hpcg_content(hpcg_modifiers, hpcg_res)
                new_twin[key]["contents"].append(content)

        meta_with_twin["twin_description"] = new_twin
        db.replace_one({"_id": ObjectId(self.mongodb_id)}, meta_with_twin)
        print("HPCG benchmark result added to Digital Twin")


    def add_hpcg_benchmark(self, HPCG_PARAM):

        hpcg_modifiers = hpcg_benchmark.generate_hpcg_bench_sh(self, HPCG_PARAM)
        #hpcg_benchmark.execute_hpcg_bench(self)
        hpcg_res = hpcg_benchmark.parse_hpcg_bench(self)

        self.update_twin_document__add_hpcg_benchmark(hpcg_modifiers, hpcg_res)

    def update_twin_document__add_roofline_dashboard(self, url):
        x = 1
        print("URL:", url)
        print("Roofline dashboard added..")
        
    def generate_roofline_dashboard(self):
        url = roofline_dashboard.generate_roofline_dashboard(self)
        self.update_twin_document__add_roofline_dashboard(url)

        
    def generate_observation_dashboard_type1(self): ##Applications runs on different threads at the same time
        x = 1

        
    def generate_observation_dashboard_type2(self): ##Applications runs at different times then overlapped
        x = 1

        
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
