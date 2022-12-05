#!/bin/bash 


make -C /tmp/dt_probing/benchmarks/hpcg/ arch=GCC_OMP 
cd /tmp/dt_probing/benchmarks/hpcg/bin/ 
export OMP_NUM_THREADS=1 
likwid-pin -c N:0 ./xhpcg 
export OMP_NUM_THREADS=2 
likwid-pin -c N:0-1 ./xhpcg 
export OMP_NUM_THREADS=4 
likwid-pin -c N:0-3 ./xhpcg 
export OMP_NUM_THREADS=8 
likwid-pin -c N:0-7 ./xhpcg 
