import sys
sys.path.append('../system_query')

import os
import detect_utils


def get_to_keep(fname):

    reader = open(fname, 'r')
    lines = reader.readlines()
    lines = [x.strip('\n') for x in lines]

    return lines

def get_to_prune(pmprobe_zero, to_keep):

    to_prune = []

    for item in pmprobe_zero:
        if item not in to_keep:
            to_prune.append(item)

    return to_prune

if __name__ == "__main__":

    confname = sys.argv[1]
    
    #os.system('sh standard_deploy.sh')
    
    pminfo = detect_utils.output_lines('pminfo')
    #print(pminfo)

    pmprobe_zero = detect_utils.output_lines('pmprobe')
    pmprobe_zero = [x.split(" ")[0] for x in pmprobe_zero]
    print('Number of probed metrics:', len(pmprobe_zero))

    

    to_keep = get_to_keep(confname)
    to_prune = get_to_prune(pmprobe_zero, to_keep)

    print('Number of metrics to keep: ', len(to_keep))
    print('Number of metrics to prune:', len(to_prune))

    '''
    for item in pmprobe_zero:
        print(item)
    print('##########')
    for item in to_keep:
        print(item)
    '''

    line_0 = '. /etc/pcp.env' + '\n'
    mid_lines = []
    for item in to_prune:
        mid_lines.append('pmnsdel ' + item + ' \n')

    #z_line_0 = 'systemctl enable pmcd'
    z_line_1 = '$PCP_RC_DIR/pmcd start' + '\n'
    
    with open('prune.sh', 'w+') as scr:
        scr.write(line_0)
        for item in mid_lines:
            scr.write(item)
        #scr.write(z_line_0)
        scr.write(z_line_1)


        
    #os.system('sh prune.sh')
        
