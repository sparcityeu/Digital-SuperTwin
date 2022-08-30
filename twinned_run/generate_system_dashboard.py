import os
import sys
import json
import requests

from grafanalib.core import Dashboard
from grafanalib._gen import DashboardEncoder

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


def add_query(_pd, measurement, fields):

    next_refid = 65

    for field in fields:

        _qd = {} ##query dictionary
        _qd["alias"] = field.strip("_")
        _qd["measurement"] = measurement
        _qd["orderByTime"] = "ASC"
        _qd["policy"] = "default"
        _qd["query"] = ""
        _qd["resultFormat"] = "time_series"
        _qd["hide"] = False
        _qd["tags"] = []
        _qd["timeField"] = "@timestamp"
        
        _qd["refId"] = str(chr(next_refid))
        next_refid += 1

        _qd["bucketAggs"] = [{"field": "@timestamp", "id": "2",
                              "settings": {"interval": "auto"},
                              "type": "date_histogram"}]

        _qd["datasource"] = {}
        _qd["datasource"]["type"] = "influxdb"
        _qd["datasource"]["uid"] = _pd["datasource"]["uid"] ##Same with panel, guess why?

        _qd["groupBy"] = [{"params": ["1s"], "type": "time"}, {"params": ["null"], "type": "fill"}]

        _qd["metrics"] = [{"id": "1", "type": "count"}]

        _qd["select"] = [[{"params": [field], "type": "field"}, {"params": [], "type": "last"}]]
        

        next_refid = 65
        _pd["targets"].append(_qd)

    return _pd


def add_panel(measurement, fields):

    _pd = {} ##Panel dictionary
    _pd["title"] = measurement ##param: panel title
    _pd["type"] = "timeseries"
    _pd["transparent"] = True
    _pd["description"] = ""
    _pd["id"] = next_panel_id()
    
    _pd["datasource"] = {}
    _pd["datasource"]["type"] = "influxdb"
    _pd["datasource"]["uid"] = "54U16937k" ##param: influxdb id, need to get it from 'twin'


    _pd["fieldConfig"] = {}
    _pd["fieldConfig"]["defaults"] = {}
    _pd["fieldConfig"]["defaults"]["color"] = {}
    _pd["fieldConfig"]["defaults"]["color"]["mode"] = "palette-classic"
    
    _pd["fieldConfig"]["defaults"]["custom"] = {}
    _pd["fieldConfig"]["defaults"]["custom"]["axisCenteredZero"] = False
    _pd["fieldConfig"]["defaults"]["custom"]["axisColorMode"] = "text"
    _pd["fieldConfig"]["defaults"]["custom"]["axisLabel"] = ""
    _pd["fieldConfig"]["defaults"]["custom"]["axisPlacement"] = "auto"
    _pd["fieldConfig"]["defaults"]["custom"]["barAlignment"] = 0
    _pd["fieldConfig"]["defaults"]["custom"]["drawStyle"] = "line"
    _pd["fieldConfig"]["defaults"]["custom"]["fillOpacity"] = 0
    _pd["fieldConfig"]["defaults"]["custom"]["gradientMode"] = "none"

    _pd["fieldConfig"]["defaults"]["custom"]["hidefrom"] = {}
    _pd["fieldConfig"]["defaults"]["custom"]["hidefrom"]["legend"] = False
    _pd["fieldConfig"]["defaults"]["custom"]["hidefrom"]["tooltip"] = False
    _pd["fieldConfig"]["defaults"]["custom"]["hidefrom"]["viz"] = False

    _pd["fieldConfig"]["defaults"]["custom"]["lineInterpolation"] = "linear"
    _pd["fieldConfig"]["defaults"]["custom"]["lineWidth"] = 1
    _pd["fieldConfig"]["defaults"]["custom"]["pointSize"] = 5

    _pd["fieldConfig"]["defaults"]["custom"]["scaleDistribution"] = {}
    _pd["fieldConfig"]["defaults"]["custom"]["scaleDistribution"]["type"] = "linear"

    _pd["fieldConfig"]["defaults"]["custom"]["showPoints"] = "auto"
    _pd["fieldConfig"]["defaults"]["custom"]["spanNulls"] = False

    _pd["fieldConfig"]["defaults"]["custom"]["stacking"] = {}
    _pd["fieldConfig"]["defaults"]["custom"]["stacking"]["group"] = "A"
    _pd["fieldConfig"]["defaults"]["custom"]["stacking"]["mode"] = "none"

    _pd["fieldConfig"]["defaults"]["custom"]["thresholdStyle"] = {}
    _pd["fieldConfig"]["defaults"]["custom"]["thresholdStyle"]["mode"] = "off"

    _pd["fieldConfig"]["defaults"]["mappings"] = []

    _pd["fieldConfig"]["defaults"]["thresholds"] = {}
    _pd["fieldConfig"]["defaults"]["thresholds"]["mode"] = "absolute"
    
    _pd["fieldConfig"]["defaults"]["thresholds"]["steps"] = []
    _sd0 = {"color": "green", "value": None}
    _sd1 = {"color": "red", "value": 80}
    _pd["fieldConfig"]["defaults"]["thresholds"]["steps"].append(_sd0)
    _pd["fieldConfig"]["defaults"]["thresholds"]["steps"].append(_sd1)

    _pd["fieldConfig"]["overrides"] = []

    _pd["gridPos"] = {"h": 7, "w": 24, "x": 0, "y": next_y()}
    _pd["targets"] = []
    
    
    #fields = ["_sda"]
    print("_pd, before:", _pd)
    _pd = add_query(_pd, measurement, fields)
    print("###############################")
    print("_pd, after:", _pd)
    
    return _pd

##NEED TO REWRITE PANEL THING
##NEED TO REWRITE SELECT-QUERY PART - PERHAPS IT WAS ELASTIC SEARCH, DATE HISTOGRAM THING
    
    
def main():
    
    server = grafana_server
    api_key = grafana_api_key
    
    empty_dash = template_dict()
    empty_dash["panels"] = []

    measurement = "disk_dev_write" #param: measurement
    measurement2 = "disk_dev_read" #param: measurement
    fields = ["_sda", "_nvme0n1", "_nvme1n1"]
    
    empty_dash["panels"].append(add_panel("disk_dev_write", fields))
    empty_dash["panels"].append(add_panel("disk_dev_write_merge", fields))
    empty_dash["panels"].append(add_panel("disk_dev_read", fields))
    empty_dash["panels"].append(add_panel("disk_dev_read_merge", fields))
    
    

    #json_dash = json.dumps(empty_dash)
    #print(type(json_dash))

    json_dash_obj = get_dashboard_json(empty_dash, overwrite = True)
    print(json_dash_obj)
    upload_to_grafana(json_dash_obj, grafana_server, grafana_api_key)
    

if __name__ == "__main__":

    main()
