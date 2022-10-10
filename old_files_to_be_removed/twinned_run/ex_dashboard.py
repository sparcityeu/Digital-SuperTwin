

def ret_ex():

    ret = {
        "annotations": {
            "list": [
                {
                    "builtIn": 1,
                    "datasource": "-- Grafana --",
                    "enable": true,
                    "hide": true,
                    "iconColor": "rgba(0, 211, 255, 1)",
                    "name": "Annotations & Alerts",
                    "target": {
                        "limit": 100,
                        "matchAny": false,
                        "tags": [],
                        "type": "dashboard"
                    },
                    "type": "dashboard"
                }
            ]
        },
        "editable": true,
        "fiscalYearStartMonth": 0,
        "gnetId": null,
        "graphTooltip": 0,
        "id": null,
        "links": [],
        "liveNow": false,
        "panels": [
            {
                "datasource": "InfluxDB-LOCAL",
                "fieldConfig": {
                    "defaults": {
                        "color": {
                            "mode": "palette-classic"
                        },
                        "custom": {
                            "axisLabel": "",
                            "axisPlacement": "auto",
                            "barAlignment": 0,
                            "drawStyle": "line",
                            "fillOpacity": 0,
                            "gradientMode": "none",
                            "hideFrom": {
                                "legend": false,
                                "tooltip": false,
                                "viz": false
                            },
                            "lineInterpolation": "linear",
                            "lineWidth": 1,
                            "pointSize": 5,
                            "scaleDistribution": {
                                "type": "linear"
                            },
                            "showPoints": "auto",
                            "spanNulls": false,
                            "stacking": {
                                "group": "A",
                                "mode": "none"
                            },
                            "thresholdsStyle": {
                                "mode": "off"
                            }
                        },
                        "mappings": [],
                        "thresholds": {
                            "mode": "absolute",
                            "steps": [
                                {
                                    "color": "green",
                                    "value": null
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
                "gridPos": {
                    "h": 6,
                    "w": 24,
                    "x": 0,
                    "y": 0
                },
                "id": 2,
                "options": {
                    "legend": {
                        "calcs": [],
                        "displayMode": "list",
                        "placement": "bottom"
                    },
                    "tooltip": {
                        "mode": "single"
                    }
                },
                "targets": [
                    {
                        "alias": "",
                        "bucketAggs": [
                            {
                                "field": "@timestamp",
                                "id": "2",
                                "settings": {
                                    "interval": "auto"
                                },
                                "type": "date_histogram"
                            }
                        ],
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
                        "measurement": "disk_dev_read",
                        "metrics": [
                            {
                                "id": "1",
                                "type": "count"
                            }
                        ],
                        "orderByTime": "ASC",
                        "policy": "default",
                        "query": "",
                        "refId": "A",
                        "resultFormat": "time_series",
                        "select": [
                            [
                                {
                                    "params": [
                                        "_nvme0n1"
                                    ],
                                    "type": "field"
                                },
                                {
                                    "params": [],
                                    "type": "last"
                                }
                            ]
                        ],
                        "tags": [],
                        "timeField": "@timestamp"
                    }
                ],
                "title": "disk dev read",
                "transparent": true,
                "type": "timeseries"
            }
        ],
        "schemaVersion": 31,
        "style": "dark",
        "tags": [],
        "templating": {
            "list": []
        },
        "time": {
            "from": "now-6h",
            "to": "now"
        },
        "timepicker": {},
        "timezone": "",
        "title": "API dashboard",
        "uid": null,
        "version": 0
    }

    return ret
