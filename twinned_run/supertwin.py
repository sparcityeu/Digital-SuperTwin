import sys
sys.path.append("../create_dt")
sys.path.append("../system_query")

import detect_utils
import create_dt
import generate_dt
import remote_probe
import initiate
import instantiate

import json
import requests
from os import getenv
from os.path import exists

import webbrowser


def readstate():

    if(not exists("supertwin.state")):
        detect_utils.cmd("touch supertwin.state")
    
    reader = open("supertwin.state", "r")
            
    line = reader.readlines()
    reader.close()
    if(len(line) == 0):
        return -1

    state_list = []
    
    entries = line[0].split("##")
    while('' in entries):
        entries.remove('')
    print("entries:", entries)
    for i in range(0, len(entries)):
        system_dict = {}
        system = entries[i].split("|")
        system_dict[system[0]] = {}
        system_dict[system[0]]["twin_id"] = system[1] ## twin_document_id
        system_dict[system[0]]["sampler_pid"] = system[2] ## sampler_pid
        state_list.append(system_dict)

    return state_list

def makestate(SSHhost, twinDocument_id, monitorPID):

    writer = open("supertwin.state", "w")
    statestring = ""
    statestring += "##"
    statestring += SSHhost
    statestring += "|"
    statestring += str(twinDocument_id)
    statestring += "|"
    statestring += str(monitorPID)
    statestring += "##" 
    writer.write(statestring)

def is_system_exist(state, SSHhost):
    
    for dicts in state:
        if(list(dicts.keys())[0] == SSHhost):
            return True, dicts

    return False, -1
    

def main():

    state = readstate()
    mode = sys.argv[1]
    if(len(sys.argv) == 3):
        command = sys.argv[2] ##Need further care

    SSHhost = input("Address of the remote system: ")

    if(mode == "start" and state == -1):
        hostName, hostIP, hostProbFile = remote_probe.main(SSHhost)
        monitoringMetricsConf = input("Monitoring metrics configuration: ")
        monitorPID, twinDocument_id = initiate.main(hostName, hostIP, hostProbFile, monitoringMetricsConf)
        print("A daemon is sampling", hostName, "with PID", monitorPID)
        makestate(SSHhost, twinDocument_id, monitorPID)

    elif(mode == "start" and state != -1):
        exist, this = is_system_exist(state, SSHhost)
        print("System exists!")
        print("Twin id:", this[SSHhost]["twin_id"])
        print("Sampler pid:", this[SSHhost]["sampler_pid"])
        
    elif(mode == "observe" ):
        print("Start observation")

    else:
        print("Wrong input")
        exit(1)
        

    '''
    try:
        detect_utils.cmd("sudo kill " + str(monitorPID))
    except:
        x = 1
    '''
    

if __name__ == "__main__":

    main()
