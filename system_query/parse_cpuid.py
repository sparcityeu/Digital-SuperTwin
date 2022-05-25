import detect_utils

def gv_parentheses(cpuid_string):
    str_list = cpuid_string.split(' ')
    return str_list[-1].strip('(').strip(')')

def gv_parentheses_space(cpuid_string):
    str_list = cpuid_string.split(' ')
    return str_list[-2].strip('(').strip(')') + ' ' +str_list[-1].strip('(').strip(')')
    

def parse_cpuid():

    info = {'tlb': [],
            'cache': {},
            'monitoring': {},
            'freq': {} }
    
    tlb = detect_utils.output_lines('sudo cpuid -1 -l 2')
    for item in tlb:
        if(item.find('data TLB') != -1):
            item = item[item.find('data TLB'):]
            fields = item.split(',')
            temp = {'type': fields[0],
                    'association': fields[1].strip(' '),
                    'size': fields[2].strip(' ')}
            info['tlb'].append(temp)
            
        if(item.find('instruction TLB') != -1):
            item = item[item.find('instruction TLB'):]
            fields = item.split(',')
            temp = {'type': fields[0],
                    'association': fields[1].strip(' '),
                    'size': fields[2].strip(' ')}
            info['tlb'].append(temp)

        if(item.find('L2 TLB') != -1):
            item = item[item.find('L2 TLB'):]
            fields = item.split(',')
            temp = {'type': fields[0],
                    'association': fields[1].strip(' '),
                    'size': fields[2].strip(' ')}
            info['tlb'].append(temp)

                    
    cache_0 = detect_utils.output_lines('sudo cpuid -1 -l 4 -s 0')
    info['cache']['L1D'] = {}
    info['cache']['L1D']['line_size'] = gv_parentheses(cache_0[8])
    info['cache']['L1D']['line_partitions'] = gv_parentheses(cache_0[9])
    info['cache']['L1D']['associativity'] = gv_parentheses(cache_0[10])
    info['cache']['L1D']['number_of_sets'] = gv_parentheses(cache_0[11])
    info['cache']['L1D']['size'] = gv_parentheses_space(cache_0[16])
    
    cache_1 = detect_utils.output_lines('sudo cpuid -1 -l 4 -s 1')
    info['cache']['L1I'] = {}
    info['cache']['L1I']['line_size'] = gv_parentheses(cache_1[8])
    info['cache']['L1I']['line_partitions'] = gv_parentheses(cache_1[9])
    info['cache']['L1I']['associativity'] = gv_parentheses(cache_1[10])
    info['cache']['L1I']['number_of_sets'] = gv_parentheses(cache_1[11])
    info['cache']['L1I']['size'] = gv_parentheses_space(cache_1[16])
    
    cache_2 = detect_utils.output_lines('sudo cpuid -1 -l 4 -s 2')
    info['cache']['L2'] = {}
    info['cache']['L2']['line_size'] = gv_parentheses(cache_2[8])
    info['cache']['L2']['line_partitions'] = gv_parentheses(cache_2[9])
    info['cache']['L2']['associativity'] = gv_parentheses(cache_2[10])
    info['cache']['L2']['number_of_sets'] = gv_parentheses(cache_2[11])
    info['cache']['L2']['size'] = gv_parentheses_space(cache_2[16])

    cache_3 = detect_utils.output_lines('sudo cpuid -1 -l 4 -s 3')
    info['cache']['L3'] = {}
    info['cache']['L3']['line_size'] = gv_parentheses(cache_3[8])
    info['cache']['L3']['line_partitions'] = gv_parentheses(cache_3[9])
    info['cache']['L3']['associativity'] = gv_parentheses(cache_3[10])
    info['cache']['L3']['number_of_sets'] = gv_parentheses(cache_3[11])
    info['cache']['L3']['size'] = gv_parentheses_space(cache_3[16])

    monitoring = detect_utils.output_lines('sudo cpuid -1 -l 10')
    info['monitoring']['no_of_pmcs'] = gv_parentheses(monitoring[3])
    info['monitoring']['bit_width_of_pmcs'] = gv_parentheses(monitoring[4])
    info['monitoring']['no_of_fixed_pmcs'] = gv_parentheses(monitoring[15])
    info['monitoring']['bit_width_of_fixed_pmcs'] = gv_parentheses(monitoring[16])
    

    freq = detect_utils.output_lines('sudo cpuid -1 -l 22')
    info['freq']['base_mhz'] = gv_parentheses(freq[2])
    info['freq']['max_mhz'] = gv_parentheses(freq[3])
    info['freq']['bus_mhz'] = gv_parentheses(freq[4])

    #print(info)
    return info

if __name__ == "__main__":

    parse_cpuid()

    
