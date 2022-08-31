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


    return pcp_conf_name


#def launch_sampling()


def main(SSHhost, command):

    config_file = input("Metrics configuration file: ")
    SSHuser = input("User: ")
    SSHpass = getpass.getpass()

    ##Connect to remote host
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SSHhost, username  = SSHuser, password = SSHpass)

    ##Get the hostname
    stdout = ssh.exec_command("hostname")[1]

    for line in stdout:
        print("Remote host name:", line.strip("\n"))
        remotehost_name = line.strip("\n")

    ##observation_id
    this_observation_id = str(uuid.uuid4())
    print(this_observation_id)


    pcp_conf_name = generate_pcp2influxdb_config(config_file, SSHhost, remotehost_name, this_observation_id)
    
    ##Launch sampler
    sampling_command = "pcp2influxdb -t 1 -c " + pcp_conf_name + " :configured"
    sampling_args = shlex.split(sampling_command)
    sampling_process = Popen(sampling_args)
    ##Launch sampler

    ##Launch remote process
    command = 'echo $$; exec ' + command
    stdin, stdout, stderr = ssh.exec_command(command)
    pid = int(stdout.readline())
    print("Executing command: ", command, "on:", SSHhost, "pid:", pid)
    exit_status = stdout.channel.recv_exit_status()
    ##Launch remote process

    ##Stop sampler
    sampling_process.kill()
    ##Stop sampler
    

if __name__ == "__main__":

    main("10.36.54.195", "stress --cpu 44 --io 4 --vm 2 --vm-bytes 128M --timeout 10s")
