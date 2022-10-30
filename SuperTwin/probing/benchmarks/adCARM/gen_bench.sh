#!/bin/bash 


cd /tmp/dt_probing/benchmarks/adCARM/


python3 run.py  dolap_gen.conf -t 1 

python3 run.py  dolap_gen.conf -t 2 

python3 run.py  dolap_gen.conf -t 4 

python3 run.py  dolap_gen.conf -t 8 

python3 run.py  dolap_gen.conf -t 16 

python3 run.py  dolap_gen.conf -t 22 

python3 run.py  dolap_gen.conf -t 32 

python3 run.py  dolap_gen.conf -t 32 --interleaved  

python3 run_binded.py  dolap_gen.conf -t 32 -b 'likwid-pin|-q|-c|S0:0-31' 

python3 run_binded.py  dolap_gen.conf -t 32 -b 'likwid-pin|-q|-c|S0:0-31' --interleaved 

python3 run.py  dolap_gen.conf -t 44 

python3 run.py  dolap_gen.conf -t 44 --interleaved  

python3 run_binded.py  dolap_gen.conf -t 44 -b 'likwid-pin|-q|-c|S0:0-43' 

python3 run_binded.py  dolap_gen.conf -t 44 -b 'likwid-pin|-q|-c|S0:0-43' --interleaved 

python3 run.py  dolap_gen.conf -t 64 

python3 run_binded.py  dolap_gen.conf -t 64 -b 'likwid-pin|-q|-c|S0:0-31@S1:0-31' 

python3 run.py  dolap_gen.conf -t 88 

python3 run_binded.py  dolap_gen.conf -t 88 -b 'likwid-pin|-q|-c|S0:0-43@S1:0-43' 

