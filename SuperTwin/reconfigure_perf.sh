#!/bin/bash 

cd /var/lib/pcp/pmdas/perfevent
cp /tmp/dt_files/perfevent.conf /var/lib/pcp/pmdas/perfevent
/var/lib/pcp/pmdas/perfevent/./Remove
printf 'pipe' | /var/lib/pcp/pmdas/perfevent/./Install
