import sys
import os
import paramiko
import getpass
import remote_probe
import uuid

import subprocess
from subprocess import Popen, PIPE
import shlex

from threading import Thread

import pymongo
from pymongo import MongoClient

import datetime
import time

import generate_observation_dashboard
import generate_spmv_observation_dashboard

def run_command(ssh_client, command):

    transport = ssh_client.get_transport()
    session = transport.open_session()
    session.set_combine_stderr(True)
    session.get_pty()
    session.exec_command(command)

    print("Executing command: ", command)


def generate_pcp2influxdb_config(config_file, sourceIP, source_name, observation_id):

    reader = open(config_file, "r")
    metrics = reader.readlines()
    reader.close()
    
    metrics = [x.strip("\n") for x in metrics]

    influx_db_name = source_name + "_main"
    tag = "_observation_" + observation_id

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


    return pcp_conf_name, metrics


def launch_sampling(pcp_conf_name, command, ssh_instance, SSHhost, master):

    if(master):
        ##Launch sampler
        sampling_command = "pcp2influxdb -t 0.5 -c " + pcp_conf_name + " :configured"
        sampling_args = shlex.split(sampling_command)
        sampling_process = Popen(sampling_args)
        ##Launch sampler

    #time.sleep(5)

    ##Launch remote process
    #command = 'echo $$; exec ' + command
    stdin, stdout, stderr = ssh_instance.exec_command(command)
    #print('stdout:', stdout.readlines())
    #pid = int(stdout.readline())
    #print("Executing command: ", command, "on:", SSHhost, "pid:", pid)
    print("Executing command: ", command, "on:", SSHhost)
    exit_status = stdout.channel.recv_exit_status()
    ##Launch remote process

    ##Stop sampler
    if(master):
        sampling_process.kill()
    ##Stop sampler


def get_mongo_database(mongodb_name):

    ##Create a connection for mongodb
    CONNECTION_STRING = "mongodb://localhost:27017"
    client = MongoClient(CONNECTION_STRING)

    ##Create the database for this instance(s)
    return client[mongodb_name]

    
def add_to_mongodb(remotehost_name, observation_id, command, metrics):

    ##Get mongodb
    mongodb = get_mongo_database(remotehost_name)
    collection = mongodb["observations"]
    ##Get mongodb

    date = datetime.datetime.now()
    date = date.strftime("%d-%m-%Y")

    tag = "_observation_" + observation_id
    
    metadata = {
        "date": date,
        "observation_id": observation_id,
        "command": command,
        "influxdb_tag": tag,
        "no metrics": len(metrics),
        "metrics": metrics,
        "report location": "report"
    }

    collection.insert_one(metadata)

    
def main(SSHhost, SSHuser, SSHpass, config_file, command, master):

    ##Connect to remote host
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SSHhost, username  = SSHuser, password = SSHpass)

    ##Get the hostname
    stdout = ssh.exec_command("hostname")[1]

    for line in stdout:
        print("Remote host name:", line.strip("\n"))
        remotehost_name = line.strip("\n")

    if(master):
        ##observation_id
        this_observation_id = str(uuid.uuid4())
        print("Observation id:", this_observation_id)


        pcp_conf_name, metrics = generate_pcp2influxdb_config(config_file, SSHhost, remotehost_name, this_observation_id)

        ##change metrics from pcp to influx
        metrics = [x.replace(".", "_") for x in metrics]

        time_from = round(time.time()*1000)
        launch_sampling(pcp_conf_name, command, ssh, remotehost_name, master)
        time_to = round(time.time()*1000)
        add_to_mongodb(remotehost_name, this_observation_id, command, metrics)

        _time_window = str(round((time_to - time_from)))
        _time = str(round((time_from + time_to) /2))
        
        m_s_a = []
        for item in metrics:
            m_s_a.append([item, "*"])
        

        ret = generate_spmv_observation_dashboard.main(m_s_a, this_observation_id, time_from, time_to)
        url = "http://localhost:3000" + ret['url'] + "?" + "time=" + _time + "&" + "time.window=" + _time_window
        print("Report generated at:", url)

    else:
        launch_sampling("", command, ssh, remotehost_name, master)

if __name__ == "__main__":

    #main("10.36.54.195", "stress --cpu 44 --io 4 --vm 2 --vm-bytes 128M --timeout 30s")
    #main("10.36.54.195", "taskset -c 0 ./dt_latest/Digital-SuperTwin/spmv/degree ./dt_latest/Digital-SuperTwin/spmv/garon2.mtx")
    #main("10.36.54.195", "taskset -c 0 ./dt_latest/Digital-SuperTwin/spmv/degree dt_latest/Digital-SuperTwin/spmv/mixtank_new/mixtank_new.mtx")

    config_file = input("Metrics configuration file: ")
    SSHuser = input("User: ")
    SSHpass = getpass.getpass()

    
    thread1 = Thread(target = main, args=("10.36.54.195", SSHuser, SSHpass, config_file, "taskset -c 0 ./dt_latest/Digital-SuperTwin/spmv/degree dt_latest/Digital-SuperTwin/spmv/mixtank_new/mixtank_new.mtx", True))
    thread2 = Thread(target = main, args=("10.36.54.195", SSHuser, SSHpass, config_file, "taskset -c 1 ./dt_latest/Digital-SuperTwin/spmv/rcm dt_latest/Digital-SuperTwin/spmv/mixtank_new/mixtank_new.mtx", False))
    thread3 = Thread(target = main, args=("10.36.54.195", SSHuser, SSHpass, config_file, "taskset -c 2 ./dt_latest/Digital-SuperTwin/spmv/none dt_latest/Digital-SuperTwin/spmv/mixtank_new/mixtank_new.mtx", False))
    thread4 = Thread(target = main, args=("10.36.54.195", SSHuser, SSHpass, config_file, "taskset -c 3 ./dt_latest/Digital-SuperTwin/spmv/random dt_latest/Digital-SuperTwin/spmv/mixtank_new/mixtank_new.mtx", False))
    
    thread1.start()
    thread2.start()
    thread3.start()
    thread4.start()
