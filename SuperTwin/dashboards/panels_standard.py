def ret_ts_panel(y, title):
    ts = {
        "id": 2,
        "gridPos": {
            "h": 9,
            "w": 19,
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
            "w": 5,
            "x": 19,
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

    return gp

def grafana_layout_2(fig):

    fig.update_layout({
        #"legend": {
        #    "orientation": "h",
        #    "x": 0,
        #    "y": 1.3
        #},
        "margin": {
            "b": 0,
            "l": 0,
            "r": 0,
            "t": 0
        },
        "modebar": {
            "orientation": "v"
        },
        "paper_bgcolor": "rgba(0,0,0,0)",
        "plot_bgcolor": "rgba(0,0,0,0)",
        "xaxis": {
            "autorange": False,
            "dtick": 0.30102999566,
            "nticks": 32,
            "rangemode": "tozero",
            "showspikes": False,
            "title": {
                "text": "Arithmetic Intensity"
            },
            "type": "log",
            "range": [
                -1.8194309088656293,
                3.1052677216436475
            ]
        },
        "yaxis": {
            "autorange": False,
            "dtick": 0.30102999566,
            "rangemode": "tozero",
            "showspikes": False,
            "title": {
                "text": "Performance [GFlop/s]"
            },
            "type": "log",
            "range": [
                -1.2040179707535978,
                3.717236972979037
            ]
        }
    })

    return fig

def two_templates_two(data, layout):
    
    template = {
        "id": 42,
        "gridPos": {
            "h": 6,
            "w": 24,
            "x": 0,
            "y": 0
        },
        "type": "ae3e-plotly-panel",
        "title": "Cache Aware Roofline Model",
        "datasource": {
            "type": "simpod-json-datasource",
            "uid": "yjaMegMVk"
        },
        "options": {
            "script": "console.log(data)\n\n\nreturn {};",
            "onclick": "console.log(data)\nwindow.updateVariables({query:{'var-project':'test'}, partial: true})",
            "config": {
                "displayModeBar": False,
                "locale": "en"
            },
            "data": data,
            "layout": layout
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
                "datasource": {
                    "type": "simpod-json-datasource",
                    "uid": "yjaMegMVk"
                },
                "metrics": [
                    {
                        "id": "1",
                        "type": "count"
                    }
                ],
                "payload": "",
                "query": "",
                "refId": "A",
                "target": "system_ip",
                "timeField": "@timestamp"
            }
        ],
        "transparent": True
    }

    return template
