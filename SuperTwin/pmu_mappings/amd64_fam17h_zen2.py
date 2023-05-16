#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 16 14:35:19 2023

@author: rt7
"""

import copy

"""

    _DEFAULT_GENERIC_PMU_EVENTS.append("FP_DISPATCH_FAULTS_ANY")
    _DEFAULT_GENERIC_PMU_EVENTS.append("L1_CACHE_DATA_MISS")
    _DEFAULT_GENERIC_PMU_EVENTS.append("L1_CACHE_DATA_HIT")
    _DEFAULT_GENERIC_PMU_EVENTS.append("L3_CACHE_DATA_MISS")
    _DEFAULT_GENERIC_PMU_EVENTS.append("L3_CACHE_DATA_HIT")

    
"""


def _fill_common_pmu_dict__amd64_fam17h_zen2(_COMMON_PMU_DICT):
    """
    Events that only zen2 processors have
    """
    key = "amd64_fam17h_zen2"
    _COMMON_PMU_DICT[key] = copy.deepcopy(_COMMON_PMU_DICT["amd64_common"])
    _COMMON_PMU_DICT[key]["RETIRED_BRANCH_MISPREDICTED"] = [
        "RETIRED_BRANCH_INSTRUCTIONS_MISPREDICTED"
    ]
    _COMMON_PMU_DICT[key]["RETIRED_BRANCH_TAKEN_MISPREDICTED"] = [
        "RETIRED_TAKEN_BRANCH_INSTRUCTIONS_MISPREDICTED"
    ]
    _COMMON_PMU_DICT[key]["RETIRED_BRANCH_TAKEN"] = [
        "RETIRED_TAKEN_BRANCH_INSTRUCTIONS"
    ]

    _COMMON_PMU_DICT[key]["FP_ADDITION_SUBTRACTION_RETIRED"] = [
        "RETIRED_SSE_AVX_FLOPS:ADD_SUB_FLOPS",  # single precision
        "+",
        "RETIRED_SSE_AVX_FLOPS:MAC_FLOPS",  # double precision
    ]
    _COMMON_PMU_DICT[key]["FP_MUL_RETIRED"] = [
        "RETIRED_SSE_AVX_FLOPS:MULT_FLOPS"
    ]
    _COMMON_PMU_DICT[key]["FP_DIV_RETIRED"] = [
        "RETIRED_SSE_AVX_FLOPS:DIV_FLOPS"
    ]
    _COMMON_PMU_DICT[key]["FP_RETIRED"] = [
        "RETIRED_SSE_AVX_FLOPS:ADD_SUB_FLOPS",  ## sinlge precision
        "+",
        "RETIRED_SSE_AVX_FLOPS:MULT_FLOPS",  ## mul flops
        "+",
        "RETIRED_SSE_AVX_FLOPS:DIV_FLOPS",  ## div flops
        "+",
        "RETIRED_SSE_AVX_FLOPS:MAC_FLOPS",  ## double precision
    ]  ## counts all floating-point operations retired,
    ## including additions, subtractions, multiplications, divisions, and other arithmetic or mathematical operations.

    _COMMON_PMU_DICT[key]["L2_CACHE_DATA_HIT"] = [
        "CORE_TO_L2_CACHEABLE_REQUEST_ACCESS_STATUS:LS_RD_BLK_L_HIT_X",  # Number of data cache reads hitting in the L2
    ]
    _COMMON_PMU_DICT[key]["L2_CACHE_DATA_MISS"] = [
        "CORE_TO_L2_CACHEABLE_REQUEST_ACCESS_STATUS:LS_RD_BLK_C",  # Number of data cache fill requests missing in the L2 (all types).. meaning both read/write
    ]

    _COMMON_PMU_DICT[key]["TOTAL_DATA_CACHE_MISS"] = [
        "DATA_CACHE_REFILLS_FROM_SYSTEM:LS_MABRESP_LCL_DRAM",  # "Demand Data Cache fills by data source. Fill from DRAM (home node local).."
        "+",
        "DATA_CACHE_REFILLS_FROM_SYSTEM:LS_MABRESP_RMT_DRAM",  # "Demand Data Cache fills by data source. Fill from DRAM (home node remote).."
    ]

    _COMMON_PMU_DICT[key]["L1_CACHE_DATA_HIT"] = ["AMD64_FAM17H_L1_MISS_EVENT"]


def initialize(_DEFAULT_GENERIC_PMU_EVENTS, _COMMON_PMU_DICT):
    _fill_common_pmu_dict__amd64_fam17h_zen2(_COMMON_PMU_DICT)
