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

def get_date_tag():

    date = datetime.datetime.now()
    ##Per run
    tag_date = date.strftime("%d%m%Y_%f")

    return tag_date


def generate_pcp2influxdb_config(config_file, tag, SShost):
    
    reader = open(config_file, "r")
    metrics = reader.readlines()
    reader.close()

    metrics = [x.strip("\n") for x in metrics]

    config_lines = ["[options]" + "\n",
                    "influx_server = http://127.0.0.1:8086" + "\n",
                    "influx_db = " + "digital_twin" + "\n",
                    "influx_tags = " + "tag=" +"observation_"+ tag + "\n",
                    "\n\n",
                    "[configured]" + "\n"]

    
    for metric in metrics:
        config_lines.append(metric + " = ,," + "\n")

        
    pcp_conf_name = "pcp_" + tag + ".conf" 
    writer = open(pcp_conf_name, "w")
    
    for line in config_lines:
        writer.write(line)
    writer.close()


    return pcp_conf_name, "observation_" + tag


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
        
    ##Get mongodb
    #mongodb_name = conf_prefix + same_tag
    mongodb_name = "digital_twin"
    mongodb = get_mongo_database(mongodb_name)
    #collection = mongodb[mongodb_name + "_" + same_tag]
    collection = mongodb["observations"]
    ##Get mongodb
        
    ##Get influxdb
    pcp_conf_name, influxdb_name = generate_pcp2influxdb_config(config_file, same_tag)
    get_influx_database("digital_twin")
    ##Get influxdb

    
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


    metadata = {
        "hostname": hostname,
        "date": date,
        #"dt_base": dt_base,
        "dt_pruned": dt_pruned,
        "influxdb": "digital_twin",
        "influxdb_tag": "observation_" + str(same_tag),
        "command": command,
        #"command_options": p1_args
    }
    collection.insert_one(metadata)


def run_commands(hostname, date, config_file, dt_pruned, commands):
    
    for command in commands:
        
        run_single(hostname, date, config_file, dt_pruned, command)

def read_commands(commands_file):

    reader = open(commands_file, "r")
    reader_lines = reader.readlines()
    reader_lines = [x.strip("\n") for x in reader_lines]
    reader_lines = [x for x in reader_lines if x.find("#") == -1]

    return reader_lines

def progress4(filename, size, sent, peername):
    sys.stdout.write("(%s:%s) %s's progress: %.2f%%   \r" % (peername[0], peername[1], filename, float(sent)/float(size)*100) )
    
def main():

    config_file = sys.argv[1]
    SSHhost = input("Address of remote system: ")
    SSHuser = input("User: ")
    SSHkey = getpass.getpass() ##This should be SSHpass

    print("#####")
    
    ##Connect to remote host
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SSHhost, username = SSHuser, password = SSHkey)
    stdout = ssh.exec_command("hostname")[1]
    for line in stdout:
        print("Remote host name:", line.strip("\n"))
    #ssh.close() ##Will close the ssh client later
    ##Connect to remote host

    ##Get this framework's path
    path = detect_utils.cmd("pwd")[1].strip('\n')
    path = path[:path.index("Digital-SuperTwin") + 18] ##18 characters for "Digital-SuperTwin" + "/"
    #path += "!(.*)" ##To avoid .git/ and other hidden folders
    system_query_path = path + "system_query"
    pmu_query_path = path + "pmu_event_query"
    print("Digital SuperTwin local path:", path) 
    ##Get this framework's path
    

    ##Setup scp and transmit Digital-Twin probing
    ####
    ##Migrate to invoke_shell()
    ##note that there is also exec_command() but
    ##exec_command is not viable for every server hence invoke_shell is a more general solution
    ####
    scp = SCPClient(ssh.get_transport(), progress4=progress4)
    transport = ssh.get_transport()
    session = transport.open_session()
    session.set_combine_stderr(True)
    session.get_pty()
    stdin = session.makefile('wb', -1)
    stdout = session.makefile('rb', -1)
    session.exec_command("sudo rm -r /tmp/dt_probing")
    stdin.write(SSHkey + '\n')
    stdin.flush()
    session = transport.open_session()
    session.set_combine_stderr(True)
    session.get_pty()
    stdin = session.makefile('wb', -1)
    stdout = session.makefile('rb', -1)
    session.exec_command("mkdir /tmp/dt_probing/")
    scp.put(system_query_path, recursive=True, remote_path="/tmp/dt_probing")
    scp.put(pmu_query_path, recursive=True, remote_path="/tmp/dt_probing")
    #scp.close() #For now
    ##Setup scp and transmit Digital-Twin probing
    exit(1)
    
    #dt_base = create_dt.main("")
    dt_pruned = create_dt.main(config_file)
    print("dt_pruned:", dt_pruned)
    exit(1)
    

    ##Runs metadata
    hostname = detect_utils.cmd('hostname')[1].strip('\n')
    date = datetime.datetime.now()
    date = date.strftime("%d-%m-%Y")

    
    commands = read_commands(sys.argv[2])
    print("commands:", commands)
    
    run_commands(hostname, date, config_file, dt_pruned, commands)
    
    
if __name__ == "__main__":

    main()
    































