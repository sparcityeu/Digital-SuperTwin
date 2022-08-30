import os
import sys
import json
import requests

from grafanalib.core import Dashboard
from grafanalib._gen import DashboardEncoder


observation_table_panel = {
  "id": 2,
  "gridPos": {
    "h": 8,
    "w": 24,
    "x": 0,
    "y": 18
  },
  "type": "table",
  "title": "Observations",
  "datasource": {
    "type": "hamedkarbasi93-nodegraphapi-datasource",
    "uid": "Hif9Y8W4k"
  },
  "pluginVersion": "9.1.0-beta1",
  "fieldConfig": {
    "defaults": {
      "custom": {
        "align": "auto",
        "displayMode": "auto",
        "inspect": False
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
      },
      "color": {
        "mode": "thresholds"
      }
    },
    "overrides": [
      {
        "matcher": {
          "id": "byName",
          "options": "Nodes detail__role"
        },
        "properties": [
          {
            "id": "displayName",
            "value": "command"
          }
        ]
      },
      {
        "matcher": {
          "id": "byName",
          "options": "Nodes title"
        },
        "properties": [
          {
            "id": "displayName",
            "value": "# of metrics"
          }
        ]
      },
      {
        "matcher": {
          "id": "byName",
          "options": "Nodes mainStat"
        },
        "properties": [
          {
            "id": "displayName",
            "value": "report"
          }
        ]
      }
    ]
  },
  "options": {
    "showHeader": True,
    "footer": {
      "show": False,
      "reducer": [
        "sum"
      ],
      "fields": ""
    },
    "sortBy": [],
    "frameIndex": 0
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
        "type": "hamedkarbasi93-nodegraphapi-datasource",
        "uid": "Hif9Y8W4k"
      },
      "metrics": [
        {
          "id": "1",
          "type": "count"
        }
      ],
      "query": "",
      "refId": "A",
      "timeField": "@timestamp"
    }
  ],
    "transparent":True
}

text_panel_1 = {
  "id": 4,
  "gridPos": {
    "h": 3,
    "w": 8,
    "x": 0,
    "y": 0
  },
  "type": "text",
  "title": "Hostname",
  "datasource": {
    "type": "elasticsearch",
    "uid": "TSVKafhnk"
  },
  "pluginVersion": "9.1.0-beta1",
  "options": {
    "mode": "markdown",
    "content": "<center><b><font size=\"+8\">DOLAP</font></b></center>" ##This will change
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
        "type": "elasticsearch",
        "uid": "TSVKafhnk"
      },
      "metrics": [
        {
          "id": "1",
          "type": "count"
        }
      ],
      "query": "",
      "refId": "A",
      "timeField": "@timestamp"
    }
  ],
  "transparent": True
}


text_panel_2 = {
  "id": 5,
  "gridPos": {
    "h": 3,
    "w": 8,
    "x": 8,
    "y": 0
  },
  "type": "text",
  "title": "IP",
  "datasource": {
    "type": "elasticsearch",
    "uid": "TSVKafhnk"
  },
  "pluginVersion": "9.1.0-beta1",
  "options": {
    "mode": "markdown",
    "content": "<center><b><font size=\"+8\">10.36.54.195</font></b></center>" ##This will change
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
        "type": "elasticsearch",
        "uid": "TSVKafhnk"
      },
      "metrics": [
        {
          "id": "1",
          "type": "count"
        }
      ],
      "query": "",
      "refId": "A",
      "timeField": "@timestamp"
    }
  ],
  "transparent": True
}

text_panel_3 = {
  "id": 6,
  "gridPos": {
    "h": 3,
    "w": 8,
    "x": 16,
    "y": 0
  },
  "type": "text",
  "title": "Number of Metrics",
  "datasource": {
    "type": "elasticsearch",
    "uid": "TSVKafhnk"
  },
  "pluginVersion": "9.1.0-beta1",
  "options": {
    "mode": "markdown",
    "content": "<center><b><font size=\"+8\">46</font></b></center>" #This will change
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
        "type": "elasticsearch",
        "uid": "TSVKafhnk"
      },
      "metrics": [
        {
          "id": "1",
          "type": "count"
        }
      ],
      "query": "",
      "refId": "A",
      "timeField": "@timestamp"
    }
  ],
  "transparent": True
}

system_view_panel = {
  "id": 7,
  "gridPos": {
    "h": 15,
    "w": 24,
    "x": 0,
    "y": 3
  },
  "type": "nodeGraph",
  "title": "System",
  "datasource": {
    "type": "hamedkarbasi93-nodegraphapi-datasource",
    "uid": "hb8KdEWVz"
  },
  "links": [
    {
      "targetBlank": True,
      "title": "Google",
      "url": "google.com"
    },
    {
      "targetBlank": True,
      "title": "Youtube",
      "url": "youtube.com"
    }
  ],
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
        "type": "hamedkarbasi93-nodegraphapi-datasource",
        "uid": "Hif9Y8W4k"
      },
      "metrics": [
        {
          "id": "1",
          "type": "count"
        }
      ],
      "query": "",
      "refId": "A",
      "timeField": "@timestamp"
    }
  ],
  "transparent": True
}


##These should be in a config file
grafana_api_key = "eyJrIjoiM1JDaHR3Y1VENzFtSXZsNTh0Mzh0ZFpGRWhCdENvTDAiLCJuIjoiZHQwIiwiaWQiOjF9"
grafana_server = "localhost:3000"

glob_y = -7
glob_panel_id = 1

def next_y():
    global glob_y
    glob_y += 7
    
    return glob_y

def next_panel_id():
    global glob_panel_id
    glob_panel_id += 1

    return glob_panel_id


def upload_to_grafana(json, server, api_key, verify=True):
    
    '''
    upload_to_grafana tries to upload dashboard to grafana and prints response    
    :param json - dashboard json generated by grafanalib
    :param server - grafana server name
    :param api_key - grafana api key with read and write privileges
    '''
    
    headers = {'Authorization': f"Bearer {api_key}", 'Content-Type': 'application/json'}
    r = requests.post(f"http://{server}/api/dashboards/db", data=json, headers=headers, verify=verify)
    # TODO: add error handling
    # TODO: return and read uid and url, add it to observation digital twin
    print(f"{r.status_code} - {r.content}")


def get_dashboard_json(dashboard, overwrite=False, message="Updated by grafanalib"):
    '''
    get_dashboard_json generates JSON from grafanalib Dashboard object
    :param dashboard - Dashboard() created via grafanalib
    '''

    # grafanalib generates json which need to pack to "dashboard" root element
    return json.dumps(
        {
            "dashboard": dashboard,
            #"dashboard": dashboard.to_json_data(),
            "overwrite": overwrite,
            "message": message
        }, sort_keys=True, indent=2, cls=DashboardEncoder)


def template_dict():

    _template = {}

    _template["id"] = None ##to_get: id
    _template["timepicker"] = {}
    _template["timezone"] = ""
    _template["title"] = "TEMPLATE" ##param: title
    _template["uid"] = None ##to_get: uid
    _template["version"] = 1
    _template["weekStart"] = ""
    _template["schemaVersion"] = 37
    _template["style"] = "dark"
    _template["tags"] = []
    _template["editable"] = True
    _template["graphTooltip"] = 0
    _template["links"] = []
    _template["fiscalYearStartMonth"] = 0
    _template["liveNow"] = False
    #_template["refresh"] = "1s" ##Not exist in example
    
    _template["templating"] = {}
    _template["templating"]["list"] = []

    _template["time"] = {}
    _template["time"]["from"] = "now-5m" ##param: time-from
    _template["time"]["to"] = "now"      ##param: time-to

    _template["annotations"] = {}
    _template["annotations"]["list"] = []
    lzd = {} ##list zero dict, default list
    lzd["builtIn"] = 1
    lzd["enable"] = True
    lzd["hide"] = True
    lzd["iconColor"] = "rgba(0, 211, 255, 1)"
    lzd["name"] = "Annotations & Alerts"
    lzd["type"] = "dashboard"
    
    lzd["datasource"] = {}
    lzd["datasource"]["type"] = "grafana"
    lzd["datasource"]["uid"] = "-- Grafana --"

    lzd["target"] = {}
    lzd["target"]["limit"] = 100
    lzd["target"]["matchAny"] = False
    lzd["target"]["tags"] = []
    lzd["target"]["type"] = "dashboard"
    _template["annotations"]["list"].append(lzd)

    _template["panels"] = []

    return _template


def main(comp_dashes):
    
    server = grafana_server
    api_key = grafana_api_key
    
    empty_dash = template_dict()
    empty_dash["panels"].append(text_panel_1)
    empty_dash["panels"].append(text_panel_2)
    empty_dash["panels"].append(text_panel_3)
    empty_dash["panels"].append(system_view_panel)
    empty_dash["panels"].append(observation_table_panel)
    
    #measurement = "disk_dev_write" #param: measurement
    #measurement2 = "disk_dev_read" #param: measurement
    #fields = ["_sda", "_nvme0n1", "_nvme1n1"]
    
    #empty_dash["panels"].append(add_panel("disk_dev_write", fields))
    #empty_dash["panels"].append(add_panel("disk_dev_write_merge", fields))
    #empty_dash["panels"].append(add_panel("disk_dev_read", fields))
    #empty_dash["panels"].append(add_panel("disk_dev_read_merge", fields))
    
    

    #json_dash = json.dumps(empty_dash)
    #print(type(json_dash))

    json_dash_obj = get_dashboard_json(empty_dash, overwrite = True)
    print(json_dash_obj)
    upload_to_grafana(json_dash_obj, grafana_server, grafana_api_key)
    

if __name__ == "__main__":

    main()
