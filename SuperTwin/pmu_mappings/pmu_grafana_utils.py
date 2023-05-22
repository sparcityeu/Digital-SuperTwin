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

_gauge_xloc = None
_gauge_yloc = None
_gauge_wloc = None
_gauge_hloc = None

_initialized = False


def _init():
    global _id
    global _table_xloc, _table_yloc, _table_wloc, _table_hloc
    global _gauge_xloc, _gauge_yloc, _gauge_wloc, _gauge_hloc

    _id = 100
    _table_xloc = 0
    _table_yloc = 16
    _table_wloc = 14
    _table_hloc = 10

    _gauge_xloc = 14
    _gauge_yloc = 16
    _gauge_wloc = 4
    _gauge_hloc = 10


def _table_increment():
    global _id, _table_yloc

    _id = _id + 1
    _table_yloc = _table_yloc + _table_hloc


def _gauge_increment():
    global _id, _gauge_yloc

    _id = _id + 1
    _gauge_yloc = _gauge_yloc + _gauge_hloc


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


def dashboard_pmu_gauge(datasource, title, cpu_count, formula):
    global _gauge_xloc, _gauge_yloc, _gauge_wloc, _gauge_hloc
    global _initialized
    if not _initialized:
        _init()
        _initialized = True

    dash = {
        "id": _id,
        "gridPos": {
            "h": _gauge_hloc,
            "w": _gauge_wloc,
            "x": _gauge_xloc,
            "y": _gauge_yloc,
        },
        "type": "gauge",
        "title": title,
        "datasource": {"uid": datasource, "type": "influxdb"},
        "pluginVersion": "9.3.6",
        "fieldConfig": {
            "defaults": {
                "mappings": [],
                "thresholds": {
                    "mode": "absolute",
                    "steps": [
                        {"color": "green", "value": None},
                        {"color": "red", "value": 80},
                    ],
                },
                "color": {"mode": "thresholds"},
            },
            "overrides": [],
        },
        "options": {
            "reduceOptions": {
                "values": False,
                "calcs": ["lastNotNull"],
                "fields": "",
            },
            "orientation": "auto",
            "showThresholdLabels": False,
            "showThresholdMarkers": True,
        },
        "targets": [
            {
                "datasource": {"type": "influxdb", "uid": datasource},
                "refId": str(uuid.uuid4()),
                "policy": "default",
                "resultFormat": "time_series",
                "orderByTime": "ASC",
                "tags": [],
                "query": "",
                "rawQuery": True,
                "resultFormat": "time_series",
            }
        ],
    }

    dash["targets"][0][
        "query"
    ] = 'SELECT sum("_cpu_all") AS "sum_value" FROM ('
    for event in formula:
        if len(event) == 1:
            continue
        for cpu in range(cpu_count):
            dash["targets"][0]["query"] = dash["targets"][0]["query"] + (
                "SELECT '_cpu"
                + str(cpu)
                + "'"
                + ' as "_cpu_all"'
                + " FROM 'perfevent_hwcounters_"
                + event.replace(":", "_")
                + "_value' WHERE $timeFilter "
            )
            if event != formula[-1]:
                dash["targets"][0]["query"] = (
                    dash["targets"][0]["query"] + " union "
                )

    dash["targets"][0]["query"] = (
        dash["targets"][0]["query"] + ") GROUP BY time(1s);"
    )

    _gauge_increment()
    return dash
