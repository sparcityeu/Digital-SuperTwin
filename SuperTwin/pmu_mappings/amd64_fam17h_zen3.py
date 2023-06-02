#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 16 14:35:19 2023

@author: rt7
"""

import copy


def _fill_common_pmu_dict__amd64_fam19h_zen3(_COMMON_PMU_DICT):
    """
    Events that only zen3 processors have
    """
    key = "amd64_fam19h_zen3"
    alias = "amd64_fam19h"
    _COMMON_PMU_DICT[key] = copy.deepcopy(_COMMON_PMU_DICT["amd64_common"])
    _COMMON_PMU_DICT[key]["alias"] = alias
    _COMMON_PMU_DICT[key]["L1_CACHE_MISS"] = ["AMD64_FAM19H_L1_MISS_EVENT"]
    _COMMON_PMU_DICT[key]["L1_CACHE_HIT"] = ["AMD64_FAM19H_L1_HIT_EVENT"]


def initialize(_DEFAULT_GENERIC_PMU_EVENTS, _COMMON_PMU_DICT):
    _fill_common_pmu_dict__amd64_fam19h_zen3(_COMMON_PMU_DICT)
