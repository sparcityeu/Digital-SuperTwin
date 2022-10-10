#!/bin/bash

##TO DO: generate this file

source /opt/intel/oneapi/setvars.sh
make

#export KMP_AFFINITY=compact
KMP_AFFINITY=granularity=fine,compact,1,0

export OMP_NUM_THREADS=1
likwid-pin -c N:0 ./stream.omp.AVX512.80M.20x.icc &>> t1.txt

export OMP_NUM_THREADS=2
likwid-pin -c N:0-1 ./stream.omp.AVX512.80M.20x.icc &>> t2.txt

export OMP_NUM_THREADS=4
likwid-pin -c N:0-3 ./stream.omp.AVX512.80M.20x.icc &>> t4.txt

export OMP_NUM_THREADS=8
likwid-pin -c N:0-7 ./stream.omp.AVX512.80M.20x.icc &>> t8.txt

export OMP_NUM_THREADS=16
likwid-pin -c N:0-15 ./stream.omp.AVX512.80M.20x.icc &>> t16.txt

export OMP_NUM_THREADS=22
likwid-pin -c N:0-21 ./stream.omp.AVX512.80M.20x.icc &>> t22.txt

export OMP_NUM_THREADS=32
likwid-pin -c N:0-31 ./stream.omp.AVX512.80M.20x.icc &>> t32.txt

export OMP_NUM_THREADS=44
likwid-pin -c N:0-43 ./stream.omp.AVX512.80M.20x.icc &>> t44.txt

export OMP_NUM_THREADS=64
likwid-pin -c N:0-63 ./stream.omp.AVX512.80M.20x.icc &>> t64.txt

export OMP_NUM_THREADS=88
likwid-pin -c N:0-87 ./stream.omp.AVX512.80M.20x.icc &>> t88.txt
