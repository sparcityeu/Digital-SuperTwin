import sys
sys.path.append("../create_dt")
sys.path.append("../system_query")

import detect_utils
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

#import system_dashboard
#import generate_general_dashboard
#import generate_system_dashboard

from threading import Thread

def get_date_tag():

    date = datetime.datetime.now()
    ##Per run
    tag_date = date.strftime("%d%m%Y_%f")

    return tag_date


def generate_pcp2influxdb_config(db_name, db_tag, sourceIP, source_name, metrics):
    
    
    config_lines = ["[options]" + "\n",
                    "influx_server = http://127.0.0.1:8086" + "\n",
                    "influx_db = " + db_name + "\n",
                    "influx_tags = " + "tag=" + db_tag + "\n",
                    "source = " + sourceIP + "\n",
                    "\n\n",
                    "[configured]" + "\n"]

    
    for metric in metrics:
        config_lines.append(metric + " = ,," + "\n")

        
    pcp_conf_name = "pcp_" + source_name + db_tag + ".conf" 
    writer = open(pcp_conf_name, "w")
    
    for line in config_lines:
        writer.write(line)
    writer.close()


    return pcp_conf_name


def main(hostname, hostIP, db_name, db_tag, metrics):

    ##Get influxdb
    pcp_conf_name = generate_pcp2influxdb_config(db_name, db_tag, hostIP, hostname, metrics)
    print("pcp2influxdb configuration:", pcp_conf_name, "generated")
    ##Get influxdb
    
    ##This is where actual thing happens
    #####################################################################
    p0_command = "pcp2influxdb -t 1 -c " + pcp_conf_name + " :configured"
    p0_args = shlex.split(p0_command)
    
    p0 = Popen(p0_args)
    monitor_pid = p0.pid
    #p0.wait(10)
    #p0.kill()
    #####################################################################
    print("A daemon with pid:", monitor_pid, "is started monitoring", hostname)
    
    return monitor_pid
    
if __name__ == "__main__":

    main("dolap", "10.36.54.195", "probing_dolap.json", "dolap_main.conf")
    































