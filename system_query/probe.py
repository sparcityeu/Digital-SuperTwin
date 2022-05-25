import system
import diskinfo
import smart_utils
import smart_utils_info
import detect_utils

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


chosen_info['cpu'] = {}
chosen_info['cpu']['specs'] = {}
chosen_info['cpu']['specs']['model'] = ''
chosen_info['cpu']['specs']['type'] = ''
chosen_info['cpu']['specs']['sockets'] = ''
chosen_info['cpu']['specs']['cores'] = ''
chosen_info['cpu']['specs']['threads'] = ''
chosen_info['cpu']['specs']['hyperthreading'] = ''
#chosen_info['cpu']['specs']['min_mhz'] = '' 
#chosen_info['cpu']['specs']['max_mhz'] = ''
#chosen_info['cpu']['specs']['bus_mhz'] = ''
chosen_info['cpu']['specs']['flags'] = ''

##tlb from cpuid
##performance counters from cpuid
##gpu(s) from likwid-topology




if __name__ == "__main__":

    hostname = detect_utils.cmd('hostname')[1].strip('\n')
    system_list = system.detect()
    diskinfo_list = diskinfo.detect()

    system = {}

    for item in system_list:
        #print(item)
        #print(item[0], item[1], item[2], item[3])

        
        try:
            system[item[0]]
        except:
            system[item[0]] = {}

        try:
            system[item[0]][item[1]]
        except:
            system[item[0]][item[1]] = {}

        try:
            system[item[0]][item[1]][item[2]]
        except:
            system[item[0]][item[1]][item[2]] = {}
        

    for item in system_list:
        system[item[0]][item[1]][item[2]] = item[3]


    print('##################')
    for key in system:
        print('### key:', key)
        for inner in system[key]:
            print('### inner:', inner)
            print(system[key][inner])


    disk = {}

    for item in diskinfo_list:

        try:
            disk[item[0]]
        except:
            disk[item[0]] = {}

        try:
            disk[item[0]][item[1]]
        except:
            disk[item[0]][item[1]] = {}

        try:
            disk[item[0]][item[1]][item[2]]
        except:
            disk[item[0]][item[1]][item[2]] = {}
        

    for item in diskinfo_list:
        disk[item[0]][item[1]][item[2]] = item[3]


    print('##################')
    for key in disk:
        print('### key:', key)
        for inner in disk[key]:
            print('### inner:', inner)
            print(disk[key][inner])




            
