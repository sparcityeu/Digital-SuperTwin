import sys
sys.path.append('../system_query')

import os
import detect_utils


if __name__ == "__main__":

    #os.system('sh standard_deploy.sh')
    
    pminfo = detect_utils.output_lines('pminfo')
    #print(pminfo)

    pmprobe_zero = detect_utils.output_lines('pmprobe -n /var/lib/pcp/pmns/root')
    print('Number of probed metrics:', len(pmprobe_zero))

    to_prune = []
    for i in range(220, len(pmprobe_zero)):
        fields = pmprobe_zero[i].split(" ")
        #print(fields)

        no_vals = int(fields[1])
        #if(no_vals < 1):
        to_prune.append(fields[0])



    #print('to_prune:', to_prune)
    print('Number of metrics to prune:', len(to_prune))

    
    line_0 = '. /etc/pcp.env' + '\n'
    mid_lines = []
    for item in to_prune:
        mid_lines.append('pmnsdel -n /var/lib/pcp/pmns/root ' + item + ' \n')

    #z_line_0 = 'systemctl enable pmcd'
    z_line_1 = '$PCP_RC_DIR/pmcd start' + '\n'
    
    with open('prune.sh', 'w+') as scr:
        scr.write(line_0)
        for item in mid_lines:
            scr.write(item)
        #scr.write(z_line_0)
        scr.write(z_line_1)


        
    #os.system('sh prune.sh')
        
