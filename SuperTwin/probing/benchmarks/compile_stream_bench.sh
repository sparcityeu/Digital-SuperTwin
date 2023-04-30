#!/bin/bash 


source /opt/intel/oneapi/setvars.sh 
make -C /tmp/dt_probing/benchmarks/STREAM stream_avx512

mkdir /tmp/dt_probing/benchmarks/STREAM_RES_rt7-laptop-vivo
