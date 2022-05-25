import system
import diskinfo
import smart_utils
import smart_utils_info
import detect_utils
import parse_cpuid
import parse_likwid_topology

##Chosen info to generate dtdl twin
chosen_info = {}
chosen_info['hostname'] = ''
chosen_info['os'] = ''
chosen_info['arch']  =  ''
chosen_info['uuid'] = ''

chosen_info['system'] = {}

chosen_info['system']['motherboard'] = {}
chosen_info['system']['motherboard']['name'] = ''
chosen_info['system']['motherboard']['vendor'] = ''

chosen_info['system']['bios'] = {}
chosen_info['system']['bios']['version'] = ''
chosen_info['system']['bios']['date'] = ''
chosen_info['system']['bios']['vendor'] = ''

chosen_info['system']['kernel'] = {}
chosen_info['system']['kernel']['version'] = ''

chosen_info['memory'] = {}
chosen_info['memory']['total'] = {}
chosen_info['memory']['total']['size'] = ''
chosen_info['memory']['total']['banks'] = ''

chosen_info['memory']['banks'] = {}
#for bank
chosen_info['memory']['banks']['id'] = ''
chosen_info['memory']['banks']['size'] = ''
chosen_info['memory']['banks']['slot'] = ''
chosen_info['memory']['banks']['clock'] = ''
chosen_info['memory']['banks']['description'] = ''
chosen_info['memory']['banks']['vendor'] = ''
chosen_info['memory']['banks']['model'] = ''

#consider update()
chosen_info['network'] = {}
chosen_info['network']['name'] = {}
chosen_info['network']['name']['ipv4'] = ''
chosen_info['network']['name']['serial'] = ''
chosen_info['network']['name']['link'] = ''
chosen_info['network']['name']['businfo'] = ''
chosen_info['network']['name']['vendor'] = ''
chosen_info['network']['name']['model'] = ''
chosen_info['network']['name']['firmware'] = ''


##Note that this info here is "to be expanded" for all cpus, all includes all specs and events
chosen_info['cpu'] = {}
chosen_info['cpu']['specs'] = {}
chosen_info['cpu']['specs']['model'] = ''
chosen_info['cpu']['specs']['type'] = ''
chosen_info['cpu']['specs']['sockets'] = ''
chosen_info['cpu']['specs']['cores'] = ''
chosen_info['cpu']['specs']['threads'] = ''
chosen_info['cpu']['specs']['hyperthreading'] = ''
chosen_info['cpu']['specs']['min_mhz'] = '' 
chosen_info['cpu']['specs']['max_mhz'] = ''
chosen_info['cpu']['specs']['bus_mhz'] = ''
chosen_info['cpu']['specs']['flags'] = ''

chosen_info['cpu']['tlb'] = {}
chosen_info['cpu']['cache'] = {}

chosen_info['numa'] = {}

chosen_info['gpus'] = {}

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
    
if __name__ == "__main__":

    hostname = detect_utils.cmd('hostname')[1].strip('\n')
    system_list = system.detect()
    diskinfo_list = diskinfo.detect()

    system = {}
    disk = {}

    system = generate_hardware_dict(system, system_list)
    disk = generate_hardware_dict(disk, diskinfo_list)                
    cache_info = parse_cpuid.parse_cpuid()
    socket_groups, domains, cache_topology, gpu_info = parse_likwid_topology.parse_likwid()


    print('#############################')
    print_hardware_dict(system)
    print('#############################')
    print_hardware_dict(disk)
    print('#############################')
    print(cache_info)
    print('#############################')
    print(socket_groups)
    print('#############################')
    print(domains)
    print('#############################')
    print(cache_topology)
    print('#############################')
    print(gpu_info)
    print('#############################')
