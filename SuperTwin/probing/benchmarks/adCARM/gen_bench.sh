#!/bin/bash/ 


cd /tmp/dt_probing/benchmarks/adCARM/


python3 run.py  config/dolap_gen.conf -t 1

python3 run_binded.py  config/dolap_gen.conf -t 2 -b 'likwid-pin|-q|-m|-c|S0:0@S1:22'

python3 run_binded.py  config/dolap_gen.conf -t 4 -b 'likwid-pin|-q|-m|-c|S0:0,1@S1:22,23'

python3 run_binded.py  config/dolap_gen.conf -t 8 -b 'likwid-pin|-q|-m|-c|S0:0,1,2,3@S1:22,23,24,25'

python3 run_binded.py  config/dolap_gen.conf -t 16 -b 'likwid-pin|-q|-m|-c|S0:0,1,2,3,4,5,6,7@S1:22,23,24,25,26,27,28,29'

python3 run_binded.py  config/dolap_gen.conf -t 22 -b 'likwid-pin|-q|-m|-c|S0:0,1,2,3,4,5,6,7,8,9,10@S1:22,23,24,25,26,27,28,29,30,31,32'

python3 run_binded.py  config/dolap_gen.conf -t 32 -b 'likwid-pin|-q|-m|-c|S0:0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15@S1:22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37'

python3 run_binded.py  config/dolap_gen.conf -t 44 -b 'likwid-pin|-q|-m|-c|S0:0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21@S1:22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43'

python3 run_binded.py  config/dolap_gen.conf -t 64 -b 'likwid-pin|-q|-m|-c|S0:0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,44,45,46,47,48,49,50,51,52,53@S1:22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,66,67,68,69,70,71,72,73,74,75'

python3 run_binded.py  config/dolap_gen.conf -t 88 -b 'likwid-pin|-q|-m|-c|S0:0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65@S1:22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,66,67,68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87'

