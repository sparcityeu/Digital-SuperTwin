import sys
sys.path.append("../create_dt")
sys.path.append("../system_query")

import detect_utils
import create_dt
import generate_dt
from pprint import pprint
import json

import datetime
import subprocess
from subprocess import Popen, PIPE
import shlex

##databases
#import influxdb_client
#from influxdb_client.client.write_api import SYNCHRONOUS

from influxdb import InfluxDBClient

import pymongo
from pymongo import MongoClient

import asyncio

import getpass
import paramiko

from scp import SCPClient

import system_dashboard

def get_date_tag():

    date = datetime.datetime.now()
    ##Per run
    tag_date = date.strftime("%d%m%Y_%f")

    return tag_date


def generate_pcp2influxdb_config(config_file, tag, sourceIP, source_name):
    
    reader = open(config_file, "r")
    metrics = reader.readlines()
    reader.close()

    metrics = [x.strip("\n") for x in metrics]

    influx_db_name = source_name + "_main" 

    config_lines = ["[options]" + "\n",
                    "influx_server = http://127.0.0.1:8086" + "\n",
                    "influx_db = " + influx_db_name + "\n",
                    "influx_tags = " + "tag=" + tag + "\n",
                    "source = " + sourceIP + "\n",
                    "\n\n",
                    "[configured]" + "\n"]

    
    for metric in metrics:
        config_lines.append(metric + " = ,," + "\n")

        
    pcp_conf_name = "pcp_" + source_name + tag + ".conf" 
    writer = open(pcp_conf_name, "w")
    
    for line in config_lines:
        writer.write(line)
    writer.close()


    return pcp_conf_name, influx_db_name, metrics


def get_mongo_database(mongodb_name):

    ##Create a connection for mongodb 
    CONNECTION_STRING = "mongodb://localhost:27017"
    client = MongoClient(CONNECTION_STRING)
    
    ##Create the database for this instance(s)
    return client[mongodb_name]
    

def get_influx_database(influxdb_name):

    influxdb = InfluxDBClient(host="localhost", port=8086)
    influxdb.create_database(influxdb_name)


def run_single(hostname, date, config_file, dt_pruned, command):

    print("Observing:", command)
    
    conf_prefix = config_file.replace(".", "_")
    same_tag = get_date_tag()

    
    ##This is where actual thing happens
    #####################################################################
    p0_command = "pcp2influxdb -t 1 -c " + pcp_conf_name + " :configured"
    #print("p0_command:", p0_command)
    p0_args = shlex.split(p0_command)
    #print("p0_args:", p0_args)

    p1_command = command
    p1_args = shlex.split(p1_command)

    
    p0 = Popen(p0_args)
    p1 = Popen(p1_args, stdin = subprocess.PIPE, stdout = subprocess.PIPE)
    p1.wait()
    p0.kill()
    #####################################################################

    
    ##Connect target process metrics
    pname = "_" + str(p1.pid) + "_" + p1_args[0] ##Name of the executed command
    p_dtid = create_dt.get_uid(hostname, "process", "", 1)
    for item in dt_pruned[p_dtid]["contents"]:
        item["displayName"] = pname
    ##Connect target process metrics


def run_commands(hostname, date, config_file, dt_pruned, commands):
    
    for command in commands:
        
        run_single(hostname, date, config_file, dt_pruned, command)

def read_commands(commands_file):

    reader = open(commands_file, "r")
    reader_lines = reader.readlines()
    reader_lines = [x.strip("\n") for x in reader_lines]
    reader_lines = [x for x in reader_lines if x.find("#") == -1]

    return reader_lines
    
def main(hostname, hostIP, hostProbFile, monitoringMetricsConf):

    #_sys_dict = json.load(hostProbFile)
    with open(hostProbFile, 'r') as j:
        _sys_dict = json.loads(j.read())
        
    _twin = generate_dt.main(_sys_dict)
    _tag = "_main"
    

    date = datetime.datetime.now()
    date = date.strftime("%d-%m-%Y")
    
    ##Get mongodb
    mongodb_name = hostname
    mongodb = get_mongo_database(mongodb_name)
    collection = mongodb["twin"]
    ##Get mongodb
        
    ##Get influxdb
    pcp_conf_name, influxdb_name, metrics = generate_pcp2influxdb_config(monitoringMetricsConf, _tag, hostIP, hostname)
    get_influx_database(influxdb_name)
    ##Get influxdb
    
    metadata = {
        "hostname": hostname,
        "date": date,
        "dtdl_twin": _twin,
        "influxdb": influxdb_name,
        "influxdb_tag": "_main",
        "dashboard_location": "http://127.0.0.1:3000/d/abifsd",
        "real_dashboard_location": "system_dashboard",
    }
    result = collection.insert_one(metadata)
    twin_id = str(result.inserted_id)

    ##Get system dashboard
    ##hostname is the name of database, "twin" is name of the collection and "id" will return
    ##collection that includes dtdl 
    system_dashboard.main(hostname, twin_id) 
    ##Get system dashboard
    
    ###
    #with open("one_twin.json", "w") as write_file:
    #    json.dump(_twin, write_file, indent=4)
    ###

    ##This is where actual thing happens
    #####################################################################
    p0_command = "pcp2influxdb -t 1 -c " + pcp_conf_name + " :configured"
    p0_args = shlex.split(p0_command)
    
    p0 = Popen(p0_args)
    monitor_pid = p0.pid
    #p0.wait(10)
    #p0.kill()
    #####################################################################

    return monitor_pid, str(result.inserted_id)
    
if __name__ == "__main__":

    main("dolap", "10.36.54.195", "probing_dolap.json", "dolap_main.conf")
    































