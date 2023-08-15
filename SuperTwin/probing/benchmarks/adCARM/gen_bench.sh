#!/bin/bash/ 


cd /tmp/dt_probing/benchmarks/adCARM/


python3 run.py  config/carmer7_gen.conf -t 1 --isa avx2 --inst fma --vendor intel -v 3

python3 run.py  config/carmer7_gen.conf -t 2 --isa avx2 --inst fma --vendor intel -v 3

python3 run.py  config/carmer7_gen.conf -t 4 --isa avx2 --inst fma --vendor intel -v 3

python3 run.py  config/carmer7_gen.conf -t 6 --isa avx2 --inst fma --vendor intel -v 3

python3 run.py  config/carmer7_gen.conf -t 8 --isa avx2 --inst fma --vendor intel -v 3

python3 run.py  config/carmer7_gen.conf -t 12 --isa avx2 --inst fma --vendor intel -v 3

