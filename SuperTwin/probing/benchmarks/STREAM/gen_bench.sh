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

export OMP_NUM_THREADS=16 
likwid-pin -c N:0-15 /tmp/dt_probing/benchmarks/STREAM/./stream.omp.AVX512.80M.20x.icc &>> /tmp/dt_probing/benchmarks/STREAM/STREAM_res/t16.txt 

export OMP_NUM_THREADS=22 
likwid-pin -c N:0-21 /tmp/dt_probing/benchmarks/STREAM/./stream.omp.AVX512.80M.20x.icc &>> /tmp/dt_probing/benchmarks/STREAM/STREAM_res/t22.txt 

export OMP_NUM_THREADS=32 
likwid-pin -c N:0-31 /tmp/dt_probing/benchmarks/STREAM/./stream.omp.AVX512.80M.20x.icc &>> /tmp/dt_probing/benchmarks/STREAM/STREAM_res/t32.txt 

export OMP_NUM_THREADS=44 
likwid-pin -c N:0-43 /tmp/dt_probing/benchmarks/STREAM/./stream.omp.AVX512.80M.20x.icc &>> /tmp/dt_probing/benchmarks/STREAM/STREAM_res/t44.txt 

export OMP_NUM_THREADS=64 
likwid-pin -c N:0-63 /tmp/dt_probing/benchmarks/STREAM/./stream.omp.AVX512.80M.20x.icc &>> /tmp/dt_probing/benchmarks/STREAM/STREAM_res/t64.txt 

export OMP_NUM_THREADS=88 
likwid-pin -c N:0-87 /tmp/dt_probing/benchmarks/STREAM/./stream.omp.AVX512.80M.20x.icc &>> /tmp/dt_probing/benchmarks/STREAM/STREAM_res/t88.txt 

