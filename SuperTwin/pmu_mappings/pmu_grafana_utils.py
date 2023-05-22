#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 22 12:47:42 2023

@author: rt7
"""
import uuid

_id = None
_xloc = None
_yloc = None
_wloc = None
_hloc = None

_initialized = False


def _init():
    global _id, _xloc, _yloc, _wloc, _hloc
    _id = 100
    _xloc = 0
    _yloc = 16
    _wloc = 18
    _hloc = 10


def _increment():
    global _id, _yloc

    _id = _id + 1
    _yloc = _yloc + _hloc


def dashboard_pmu_unit(datasource, title, cpu_count, formula):
    global _id, _xloc, _yloc, _wloc, _hloc
    global _initialized
    if not _initialized:
        _init()
        _initialized = True

    dash = {
        "id": _id,
        "gridPos": {"x": _xloc, "y": _yloc, "w": _wloc, "h": _hloc},
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

    _increment()
    return dash
