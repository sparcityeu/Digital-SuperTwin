#!/bin/bash/ 


cd /tmp/dt_probing/benchmarks/adCARM/


python3 run.py  config/carmerOsman_intel_gen.conf -t 1 --isa avx512 --inst fma --vendor intel

python3 run_binded.py  config/carmerOsman_intel_gen.conf -t 2 --isa avx512 --inst fma --vendor intel -b 'likwid-pin|-q|-c|N:0-1'

python3 run_binded.py  config/carmerOsman_intel_gen.conf -t 4 --isa avx512 --inst fma --vendor intel -b 'likwid-pin|-q|-c|N:0-3'

python3 run_binded.py  config/carmerOsman_intel_gen.conf -t 8 --isa avx512 --inst fma --vendor intel -b 'likwid-pin|-q|-c|N:0-7'

python3 run_binded.py  config/carmerOsman_intel_gen.conf -t 16 --isa avx512 --inst fma --vendor intel -b 'likwid-pin|-q|-c|N:0-15'

python3 run_binded.py  config/carmerOsman_intel_gen.conf -t 28 --isa avx512 --inst fma --vendor intel -b 'likwid-pin|-q|-c|N:0-27'

python3 run_binded.py  config/carmerOsman_intel_gen.conf -t 32 --isa avx512 --inst fma --vendor intel -b 'likwid-pin|-q|-c|N:0-31'

python3 run_binded.py  config/carmerOsman_intel_gen.conf -t 56 --isa avx512 --inst fma --vendor intel -b 'likwid-pin|-q|-c|N:0-55'

