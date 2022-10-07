from influxdb import InfluxDBClient
import pymongo
from pymongo import MongoClient

from bson.objectid import ObjectId
from bson.json_util import dumps
from bson.json_util import loads

import datetime
import json


def get_mongo_database(mongodb_name, CONNECTION_STRING):

    ##Create a connection for mongodb
    client = MongoClient(CONNECTION_STRING)

    ##Create the database for this instance(s)
    return client[mongodb_name]

def get_influx_database(address, influxdb_name):

    fields = address.split("//")[1]
    print("fields:", fields)
    fields = fields.split(":")
    host = fields[0]
    port = fields[1]
    print("host:", host, "port:", port)
    influxdb = InfluxDBClient(host=host, port=port)
    

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
    
    mongodb = get_mongo_database(hostname, CONNECTION_STRING)
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
    
def read_env():
    reader = open("env.txt", "r")
    lines = reader.readlines()
    reader.close()

    mongodb_addr = lines[0].split("=")[1].strip("\n")
    influxdb_addr = lines[1].split("=")[1].strip("\n")
    grafana_addr = lines[2].split("=")[1].strip("\n")
    grafana_token = lines[3].split("=")[1].strip("\n")
    
    #print("mongodb_addr:", mongodb_addr)
    #print("influxdb_addr:", influxdb_addr)
    #print("grafana_addr:", grafana_addr)
    #print("grafana_token:", grafana_token)
    
    return mongodb_addr, influxdb_addr, grafana_addr, grafana_token

def read_monitor_metrics():

    reader = open("monitor_metrics.txt", "r")
    lines = reader.readlines()
    reader.close()

    metrics = []

    for line in lines:
        if(line.find("#") == -1):
            metrics.append(line.strip("\n"))

    return metrics

def update_state(addr, twin_id, collection_id):

    writer = open("supertwin.state", "a")
    #writer.write("#--------------------------------------------------#")
    #writer.write("\n")
    writer.write(addr + "|" + twin_id + "|" + collection_id)
    writer.write("\n")
    writer.close()

def check_state(addr):

    exist = False
    twin_id = None
    collection_id = None
        
    reader = open("supertwin.state", "r")
    lines = reader.readlines()

    for line in lines:
        #if(line.find("#---") == -1):
        fields = line.strip("\n").split("|")
        if(addr == fields[0]):
            exist = True
            addr = fields[0]
            twin_id = fields[1]
            collection_id = fields[2]
            return exist, twin_id, collection_id
            
    return exist, twin_id, collection_id
    
#def update_twin_document__add_benchmark(SuperTwin):
#def update_twin_document__monitor_metrics(SuperTwin):
