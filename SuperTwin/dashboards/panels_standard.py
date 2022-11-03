def ret_ts_panel(y, title):
    ts = {
        "id": 2,
        "gridPos": {
            "h": 9,
            "w": 16,
            "x": 0,
            "y": y
        },
        "type": "timeseries",
        "title": title,
        "datasource": {
            "type": "influxdb",
            "uid": "54U16937k"
        },
        "fieldConfig": {
            "defaults": {
                "custom": {
                    "drawStyle": "line",
                    "lineInterpolation": "linear",
                    "barAlignment": 0,
                    "lineWidth": 2,
                    "fillOpacity": 20,
                    "gradientMode": "hue",
                    "spanNulls": True,
                    "showPoints": "never",
                    "pointSize": 5,
                    "stacking": {
                        "mode": "none",
                        "group": "A"
                    },
                    "axisPlacement": "auto",
                    "axisLabel": "",
                    "axisColorMode": "text",
                    "scaleDistribution": {
                        "type": "linear"
                    },
                    "axisCenteredZero": False,
                    "hideFrom": {
                        "tooltip": False,
                        "viz": False,
                        "legend": False
                    },
                    "thresholdsStyle": {
                        "mode": "off"
                    },
                    "lineStyle": {
                        "fill": "solid"
                    }
                },
                "color": {
                    "mode": "palette-classic"
                },
                "mappings": [],
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
                }
            },
            "overrides": []
        },
        "options": {
            "tooltip": {
                "mode": "single",
                "sort": "none"
            },
            "legend": {
                "showLegend": True,
                "displayMode": "list",
                "placement": "bottom",
                "calcs": []
            }
        },
        "targets": [],
        "transparent": True
    }

    return ts

def ret_query(alias, measurement, field, tag):
    query = {
                "alias": alias,
                "datasource": {
                    "type": "influxdb",
                    "uid": "54U16937k"
                },
                "groupBy": [
                    {
                        "params": [
                            "1s"
                        ],
                        "type": "time"
                    },
                    {
                        "params": [
                            "null"
                        ],
                        "type": "fill"
                    }
                ],
                "measurement": measurement,
                "orderByTime": "ASC",
                "policy": "default",
                "refId": "A",
                "resultFormat": "time_series",
                "select": [
                    [
                        {
                            "params": [
                                field
                            ],
                            "type": "field"
                        },
                        {
                            "params": [],
                            "type": "mean"
                        }
                    ]
                ],
                "tags": [
                    {
                        "key": "tag",
                        "operator": "=",
                        "value": tag
                    }
                ]
            }
    return query

def ret_gauge_panel(title, y):

    gp = {
        "id": 3,
        "gridPos": {
            "h": 9,
            "w": 8,
            "x": 16,
            "y": y
        },
        "type": "gauge",
        "title": title,
        "datasource": {
            "type": "influxdb",
            "uid": "54U16937k"
        },
        "pluginVersion": "9.2.2",
        "fieldConfig": {
            "defaults": {
                "mappings": [],
                "thresholds": {
                    "mode": "percentage",
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
                "color": {
                    "mode": "thresholds"
                },
                "unit": "none"
            },
            "overrides": []
        },
        "options": {
            "reduceOptions": {
                "values": False,
                "calcs": [
                    "mean"
                ],
                "fields": ""
            },
            "orientation": "auto",
            "showThresholdLabels": False,
            "showThresholdMarkers": True
        },
        "targets": [],
        "transparent": True
    }
    
