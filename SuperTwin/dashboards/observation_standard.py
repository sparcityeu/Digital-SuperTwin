import os
import sys
sys.path.append("../")
import utils
import json
import requests
import uuid

from grafanalib.core import Dashboard
from grafanalib._gen import DashboardEncoder

import panels_standard as ps

from bson.objectid import ObjectId
from bson.json_util import dumps
from bson.json_util import loads

from influxdb import InfluxDBClient
import influx_help
import time

import plotly.graph_objects as go
import plotly.io as io


##These should be in a config file
grafana_api_key = "eyJrIjoiM1JDaHR3Y1VENzFtSXZsNTh0Mzh0ZFpGRWhCdENvTDAiLCJuIjoiZHQwIiwiaWQiOjF9"
grafana_server = "localhost:3000"

y = -2

def next_y():
    global y
    y += 9
    return y

def current_y():
    global y
    return y

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
    return dict(r.json())

def get_dashboard_json(dashboard, overwrite, message="Updated by grafanalib"):
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

def template_dict(observation_id):

    _template = {}

    _template["id"] = None ##to_get: id
    #_template["id"] = next_dash_id() ##to_get: id
    _template["timepicker"] = {}
    _template["timezone"] = ""
    _template["title"] = "PMUs-" + observation_id ##param: title
    #_template["title"] = str(uuid.uuid4()) ##param: title
    _template["uid"] = None ##to_get: uid
    #_template["uid"] = str(uuid.uuid4()) ##to_get: uid
    _template["version"] = 0
    _template["weekStart"] = ""
    _template["schemaVersion"] = 37
    _template["style"] = "dark"
    _template["tags"] = []
    _template["editable"] = True
    _template["graphTooltip"] = 0
    _template["links"] = []
    _template["fiscalYearStartMonth"] = 0
    _template["liveNow"] = False
    _template["refresh"] = "5s" ##Not exist in example
    
    _template["templating"] = {}
    _template["templating"]["list"] = []

    _template["time"] = {}
    _template["time"]["from"] = "now-5m" ##param: time-from
    _template["time"]["to"] = "now"      ##param: time-to

    #_template["time"]["from"] = str(time_from) ##param: time-from
    #_template["time"]["to"] = str(time_to)     ##param: time-to
    

    _template["annotations"] = {}
    _template["annotations"]["list"] = []
    lzd = {} ##list zero dict, default list
    lzd["builtIn"] = 1
    lzd["enable"] = True
    lzd["hide"] = True
    lzd["iconColor"] = "rgba(0, 211, 255, 1)"
    #lzd["name"] = "Annotations & Alerts"
    lzd["name"] = str(uuid.uuid4())
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

def find_from_likwid_pin(affinity):

    fields = affinity.split(" ")
    affinity = fields[2]

    involved = {}
    socket_threads = affinity.split("@")
    
    for st in socket_threads:
        socket = "socket" + str(int(st.split(":")[0].strip("S"))) ##likwid-pin to DTD id socket
        threads = st.split(":")[1]

        cpus = []
        _from = int(threads.split("-")[0]) ##likwid-pin to DTD id core
        try:
            _to = int(threads.split("-")[1])
            for i in range(_from, _to):
                cpus.append("thread" + str(i))
        except:                 ##Single threaded experiment
            cpus.append("thread" + str(_from))

        involved[socket] = cpus

    return involved


def get_field_and_metric(SuperTwin, involved, pmu_metric):

        
    db = utils.get_mongo_database(SuperTwin.name, SuperTwin.mongodb_addr)["twin"]
    meta_with_twin = loads(dumps(db.find({"_id": ObjectId(SuperTwin.mongodb_id)})))[0]                
    twin = meta_with_twin["twin_description"]
        
    for t_key in twin.keys(): ##Every component is a digital twin
        for s_key in involved.keys(): ##Socket
            for c_key in involved[s_key]: ##Thread
            
                if(t_key.find(c_key) != -1):
                    contents = twin[t_key]["contents"]
                    for content in contents:
                        if("PMUName" in content.keys()):
                            if(pmu_metric == content["PMUName"]):
                                return content["displayName"], content["DBName"]
                            
                    
                    
def main(SuperTwin, observation):

    ##Multi-threaded visualizations are under development
    print("observation:", observation)

    involved = find_from_likwid_pin(observation["affinity"])
    
    empty_dash = template_dict(observation["uid"])
    empty_dash["panels"] = []

    norm_ids = []
    for key in observation["elements"].keys():
        norm_ids.append(key + "_normalized")

    metrics_to_vis = []
    for item in observation["metrics"]:
        if(item.find(":") != -1): ##Choose only PMUs for now
            metrics_to_vis.append(item)
            
    for metric in metrics_to_vis:
        ts = ps.ret_ts_panel(next_y(), metric) ##For metric, get time series panel
        gp = ps.ret_gauge_panel(metric + " MEAN", current_y()) ##For metric, get gauge panel
        cpu_field, metric_field = get_field_and_metric(SuperTwin, involved, metric)
        
        for _id in observation["elements"].keys():
            norm_id = _id + "_normalized"
            alias = observation["elements"][_id]["name"]
            ts["targets"].append(ps.ret_query(alias, metric_field, cpu_field, norm_id)) ##For "observation", get query
            gp["targets"].append(ps.ret_query(alias, metric_field, cpu_field, norm_id)) ##For "observation", get query
        empty_dash["panels"].append(ts)
        empty_dash["panels"].append(gp)
        #print("panels:", empty_dash["panels"])
    
    my_max = 0
    max_key = ""
    for key in observation["elements"]:
        if(observation["elements"][key]["duration"] > my_max):
            my_max = observation["elements"][key]["duration"]
            max_key = key


    
    fig = go.Figure(layout={})
    keys = list(observation["elements"].keys())
    ref = observation["elements"][keys[0]]["duration"]

    fig.add_trace(go.Indicator(
        mode = "number",
        value = observation["elements"][keys[0]]["duration"],
        domain = {'row': 0, 'column': 0},
        number = {"font": {"color": "black", "size": 60}, "suffix": "s"},
        title = {'text': observation["elements"][keys[0]]["name"] , "font": {"color": "gray", "size": 36}})
    )
    
    for i in range(1, len(keys)):
        fig.add_trace(go.Indicator(
            mode = "number+delta",
            delta = {'reference': ref, 'position': 'right', 'relative': True, 'increasing':{'color':'red'}, 'decreasing':{'color':'green'}},
            value = observation["elements"][keys[i]]["duration"],
            domain = {'row': 0, 'column': i},
            number = {"font": {"color": "black", "size": 60}, "suffix": "s"},
            title = {'text': observation["elements"][keys[i]]["name"] , "font": {"color": "gray", "size": 36 }})
        )
        
    
    
    fig = ps.grafana_layout_2(fig)
    
    fig.update_layout(grid = {'rows': 1, 'columns': len(observation["elements"].keys()), 'pattern': "independent"})
    dict_fig = json.loads(io.to_json(fig))


    empty_dash["panels"].append(ps.two_templates_two(dict_fig["data"], dict_fig["layout"]))
    ######################################
    ##create dashboard data

    #locate time and upload
    ######################################
    db = utils.get_influx_datasource(SuperTwin.influxdb_addr)
    db.switch_database(SuperTwin.influxdb_name)
            
    _, metric_field = get_field_and_metric(SuperTwin, involved, metric)
    qs = influx_help.query_string(metric_field, max_key + "_normalized")
    
    res = list(db.query(qs))[0]
    res_min = res[0]["time"]
    res_max = res[len(res) - 1]["time"]

    json_dash_obj = get_dashboard_json(empty_dash, overwrite = False)
    g_url = upload_to_grafana(json_dash_obj, SuperTwin.grafana_addr, SuperTwin.grafana_token)

    try:
        time_from = int(time.mktime(time.strptime(res_min , "%Y-%m-%dT%H:%M:%S.%fZ"))) *1000 + 10800000 ##Convert to milliseconds then add browser time.
    except:
        time_from = int(time.mktime(time.strptime(res_min , "%Y-%m-%dT%H:%M:%SZ"))) *1000 + 10800000 ##Convert to milliseconds then add browser time.
    
    try:
        time_to = int(time.mktime(time.strptime(res_max , "%Y-%m-%dT%H:%M:%S.%fZ"))) *1000 + 10800000
    except:
        time_to = int(time.mktime(time.strptime(res_max , "%Y-%m-%dT%H:%M:%SZ"))) *1000 + 10800000
    
    _time_window = str(round((time_to - time_from)))
    _time = str(round((time_from + time_to) /2))

    url = "http://localhost:3000" + g_url['url'] + "?" + "time=" + _time + "&" + "time.window=" + _time_window

    print("Generated report at:", url)
    return url


if __name__ == "__main__":

    main()
