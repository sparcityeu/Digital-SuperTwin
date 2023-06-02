#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 16 14:33:28 2023

@author: rt7
"""

import copy


def _fill_common_pmu_dict__intel_common(_COMMON_PMU_DICT):
    """
    Events that all Intel processors have.
    """
    key = "intel_common"
    _COMMON_PMU_DICT[key] = {}
    _COMMON_PMU_DICT[key]["RETIRED_INSTRUCTIONS"] = ["INSTRUCTIONS_RETIRED"]
    _COMMON_PMU_DICT[key]["RETIRED_BRANCH_INSTRUCTIONS"] = [
        "BRANCH_INSTRUCTIONS_RETIRED"
    ]


def _fill_common_pmu_dict__intel_icl(_COMMON_PMU_DICT):
    key = "icl"
    alias = "icl"
    _COMMON_PMU_DICT[key] = copy.deepcopy(_COMMON_PMU_DICT["intel_common"])
    _COMMON_PMU_DICT[key]["alias"] = alias


def initialize(_DEFAULT_GENERIC_PMU_EVENTS, _COMMON_PMU_DICT):
    _fill_common_pmu_dict__intel_common(_COMMON_PMU_DICT)
    _fill_common_pmu_dict__intel_icl(_COMMON_PMU_DICT)
