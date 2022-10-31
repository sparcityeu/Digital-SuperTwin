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
import adcarm_benchmark
import observation
#import roofline_dashboard

import static_data

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
##HPCG benchmark parameters

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
        "uid": supertwin.uid,
        "address": supertwin.addr,
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


def register_twin_state(SuperTwin):

    db = utils.get_mongo_database(SuperTwin.name, SuperTwin.mongodb_addr)["twin"]
    meta = loads(dumps(db.find({"_id": ObjectId(SuperTwin.mongodb_id)})))[0]

    
    meta["twin_state"] = {}
    meta["twin_state"]["SSHuser"] = SuperTwin.SSHuser
    meta["twin_state"]["SSHpass"] = utils.obscure(str.encode(SuperTwin.SSHpass))
    meta["twin_state"]["monitor_tag"] = SuperTwin.monitor_tag
    meta["twin_state"]["benchmarks"] = SuperTwin.benchmarks
    meta["twin_state"]["benchmark_results"] = SuperTwin.benchmark_results

    db.replace_one({"_id": ObjectId(SuperTwin.mongodb_id)}, meta)
    
    print("Twin state is registered to db..")


def query_twin_state(name, mongodb_id, mongodb_addr):

    db = utils.get_mongo_database(name, mongodb_addr)["twin"]
    meta = loads(dumps(db.find({"_id": ObjectId(mongodb_id)})))[0]
    print("Found db..")
    
    return meta

            
class SuperTwin:

    def __init__(self, *args):

        exist = False
        name = None
        twin_id = None
        collection_id =None
        
        if(len(args) > 0): ##Check if existed and wanted to be reconstructed from non-existed
            try:
                exist, name, twin_id, collection_id = utils.check_state(args[0])
            except:
                print("A SuperTwin instance is tried to be reconstructed from address", args[0])
                print("However, there is no such twin with that address..")
                exit(1)
        
        if(len(args) > 0 or exist): ##Reconstruct from db

            self.addr = args[0]
            self.name = name
            self.mongodb_id = collection_id
            self.mongodb_addr, self.influxdb_addr, self.grafana_addr, self.grafana_token = utils.read_env()
            self.monitor_metrics = utils.read_monitor_metrics()
            meta = query_twin_state(self.name, self.mongodb_id, self.mongodb_addr)
            #print("meta:", meta)
            self.SSHuser = meta["twin_state"]["SSHuser"]
            self.SSHpass = utils.unobscure(meta["twin_state"]["SSHpass"]).decode()
            self.monitor_tag = meta["twin_state"]["monitor_tag"]
            self.benchmarks = meta["twin_state"]["benchmarks"]
            self.benchmark_results = meta["twin_state"]["benchmark_results"]
            
            self.prob_file = meta["prob_file"]
            self.uid = meta["uid"]
            self.influxdb_name = meta["influxdb_name"]
            self.monitor_tag = meta["influxdb_tag"]
            self.monitor_pid = meta["monitor_pid"]
            self.roofline_dashboard = meta["roofline_dashboard"]
            self.monitoring_dashboard = meta["monitoring_dashboard"]

            print("SuperTwin is reconstructed from db..")

        else: ##Construct from scratch
            
            self.addr = input("Address of the remote system: ")
            self.uid = str(uuid.uuid4())
            print("Creating a new digital twin with id:", self.uid)
            
            self.name, self.prob_file, self.SSHuser, self.SSHpass = remote_probe.main(self.addr)
                        
            self.influxdb_name = self.name + "_main"
            self.mongodb_addr, self.influxdb_addr, self.grafana_addr, self.grafana_token = utils.read_env()
            utils.get_influx_database(self.influxdb_addr, self.influxdb_name)
            self.monitor_metrics = utils.read_monitor_metrics() ##These are the continuously sampled metrics
            self.monitor_tag = "_monitor"
            self.monitor_pid = sampling.main(self.name, self.addr, self.influxdb_name, self.monitor_tag, self.monitor_metrics)
            self.mongodb_id = insert_twin_description(get_twin_description(self.prob_file),self)
            
            print("Collection id:", self.mongodb_id)
            utils.update_state(self.name, self.addr, self.uid, self.mongodb_id)
            self.resurrect_and_clear_monitors() ##If there is any zombie monitor sampler
            
            ##benchmark members
            self.benchmarks = 0
            self.benchmark_results = 0
            self.add_stream_benchmark()
            self.add_hpcg_benchmark(HPCG_PARAM) ##One can change HPCG_PARAM and call this function repeatedly as wanted
            self.add_adcarm_benchmark()
            #self.generate_roofline_dashboard()
            
            register_twin_state(self)
            
            
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
                    _dict["@type"] = "benchmark_result"
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
        content["@global_parameters"] = hpcg_res["parameters"] 
        
        content["@mvres"] = hpcg_res["Max_Glob"] 
        content["@mvres_name"] = "Global Max"
        content["@mvres_unit"] = "GFlop/s"
        
        content["@contents"] = []
        
        for _field_key in hpcg_res:
            if(_field_key == "spmv" or _field_key == "ddot" or _field_key == "waxpby"):
                for _thread_key in hpcg_res[_field_key]: 
                    _dict = {}
                    _dict["@id"] = id_base + "benchmark_res:B" + str(benchmark_result_id) + ";1"
                    _dict["@type"] = "benchmark_result"
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

    
    def prepare_adcarm_content(self, adcarm_modifiers, adcarm_res):
        ##We are not probably using adcarm_modifiers here
        ##It only contains global environment variable changes in the system
        ##Since it is also exist in adcarm_res, in contrary to other benchmarks

        def max_threads():
            threads = adcarm_res["threads"].keys()
            threads = [int(x) for x in threads]
            max_thread = max(threads)
            return str(max_thread)

        def which():
            runs = adcarm_res["threads"][max_threads()]

            for i in range(len(runs)):
                if("binding" not in runs[i].keys()):
                    return i
        
        benchmark_id = str(self.benchmarks) ##These may get GLOBAL (including other systems) later
        benchmark_result_id = self.benchmark_results

        id_base = "dtmi:dt:" + self.name + ":"

        content = {}
        content["@id"] = id_base + "benchmark:B" + benchmark_id + ";1"
        content["@type"] = "benchmark"
        content["@date"] = datetime.datetime.now().strftime("%d-%m-%Y")
        content["@name"] = "CARM"
        
        if(adcarm_modifiers["environment"] != []):
            content["@environment"] = adcarm_modifiers["environment"]
            
        #content["@global_parameters"] = carm config values, L1size, L2size, Frequency?
        content["@mvres"] = adcarm_res["threads"][max_threads()][which()]["FP"]
        content["@mvres_name"] = "Max threads ridge point, without modifiers"
        content["@mvres_unit"] = "GFlop/s"

        content["@contents"] = []

        for _thread_key in adcarm_res["threads"]:
            for i in range(len(adcarm_res["threads"][_thread_key])):
                _run_dict = adcarm_res["threads"][_thread_key][i]
                _dict = {}
                _dict["@id"] = id_base + "benchmark_res:B" + str(benchmark_result_id) + ";1"
                _dict["@type"] = "benchmark_result"
                _dict["@threads"] = int(_thread_key)
                if("binding" in _run_dict.keys()):
                    _dict["@modifier"] = _run_dict["binding"]

                _dict["@local_parameters"] = []
                _dict["@local_parameters"].append({'inst': _run_dict["inst"]})
                _dict["@local_parameters"].append({'isa': _run_dict["isa"]})
                _dict["@local_parameters"].append({'precision': _run_dict["precision"]})
                _dict["@local_parameters"].append({'ld_st_ratio': int(_run_dict["ldstratio"])})
                _dict["@local_parameters"].append({'only_ld': bool(_run_dict["onlyld"])})
                _dict["@local_parameters"].append({'interleaved': bool(_run_dict["interleaved"])})
                _dict["@local_parameters"].append({'numops': int(_run_dict["numops"])})
                _dict["@local_parameters"].append({'dram_bytes': int(_run_dict["drambytes"])})
                
                _dict["@result"] = []
                _dict["@result"].append({"L1": _run_dict["L1"]})
                _dict["@result"].append({"L2": _run_dict["L2"]})
                _dict["@result"].append({"L3": _run_dict["L3"]})
                _dict["@result"].append({"DRAM": _run_dict["DRAM"]})
                _dict["@result"].append({"FP": _run_dict["FP"]})

                _dict["@unit"] = "GFLOPs/s"

                content["@contents"].append(_dict)
                benchmark_result_id += 1

            
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

    def update_twin_document__add_adcarm_benchmark(self, adcarm_modifiers, adcarm_res):
        ##Different from stream and hpcg benchmarks, adcarm have it's modifiers in result

        db = utils.get_mongo_database(self.name, self.mongodb_addr)["twin"]
        meta_with_twin = loads(dumps(db.find({"_id": ObjectId(self.mongodb_id)})))[0]
        new_twin = meta_with_twin["twin_description"]

                
        for key in new_twin:
            if(key.find("system") != -1): ##Get the system interface and add the benchmarks
                content = self.prepare_adcarm_content(adcarm_modifiers, adcarm_res)
                new_twin[key]["contents"].append(content)

        meta_with_twin["twin_description"] = new_twin
        db.replace_one({"_id": ObjectId(self.mongodb_id)}, meta_with_twin)
        print("CARM benchmark result added to Digital Twin")
        

    def add_adcarm_benchmark(self):
        adcarm_config = adcarm_benchmark.generate_adcarm_config(self)
        adcarm_modifiers = adcarm_benchmark.generate_adcarm_bench_sh(self, adcarm_config)
        #adcarm_benchmark.execute_adcarm_bench(self)
        adcarm_res = adcarm_benchmark.parse_adcarm_bench()
                        
        self.update_twin_document__add_adcarm_benchmark(adcarm_modifiers, adcarm_res)
        

    def update_twin_document__add_roofline_dashboard(self, url):

        db = utils.get_mongo_database(self.name, self.mongodb_addr)["twin"]
                
        to_new = loads(dumps(db.find({"_id": ObjectId(self.mongodb_id)})))[0]
        to_new["system_dashboard"] = "http://localhost:3000" + url
        db.replace_one({"_id": ObjectId(self.mongodb_id)}, to_new)
        print("Roofline dashboard added to Digital Twin")
        
        
    def generate_roofline_dashboard(self):
        url = roofline_dashboard.generate_roofline_dashboard(self)
        static_data.main(self)
        self.update_twin_document__add_roofline_dashboard(url)

    def generate_bench_info_dashboard(self):
        ##This will parse digital twin to get benchmark information
        x = 1

    def generate_monitor_dashboard(self):
        ##This will generate monitor dashboard panels.
        ##However monitor dashboard panels should be called by observation panels

        x = 1

    def reconfigure_perfevent(self):

        x = 1

    def execute_observation(self, command, metrics):
        observation_id = str(uuid.uuid4())
        
    def execute_observation_batch_element(self, command, observation_id, element_id):
        this_observation_id = observation_id + "_" + str(element_id)

    def execute_observation_batch(self, commands, metrics):
        
        observation_id = str(uuid.uuid4())
        #reconfigure_perfevent(metrics)
        
        
        
    def generate_observation_dashboard_type1(self): ##Applications runs on different threads at the same time
        x = 1

    def generate_observation_dashboard_type2(self): ##Applications runs at different times then overlapped
        x = 1


    
                

if __name__ == "__main__":

    #my_SuperTwin = SuperTwin()
    otherTwin = SuperTwin("10.36.54.195")
    mongodb_id = insert_twin_description(get_twin_description(otherTwin.prob_file),otherTwin)
    
    
