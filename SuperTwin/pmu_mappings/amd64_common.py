#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 16 14:30:48 2023

@author: rt7
"""


def _fill_common_pmu_dict__amd64_common(_COMMON_PMU_DICT):
    """
    Events that all AMD processors have.
    """

    key = "amd64_common"
    alias = key
    _COMMON_PMU_DICT[key] = {}
    _COMMON_PMU_DICT[key]["alias"] = alias
    _COMMON_PMU_DICT[key]["RETIRED_INSTRUCTIONS"] = ["RETIRED_INSTRUCTIONS"]
    _COMMON_PMU_DICT[key]["RETIRED_BRANCH_INSTRUCTIONS"] = [
        "RETIRED_BRANCH_INSTRUCTIONS"
    ]

    ## OTHER COMMON EVENTS GOES HERE


def _fill_common_pmu_dict__amd64_rapl(_COMMON_PMU_DICT):
    key = "amd64_rapl"
    alias = key
    _COMMON_PMU_DICT[key] = {}
    _COMMON_PMU_DICT[key]["alias"] = alias
    _COMMON_PMU_DICT[key]["RAPL_ENERGY_PKG"] = ["RAPL_ENERGY_PKG"]


def initialize(_DEFAULT_GENERIC_PMU_EVENTS, _COMMON_PMU_DICT):
    _fill_common_pmu_dict__amd64_rapl(_COMMON_PMU_DICT)
    _fill_common_pmu_dict__amd64_common(_COMMON_PMU_DICT)
