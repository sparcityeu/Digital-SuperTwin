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


def get_date_tag():

    date = datetime.datetime.now()
    ##Per run
    tag_date = date.strftime("%d%m%Y_%f")

    return tag_date

def add_pcp(SuperTwin, config_lines):

    #"4186626 /var/lib/pcp/pmdas/root/pmdaroot"
    
    pcp_lines = ["pcp_pmproxy_mem = pcp_pmproxy_mem \n",
                 "pcp_pmproxy_mem.formula = proc.psinfo.rss \n",
                 'pcp_pmproxy_mem.instances = ' + '"' + SuperTwin.pcp_pids["pmproxy"] + ' /usr/lib/pcp/bin/pmproxy' + '"' + '\n'
                 'pcp_pmproxy_mem.label = "pcp_pmproxy_mem" \n',
                                 
                 "pcp_pmproxy_cpu = pcp_pmproxy_cpu\n",
                 "pcp_pmproxy_cpu.formula = 0.1 * (proc.psinfo.utime + proc.psinfo.stime) \n",
                 'pcp_pmproxy_cpu.instances = ' + '"' + SuperTwin.pcp_pids["pmproxy"] + ' /usr/lib/pcp/bin/pmproxy' + '"' + '\n',
                 'pcp_pmproxy_cpu.label = "pcp_pmproxy_cpu" \n',
                 ##
                 "pcp_pmie_mem = pcp_pmie_mem \n",
                 "pcp_pmie_mem.formula = proc.psinfo.rss \n",
                 'pcp_pmie_mem.instances = ' + '"' + SuperTwin.pcp_pids["pmie"] + ' /usr/bin/pmie' + '"' + '\n'
                 'pcp_pmie_mem.label = "pcp_pmie_mem" \n',
                                 
                 "pcp_pmie_cpu = pcp_pmie_cpu\n",
                 "pcp_pmie_cpu.formula = 0.1 * (proc.psinfo.utime + proc.psinfo.stime) \n",
                 'pcp_pmie_cpu.instances = ' + '"' + SuperTwin.pcp_pids["pmie"] + ' /usr/bin/pmie' + '"' + '\n',
                 'pcp_pmie_cpu.label = "pcp_pmie_cpu" \n',
                 ##
                 "pcp_pmcd_mem = pcp_pmcd_mem \n",
                 "pcp_pmcd_mem.formula = proc.psinfo.rss \n",
                 'pcp_pmcd_mem.instances = ' + '"' + SuperTwin.pcp_pids["pmcd"] + ' /usr/lib/pcp/bin/pmcd' + '"' + '\n'
                 'pcp_pmcd_mem.label = "pcp_pmproxy_mem" \n',
                                 
                 "pcp_pmcd_cpu = pcp_pmcd_cpu\n",
                 "pcp_pmcd_cpu.formula = 0.1 * (proc.psinfo.utime + proc.psinfo.stime) \n",
                 'pcp_pmcd_cpu.instances = ' + '"' + SuperTwin.pcp_pids["pmcd"] + ' /usr/lib/pcp/bin/pmcd' + '"' + '\n',
                 'pcp_pmcd_cpu.label = "pcp_pmproxy_cpu" \n',
                 ##
                 "pcp_pmdaproc_mem = pcp_pmdaproc_mem \n",
                 "pcp_pmdaproc_mem.formula = proc.psinfo.rss \n",
                 'pcp_pmdaproc_mem.instances = ' + '"' + SuperTwin.pcp_pids["pmdaproc"] + ' /var/lib/pcp/pmdas/proc/pmdaproc' + '"' + '\n'
                 'pcp_pmdaproc_mem.label = "pcp_pmdraproc_mem" \n',
                                 
                 "pcp_pmdaproc_cpu = pcp_pmdaproc_cpu\n",
                 "pcp_pmdaproc_cpu.formula = 0.1 * (proc.psinfo.utime + proc.psinfo.stime) \n",
                 'pcp_pmdaproc_cpu.instances = ' + '"' + SuperTwin.pcp_pids["pmdaproc"] + ' /var/lib/pcp/pmdas/proc/pmdaproc' + '"' + '\n',
                 'pcp_pmdaproc_cpu.label = "pcp_pmdaproc_cpu" \n',
                 ##
                 "pcp_pmdalinux_mem = pcp_pmdalinux_mem \n",
                 "pcp_pmdalinux_mem.formula = proc.psinfo.rss \n",
                 'pcp_pmdalinux_mem.instances = ' + '"' + SuperTwin.pcp_pids["pmdalinux"] + ' /var/lib/pcp/pmdas/linux/pmdalinux' + '"' + '\n'
                 'pcp_pmdalinux_mem.label = "pcp_pmdalinux_mem" \n',
                                 
                 "pcp_pmdalinux_cpu = pcp_pmdalinux_cpu\n",
                 "pcp_pmdalinux_cpu.formula = 0.1 * (proc.psinfo.utime + proc.psinfo.stime) \n",
                 'pcp_pmdalinux_cpu.instances = ' + '"' + SuperTwin.pcp_pids["pmdalinux"] + ' /var/lib/pcp/pmdas/linux/pmdalinux' + '"' + '\n',
                 'pcp_pmdalinux_cpu.label = "pcp_pmdalinux_cpu" \n',
                 ##
                 "pcp_pmdalmsensors_mem = pcp_pmdalmsensors_mem \n",
                 "pcp_pmdalmsensors_mem.formula = proc.psinfo.rss \n",
                 'pcp_pmdalmsensors_mem.instances = ' + '"' + SuperTwin.pcp_pids["pmdalmsensors"] + ' /var/lib/pcp/pmdas/lmsensors/pmdalmsensors' + '"' + '\n'
                 'pcp_pmdalmsensors_mem.label = "pcp_pmdalmsensors_mem" \n',
                                 
                 "pcp_pmdalmsensors_cpu = pcp_pmdalmsensors_cpu\n",
                 "pcp_pmdalmsensors_cpu.formula = 0.1 * (proc.psinfo.utime + proc.psinfo.stime) \n",
                 'pcp_pmdalmsensors_cpu.instances = ' + '"' + SuperTwin.pcp_pids["pmdalmsensors"] + ' /var/lib/pcp/pmdas/lmsensors/pmdalmsensors' + '"' + '\n',
                 'pcp_pmdalmsensors_cpu.label = "pcp_pmdalmsensors_cpu" \n',
                 ##
                 "pcp_pmdaperfevent_mem = pcp_pmdalmsensors_mem \n",
                 "pcp_pmdaperfevent_mem.formula = proc.psinfo.rss \n",
                 'pcp_pmdaperfevent_mem.instances = ' + '"' + SuperTwin.pcp_pids["pmdaperfevent"] + ' /var/lib/pcp/pmdas/perfevent/pmdaperfevent' + '"' + '\n'
                 'pcp_pmdaperfevent_mem.label = "pcp_pmdaperfevent_mem" \n',
                                 
                 "pcp_pmdaperfevent_cpu = pcp_pmdaperfevent_cpu\n",
                 "pcp_pmdaperfevent_cpu.formula = 0.1 * (proc.psinfo.utime + proc.psinfo.stime) \n",
                 'pcp_pmdaperfevent_cpu.instances = ' + '"' + SuperTwin.pcp_pids["pmdaperfevent"] + ' /var/lib/pcp/pmdas/perfevent/pmdaperfevent' + '"' + '\n',
                 'pcp_pmdaperfevent_cpu.label = "pcp_pmdaperfevent_cpu" \n',
                 ]

    
    return config_lines + pcp_lines
                
                

def get_pid(line):

    fields = line.split(" ")
    fields = [x for x in fields if x != ""]

    return fields[1]


def complete_to_six(pids):

    for key in pids:
        pid = pids[key]
        while(len(pid) < 6):
            pid = "0" + pid
        pids[key] = pid

    return pids

    
def get_pcp_pids(SuperTwin):

    SSHuser = SuperTwin.SSHuser
    SSHpass = SuperTwin.SSHpass

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SuperTwin.addr, username = SSHuser, password = SSHpass)

    stdin, stdout, stderr = ssh.exec_command("ps aux | grep pcp")
    output = stdout.read()
    #print("pcps:", output, type(output))
    #print("#########3")
    #print(output.decode("utf-8"))
    output = output.decode("utf-8")
    output = output.split("\n")

    pids = {}
    
    for item in output:
        
        if(item.find("pmproxy") != -1):
            pids["pmproxy"] = get_pid(item)
        if(item.find("pmie") != -1):
            pids["pmie"] = get_pid(item)
        if(item.find("pmcd") != -1):
            pids["pmcd"] = get_pid(item)
        if(item.find("pmdaproc") != -1):
            pids["pmdaproc"] = get_pid(item)
        if(item.find("pmdalinux") != -1):
            pids["pmdalinux"] = get_pid(item)
        if(item.find("pmdalmsensors") != -1):
            pids["pmdalmsensors"] = get_pid(item)
        if(item.find("pmdaperfevent") != -1):
            pids["pmdaperfevent"] = get_pid(item)

    print("pids:", pids)
    pids = complete_to_six(pids)
    print("pids:", pids)
    return pids
    
#def generate_pcp2influxdb_config(db_name, db_tag, sourceIP, source_name, metrics):
def generate_pcp2influxdb_config(SuperTwin):

    db_name = SuperTwin.name
    db_tag = SuperTwin.monitor_tag
    sourceIP = SuperTwin.addr
    source_name = SuperTwin.name
    metrics = SuperTwin.monitor_metrics
    always_have_metrics = utils.always_have_metrics("monitor", SuperTwin)
    
    for item in always_have_metrics:
        if item not in metrics:
            metrics.append(item)
            
    config_lines = ["[options]" + "\n",
                    "influx_server = http://127.0.0.1:8086" + "\n",
                    "influx_db = " + db_name + "\n",
                    "influx_tags = " + "tag=" + db_tag + "\n",
                    "source = " + sourceIP + "\n",
                    "\n\n",
                    "[configured]" + "\n"]

    
    #metrics = [x for x in metrics if x != ""] ##Just to make sure
    #for metric in metrics:
    #    config_lines.append(metric + " = ,," + "\n")

    ##Add remote ship overheead
    config_lines = add_pcp(SuperTwin, config_lines)

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
    metrics = SuperTwin.observation_metrics
    always_have_metrics = utils.always_have_metrics("observation", SuperTwin)
    
    for item in always_have_metrics:
        if item not in metrics:
            metrics.append(item)

    metrics = [x.strip("node").strip(" ") for x in metrics]
    metrics = ["perfevent.hwcounters." + x.replace(":", "_") + ".value" for x in metrics]
    
    config_lines = ["[options]" + "\n",
                    "influx_server = http://127.0.0.1:8086" + "\n",
                    "influx_db = " + db_name + "\n",
                    "influx_tags = " + "tag=" + db_tag + "\n",
                    "source = " + sourceIP + "\n",
                    "\n\n",
                    "[configured]" + "\n"]

    
    for metric in metrics:
        config_lines.append(metric + " = ,," + "\n")
        
    pcp_conf_name = "pcp_obsconf_" + source_name + "_" + db_tag + ".conf" 
    writer = open(pcp_conf_name, "w")
    
    for line in config_lines:
        writer.write(line)
    writer.close()


    return pcp_conf_name


def generate_perfevent_conf(SuperTwin):

    metrics = SuperTwin.observation_metrics
    always_have_metrics = utils.always_have_metrics("observation", SuperTwin)
    
    for item in always_have_metrics:
        if item not in metrics:
            metrics.append(item)

            
    msr = utils.get_msr(SuperTwin)

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



#def main(hostname, hostIP, db_name, db_tag, metrics):
def main(SuperTwin):

    ##Get influxdb
    #pcp_conf_name = generate_pcp2influxdb_config(db_name, db_tag, hostIP, hostname, metrics)
    pcp_conf_name = generate_pcp2influxdb_config(SuperTwin)
    print("pcp2influxdb configuration:", pcp_conf_name, "generated")
    
    ##This is where actual thing happens
    #####################################################################
    p0_command = "pcp2influxdb -t 1 -c " + pcp_conf_name + " :configured"
    p0_args = shlex.split(p0_command)
    
    p0 = Popen(p0_args)
    monitor_pid = p0.pid
    #####################################################################
    print("A daemon with pid:", monitor_pid, "is started monitoring", SuperTwin.name)
    
    return monitor_pid
    
if __name__ == "__main__":

    
    main()
    































