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
export OMP_NUM_THREADS=16 
likwid-pin -c N:0-15 ./xhpcg 
export OMP_NUM_THREADS=22 
likwid-pin -c N:0-21 ./xhpcg 
export OMP_NUM_THREADS=32 
likwid-pin -c N:0-31 ./xhpcg 
export OMP_NUM_THREADS=44 
likwid-pin -c N:0-43 ./xhpcg 
export OMP_NUM_THREADS=64 
likwid-pin -c N:0-63 ./xhpcg 
export OMP_NUM_THREADS=88 
likwid-pin -c N:0-87 ./xhpcg 
