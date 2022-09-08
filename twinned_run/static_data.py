from flask import Flask, request, jsonify, json, abort
from flask_cors import CORS, cross_origin

import pandas as pd

import pprint

import pymongo
from pymongo import MongoClient

from bson.objectid import ObjectId

app = Flask(__name__)

cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

methods = ('GET', 'POST')


dummy_time = 1450754160000 ##Dummy time works, but for a better solution, "time_from" and "time_to" from incoming query could be used


data = {}


@app.route('/', methods=methods)
@cross_origin()
def hello_world():
    return 'OK'

@app.route('/search', methods=methods)
@cross_origin()
def find_metrics():
    #print('/search:', request.headers, request.get_json())
    return jsonify(list(data))
    


@app.route('/query', methods=methods)
@cross_origin(max_age=600)
def query_metrics():
    print(request.headers, request.get_json())
    req = request.get_json()
    print("############")
    print("Request Targets:", req["targets"])
    print("############")
    pprint.pprint(req["targets"][0]["target"])

    target = req["targets"][0]["target"]
    print("TARGET:", target, "DATA:", data[target])
    answer = [{"target": target, "datapoints": [[data[target], dummy_time]]}]
    
    
    return jsonify(answer)





def fill_data(data, hostname, hostip):

    system_hostname = hostname
    system_ip = hostip
    system_os = ""
    system_no_numa_nodes = 0
    system_no_disks = 0

    cpu_model = ""
    cpu_cores = 0
    cpu_threads = 0
    cpu_hyperthreading = ""
    cpu_maxmhz = 0
    cpu_minmhx = 0
    
    
    l1dcache_size = 0
    l1dcache_associativity = 0
    l1dcache_linesize = 0
    l1dcache_nosets = 0

    l2cache_size = 0 ##MegaBytes
    l2cache_associativity = 0 
    l2cache_linesize = 0 ##Bytes
    l2cache_nosets = 0

    l3cache_size = 0
    l3cache_associativity = 0
    l3cache_linesize = 0
    l3cache_nosets = 0

    cpu = True
    l1d_cache = True
    l2_cache = True
    l3_cache = True
    
    #Get all data in one loop, using 'cases'
    for key in data:
        print("key:", key)

        ##SYSTEM
        if(key.find("system") != -1):
            subdata = data[key]["contents"]
            #print("subdata:", subdata)

            for content in subdata:
                if(content["@id"].find("os") != -1):
                    system_os = content["description"]

        ##CPU
        if(key.find("socket") != -1 and cpu):
            subdata = data[key]["contents"]

            for content in subdata:
                if(content["name"] == "model"):
                    cpu_model = content["description"]
                if(content["name"] == "cores"):
                    cpu_cores = int(content["description"])
                if(content["name"] == "threads"):
                    cpu_threads = int(content["description"])
                if(content["name"] == "hyperthreading"):
                    cpu_hyperthreading = content["description"]
                if(content["name"] == "max_mhz"):
                    cpu_maxmhz = float(content["description"])
                if(content["name"] == "min_mhz"):
                    cpu_minmhz = float(content["description"])
                
            cpu = False


        #l1dcache
        if(key.find("L1D") != -1 and l1d_cache):
            subdata = data[key]["contents"]

            for content in subdata:
                if(content["name"] == "associativity"):
                    l1dcache_associativity = content["description"]
                if(content["name"] == "size"):
                    l1dcache_size = content["description"]
                if(content["name"] == "no_sets"):
                    l1dcache_nosets = content["description"]
                if(content["name"] == "cache_line_size"):
                    l1dcache_linesize = content["description"]

            l1d_cache = False


        #l2cache
        if(key.find("L2") != -1 and l2_cache):
            subdata = data[key]["contents"]

            for content in subdata:
                if(content["name"] == "associativity"):
                    l2cache_associativity = content["description"]
                if(content["name"] == "size"):
                    l2cache_size = content["description"]
                if(content["name"] == "no_sets"):
                    l2cache_nosets = content["description"]
                if(content["name"] == "cache_line_size"):
                    l2cache_linesize = content["description"]

            l2_cache = False



        #l3cache
        if(key.find("L3") != -1 and l3_cache):
            subdata = data[key]["contents"]

            for content in subdata:
                if(content["name"] == "associativity"):
                    l3cache_associativity = content["description"]
                if(content["name"] == "size"):
                    l3cache_size = content["description"]
                if(content["name"] == "no_sets"):
                    l3cache_nosets = content["description"]
                if(content["name"] == "cache_line_size"):
                    l3cache_linesize = content["description"]

            l3_cache = False
                    
        ##NO_NUMA_NODES
        if(key.find("socket") != -1):
            system_no_numa_nodes += 1
            

        ##disks
        if(key.find("disk;1") != -1):
            system_no_disks = int(data[key]["contents"][0]["description"])

            

    
    data = {"system_hostname": system_hostname,
            "system_ip": system_ip,
            "system_os": system_os,
            "system_no_numa_nodes": system_no_numa_nodes,
            "system_no_disks": system_no_disks,
            "cpu_model" : cpu_model,
            "cpu_cores": cpu_cores,
            "cpu_threads": cpu_threads,
            "cpu_hyperthreading": cpu_hyperthreading,
            "cpu_maxmhz": cpu_maxmhz,
            "cpu_minmhz": cpu_minmhz,
            "l1dcache_size": l1dcache_size,
            "l1dcache_associativity": l1dcache_associativity,
            "l1dcache_linesize": l1dcache_linesize,
            "l1dcache_nosets": l1dcache_nosets,
            "l2cache_size": l2cache_size,
            "l2cache_associativity": l2cache_associativity,
            "l2cache_linesize": l2cache_linesize,
            "l2cache_nosets": l2cache_nosets,
            "l3cache_size": l3cache_size,
            "l3cache_associativity": l3cache_associativity,
            "l3cache_linesize": l3cache_linesize,
            "l3cache_nosets": l3cache_nosets}
    
    return data


def main(hostname, hostip):
    
    global data
    
    CONNECTION_STRING = "mongodb://localhost:27017"
    client = MongoClient(CONNECTION_STRING)

    db = client[hostname]
    collection = db["twin"]

    print("collection:", collection)

    response = collection.find_one({'_id': ObjectId("6311d56ba3f0c3bce0173ee6")})

    #print("response:", response)
    data = fill_data(response["dtdl_twin"], hostname, hostip)
    print("DATA:", data)
    app.run(host='0.0.0.0', port=5052, debug=True)


if __name__ == '__main__':

    main("dolap", "10.36.54.195")
