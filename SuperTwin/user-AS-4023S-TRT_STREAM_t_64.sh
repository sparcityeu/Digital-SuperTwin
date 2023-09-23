#!/bin/bash
source /opt/intel/oneapi/setvars.sh
cd /tmp/dt_probing/benchmarks/STREAM 
likwid-pin -q -c N:0-63 ./stream_avx2 &>> ../STREAM_RES_user-AS-4023S-TRT/t_64.txt
