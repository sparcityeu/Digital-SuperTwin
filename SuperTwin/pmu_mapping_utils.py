#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 10 13:29:41 2023
@author: rt7
"""

import copy
import re

_DEFAULT_GENERIC_PMU_EVENTS = []
_COMMON_PMU_DICT = {
    "pmu_name": {
        "generic_pmu_event_name": [
            "specific_pmu_event",  ## sub pmu event name
            "*",  ## operator
            "specific_pmu_event_2",  ## sub pmu event name 2
        ]
    }
}

_initialized = False


def _fill_default_pmu_event_names():
    """All generic pmu event names (our convention)"""

    _DEFAULT_GENERIC_PMU_EVENTS.append("RAPL_ENERGY_PKG")
    _DEFAULT_GENERIC_PMU_EVENTS.append("FP_RETIRED")
    _DEFAULT_GENERIC_PMU_EVENTS.append("FP_DISPATCH_FAULTS_ANY")
    _DEFAULT_GENERIC_PMU_EVENTS.append("RETIRED_INSTRUCTIONS")
    _DEFAULT_GENERIC_PMU_EVENTS.append("RETIRED_BRANCH_TAKEN")
    _DEFAULT_GENERIC_PMU_EVENTS.append("RETIRED_BRANCH_TAKEN_MISPREDICTED")
    _DEFAULT_GENERIC_PMU_EVENTS.append("RETIRED_BRANCH_MISPREDICTED")
    _DEFAULT_GENERIC_PMU_EVENTS.append("L1_CACHE_MISS")
    _DEFAULT_GENERIC_PMU_EVENTS.append("L1_CACHE_HIT")
    _DEFAULT_GENERIC_PMU_EVENTS.append("L2_CACHE_MISS")
    _DEFAULT_GENERIC_PMU_EVENTS.append("L2_CACHE_HIT")
    _DEFAULT_GENERIC_PMU_EVENTS.append("L3_CACHE_MISS")
    _DEFAULT_GENERIC_PMU_EVENTS.append("L3_CACHE_HIT")


def _fill_common_pmu_dict__intel_common():
    """
    Events that all Intel processors have.
    """
    key = "ix86arch"
    _COMMON_PMU_DICT[key] = {}
    _COMMON_PMU_DICT[key]["RETIRED_INSTRUCTIONS"] = ["INSTRUCTIONS_RETIRED"]
    _COMMON_PMU_DICT[key]["RETIRED_BRANCH_INSTRUCTIONS"] = [
        "BRANCH_INSTRUCTIONS_RETIRED"
    ]


def _fill_common_pmu_dict__intel_icl():
    pass


def _fill_common_pmu_dict__amd64_common():
    """
    Events that all AMD processors have.
    """

    key = "amd64_common"
    _COMMON_PMU_DICT[key] = {}
    _COMMON_PMU_DICT[key]["RETIRED_INSTRUCTIONS"] = ["RETIRED_INSTRUCTIONS"]
    _COMMON_PMU_DICT[key]["RETIRED_BRANCH_INSTRUCTIONS"] = [
        "RETIRED_BRANCH_INSTRUCTIONS"
    ]
    _COMMON_PMU_DICT[key]["RAPL_ENERGY_PKG"] = ["RAPL_ENERGY_PKG"]

    ## OTHER COMMON EVENTS GOES HERE


def _fill_common_pmu_dict__amd64_fam17h_zen2():
    """
    Events that only zen2 processors have
    """
    key = "amd64_fam17h_zen2"
    _COMMON_PMU_DICT[key] = copy.deepcopy(_COMMON_PMU_DICT["amd64_common"])
    _COMMON_PMU_DICT[key]["L1_CACHE_MISS"] = ["AMD64_FAM17H_L1_MISS_EVENT"]
    _COMMON_PMU_DICT[key]["L1_CACHE_HIT"] = ["AMD64_FAM17H_L1_HIT_EVENT"]


def _fill_common_pmu_dict__amd64_fam19h_zen3():
    """
    Events that only zen3 processors have
    """
    key = "amd64_fam19h_zen3"
    _COMMON_PMU_DICT[key] = copy.deepcopy(_COMMON_PMU_DICT["amd64_common"])
    _COMMON_PMU_DICT[key]["L1_CACHE_MISS"] = ["AMD64_FAM19H_L1_MISS_EVENT"]
    _COMMON_PMU_DICT[key]["L1_CACHE_HIT"] = ["AMD64_FAM19H_L1_HIT_EVENT"]


def initialize():
    global _initialized
    if not _initialized:
        _fill_default_pmu_event_names()

        ## AMD init.
        _fill_common_pmu_dict__amd64_common()
        _fill_common_pmu_dict__amd64_fam17h_zen2()
        _fill_common_pmu_dict__amd64_fam19h_zen3()

        ## Intel init.
        _fill_common_pmu_dict__intel_common()
        _fill_common_pmu_dict__intel_icl()

        _initialized = True


def add_configuration(file_name):
    fd = open(file_name, "r")
    lines = fd.readlines()
    fd.close()

    pmu_name = None
    for line in lines:
        line = re.sub(r"\s", "", line)
        if len(line) == 0:
            continue
        if line.startswith("["):
            pmu_line = line.replace("[", "").replace("]", "")
            pmu_name = ""
            pmu_conf = ""
            if ":" in pmu_line:
                pmu_name = pmu_line.split(":")[0]
                pmu_conf = pmu_line.split(":")[1]
            else:
                pmu_name = pmu_line

            if (
                "override" in pmu_conf
                or pmu_name not in _COMMON_PMU_DICT.keys()
            ):
                _COMMON_PMU_DICT[pmu_name] = {}

        else:
            if pmu_name == "":
                raise RuntimeError(
                    "File format is erronous!!" + help_conf_file()
                )
            else:
                line = line.split(":")
                common_event_name = line[0]
                common_event_formula = re.split(r"(\+|\-|\*|/)", line[1])
                if common_event_name not in _DEFAULT_GENERIC_PMU_EVENTS:
                    _DEFAULT_GENERIC_PMU_EVENTS.append(common_event_name)
                _COMMON_PMU_DICT[pmu_name][
                    common_event_name
                ] = common_event_formula


def get(pmu_name, pmu_generic_event):
    if not _initialized:
        raise RuntimeError(
            "Module not initialized. Please call initialize() before using get()."
        )
    return copy.deepcopy(_COMMON_PMU_DICT[pmu_name][pmu_generic_event])


def help_conf_file():
    return """Follow the structure below
[pmu_name] : <(add | override)>
<generic_event_name1> : <specific_pmu_event_1>
<generic_event_name2> : <specific_pmu_event_1> <OP> <specific_pmu_event_2>
(<OP>: + || - || * || / )
([pmu_name] : override) -> deletes all default pmu events defined with this pmu_name
([pmu_name] : add) -> adds new pmu generic events with formula, if previously defined it overrides the formula
"""


initialize()
add_configuration("amd64_fam15_pmu_emapping.txt")
