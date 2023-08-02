#!/bin/bash

PASSWD="$1"
export LD_LIBRARY_PATH="$(echo $HOME)/intel/oneapi/mkl/2023.2.0/lib/intel64/:$LD_LIBRARY_PATH"

export LD_LIBRARY_PATH="$(echo $HOME)/intel/oneapi/mkl/2023.2.0/lib/intel64/:$LD_LIBRARY_PATH"

export LD_LIBRARY_PATH="$(echo $HOME)/intel/oneapi/compiler/2023.2.0/linux/compiler/lib/intel64_lin/:$LD_LIBRARY_PATH"
 
echo "$PASSWD" | sudo -S ldconfig
