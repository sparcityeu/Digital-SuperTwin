def stat_panel(datasource, _id, h, w, x, y, color_scheme, title):
    panel = {
        "id": _id,
        "gridPos": {
            "h": h,
            "w": w,
            "x": x,
            "y": y
        },
        "type": "stat",
        "title": title,
        "datasource": {
            "type": "influxdb",
            "uid": datasource ##Make it connected
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
                    "mode": color_scheme
                }
            },
            "overrides": []
        },
        "options": {
            "reduceOptions": {
                "values": False,
                "calcs": [
                    "lastNotNull"
                ],
                "fields": ""
            },
            "orientation": "auto", ##or "vertical"
            "textMode": "auto",
            "colorMode": "background",
            "graphMode": "area",
            "justifyMode": "auto"
        },
        "targets": [],
        "transparent": True
    }

    return panel


def stat_query(datasource, alias, measurement, param):

    query = {
        "alias": alias,
        "datasource": {
            "type": "influxdb",
            "uid": datasource
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
                        param
                    ],
                    "type": "field"
                },
                {
                    "params": [],
                    "type": "mean"
                }
            ]
        ],
        "tags": []
    }

    return query

def name_panel(datasource, _id, name):

    name = {
        "id": _id,
        "gridPos": {
            "h": 5,
            "w": 4,
            "x": 0,
            "y": 0
        },
        "type": "stat",
        "title": "Hostname",
        "datasource": {
            "type": "influxdb",
            "uid": datasource
    },
        "pluginVersion": "9.2.2",
        "fieldConfig": {
            "defaults": {
                "mappings": [
                    {
                        "options": {
                            "0": {
                                "index": 0,
                                "text": name
                            }
          },
                    "type": "value"
        }
            ],
                "thresholds": {
                    "mode": "absolute",
        "steps": [
            {
                "color": "text",
                "value": None
            }
        ]
                },
                "color": {
                    "mode": "thresholds"
                }
            },
            "overrides": []
        },
        "options": {
            "reduceOptions": {
                "values": False,
                "calcs": [
                    "lastNotNull"
                ],
                "fields": ""
            },
            "orientation": "auto",
            "textMode": "auto",
            "colorMode": "background",
            "graphMode": "none",
            "justifyMode": "auto"
        },
        "targets": [
            {
                "datasource": {
                    "type": "influxdb",
                    "uid": datasource
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
                "measurement": "network_all_in_bytes",
                "orderByTime": "ASC",
                "policy": "default",
                "refId": "A",
                "resultFormat": "time_series",
                "select": [
                    [
                        {
                            "params": [
                                "value"
                            ],
                            "type": "field"
                        },
                        {
                            "params": [],
                            "type": "mean"
                        },
                        {
                            "params": [
                                "*0"
                            ],
                            "type": "math"
                        }
                    ]
                ],
                "tags": []
            }
        ],
        "transparent": True
    }

    return name

def clock_panel(datasource, _id, h, w, x, y, color_scheme, title):

    cp = {
        "id": _id,
        "gridPos": {
            "h": h,
            "w": w,
            "x": x,
            "y": y
        },
        "type": "heatmap",
        "title": title,
        "transformations": [],
        "datasource": {
            "type": "influxdb",
            "uid": datasource
        },
        "pluginVersion": "9.2.2",
        "fieldConfig": {
            "defaults": {
                "custom": {
                    "scaleDistribution": {
                        "type": "linear"
                    },
                    "hideFrom": {
                        "tooltip": False,
                        "viz": False,
                        "legend": False
                    }
                }
            },
            "overrides": []
        },
        "options": {
            "calculate": False,
            "yAxis": {
                "axisPlacement": "left",
                "reverse": False
            },
            "rowsFrame": {
                "layout": "auto"
            },
            "color": {
                "mode": "scheme",
                "fill": "green",
                "scale": "exponential",
                "exponent": 0.5,
                "scheme": color_scheme,
                "steps": 28,
                "reverse": False
            },
            "cellGap": 1,
        "filterValues": {
            "le": 1e-9
        },
            "tooltip": {
                "show": True,
                "yHistogram": False
            },
            "legend": {
                "show": True
            },
            "exemplars": {
                "color": "rgba(255,0,255,0.7)"
        }
        },
        "targets": [],
        "tags": [],
        "transparent": True
    }
    
    return cp
    
def clock_query(datasource, alias, measurement, param):

    cq = { "alias": alias,
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
              "type": "influxdb",
              "uid": datasource
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
                          param
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
                  "value": "_monitor"
              }
          ],
        "timeField": "@timestamp"
    }
    
    return cq


def small_single_timeseries(datasource, _id, h, w, x, y, title):

    sst = {
        "id": _id,
        "gridPos": {
            "h": h,
            "w": w,
            "x": x,
            "y": y
        },
        "type": "timeseries",
        "title": title,
        "datasource": {
            "type": "influxdb",
            "uid": datasource
        },
        "pluginVersion": "9.2.2",
        "fieldConfig": {
            "defaults": {
                "custom": {
                    "drawStyle": "line",
                    "lineInterpolation": "linear",
                    "barAlignment": 0,
                    "lineWidth": 2,
                    "fillOpacity": 20,
                    "gradientMode": "hue",
                    "spanNulls": False,
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
                    }
                },
                "color": {
                    "mode": "fixed"
                },
                "mappings": [],
                "thresholds": {
                    "mode": "percentage",
                    "steps": [
                        {
                            "color": "text",
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

    return sst

def small_single_query(datasource, alias, measurement):

    query = {
      "alias": alias,
      "datasource": {
        "type": "influxdb",
        "uid": datasource
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
                "value"
            ],
            "type": "field"
          },
          {
            "params": [],
            "type": "mean"
          }
        ]
      ],
      "tags": []
    }
        
    return query


def all_network_panel(datasource, _id, h, w, x, y):

    np = {
        "id": _id,
        "gridPos": {
            "h": h,
            "w": w,
            "x": x,
            "y": y
        },
        "type": "timeseries",
        "title": "Network",
        "datasource": {
            "type": "influxdb",
            "uid": datasource
        },
        "pluginVersion": "9.2.2",
        "fieldConfig": {
        "defaults": {
            "custom": {
                "drawStyle": "line",
                "lineInterpolation": "stepAfter",
                "barAlignment": 0,
                "lineWidth": 2,
                "fillOpacity": 20,
                "gradientMode": "hue",
                "spanNulls": False,
                "showPoints": "auto",
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
        "targets": [
            {
                "alias": "Network In",
                "datasource": {
                    "type": "influxdb",
                    "uid": datasource
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
                "measurement": "network_all_in_bytes",
                "orderByTime": "ASC",
                "policy": "default",
                "refId": "A",
                "resultFormat": "time_series",
                "select": [
                    [
                        {
                            "params": [
                                "value"
                            ],
                            "type": "field"
                        },
                        {
                            "params": [],
                            "type": "mean"
                        }
                    ]
                ],
                "tags": []
            },
            {
                "alias": "Network out",
                "datasource": {
                    "type": "influxdb",
                    "uid": datasource
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
                "hide": False,
                "measurement": "network_all_out_bytes",
                "orderByTime": "ASC",
                "policy": "default",
                "refId": "B",
                "resultFormat": "time_series",
                "select": [
                    [
                        {
                            "params": [
                                "value"
                            ],
                            "type": "field"
                        },
                        {
                            "params": [],
                            "type": "mean"
                        }
                    ]
                ],
                "tags": []
            }
        ],
        "transparent": True
    }

    return np


def disk_panel(datasource, _id, h, w, x, y, title):

    dp = {
        "id": _id,
        "gridPos": {
            "h": h,
            "w": w,
            "x": x,
            "y": y
        },
        "type": "timeseries",
        "title": title,
        "datasource": {
            "type": "influxdb",
            "uid": datasource
        },
        "pluginVersion": "9.2.2",
        "fieldConfig": {
            "defaults": {
                "custom": {
                    "drawStyle": "line",
                    "lineInterpolation": "linear",
                    "barAlignment": 0,
                    "lineWidth": 2,
                    "fillOpacity": 20,
                    "gradientMode": "hue",
                    "spanNulls": False,
                    "showPoints": "auto",
                    "pointSize": 5,
                    "stacking": {
                        "mode": "normal",
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

    return dp


def general_panel(datasource, _id, h, w, x, y, title):

    gp = {
        "id": _id,
        "gridPos": {
            "h": h,
            "w": w,
            "x": x,
            "y": y
        },
        "type": "timeseries",
        "title": title,
        "datasource": {
            "type": "influxdb",
            "uid": datasource
        },
        "pluginVersion": "9.2.2",
        "fieldConfig": {
            "defaults": {
                "custom": {
                    "drawStyle": "line",
                    "lineInterpolation": "linear",
                    "barAlignment": 0,
                    "lineWidth": 2,
                    "fillOpacity": 20,
                    "gradientMode": "hue",
                    "spanNulls": False,
                    "showPoints": "auto",
                    "pointSize": 5,
                    "stacking": {
                        "mode": "normal",
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

    return gp
