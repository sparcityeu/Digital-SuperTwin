#!/bin/bash 


source /opt/intel/oneapi/setvars.sh 
make -C /tmp/dt_probing/benchmarks/STREAM stream_avx2

mkdir /tmp/dt_probing/benchmarks/STREAM_RES_carmer33
