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
