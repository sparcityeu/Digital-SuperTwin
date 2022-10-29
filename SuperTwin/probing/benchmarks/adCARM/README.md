# adCARM

<p>
  <a href="https://doi.org/10.1109/L-CA.2013.6" alt="Publication">
    <img src="https://img.shields.io/badge/DOI-10.1109/L--CA.2013.6-blue.svg"/></a>
    
</p>

<p>
  <a href="https://doi.org/10.1016/j.future.2020.01.044" alt="Publication">
    <img src="https://img.shields.io/badge/DOI-10.1016/j.future.2020.01.044-blue.svg"/></a>
    
</p>

This tool performs the micro-benchmarking necessary to constuct the Cache-Aware Roofline Model (CARM) for floating-point operations on Intel CPUs. It supports different instruction set extensions (AVX512, AVX, SSE and Scalar), different data precisions (double- and single-precision), different floating point instructions (fused multiply and add, addition, multiplication and division). The micro-benchmarks can be performed for any number of threads. The tool provides as output a vizualization of CARM, as well as the measurements obtained for the different memory levels and selected FP instruction.

## Requirements
- gcc (>= 4.9 for AVX512 tests and only tested with gcc 9.3)
- python (only tested with python 3.8.8)
    - matplolib (only tested with 3.3.4)

## How to use

The first step is to create a configuration file for the system to test under the **config** folder. This configuration file must include four fields:
- identifier of the system
- nominal frequency of the CPU (in Ghz)
- L1 size per core (in KiB)
- L2 size per core (in KiB)
- Total L3 size (in KiB)

After the creating the configuration file, the tool can executed as:

```
python run.py --test <test> --inst <fp_inst> --num_ops <num_ops> --isa <isa> --precision <data_precision> --ld_st_ratio <ld_st_ratio> --dram_bytes <dram_bytes> is the size of the array used for the DRAM benchmark in KiB; --threads <num_threads> [--only_ld] [--interleaved] <path_config_file>
```

where
 - --test <test> is the test to be performed (roofline, fp, mem);
 - --inst <fp_inst> is the floating point instruction (fma, add, mul, div);
 - --num_ops <num_ops> is the number of FP operations used for the FP benchmark;
 - --isa <isa> is the instruction set extension (avx512, avx, sse, scalar);
 - --precision <data_precision> is the precision of the data (dp, sp);
 - --ld_st_ratio <ld_st_ratio> is the number of loads per store involed in the memory benchmarks;
 - --dram_bytes <dram_bytes> is the size of the array used for the DRAM benchmark in KiB;
 - --threads <num_threads> is the number of threads used for the test;
 - [--only_ld] indicates that the memory benchmarks will just contain loads (<ld_st_ratio> is ignored);
 - [--interleaved] indicates if the cores belong to interleaved numa domains (e.g. core 0 -> node 0, core 1 -> node 1, core 2 -> node 0, etc). Used for thread binding;
 - <path_config_file> is the path for configuration file of the system.


A simple run can be executed with the command

```
python run.py <path_config_file>
```

which by default runs the micro-benchmarks necessary to obtain CARM data, for AVX512 instructions and double-precision variables. The FP instruction used is the FMA (32768 operations) and the memory benchmarks contain 2 loads per each store, with the DRAM test using an array with size 512MiB. 


For additional information regarding the input arguments, run the command:

```
python run.py -h
```

## In papers and reports, please refer to this tool as follows

A. Ilic, F. Pratas and L. Sousa, "Cache-aware Roofline model: Upgrading the loft," in IEEE Computer Architecture Letters, vol. 13, no. 1, pp. 21-24, 21 Jan.-June 2014, doi: 10.1109/L-CA.2013.6.

Diogo Marques, Aleksandar Ilic, Zakhar A. Matveev, and Leonel Sousa. "Application-driven cache-aware roofline model." Future Generation Computer Systems 107 (2020): 257-273.