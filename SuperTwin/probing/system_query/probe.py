import system
import diskinfo
import smart_utils
import smart_utils_info
import detect_utils
import parse_cpuid
import parse_likwid_topology
import parse_lshw
import json
from pprint import pprint

import sys
sys.path.append("/tmp/dt_probing/pmu_event_query") ##For remote probing
sys.path.append("../pmu_event_query") ##For local structure
import parse_evtinfo

def pretty_print_info(info):
    pprint(info)

def choose_info(hostname, system, cache_info, socket_groups, domains, cache_topology, affinity, gpu_info, PMUs, pmprobe):
    ##Chosen info to generate dtdl twin
    chosen_info = {}
    chosen_info['hostname'] = hostname
    chosen_info['os'] = system['system']['os']['version']
    chosen_info['arch']  =  system['system']['kernel']['arch']
    chosen_info['uuid'] = system['uuid']
    
    chosen_info['system'] = {}
    
    chosen_info['system']['motherboard'] = {}
    chosen_info['system']['motherboard']['name'] = system['system']['motherboard']['name']
    chosen_info['system']['motherboard']['vendor'] = system['system']['motherboard']['vendor']
    
    chosen_info['system']['bios'] = {}
    chosen_info['system']['bios']['version'] = system['firmware']['bios']['version']
    chosen_info['system']['bios']['date'] = system['firmware']['bios']['date']
    chosen_info['system']['bios']['vendor'] = system['firmware']['bios']['vendor']
    
    chosen_info['system']['kernel'] = {}
    chosen_info['system']['kernel']['version'] = system['system']['kernel']['version']
    
    chosen_info['memory'] = {}
    chosen_info['memory']['total'] = {}
    chosen_info['memory']['total']['size'] = int(system['memory']['total']['size'])
    chosen_info['memory']['total']['banks'] = int(system['memory']['total']['banks'])
    
    chosen_info['memory']['banks'] = {}

    #pprint(system['memory'])
    
    #for bank
    _id = 0
    for key in system['memory']:
        if(key.find('bank:') != -1):
            ident = key
            temp_bank = {}
            temp_bank['id'] = _id
            _id += 1

            try:
                temp_bank['size'] = int(system['memory'][ident]['size'])
                temp_bank['slot'] = system['memory'][ident]['slot']
                temp_bank['clock'] = int(system['memory'][ident]['clock'])
                temp_bank['description'] = system['memory'][ident]['description']
                temp_bank['vendor'] = system['memory'][ident]['vendor']
                temp_bank['model'] = system['memory'][ident]['product']
                chosen_info['memory']['banks'][ident] = temp_bank
            except:
                _id -= 1
        

    chosen_info['network'] = {}
    for key in system['network']:
        chosen_info['network'][key] = {}
        try:
            chosen_info['network'][key]['ipv4'] = system['network'][key]['ipv4']
        except:
            chosen_info['network'][key]['ipv4'] = ''

        try:
            chosen_info['network'][key]['businfo'] = system['network'][key]['businfo']
            chosen_info['network'][key]['vendor'] = system['network'][key]['vendor']
            chosen_info['network'][key]['model'] = system['network'][key]['product']
            chosen_info['network'][key]['firmware'] = system['network'][key]['firmware']
            chosen_info['network'][key]['virtual'] = 'no'
        except:
            chosen_info['network'][key]['businfo'] = 'virtual'
            chosen_info['network'][key]['vendor'] = 'virtual'
            chosen_info['network'][key]['model'] = 'virtual'
            chosen_info['network'][key]['firmware'] = 'virtual'
            chosen_info['network'][key]['virtual'] = 'yes'

        try:
            chosen_info['network'][key]['speed'] = system['network'][key]['speed']
        except:
            chosen_info['network'][key]['speed'] = 'no-link'
            
        chosen_info['network'][key]['serial'] = system['network'][key]['serial']
        chosen_info['network'][key]['link'] = system['network'][key]['link']
        
    ##ugly workaround for windows ruined partition 
    if(system['disk']['logical']['count'] == 1):
        system['disk']['nvme0n1'] = {'model': 'KINGSTON SKC2000M8500G',
                                     'size': 500107862016,
                                     'units': 'bytes'}
        system['disk']['logical']['count'] = 2
    ##ugly workaround for windows ruined partition

    chosen_info['disk'] = {}
    chosen_info['disk']['no_disks'] = system['disk']['logical']['count']
    for key in system['disk']:
        if(key != 'logical'):
            chosen_info['disk'][key] = {}
            chosen_info['disk'][key]['size'] = system['disk'][key]['size']
            chosen_info['disk'][key]['model'] = system['disk'][key]['model']
            #chosen_info['disk'][key]['rotational'] = int(disk['disk'][key]['rotational'])
    
    ##Note that this info here is "to be expanded" for all cpus, all includes all specs and events
    chosen_info['cpu'] = {}
    chosen_info['cpu']['specs'] = {}
    chosen_info['cpu']['specs']['sockets'] = int(system['cpu']['physical']['number'])
    ##From there, assumes all cpus will be identical on the same machine
    chosen_info['cpu']['specs']['model'] = system['cpu']['physical_0']['product']
    chosen_info['cpu']['specs']['type'] = system['cpu']['physical_0']['architecture']
    chosen_info['cpu']['specs']['cores'] = int(system['cpu']['physical_0']['cores'])
    chosen_info['cpu']['specs']['threads'] = int(system['cpu']['physical_0']['threads'])
    chosen_info['cpu']['specs']['threads_per_core'] = int(system['cpu']['physical_0']['threads_per_core'])
    chosen_info['cpu']['specs']['hyperthreading'] = system['cpu']['physical']['smt']
    chosen_info['cpu']['specs']['min_mhz'] = system['cpu']['physical_0']['min_Mhz']
    chosen_info['cpu']['specs']['max_mhz'] = system['cpu']['physical_0']['max_Mhz']
    #chosen_info['cpu']['specs']['bus_mhz'] = system['cpu']['physical_0']['bus_mhz']
    chosen_info['cpu']['specs']['flags'] = system['cpu']['physical_0']['flags']
    
    chosen_info['cpu']['tlb'] = cache_info['tlb']
    chosen_info['cpu']['cache'] = cache_topology
    
    chosen_info['numa'] = domains
    chosen_info['affinity'] = affinity
    
    chosen_info['gpus'] = gpu_info
    chosen_info['PMUs'] = PMUs
    chosen_info['metrics_avail'] = pmprobe

    return chosen_info
    
    ##tlb from cpuid
    ##performance counters from cpuid
    ##gpu(s) from likwid-topology
    
def generate_hardware_dict(to_gen, info_list):

    for item in info_list:
                
        try:
            to_gen[item[0]]
        except:
            to_gen[item[0]] = {}

        try:
            to_gen[item[0]][item[1]]
        except:
            to_gen[item[0]][item[1]] = {}

        try:
            to_gen[item[0]][item[1]][item[2]]
        except:
            to_gen[item[0]][item[1]][item[2]] = {}
        

    for item in info_list:
        to_gen[item[0]][item[1]][item[2]] = item[3]

    return to_gen

def print_hardware_dict(hw_dict):

    print('##################')
    for key in hw_dict:
        print('### key:', key)
        for inner in hw_dict[key]:
            print('### inner:', inner)
            print(hw_dict[key][inner])

            
def get_pmprobe():

    metrics_avail = []
    
    metric_lines = detect_utils.output_lines("pmprobe")
    metric_lines = [x.strip("\n") for x in metric_lines]

    for metric_line in metric_lines:

        fields = metric_line.split(" ")
        metric = fields[0]
        instances = int(fields[1])

        if(instances > 0): ##Do not include metrics that are not available
            metrics_avail.append(metric)

    return metrics_avail
            

def main():

    hostname = detect_utils.cmd('hostname')[1].strip('\n')
    system_list = system.detect()
    diskinfo_list = diskinfo.detect()

    _system = {}
    
    _system = parse_lshw.parse_lshw()
    cache_info = parse_cpuid.parse_cpuid()
    socket_groups, domains, cache_topology, gpu_info = parse_likwid_topology.parse_likwid()
    affinity = parse_likwid_topology.parse_affinity()
    PMUs = parse_evtinfo.main()
    pmprobe = get_pmprobe()
    
    info = choose_info(hostname, _system, cache_info, socket_groups, domains, cache_topology, affinity, gpu_info, PMUs, pmprobe)


    print("Will write to file")
    with open("/tmp/dt_probing/system_query/probing.json", "w") as outfile:
        json.dump(info, outfile)
    print("Should have write to file")
        
    #pprint(info)
    print("Probing done succesfuly..")
    
    return info

if __name__ == "__main__":

    main()
    
