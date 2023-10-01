#!/bin/bash/ 


cd /tmp/dt_probing/benchmarks/adCARM/


python3 run.py  config/carmerOsman_zen2_gen.conf -t 1 --isa avx2 --inst fma --vendor intel

python3 run_binded.py  config/carmerOsman_zen2_gen.conf -t 2 -b 'likwid-pin|-q|-c|N:0-1'

python3 run_binded.py  config/carmerOsman_zen2_gen.conf -t 4 -b 'likwid-pin|-q|-c|N:0-3'

python3 run_binded.py  config/carmerOsman_zen2_gen.conf -t 8 -b 'likwid-pin|-q|-c|N:0-7'

python3 run_binded.py  config/carmerOsman_zen2_gen.conf -t 16 -b 'likwid-pin|-q|-c|N:0-15'

python3 run_binded.py  config/carmerOsman_zen2_gen.conf -t 24 -b 'likwid-pin|-q|-c|N:0-23'

python3 run_binded.py  config/carmerOsman_zen2_gen.conf -t 32 -b 'likwid-pin|-q|-c|N:0-31'

python3 run_binded.py  config/carmerOsman_zen2_gen.conf -t 48 -b 'likwid-pin|-q|-c|N:0-47'

python3 run_binded.py  config/carmerOsman_zen2_gen.conf -t 64 -b 'likwid-pin|-q|-c|N:0-63'

python3 run_binded.py  config/carmerOsman_zen2_gen.conf -t 96 -b 'likwid-pin|-q|-c|N:0-95'

