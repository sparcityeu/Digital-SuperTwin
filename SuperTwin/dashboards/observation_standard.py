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
    #_template["refresh"] = "1s" ##Not exist in example
    
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
    print("involved:", involved)
    
    for t_key in twin.keys(): ##Every component is a digital twin
        for s_key in involved.keys(): ##Socket
            #print("!:", involved[s_key])
            for c_key in involved[s_key]: ##Thread
            
                if(t_key.find(c_key) != -1):
                    contents = twin[t_key]["contents"]
                    #print("contents:", contents)
                    for content in contents:
                        if("PMUName" in content.keys()):
                            if(pmu_metric == content["PMUName"]):
                                return content["displayName"], content["DBName"]
                            
                    
                    
#def get_time_window(SuperTwin, observation): ##Get first and last timestamp from db

    

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
        print("returned:", cpu_field, metric_field)
        for _id in observation["elements"].keys():
            norm_id = _id + "_normalized"
            alias = observation["elements"][_id]["name"]
            ts["targets"].append(ps.ret_query(alias, metric_field, cpu_field, norm_id)) ##For "observation", get query
            gp["targets"].append(ps.ret_query(alias, metric_field, cpu_field, norm_id)) ##For "observation", get query
        empty_dash["panels"].append(ts)
        empty_dash["panels"].append(gp)
        #print("panels:", empty_dash["panels"])
    json_dash_obj = get_dashboard_json(empty_dash, overwrite = False)
    g_url = upload_to_grafana(json_dash_obj, grafana_server, grafana_api_key)


    
    my_max = 0
    max_key = ""
    for key in observation["elements"]:
        if(observation["elements"][key]["duration"] > my_max):
            my_max = observation["elements"][key]["duration"]
            max_key = key


    '''
    fig = go.Figure(layout={})
    #ref = observation["elements"][observation["uid"] + "_0"]["duration"]
    ref = 47
    x = 0
    for key in observation["elements"]:
        fig.add_trace(go.Indicator(
            mode = "number+gauge+delta",
            gauge = {'shape': "bullet"},
            delta = {'reference': ref, 'relative': True},
            value = observation["elements"][key]["duration"],
            domain = {'row': x, 'column': 0},
            title = {'text': observation["elements"][key]["name"] }))
        x = x + 1
                      
    fig = ps.grafana_layout_2(fig)
    
    fig.update_layout(grid = {'rows': 1, 'columns': len(observation["elements"].keys()), 'pattern': "independent"})
    dict_fig = json.loads(io.to_json(fig))

    print("JUST")
    empty_dash["panels"].append(ps.two_templates_two(dict_fig["data"], dict_fig["layout"]))
    '''                  
    #####################################3
    db = utils.get_influx_database(SuperTwin.influxdb_addr, SuperTwin.influxdb_name)
    db.switch_database(SuperTwin.influxdb_name)
            
    _, metric_field = get_field_and_metric(SuperTwin, involved, metric)
    qs = influx_help.query_string(metric_field, max_key + "_normalized")
    
    res = list(db.query(qs))[0]
    res_min = res[0]["time"]
    res_max = res[len(res) - 1]["time"]

    print("res_min:", res_min)
    print("res_max:", res_max)
    
    time_from = int(time.mktime(time.strptime(res_min , "%Y-%m-%dT%H:%M:%S.%fZ"))) *1000 + 10800000 ##Convert to milliseconds then add browser time.
    print("res_min:", res_min, "time_from:", time_from)
    time_to = int(time.mktime(time.strptime(res_max , "%Y-%m-%dT%H:%M:%S.%fZ"))) *1000 + 10800000
    print("Time from:", time_from)
    _time_window = str(round((time_to - time_from)))
    _time = str(round((time_from + time_to) /2))

    print("g_url:", g_url)
    url = "http://localhost:3000" + g_url['url'] + "?" + "time=" + _time + "&" + "time.window=" + _time_window

    print("GENERATED:", url)

    
    
    
    return g_url


if __name__ == "__main__":

    observation = {'uid': 'd1b03d31-7133-423e-a06a-021b799dca16', 'affinity': 'likwid-pin -c S0:0', 'metrics': ['L1D:REPLACEMENT', 'L1D_PEND_MISS:PENDING', 'L1D_PEND_MISS:FB_FULL', 'L1D_PEND_MISS:EDGE', 'MEM_LOAD_RETIRED:L1_HIT', 'MEM_LOAD_RETIRED:L1_MISS', 'RAPL_ENERGY_PKG node', 'RAPL_ENERGY_DRAM node', 'kernel.all.pressure.cpu.some.total', 'hinv.cpu.clock', 'lmsensors.coretemp_isa_0000.package_id_0', 'lmsensors.coretemp_isa_0001.package_id_1', 'kernel.percpu.cpu.idle', 'kernel.pernode.cpu.idle', 'disk.dev.read', 'disk.dev.write', 'disk.dev.total', 'disk.dev.read_bytes', 'disk.dev.write_bytes', 'disk.dev.total_bytes', 'disk.all.read', 'disk.all.write', 'disk.all.total', 'disk.all.read_bytes', 'disk.all.write_bytes', 'disk.all.total_bytes', 'mem.util.used', 'mem.util.free', 'swap.pagesin', 'mem.numa.util.free', 'mem.numa.util.used', 'mem.numa.alloc.hit', 'mem.numa.alloc.miss', 'mem.numa.alloc.local_node', 'mem.numa.alloc.other_node', 'network.all.in.bytes', 'network.all.out.bytes', 'perfevent.hwcounters.RAPL_ENERGY_PKG.value', 'perfevent.hwcounters.RAPL_ENERGY_PKG.dutycycle', 'perfevent.hwcounters.RAPL_ENERGY_DRAM.value', 'perfevent.hwcounters.RAPL_ENERGY_DRAM.dutycycle'], 'elements': {'d1b03d31-7133-423e-a06a-021b799dca16_0': {'name': 'random', 'command': './random 1138_bus.mtx', 'duration': 4.234471925999969}, 'd1b03d31-7133-423e-a06a-021b799dca16_1': {'name': 'none', 'command': './none 1138_bus.mtx', 'duration': 5.1262109729868826}, 'd1b03d31-7133-423e-a06a-021b799dca16_2': {'name': 'rcm', 'command': './rcm 1138_bus.mtx', 'duration': 3.9959133730153553}, 'd1b03d31-7133-423e-a06a-021b799dca16_3': {'name': 'degree', 'command': './degree 1138_bus.mtx', 'duration': 4.8339896720135584}}}

    main("sa", observation)
