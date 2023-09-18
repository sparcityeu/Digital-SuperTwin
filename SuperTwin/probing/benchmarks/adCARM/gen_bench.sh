#!/bin/bash/ 


cd /tmp/dt_probing/benchmarks/adCARM/


python3 run.py  config/carmer33_gen.conf -t 1 --isa avx2 --inst fma 

python3 run.py  config/carmer33_gen.conf -t 2 --isa avx2 --inst fma 

python3 run.py  config/carmer33_gen.conf -t 4 --isa avx2 --inst fma 

python3 run.py  config/carmer33_gen.conf -t 6 --isa avx2 --inst fma 

python3 run.py  config/carmer33_gen.conf -t 8 --isa avx2 --inst fma 

python3 run.py  config/carmer33_gen.conf -t 12 --isa avx2 --inst fma 

