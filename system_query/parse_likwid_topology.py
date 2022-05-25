import detect_utils
import re

def find_ind(to_find, str_list):
    for i in range(len(str_list)):
        if(str_list[i].find(to_find) != -1):
            return i

    return None

def find_ind_multiple(to_find, str_list, occurence):
    found = 0
    for i in range(len(str_list)):
        if(str_list[i].find(to_find) != -1):
            found += 1
            if(found == occurence):
                return i

    return None

def parse_cache_topology(topol, ret_dict, name, level):

    ret_dict[name] = {}
    to_find = 'Level:\t\t\t' + level 
    start = find_ind(to_find, topol)

    ret_dict[name]['size'] = topol[start + 1].split('\t')[3]
    ret_dict[name]['associativity'] = topol[start + 3].split('\t')[2]
    ret_dict[name]['no_sets'] = topol[start + 4].split('\t')[2]
    ret_dict[name]['cache_line_size'] = topol[start + 5].split('\t')[1]
    ret_dict[name]['shared_by_threads'] = topol[start + 7].split('\t')[1]
    ret_dict[name]['cache_groups'] = []
    
    cache_groups = topol[start + 8].split('\t')[2]
    #print('cache_groups:', cache_groups)
    matches = re.compile('[(]*[ ]+[0-9 ]+[)]*')
    groups = matches.findall(cache_groups)
    #print('groups:', groups)
    
    for item in groups:
        fields = item.split(' ')
        lis = []
        for field in fields:
            if field.isnumeric():
                lis.append(int(field))
        ret_dict[name]['cache_groups'].append(lis)

    return ret_dict

def parse_likwid():

    topol = detect_utils.output_lines('sudo likwid-topology --caches -G')
    
    ind_no_sockets = find_ind('Sockets:', topol)
    no_sockets = int(topol[ind_no_sockets].split('\t')[2])

    ind_cores_per_socket = find_ind('Cores per socket:', topol)
    cores_per_socket = int(topol[ind_cores_per_socket].split('\t')[1])

    ind_threads_per_core = find_ind('Threads per core:', topol)
    threads_per_core = int(topol[ind_threads_per_core].split('\t')[1])
    
    #print(no_sockets, cores_per_socket, threads_per_core)


    socket_groups = {}
    domains = {}
    for i in range(no_sockets):
        ##Socket groups
        to_find = 'Socket ' + str(i) + ':'
        socket_list = topol[find_ind(to_find, topol)].split('\t')[2].strip('(').strip(')').split(' ')
        socket_list.remove('')
        socket_list.remove('')
        
        socket_list = [int(x) for x in socket_list]
        socket_groups[str(i)] = socket_list

        ##Domains
        domains[str(i)] = {}
        to_find = 'Domain:\t\t\t' + str(i) ##if does not work in general, remove \t until none left
        start = find_ind(to_find,topol)
        processor_list = topol[start + 1].split('\t')[2].strip('(').strip(')').split(' ')

        processor_list.remove('')
        processor_list.remove('')

        processor_list = [int(x) for x in processor_list]
        domains[str(i)]['processors'] = processor_list


        distances = topol[start + 2].split('\t')[2].split(' ')
        distances = [int(x) for x in distances]
        domains[str(i)]['distances'] = distances


        domain_total_memory = topol[start + 4].split('\t')[2]
        domains[str(i)]['total_memory'] = domain_total_memory


    cache_topology = {}
    cache_topology = parse_cache_topology(topol, cache_topology, 'L1D', '1')
    cache_topology = parse_cache_topology(topol, cache_topology, 'L2', '2')
    cache_topology = parse_cache_topology(topol, cache_topology, 'L3', '3')

    ##GPUS 
    gpu_info = {}
    gpu_info['GPU_count'] = int(topol[start].split('\t')[3])
    gpu_info['GPUs'] = []

    for i in range(gpu_info['GPU_count']):
        my_dict = {}
        start = find_ind_multiple('ID:', topol, i+1)
        my_dict['ID'] = topol[start].split('\t')[3]
        my_dict['name'] = topol[start + 1].split('\t')[3]
        my_dict['compute_capability'] = topol[start + 2].split('\t')[1]
        my_dict['L2_size'] = topol[start + 3].split('\t')[2]
        my_dict['memory'] = topol[start + 4].split('\t')[3]
        my_dict['SIMD_width'] = topol[start + 5].split('\t')[2]
        my_dict['clock_rate'] = topol[start + 6].split('\t')[2]
        my_dict['memory_clock_rate'] = topol[start + 7].split('\t')[1]
        my_dict['attached_to_numa_node'] = int(topol[start + 8].split('\t')[1])
        my_dict['number_of_SPs'] = int(topol[start + 9].split('\t')[2])
        my_dict['max_threads_per_SPs'] = int(topol[start + 10].split('\t')[1])
        my_dict['max_threads_per_block'] = int(topol[start + 11].split('\t')[1])
        my_dict['max_thread_dimensions'] = topol[start + 12].split('\t')[1]
        my_dict['max_regs_per_block'] = topol[start + 13].split('\t')[1]
        my_dict['shared_mem_per_block'] = int(topol[start + 14].split('\t')[1])
        my_dict['memory_bus_width'] = int(topol[start + 15].split('\t')[1])
        my_dict['texture_alignment'] = int(topol[start + 16].split('\t')[1])
        my_dict['surface_alignment'] = int(topol[start + 17].split('\t')[1])
        my_dict['max_grid_sizes'] = topol[start + 20].split('\t')[1]
        
        gpu_info['GPUs'].append(my_dict)
        
    
    return [socket_groups, domains, cache_topology, gpu_info]



if __name__ == "__main__":

    
    socket_groups, domains, cache_topology, gpu_info = parse_likwid()
    print('Socket groups:', socket_groups)
    print('Domains:', domains)
    print('Cache topology:', cache_topology)
    print('GPU info:', gpu_info)
