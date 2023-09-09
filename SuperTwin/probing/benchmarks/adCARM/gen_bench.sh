#!/bin/bash/ 


cd /tmp/dt_probing/benchmarks/adCARM/


python3 run_binded.py  config/dolap_gen.conf -t 16 --isa avx512 --inst fma --vendor intel -b 'likwid-pin|-q|-c|N:0-15'

