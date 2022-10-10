#!/bin/bash 


source /opt/intel/oneapi/setvars.sh 
make 

KMP_AFFINITY=granularity=fine,compact,1,0 

