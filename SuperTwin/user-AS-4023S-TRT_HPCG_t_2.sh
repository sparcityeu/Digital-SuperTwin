#!/bin/bash
source /opt/intel/oneapi/setvars.sh 
cd /tmp/dt_probing/benchmarks/mkl_hpcg 
likwid-pin -q -c N:0-1 ./xhpcg_avx2
