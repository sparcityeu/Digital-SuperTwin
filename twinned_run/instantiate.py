import sys
sys.path.append("../create_dt")
sys.path.append("../system_query")

import detect_utils
import create_dt
from pprint import pprint
import json

import datetime
import subprocess
from subprocess import Popen, PIPE

##databases
#import influxdb_client
#from influxdb_client.client.write_api import SYNCHRONOUS

from influxdb import InfluxDBClient

import pymongo
from pymongo import MongoClient

import asyncio

def get_date_tag():

    date = datetime.datetime.now()
    ##Per run
    tag_date = date.strftime("%d%m%Y%f")

    return tag_date


def generate_pcp2influxdb_config(config_file, tag):
    
    reader = open(config_file, "r")
    metrics = reader.readlines()
    reader.close()

    metrics = [x.strip("\n") for x in metrics]

    config_lines = ["[options]" + "\n",
                    "influx_server = http://127.0.0.1:8086" + "\n",
                    "influx_db = " "pcp_" + tag + "\n",
                    "\n\n",
                    "[configured]" + "\n"]

    
    for metric in metrics:
        config_lines.append(metric + " = ,," + "\n")


    pcp_conf_name = "pcp" + tag + ".conf" 
    writer = open(pcp_conf_name, "w")
    
    for line in config_lines:
        writer.write(line)
    writer.close()


    return pcp_conf_name, "pcp_" + tag


def run(config_file):

    command = "sleep 30"
    
    start_timestamp = 1
    end_timestamp = 1

    

    
def get_mongo_database(mongodb_name):

    ##Create a connection for mongodb 
    CONNECTION_STRING = "mongodb://localhost:27017"
    client = MongoClient(CONNECTION_STRING)

    ##Create the database for this instance(s)
    return client[mongodb_name]
    
    

def main():

    config_file = sys.argv[1]
    print("here, config_file:", config_file)
    
    #dt_base = create_dt.main("")
    dt_pruned = create_dt.main(config_file)


    ##Runs metadata
    hostname = detect_utils.cmd('hostname')[1].strip('\n')
    date = datetime.datetime.now()
    date = date.strftime("%d-%m-%Y")

    conf_prefix = config_file.replace(".", "_")
    mongodb_name = conf_prefix + get_date_tag()

    mongodb = get_mongo_database(mongodb_name)
    collection = mongodb[mongodb_name + "_0"]


    pcp_conf_name, influx_db_name = generate_pcp2influxdb_config(config_file, get_date_tag())

    influxdb = InfluxDBClient(host="localhost", port=8086)
    influxdb.create_database(influx_db_name)

    
    command = "sleep 30"

    DETACHED_PROCESS = 0x00000008
    
    p0 = Popen(["pcp2influxdb", "-t", "1", "-c", pcp_conf_name, ":configured"], start_new_session=True)

    print("Will sleep")
    p1 = Popen(["sleep", "30"], stdin = subprocess.PIPE,
               stdout = subprocess.PIPE)
    p1.wait()
    p0.kill()
    
    '''
    print("Should kill: ", p0.pid)
    p2 = Popen(["kill", str(p0.pid)], shell=False,
              stdin = None, stdout = None, stderr = None, close_fds = True)
    print("Killed! : ", p0.pid)
    '''

    try0 = {
        "hostname": hostname,
        "date": date,
        #"dt_base": dt_base,
        "dt_pruned": dt_pruned,
        "influxdb": influx_db_name
    }
    collection.insert_one(try0)
    
if __name__ == "__main__":

    main()
    































