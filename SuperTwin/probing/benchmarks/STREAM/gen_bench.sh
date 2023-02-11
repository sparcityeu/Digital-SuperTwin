#!/bin/bash 


source /opt/intel/oneapi/setvars.sh 
make -C /tmp/dt_probing/benchmarks/STREAM/ 

KMP_AFFINITY=granularity=fine,compact,1,0 

export OMP_NUM_THREADS=1 
likwid-pin -c N:0 /tmp/dt_probing/benchmarks/STREAM/./stream.omp.AVX512.80M.20x.icc &>> /tmp/dt_probing/benchmarks/STREAM/STREAM_res/t1.txt 

export OMP_NUM_THREADS=2 
likwid-pin -c N:0-1 /tmp/dt_probing/benchmarks/STREAM/./stream.omp.AVX512.80M.20x.icc &>> /tmp/dt_probing/benchmarks/STREAM/STREAM_res/t2.txt 

export OMP_NUM_THREADS=4 
likwid-pin -c N:0-3 /tmp/dt_probing/benchmarks/STREAM/./stream.omp.AVX512.80M.20x.icc &>> /tmp/dt_probing/benchmarks/STREAM/STREAM_res/t4.txt 

export OMP_NUM_THREADS=8 
likwid-pin -c N:0-7 /tmp/dt_probing/benchmarks/STREAM/./stream.omp.AVX512.80M.20x.icc &>> /tmp/dt_probing/benchmarks/STREAM/STREAM_res/t8.txt 

