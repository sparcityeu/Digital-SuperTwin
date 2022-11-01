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

from influxdb import InfluxDBClient

import pymongo
from pymongo import MongoClient

import asyncio

import getpass
import paramiko

from scp import SCPClient
from threading import Thread

import sys
sys.path.append("../")
sys.path.append("../probing")
import remote_probe
import utils

from bson.objectid import ObjectId
from bson.json_util import dumps
from bson.json_util import loads


ALWAYS_HAVE_MONITOR = ["perfevent.hwcounters.RAPL_ENERGY_PKG.value",
                       "perfevent.hwcounters.RAPL_ENERGY_PKG.dutycycle",
                       "perfevent.hwcounters.RAPL_ENERGY_DRAM.value",
                       "perfevent.hwcounters.RAPL_ENERGY_DRAM.dutycycle"]

ALWAYS_HAVE_MONITOR_WIDER = ["perfevent.hwcounters.RAPL_ENERGY_PKG.value",
                             "perfevent.hwcounters.RAPL_ENERGY_PKG.dutycycle",
                             "perfevent.hwcounters.RAPL_ENERGY_DRAM.value",
                             "perfevent.hwcounters.RAPL_ENERGY_DRAM.dutycycle",
                             "kernel.all.pressure.cpu.some.total",
                             "hinv.cpu.clock",
                             "lmsensors.coretemp_isa_0000.package_id_0",
                             "lmsensors.coretemp_isa_0001.package_id_1",
                             "kernel.percpu.cpu.idle",
                             "kernel.pernode.cpu.idle",
                             "disk.dev.read",
                             "disk.dev.write",
                             "disk.dev.total",
                             "disk.dev.read_bytes",
                             "disk.dev.write_bytes",
                             "disk.dev.total_bytes"]

ALWAYS_HAVE_OBSERVATION = ["RAPL_ENERGY_PKG node",
                           "RAPL_ENERGY_DRAM node"]

##These may increase or increse
##TO DO: Add AMD energy PMUs

def get_date_tag():

    date = datetime.datetime.now()
    ##Per run
    tag_date = date.strftime("%d%m%Y_%f")

    return tag_date


def generate_pcp2influxdb_config(db_name, db_tag, sourceIP, source_name, metrics):
    
    for item in ALWAYS_HAVE_MONITOR_WIDER:
        if item not in metrics:
            metrics.append(item)
    
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

def generate_pcp2influxdb_config_observation(SuperTwin, observation_id):

    db_tag = observation_id
    db_name = SuperTwin.influxdb_name
    sourceIP = SuperTwin.addr
    source_name = SuperTwin.name
    
    for item in ALWAYS_HAVE_OBSERVATION:
        if item not in metrics:
            metrics.append(item)
    
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

def get_msr(SuperTwin):

    db = utils.get_mongo_database(SuperTwin.name, SuperTwin.mongodb_addr)["twin"]
    meta_with_twin = loads(dumps(db.find({"_id": ObjectId(SuperTwin.mongodb_id)})))[0]
    twin = meta_with_twin["twin_description"]                  

    for key in twin.keys():
        if(key.find("system:S1") != -1):
            contents = twin[key]["contents"]
            for content in contents:
                if(content["@id"].find("MSR") != -1):
                    return content["description"]


def generate_perfevent_conf(SuperTwin):

    metrics = SuperTwin.observation_metrics

    for item in ALWAYS_HAVE_OBSERVATION:
        if item not in metrics:
            metrics.append(item)

    for item in metrics:
        if(item.find("numa") != -1 or item.find("node") != -1):
            metrics.remove(item)
            metrics.append(item)
    
    
    msr = get_msr(SuperTwin)

    writer = open("perfevent.conf", "w+")
    writer.write("[" + msr + "]" + "\n")
    for item in metrics:
        writer.write(item + "\n")
    writer.close()

    print("Generated new perfevent pmda configuration..")

def reconfigure_perfevent(SuperTwin):

    SSHuser = SuperTwin.SSHuser
    SSHpass = SuperTwin.SSHpass

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SuperTwin.addr, username = SSHuser, password = SSHpass)

    scp = SCPClient(ssh.get_transport())

    ##scp to a location that is writable then copy to real path with sudo
    
    remote_probe.run_command(ssh, SuperTwin.name, "mkdir /tmp/dt_files")
    scp.put("perfevent.conf", remote_path="/tmp/dt_files")

    reconfigure_perf_sh = ["#!/bin/bash \n",
                           "cd /var/lib/pcp/pmdas/perfevent",
                           "cp /tmp/dt_files/perfevent.conf /var/lib/pcp/pmdas/perfevent",
                           "/var/lib/pcp/pmdas/perfevent/./Remove",
                           "printf 'pipe' | /var/lib/pcp/pmdas/perfevent/./Install"]

    writer = open("reconfigure_perf.sh", "w+")
    for line in reconfigure_perf_sh:
        writer.write(line + "\n")
    writer.close()

    scp.put("reconfigure_perf.sh", remote_path="/tmp/dt_files")
    
    remote_probe.run_sudo_command(ssh, SuperTwin.SSHpass, SuperTwin.name, "sudo sh /tmp/dt_files/reconfigure_perf.sh")

    print("Reconfigured remote perfevent pmda")

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
    































