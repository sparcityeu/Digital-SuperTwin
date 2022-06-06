import sys
sys.path.append('../system_query')

import os
import detect_utils


if __name__ == "__main__":

    #os.system('sh standard_deploy.sh')
    
    pminfo = detect_utils.output_lines('pminfo')
    #print(pminfo)

    pmprobe_zero = detect_utils.output_lines('pmprobe')
    #print(pmprobe_zero)

    to_prune = []
    for item in pmprobe_zero:
        fields = item.split(" ")
        #print(fields)

        no_vals = int(fields[1])
        if(no_vals < 1):
            to_prune.append(fields[0])



    #print('to_prune:', to_prune)
    print('len:', len(to_prune))

    
    line_0 = '. /etc/pcp.env' + '\n'
    mid_lines = []
    for item in to_prune:
        mid_lines.append('pmnsdel ' + item + ' \n')
        
    z_line_0 = '$PCP_RC_DIR/pmcd start' + '\n'
    
    with open('prune.sh', 'w+') as scr:
        scr.write(line_0)
        for item in mid_lines:
            scr.write(item)
        scr.write(z_line_0)


        
    #os.system('sh prune.sh')
        
