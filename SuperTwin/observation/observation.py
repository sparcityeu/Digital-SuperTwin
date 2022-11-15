import subprocess
from subprocess import Popen, PIPE
import shlex

import paramiko
from scp import SCPClient

from timeit import default_timer as timer

def observe_single(SuperTwin, observation_id, command, obs_conf):

        
    ##Connect to remote host
    SSHuser = SuperTwin.SSHuser                                        
    SSHpass = SuperTwin.SSHpass
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SuperTwin.addr, username = SSHuser, password = SSHpass)

    scp = SCPClient(ssh.get_transport())
    ##Connect to remote host

    command_script_name = "observation_" + observation_id + ".sh"
    
    command_script_lines = ["#!/bin/bash"]
    command_script_lines.append(command)
    
    writer = open(command_script_name, "w+")
    for line in command_script_lines:
        writer.write(line + "\n")
    writer.close()

    
    try:
        scp.put(command_script_name, remote_path="/tmp/dt_files")
    except:
        remote_probe.run_command(ssh, SuperTwin.name, "mkdir /tmp/dt_files")
        scp.put(command_script_name, remote_path="/tmp/dt_files")

    run_script = "sh /tmp/dt_files/" + command_script_name
    
    sampling_command = "pcp2influxdb -t 1 -c " + obs_conf + " :configured"
    sampling_args = shlex.split(sampling_command)
    sampling_process = Popen(sampling_args)

    start = timer()
    stdin, stdout, stderr = ssh.exec_command(run_script)
    print("Executing -and observing- command", command, "on:", SuperTwin.name)
    exit_status = stdout.channel.recv_exit_status()
    end = timer()
    print("Took", end - start, "seconds")
    sampling_process.kill()

    return end - start


def observe_single_parameters(SuperTwin, path, affinity, observation_id, command, obs_conf):

        
    ##Connect to remote host
    SSHuser = SuperTwin.SSHuser                                        
    SSHpass = SuperTwin.SSHpass
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SuperTwin.addr, username = SSHuser, password = SSHpass)

    scp = SCPClient(ssh.get_transport())
    ##Connect to remote host

    
    
    command_script_name = "observation_" + observation_id + ".sh"
    
    command_script_lines = ["#!/bin/bash"]
    command_script_lines.append("cd " + path)
    command_script_lines.append(reuser + " " + affinity + " " + command)
    
    
    writer = open(command_script_name, "w+")
    for line in command_script_lines:
        writer.write(line + "\n")
    writer.close()
    
    
    
    try:
        scp.put(command_script_name, remote_path="/tmp/dt_files")
    except:
        remote_probe.run_command(ssh, SuperTwin.name, "mkdir /tmp/dt_files")
        scp.put(command_script_name, remote_path="/tmp/dt_files")

    run_script = "sh /tmp/dt_files/" + command_script_name
    
    sampling_command = "pcp2influxdb -t 1 -c " + obs_conf + " :configured"
    sampling_args = shlex.split(sampling_command)
    sampling_process = Popen(sampling_args)

    start = timer()
    stdin, stdout, stderr = ssh.exec_command(run_script)
    print("Executing -and observing- command", command, "on:", SuperTwin.name)
    exit_status = stdout.channel.recv_exit_status()
    end = timer()
    print("Took", end - start, "seconds")
    sampling_process.kill()

    return end - start
