#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 22 12:47:42 2023

@author: rt7
"""
import uuid

_id = None
_table_xloc = None
_table_yloc = None
_table_wloc = None
_table_hloc = None

_table_total_xloc = None
_table_total_yloc = None
_table_total_wloc = None
_table_total_hloc = None

_initialized = False

flops = "($A+$B+$C+$D+$E+$F+$G+$H+0.000001)"
total_memory_instr = "(0.000001+($I+$J))"
single_precision_instr_ratio = "4 * ($A+$B+$C+$D+0.000001)/($A+$B+$C+$D+$E+$F+$G+$H+0.000001)"
double_precision_instr_ratio = "8 * ($E+$F+$G+$H+0.000001)/($A+$B+$C+$D+$E+$F+$G+$H+0.000001)"

ai = flops + "/" + "(" + total_memory_instr + "*" + "(" + \
    single_precision_instr_ratio + " + " + double_precision_instr_ratio + ")" + ")"

live_carm_pmu_mappings = {
    # ZEN2
    'RETIRED_SSE_AVX_OPERATIONS:SP_MULT_ADD_FLOPS': 'A',
    'RETIRED_SSE_AVX_OPERATIONS:SP_ADD_SUB_FLOPS': 'B',
    'RETIRED_SSE_AVX_OPERATIONS:SP_MULT_FLOPS': 'C',
    'RETIRED_SSE_AVX_OPERATIONS:SP_DIV_FLOPS': 'D',
    'RETIRED_SSE_AVX_OPERATIONS:DP_MULT_ADD_FLOPS': 'E',
    'RETIRED_SSE_AVX_OPERATIONS:DP_ADD_SUB_FLOPS': 'F',
    'RETIRED_SSE_AVX_OPERATIONS:DP_MULT_FLOPS': 'G',
    'RETIRED_SSE_AVX_OPERATIONS:DP_DIV_FLOPS': 'H',
    'LS_DISPATCH:LD_DISPATCH': 'I',
    'LS_DISPATCH:STORE_DISPATCH': 'J',
    'amd64_fam17h_zen2': [ai, "($A+$B+$C+$D+$E+$F+$G+$H)/1000000000"],
 

    # INTEL_SKL
    'MEM_INST_RETIRED:ALL_LOADS': 'Z',
    'MEM_INST_RETIRED:ALL_STORES': 'Y',
    'FP_ARITH:SCALAR_SINGLE': 'A',
    'FP_ARITH:SCALAR_DOUBLE': 'B',
    'FP_ARITH:128B_PACKED_SINGLE': 'C',
    'FP_ARITH:128B_PACKED_DOUBLE': 'D',
    'FP_ARITH:256B_PACKED_SINGLE': 'E',
    'FP_ARITH:256B_PACKED_DOUBLE': 'F',
    'FP_ARITH:512B_PACKED_SINGLE': 'G',
    'FP_ARITH:512B_PACKED_DOUBLE': 'H',

    'skl': ["(($A+$B+4*$C+2*$D+8*$E+4*$F+16*$G+8*$H)*($A+$B+$C+$D+$E+$F+$G+$H))/(4*$A*($Z+$Y)+8*$B*($Z+$Y)+16*$C*($Z+$Y)+16*$D*($Z+$Y)+32*$E*($Z+$Y)+32*$F*($Z+$Y)+64*$G*($Z+$Y)+64*$H*($Z+$Y))",
            "($A+$B+4*$C+2*$D+8*$E+4*$F+16*$G+8*$H)/1000000000"
            ],
}


def _init():
    global _id
    global _table_xloc, _table_yloc, _table_wloc, _table_hloc
    global _table_total_xloc, _table_total_yloc, _table_total_wloc, _table_total_hloc

    _id = 100
    _table_xloc = 0
    _table_yloc = 16
    _table_wloc = 14
    _table_hloc = 10

    _table_total_xloc = 14
    _table_total_yloc = 16
    _table_total_wloc = 4
    _table_total_hloc = 10


def _table_increment():
    global _id, _table_yloc

    _id = _id + 1
    _table_yloc = _table_yloc + _table_hloc


def _table_total_increment():
    global _id, _table_total_yloc

    _id = _id + 1
    _table_total_yloc = _table_total_yloc + _table_total_hloc


def dashboard_pmu_table(datasource, title, cpu_count, formula):
    global _id, _table_xloc, _table_yloc, _table_wloc, _table_hloc
    global _initialized
    if not _initialized:
        _init()
        _initialized = True

    dash = {
        "id": _id,
        "gridPos": {
            "x": _table_xloc,
            "y": _table_yloc,
            "w": _table_wloc,
            "h": _table_hloc,
        },
        "type": "timeseries",
        "title": title,
        "datasource": {"uid": datasource, "type": "influxdb"},
        "targets": [],
        "options": {
            "tooltip": {"mode": "single", "sort": "none"},
            "legend": {
                "showLegend": True,
                "displayMode": "list",
                "placement": "bottom",
                "calcs": [],
            },
        },
        "fieldConfig": {
            "defaults": {
                "custom": {
                    "drawStyle": "line",
                    "lineInterpolation": "linear",
                    "barAlignment": 0,
                    "lineWidth": 1,
                    "fillOpacity": 0,
                    "gradientMode": "none",
                    "spanNulls": False,
                    "showPoints": "auto",
                    "pointSize": 5,
                    "stacking": {"mode": "none", "group": "A"},
                    "axisPlacement": "auto",
                    "axisLabel": "",
                    "axisColorMode": "text",
                    "scaleDistribution": {"type": "linear"},
                    "axisCenteredZero": False,
                    "hideFrom": {
                        "tooltip": False,
                        "viz": False,
                        "legend": False,
                    },
                    "thresholdsStyle": {"mode": "off"},
                },
                "color": {"mode": "palette-classic"},
                "mappings": [],
                "thresholds": {
                    "mode": "absolute",
                    "steps": [
                        {"value": None, "color": "green"},
                        {"value": 80, "color": "red"},
                    ],
                },
            },
            "overrides": [],
        },
    }

    for cpu in range(cpu_count):
        for event in formula:
            if len(event) == 1:
                continue
            dash["targets"].append(
                {
                    "datasource": {"type": "influxdb", "uid": datasource},
                    "refId": str(uuid.uuid4()),
                    "policy": "default",
                    "resultFormat": "time_series",
                    "orderByTime": "ASC",
                    "tags": [],
                    "groupBy": [
                        {"type": "time", "params": ["1s"]},
                        {"type": "fill", "params": ["null"]},
                    ],
                    "select": [
                        [
                            {
                                "type": "field",
                                "params": ["_cpu" + str(cpu)],
                            },
                            {"type": "mean", "params": []},
                        ]
                    ],
                    "measurement": "perfevent_hwcounters_"
                    + event.replace(":", "_")
                    + "_value",
                    "alias": "cpu_" + str(cpu) + "_" + str(uuid.uuid4())[:4],
                }
            )

    _table_increment()
    return dash


def dashboard_pmu_table_total(datasource, title, cpu_count, formula):
    global _table_total_xloc, _table_total_yloc, _table_total_wloc, _table_total_hloc
    global _initialized
    if not _initialized:
        _init()
        _initialized = True

    dash = {
        "id": _id,
        "gridPos": {
            "x": _table_total_xloc,
            "y": _table_total_yloc,
            "w": _table_total_wloc,
            "h": _table_total_hloc,
        },
        "type": "timeseries",
        "title": title,
        "transformations": [
            {
                "id": "calculateField",
                "options": {
                    "mode": "reduceRow",
                    "reduce": {"reducer": "sum"},
                    "replaceFields": True,
                },
            }
        ],
        "datasource": {"uid": datasource, "type": "influxdb"},
        "targets": [],
        "options": {
            "tooltip": {"mode": "single", "sort": "none"},
            "legend": {
                "showLegend": True,
                "displayMode": "list",
                "placement": "bottom",
                "calcs": [],
            },
        },
        "fieldConfig": {
            "defaults": {
                "custom": {
                    "drawStyle": "line",
                    "lineInterpolation": "linear",
                    "barAlignment": 0,
                    "lineWidth": 1,
                    "fillOpacity": 0,
                    "gradientMode": "none",
                    "spanNulls": False,
                    "showPoints": "auto",
                    "pointSize": 5,
                    "stacking": {"mode": "none", "group": "A"},
                    "axisPlacement": "auto",
                    "axisLabel": "",
                    "axisColorMode": "text",
                    "scaleDistribution": {"type": "linear"},
                    "axisCenteredZero": False,
                    "hideFrom": {
                        "tooltip": False,
                        "viz": False,
                        "legend": False,
                    },
                    "thresholdsStyle": {"mode": "off"},
                },
                "color": {"mode": "palette-classic"},
                "mappings": [],
                "thresholds": {
                    "mode": "absolute",
                    "steps": [
                        {"value": None, "color": "green"},
                        {"value": 80, "color": "red"},
                    ],
                },
            },
            "overrides": [],
        },
    }

    for cpu in range(cpu_count):
        for event in formula:
            if len(event) == 1:
                continue
            dash["targets"].append(
                {
                    "datasource": {"type": "influxdb", "uid": datasource},
                    "refId": str(uuid.uuid4()),
                    "policy": "default",
                    "resultFormat": "time_series",
                    "orderByTime": "ASC",
                    "tags": [],
                    "groupBy": [
                        {"type": "time", "params": ["1s"]},
                        {"type": "fill", "params": ["null"]},
                    ],
                    "select": [
                        [
                            {
                                "type": "field",
                                "params": ["_cpu" + str(cpu)],
                            },
                            {"type": "mean", "params": []},
                        ]
                    ],
                    "measurement": "perfevent_hwcounters_"
                    + event.replace(":", "_")
                    + "_value",
                    "alias": "cpu_" + str(cpu) + "_" + str(uuid.uuid4())[:4],
                }
            )

    _table_total_increment()
    return dash


def dashboard_livecarm_table(pmu_name, datasource, title, cpu_count, formula):
    global _id, _table_xloc, _table_yloc, _table_wloc, _table_hloc
    global _initialized
    if not _initialized:
        _init()
        _initialized = True

    dash = {
        "id": _id,
        "gridPos": {
            "x": _table_xloc,
            "y": _table_yloc,
            "w": _table_wloc + 4,
            "h": _table_hloc,
        },
        "type": "xychart",
        "title": title,
        "transformations": [
            {
                "id": "joinByField",
                "options": {
                    "mode": "outer"
                }
            }
        ],
        "datasource": {"uid": datasource, "type": "influxdb"},
        "targets": [],
        "options": {
            "seriesMapping": "manual",
            "series": [
                {
                    "name": "CARM",
                    "pointColor": {
                        "fixed": "#37872D"
                    },
                    "pointSize": {
                        "fixed": 10,
                        "max": 100,
                        "min": 1
                    },
                    "x": "AI",
                    "y": "Gflops"
                }
            ],
            "tooltip": {"mode": "single", "sort": "none"},
            "legend": {
                "showLegend": True,
                "displayMode": "list",
                "placement": "bottom",
                "calcs": [],
            },

        },

        "pluginVersion": "9.5.2",
        "fieldConfig": {
            "defaults": {
                "custom": {
                    "show": "points",
                    "pointSize": {
                        "fixed": 5
                    },
                    "axisPlacement": "auto",
                    "axisLabel": "",
                    "axisColorMode": "text",
                    "scaleDistribution": {
                        "type": "log",
                        "log": 2
                    },
                    "axisCenteredZero": False,
                    "hideFrom": {
                        "tooltip": False,
                        "viz": False,
                        "legend": False
                    }
                },
                "color": {
                    "mode": "palette-classic"
                },
                "mappings": [

                ],
                "thresholds": {
                    "mode": "absolute",
                    "steps": [
                        {
                            "color": "green",
                            "value": None
                        },
                        {
                            "color": "red",
                            "value": 80
                        }
                    ]
                },
                "min": 0,
                "noValue": "0",
                "unit": "none"
            },
            "overrides": [
                {
                    "matcher": {
                        "id": "byName",
                        "options": "AI"
                    },
                    "properties": [
                        {
                            "id": "noValue",
                            "value": "0"
                        }
                    ]
                }
            ]
        },
    }

    generic_temp1, generic_temp2 = live_carm_pmu_mappings[pmu_name]

    expression_template1 = "0"
    expression_template2 = "0"

    for cpu in range(cpu_count):
        for event in formula:
            if len(event) == 1:
                continue
            dash["targets"].append(
                {
                    "datasource": {"type": "influxdb", "uid": datasource},
                    "refId": ""+live_carm_pmu_mappings[event]+str(cpu),
                    "policy": "default",
                    "resultFormat": "time_series",
                    "orderByTime": "ASC",
                    "tags": [],
                    "groupBy": [
                        {"type": "time", "params": ["1s"]},
                        {"type": "fill", "params": ["null"]},
                    ],
                    "hide": True,
                    "select": [
                        [
                            {
                                "type": "field",
                                "params": ["_cpu" + str(cpu)],
                            },
                            {"type": "mean", "params": []},
                        ]
                    ],
                    "measurement": "perfevent_hwcounters_"
                    + event.replace(":", "_")
                    + "_value",
                    "alias": "cpu_" + str(cpu) + "_" + str(uuid.uuid4())[:4],
                },
            )

        expression_template1 = expression_template1 + \
            "+" + expand_expression(generic_temp1, cpu)
        expression_template2 = expression_template2 + \
            "+" + expand_expression(generic_temp2, cpu)

    dash["targets"].append(
        {
            "datasource": {
                "name": "Expression",
                "type": "__expr__",
                "uid": "__expr__"
            },
            "expression": "("+expression_template1+")",
            "hide": False,
            "refId": "AI",
            "type": "math"
        },
    )

    dash["targets"].append(
        {
            "datasource": {
                "name": "Expression",
                "type": "__expr__",
                "uid": "__expr__"
            },
            "expression": "("+expression_template2+")",
            "hide": False,
            "refId": "Gflops",
            "type": "math"
        }
    )
    _table_increment()
    _table_total_increment()
    return dash


def expand_expression(expression, N):
    expanded_expression = expression.replace("$A", "($A"+str(N)+")")
    expanded_expression = expanded_expression.replace("$B", "($B"+str(N)+")")
    expanded_expression = expanded_expression.replace("$C", "($C"+str(N)+")")
    expanded_expression = expanded_expression.replace("$D", "($D"+str(N)+")")
    expanded_expression = expanded_expression.replace("$E", "($E"+str(N)+")")
    expanded_expression = expanded_expression.replace("$F", "($F"+str(N)+")")
    expanded_expression = expanded_expression.replace("$G", "($G"+str(N)+")")
    expanded_expression = expanded_expression.replace("$H", "($H"+str(N)+")")
    expanded_expression = expanded_expression.replace("$Z", "($Z"+str(N)+")")
    expanded_expression = expanded_expression.replace("$Y", "($Y"+str(N)+")")
    expanded_expression = expanded_expression.replace("$I", "($I"+str(N)+")")
    expanded_expression = expanded_expression.replace("$J", "($J"+str(N)+")")
    return expanded_expression
