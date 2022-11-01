import sys
sys.path.append("../create_dt")
sys.path.append("../system_query")

import detect_utils
import json
from pprint import pprint

from influxdb import InfluxDBClient

import pymongo
from pymongo import MongoClient

import getpass
import paramiko

from scp import SCPClient


def progress4(filename, size, sent, peername):
    sys.stdout.write("(%s:%s) %s's progress: %.2f%%   \r" % (peername[0], peername[1], filename, float(sent)/float(size)*100) )

    
def run_sudo_command(ssh_client, SSHkey, name, command):

    transport = ssh_client.get_transport()
    session = transport.open_session()
    session.set_combine_stderr(True)
    session.get_pty()
    stdin = session.makefile('wb', -1)
    stdout = session.makefile('rb', -1)
    session.exec_command(command)
    stdin.write(SSHkey + '\n')
    stdin.flush()

    print("Executing command on", name, ":", command)

    ##This is really weird
    ##Need to process the stdout somehow for command to be executed
    ##Will migrate to invoke_shell() or learn in a more in-depth manner
    for line in stdout:
        x = line

def run_sudo_command_perfevent(ssh_client, SSHkey, name, command):

    transport = ssh_client.get_transport()
    session = transport.open_session()
    session.set_combine_stderr(True)
    session.get_pty()
    stdin = session.makefile('wb', -1)
    stdout = session.makefile('rb', -1)
    session.exec_command(command)
    stdin.write(SSHkey + '\n')
    for line in stdout:
        x = line 
    stdin.write("y" + '\n')
    stdin.flush()

    print("Executing command on", name, ":", command)

    ##This is really weird
    ##Need to process the stdout somehow for command to be executed
    ##May also use invoke_shell() here
    for line in stdout:
        x = line
    
    
def run_command(ssh_client, name, command):

    transport = ssh_client.get_transport()
    session = transport.open_session()
    session.set_combine_stderr(True)
    session.get_pty()
    session.exec_command(command)

    print("Executing command on", name, ":", command)


def observation_command(ssh_client, command):
    
    transport = ssh_client.get_transport()
    session = transport.open_session()
    session.set_combine_stderr(True)
    session.get_pty()
    session.exec_command(command)

    print("Executing command on", name, ":", command)
    


#May migrate to invoke_shell() instead of exec_command() in the future
#Because they say exec_command() may not be compatible with ALL servers
#Let's see
def main(*args):

    SSHhost = args[0]
    
    if(len(args) == 1):
        SSHuser = input("User: ")
        SSHpass = getpass.getpass() ##This should be SSHpass
    
    else:
        SSHuser = args[1]
        SSHpass = args[2]
    
    ##Connect to remote host
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SSHhost, username = SSHuser, password = SSHpass)
    stdout = ssh.exec_command("hostname")[1]

    for line in stdout:
        print("Remote host name:", line.strip("\n"))
        remotehost_name = line.strip("\n")
    ##Connect to remote host

    ##Get this framework's path
    path = detect_utils.cmd("pwd")[1].strip('\n')
    #path = path[:path.index("Digital-SuperTwin/SuperTwin") + 29] ##18 characters for "Digital-SuperTwin" + "/"
    #print("path:", path)
    system_query_path = path + "/probing/system_query"
    pmu_query_path = path + "/probing/pmu_event_query"
    #print("Digital SuperTwin local path:", path)
    #print("system_query_path:", system_query_path)
    #print("pmu_query_path:", pmu_query_path)
    ##Get this framework's path
    
    ##Setup scp and transmit Digital-Twin probing
    #scp = SCPClient(ssh.get_transport(), progress4=progress4) ##Need to resolve carriage return trailing problem
    scp = SCPClient(ssh.get_transport())
    run_sudo_command(ssh, SSHpass, remotehost_name, "sudo rm -r /tmp/dt_probing")
    run_command(ssh, remotehost_name, "mkdir /tmp/dt_probing")
    ##scp
    print("Copying probing framework to remote system..")
    ##Issue is here, scp does not create folder when first called only copies content
    ##This is why we first scp and delete and scp again
    ##Need to fix this
    scp.put(system_query_path, recursive=True, remote_path="/tmp/dt_probing")
    run_sudo_command(ssh, SSHpass, remotehost_name, "sudo rm -r /tmp/dt_probing/*")
    scp.put(pmu_query_path, recursive=True, remote_path="/tmp/dt_probing")
    scp.put(system_query_path, recursive=True, remote_path="/tmp/dt_probing")
    print("Probing framework is copied to remote system..")
    ##scp
    run_sudo_command(ssh, SSHpass, remotehost_name, "sudo rm /tmp/dt_probing/pmu_event_query/out.txt")
    run_sudo_command(ssh, SSHpass, remotehost_name, "sudo rm /tmp/dt_probing/pmu_event_query/out_emp.txt")
    run_sudo_command(ssh, SSHpass, remotehost_name, "make -C /tmp/dt_probing/pmu_event_query")
    run_sudo_command(ssh, SSHpass, remotehost_name, "sudo /tmp/dt_probing/pmu_event_query/./showevtinfo -L -D &>> /tmp/dt_probing/pmu_event_query/out.txt")
    run_sudo_command(ssh, SSHpass, remotehost_name, "sudo /tmp/dt_probing/pmu_event_query/./showevtinfo &>> /tmp/dt_probing/pmu_event_query/out_emp.txt")
    run_sudo_command(ssh, SSHpass, remotehost_name, "sudo python3 /tmp/dt_probing/system_query/probe.py")
    #run_sudo_command(ssh, SSHpass, remotehost_name, "ls /tmp/dt_probing/system_query/")
    scp.get(recursive=True, remote_path="/tmp/dt_probing/system_query/probing.json")
    print("Remote probing is done..")
    scp.close() #For now
    ##Setup scp and transmit Digital-Twin probing

    ssh.close()

    probfile_name = "probing_" + remotehost_name + ".json"
    detect_utils.cmd("mv probing.json " + probfile_name)


    if(len(args) == 3):
        return remotehost_name, probfile_name
    else:
        return remotehost_name, probfile_name, SSHuser, SSHpass

if __name__ == "__main__":

    main()
