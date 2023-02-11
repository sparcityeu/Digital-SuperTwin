import sys
sys.path.append("../")

import utils

from string import Template
from bson.objectid import ObjectId
from bson.json_util import dumps
from bson.json_util import loads

glob_panel_id = 0

def next_panel_id():
    global glob_panel_id
    glob_panel_id += 1

    return glob_panel_id


def get_json_static_panel(h, w, x, y, title, emp, target):

    
    json_static_panel = {
        "id": next_panel_id(),
        "gridPos": {
            "h": h,
            "w": w,
            "x": x,
            "y": y
        },
        "type": "stat",
        "title": title,
        "datasource": {
            "uid": "yjaMegMVk", ##This needs to be queried from SuperTwin
            "type": "simpod-json-datasource"
        },
        "pluginVersion": "9.1.0-beta1",
        "fieldConfig": {
            "defaults": {
                "mappings": [],
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
            "colorMode": emp, ##"value" or "background"
            "graphMode": "area",
            "justifyMode": "auto"
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
                "target": target,
                "timeField": "@timestamp"
            }
        ],
        "transparent": True
    }

    return json_static_panel

def get_stream_bw(twin):

    max_bw = 0.0
    
    for key in twin:
        if(key.find(":system:") != -1):
            for content in twin[key]["contents"]:
                if(content["@type"] == "benchmark" and content["@name"] == "STREAM"):
                    max_bw = content["@mvres"]

    max_bw /= 1000 #To GB/s
    return max_bw


def peak_theoretical_flop(no_procs, core_per_proc, clock_speed, no_fma_units, max_vector_size):

    #print(type(no_procs))
    #print(type(core_per_proc))
    #print(type(clock_speed))
    #print(type(no_fma_units))
    #print(type(max_vector_size))
    
    peak_gflop_o_s = no_procs * core_per_proc * clock_speed * (2 * no_fma_units) * (max_vector_size / 64)
    return peak_gflop_o_s

def get_ridge_point(bw, flop):

    ridge = flop / bw
    return ridge


def get_roof_values(max_bw, peak_g_flop, ridge_point):

    AIs = []
    for i in range(-6, 11):
        AIs.append(2**i)
    AIs.append(ridge_point)
    AIs = sorted(AIs)

    Y = []

    for AI in AIs:
        Y.append(round(min((max_bw * AI), peak_g_flop), 2))

    return AIs, Y

def get_flops_values(twin):

    ddot_flops = 0.0
    spmv_flops = 0.0
    waxpby_flops = 0.0
    
    for key in twin:
        if(key.find(":system:") != -1):
            for content in twin[key]["contents"]:
                if(content["@type"] == "benchmark" and content["@name"] == "HPCG"):
                    ddot_flops = content["@mvres"]["ddot"]
                    spmv_flops = content["@mvres"]["spmv"]
                    waxpby_flops = content["@mvres"]["waxpby"]

    return ddot_flops, spmv_flops, waxpby_flops
    

def get_dram_roofline_panel(SuperTwin):

    db = utils.get_mongo_database(SuperTwin.name, SuperTwin.mongodb_addr)["twin"]
    meta_with_twin = loads(dumps(db.find({"_id": ObjectId(SuperTwin.mongodb_id)})))[0]
    twin = meta_with_twin["twin_description"]

    system_info = utils.fill_data(twin, SuperTwin.name, SuperTwin.addr)

    max_bw = get_stream_bw(twin)
    peak_g_flop = peak_theoretical_flop(system_info["cpu_threads"],
                                        system_info["system_no_numa_nodes"],
                                        system_info["cpu_ghz"],
                                        system_info["no_fma_units"],
                                        system_info["max_vector_size"])

    ridge_point = round(get_ridge_point(max_bw, peak_g_flop), 1)
    roofline_x, roofline_y = get_roof_values(max_bw, peak_g_flop, ridge_point)

    roofline_x_string = ""
    for i in range(len(roofline_x) - 2):
        roofline_x_string += str(roofline_x[i])
        roofline_x_string += ","
    roofline_x_string += str(roofline_x[(len(roofline_x) - 1)])

    roofline_y_string = ""
    for i in range(len(roofline_y) - 2):
        roofline_y_string += str(roofline_y[i])
        roofline_y_string += ","
    roofline_y_string += str(roofline_y[(len(roofline_y) - 1)])
        
    ddot_flops, spmv_flops, waxpby_flops = get_flops_values(twin)
    
    ddot_ai = 0.125 ##[1]
    spmv_ai = 0.25 ##[1]
    waxpby_ai = 0.125 ##[1]
        
    templated_script = Template("console.log(data)\n\nvar trace_benchmark_ddot = {\n  type: \"scatter\",\n  mode: \"markers\",\n  marker: { symbol: \"x-dot\" ,\n  size: 25},\n  x: [$ddot_ai],\n  y: [$ddot_flops],\n  line: {color: 'red'},\n  name: \"HPCG - DDOT\"\n};\n\nvar trace_benchmark_spmv = {\n  type: \"scatter\",\n  mode: \"markers\",\n  marker: { symbol: \"x-dot\" , size: 25},\n  x: [$spmv_ai],\n  y: [$spmv_flops],\n  line: {color: 'green'},\n  name: \"HPCG - SPMV\"\n};\n\nvar trace_benchmark_waxpby = {\n  type: \"scatter\",\n  mode: \"markers\",\n  marker: { symbol: \"x-dot\" , size: 25},\n  x: [$waxpby_ai],\n  y: [$waxpby_flops],\n  line: {color: 'purple'},\n  name: \"HPCG - WAXPBY\"\n};\n\nvar trace_roofline = {\n  type: \"scatter\",\n  mode: \"lines\",\n  x: [$roofline_x],\n  y: [$roofline_y],\n  line: {color: '#1AA7b4'},\n  name: \"Roofline DRAM\"\n};\n\nvar data = [trace_benchmark_ddot,trace_benchmark_spmv, trace_benchmark_waxpby,trace_roofline];\n\nvar layout = {\n\txaxis: {title: 'Arithmetic Intensity',\n          range: [0,3],\n          nticks: 10,\n          type: \"log\"},\n\tyaxis: {title: 'Performance [GFlop/s]',\n          //rangemode: \"tozero\",\n          type: \"log\"},\n  margin: { l: 50, r: 35, t: 10, b: 40},\n  legend: { orientation: \"h\",\n            y:1.1 },\n  width: 1000,\n  height: 420,\n};\n\n\n\nvar config = {locale: 'en'};\n\nreturn {data:data,layout:layout,config:config};")
    
    templated_script = templated_script.substitute(ddot_ai=ddot_ai,
                                                   ddot_flops=ddot_flops,
                                                   spmv_ai=spmv_ai,
                                                   spmv_flops=spmv_flops,
                                                   waxpby_ai=waxpby_ai,
                                                   waxpby_flops=waxpby_flops,
                                                   roofline_x=roofline_x_string,
                                                   roofline_y=roofline_y_string)

    dram_roofline_panel = {
        "id": next_panel_id(),
        "gridPos": {
            "h": 13,
            "w": 12,
            "x": 4,
            "y": 0
        },
        "type": "ae3e-plotly-panel",
        "title": "DRAM Roofline",
        "datasource": {
            "type": "simpod-json-datasource",
            "uid": "yjaMegMVk"
        },
        "options": {
            "script": templated_script, 
            "onclick": "console.log(data)\nwindow.updateVariables({query:{'var-project':'test'}, partial: true})",
            "data": "",
            "layout": ""
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


    return dram_roofline_panel


def get_stream_results(twin):

    results = {}
    results["Add"] = {}
    results["Copy"] = {}
    results["Triad"] = {}
    results["Scale"] = {}
    thread_set = []

    for key in twin:
        if(key.find(":system:") != -1):
            for content in twin[key]["contents"]:
                if(content["@type"] == "benchmark" and content["@name"] == "STREAM"):
                    for result in content["@contents"]:
                        if(result["@field"] == "Max_Thr"):
                            continue
                        thread = result["@threads"]
                        _result = float(result["@result"])

                        if(thread not in thread_set):
                            thread_set.append(thread)

                        results[result["@field"]][str(thread)] = _result

    thread_set = list(sorted(thread_set))
    return results, thread_set

                        
                        

def get_stream_scaling_panel(SuperTwin):

    db = utils.get_mongo_database(SuperTwin.name, SuperTwin.mongodb_addr)["twin"]
    meta_with_twin = loads(dumps(db.find({"_id": ObjectId(SuperTwin.mongodb_id)})))[0]
    twin = meta_with_twin["twin_description"]
    
    add_result = []
    copy_result = []
    scale_result = []
    triad_result = []
    tickvals = 1

    results, thread_set = get_stream_results(twin)

    
    for item in thread_set:
        #print("item:", item)
        #print("results:", results)
        add_result.append(results["Add"][str(item)])
        copy_result.append(results["Copy"][str(item)])
        triad_result.append(results["Triad"][str(item)])
        scale_result.append(results["Scale"][str(item)])


    add_result_string = ""
    copy_result_string = ""
    scale_result_string = ""
    triad_result_string = ""
    for i in range(len(thread_set) - 1):
        add_result_string += (str(add_result[i]) + ",")
        copy_result_string += (str(copy_result[i]) + ",")
        scale_result_string += (str(scale_result[i]) + ",")
        triad_result_string += (str(triad_result[i]) + ",")
    _len = len(thread_set) - 1
    add_result_string += str(add_result[_len])
    copy_result_string += str(copy_result[_len])
    scale_result_string += str(scale_result[_len])
    triad_result_string += str(triad_result[_len])
    
    #tickvals: [\"1\", \"2\", \"4\", \"8\", \"16\", \"22\", \"32\", \"44\", \"64\", \"88\"]

    tickvals_string = ""
    for i in range(len(thread_set) - 1):
        tickvals_string += ('\"' + str(thread_set[i]) + '\",')
    tickvals_string +=  ('\"' + str(thread_set[_len]) + '"')

    thread_set_string = ""
    for i in range(len(thread_set) - 1):
        thread_set_string += (str(thread_set[i]) + ",")
    thread_set_string += str(thread_set[_len])
    
    templated_script = Template("console.log(data)\n\nvar trace_add = {\n  type: \"scatter\",\n  mode: \"lines\",\n  x: [$thread_set],\n  y: [$add_result],\n  line: {color: 'green'},\n  name: \"Add\"\n};\n\nvar trace_copy = {\n  type: \"scatter\",\n  mode: \"lines\",\n  x: [$thread_set],\n  y: [$copy_result],\n  line: {color: 'red'},\n  name: \"Copy\"\n};\n\nvar trace_scale = {\n  type: \"scatter\",\n  mode: \"lines\",\n  x: [$thread_set],\n  y: [$scale_result],\n  line: {color: 'orange'},\n  name: \"Scale\"\n};\n\nvar trace_triad = {\n  type: \"scatter\",\n  mode: \"lines\",\n  x: [$thread_set],\n  y: [$triad_result],\n  line: {color: 'cyan'},\n  name: \"Triad\"\n};\n\nvar data = [trace_add, trace_copy, trace_scale, trace_triad];\n\nvar layout = {\n\txaxis: {title: 'Number of Threads',\n          tickvals: [$tickvals],\n          nticks: 5,\n          type: \"category\"},\n\tyaxis: {title: 'Bandwith [MB/s]',\n          rangemode: \"tozero\"},\n  margin: { l: 50, r: 35, t: 10, b: 40},\n  legend: { orientation: \"h\",\n            y:1.1 },\n  width: 600,\n  height: 450,\n};\n\nvar config = {locale: 'en'};\n\nreturn {data:data,layout:layout,config:config};")

    templated_script = templated_script.substitute(thread_set=thread_set_string,
                                                   add_result=add_result_string,
                                                   copy_result=copy_result_string,
                                                   scale_result=scale_result_string,
                                                   triad_result=triad_result_string,
                                                   tickvals=tickvals_string)
    
    stream_scaling_panel = {
        "id": next_panel_id(),
        "gridPos": {
            "h": 14,
            "w": 8,
            "x": 0,
            "y": 13
        },
        "type": "ae3e-plotly-panel",
        "title": "STREAM Multicore Scaling",
        "datasource": {
            "type": "simpod-json-datasource",
            "uid": "yjaMegMVk"
        },
        "options": {
            "script": templated_script,
            "onclick": "console.log(data)\nwindow.updateVariables({query:{'var-project':'test'}, partial: true})",
            "data": "",
            "layout": ""
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

    return stream_scaling_panel
    

def get_hpcg_results(twin):

    results = {}
    results["ddot"] = {}
    results["spmv"] = {}
    results["waxpby"] = {}
    thread_set = []

    for key in twin:
        if(key.find(":system:") != -1):
            for content in twin[key]["contents"]:
                if(content["@type"] == "benchmark" and content["@name"] == "HPCG"):
                    for result in content["@contents"]:
                        if(result["@field"] == "Max_Thr"):
                            continue
                        thread = result["@threads"]
                        _result = float(result["@result"])

                        if(thread not in thread_set):
                            thread_set.append(thread)

                        results[result["@field"]][str(thread)] = _result

    thread_set = list(sorted(thread_set))
    return results, thread_set



def get_hpcg_scaling_panel(SuperTwin):

    db = utils.get_mongo_database(SuperTwin.name, SuperTwin.mongodb_addr)["twin"]
    meta_with_twin = loads(dumps(db.find({"_id": ObjectId(SuperTwin.mongodb_id)})))[0]
    twin = meta_with_twin["twin_description"]

    ddot_result = []
    spmv_result = []
    waxpby_result = []
    tickvals = 1

    results, thread_set = get_hpcg_results(twin)

    for item in thread_set:
        ddot_result.append(results["ddot"][str(item)])
        spmv_result.append(results["spmv"][str(item)])
        waxpby_result.append(results["waxpby"][str(item)])

    ddot_result_string = ""
    spmv_result_string = ""
    waxpby_result_string = ""
    for i in range(len(thread_set) - 1):
        ddot_result_string += (str(ddot_result[i]) + ",")
        spmv_result_string += (str(spmv_result[i]) + ",")
        waxpby_result_string += (str(waxpby_result[i]) + ",")
    _len = len(thread_set) - 1
    ddot_result_string += str(ddot_result[_len])
    spmv_result_string += str(spmv_result[_len])
    waxpby_result_string += str(waxpby_result[_len])

    
    tickvals_string = ""
    for i in range(len(thread_set) - 1):
        tickvals_string += ('\"' + str(thread_set[i]) + '\",')
    tickvals_string +=  ('\"' + str(thread_set[_len]) + '"')

    thread_set_string = ""
    for i in range(len(thread_set) - 1):
        thread_set_string += (str(thread_set[i]) + ",")
    thread_set_string += str(thread_set[_len])
    

    templated_script = Template("console.log(data)\n\nvar trace_ddot = {\n  type: \"scatter\",\n  mode: \"lines\",\n  x: [$thread_set],\n  y: [$ddot_result],\n  line: {color: 'magenta'},\n  name: \"DDOT\"\n};\n\nvar trace_spmv = {\n  type: \"scatter\",\n  mode: \"lines\",\n  x: [$thread_set],\n  y: [$spmv_result],\n  line: {color: 'blue'},\n  name: \"SPmV\"\n};\n\nvar trace_waxpby = {\n  type: \"scatter\",\n  mode: \"lines\",\n  x: [$thread_set],\n  y: [$waxpby_result],\n  line: {color: 'red'},\n  name: \"WAXPBY\"\n};\n\nvar data = [trace_spmv, trace_ddot, trace_waxpby];\n\nvar layout = {\n\txaxis: {title: 'Number of Threads',\n          tickvals: [$tickvals],\n          nticks: 5,\n          type: \"category\"},\n\tyaxis: {title: 'Performance [GFlop/s]',\n          rangemode: \"tozero\"},\n  margin: { l: 50, r: 35, t: 10, b: 40},\n  legend: { orientation: \"h\",\n            y:1.1 },\n  width: 600,\n  height: 450,\n};\n\nvar config = {locale: 'en'};\n\nreturn {data:data,layout:layout,config:config};")

    templated_script = templated_script.substitute(thread_set=thread_set_string,
                                                   ddot_result=ddot_result_string,
                                                   spmv_result=spmv_result_string,
                                                   waxpby_result=waxpby_result_string,
                                                   tickvals=tickvals_string)
    
    hpcg_scaling_panel = {
        "id": next_panel_id(),
        "gridPos": {
            "h": 14,
            "w": 8,
            "x": 8,
            "y": 13
        },
        "type": "ae3e-plotly-panel",
        "title": "HPCG Multicore Scaling",
        "datasource": {
            "type": "simpod-json-datasource",
            "uid": "yjaMegMVk"
        },
        "options": {
            "script": templated_script,
            "onclick": "console.log(data)\nwindow.updateVariables({query:{'var-project':'test'}, partial: true})",
            "data": "",
            "layout": ""
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

    return hpcg_scaling_panel
    
    
def generate_roofline_dashboard(SuperTwin):

    server = SuperTwin.grafana_addr
    token = SuperTwin.grafana_token

    title = SuperTwin.name + " -- " + SuperTwin._id
    dashboard = utils.get_empty_dashboard(title)
    ##Static panels
    dashboard["panels"].append(get_json_static_panel(5, 4, 0, 0, "Hostname", "background", "system_hostname"))
    dashboard["panels"].append(get_json_static_panel(4, 4, 0, 5, "IP", "value", "system_ip"))
    dashboard["panels"].append(get_json_static_panel(4, 4, 0, 9, "OS", "value", "system_os"))
    dashboard["panels"].append(get_json_static_panel(4, 8, 16, 0, "CPU", "value", "cpu_model"))
    dashboard["panels"].append(get_json_static_panel(3, 2, 16, 4, "L1D Cache Size", "value", "l1dcache_size"))
    dashboard["panels"].append(get_json_static_panel(3, 3, 18, 4, "L2 Cache Size", "value", "l2cache_size"))
    dashboard["panels"].append(get_json_static_panel(3, 3, 21, 4, "L3 Cache Size", "value", "l3cache_size"))
    dashboard["panels"].append(get_json_static_panel(3, 2, 16, 7, "L1D Assoc.", "value", "l1dcache_associativity"))
    dashboard["panels"].append(get_json_static_panel(3, 3, 18, 7, "L1D Cache Linesize", "value", "l1dcache_linesize"))
    dashboard["panels"].append(get_json_static_panel(3, 3, 21, 7, "L1D Cache # of sets", "value", "l1dcache_nosets"))
    dashboard["panels"].append(get_json_static_panel(3, 2, 16, 10, "L2 Assoc.", "value", "l2cache_associativity"))
    dashboard["panels"].append(get_json_static_panel(3, 3, 18, 10, "L2 Cache Linesize", "value", "l2cache_linesize"))
    dashboard["panels"].append(get_json_static_panel(3, 3, 21, 10, "L2 Cache # of sets", "value", "l2cache_nosets"))
    dashboard["panels"].append(get_json_static_panel(3, 2, 16, 13, "L3 Assoc.", "value", "l3cache_associativity"))
    dashboard["panels"].append(get_json_static_panel(3, 3, 18, 13, "L3 Cache Linesize", "value", "l3cache_linesize"))
    dashboard["panels"].append(get_json_static_panel(3, 3, 21, 13, "L3 Cache # of sets", "value", "l3cache_nosets"))
    dashboard["panels"].append(get_json_static_panel(3, 2, 16, 16, "# of Sockets", "value", "system_no_numa_nodes"))
    dashboard["panels"].append(get_json_static_panel(3, 3, 18, 16, "# of Cores Per Socket", "value", "cpu_cores"))
    dashboard["panels"].append(get_json_static_panel(3, 3, 21, 16, "# of Threads Per Socket", "value", "cpu_threads"))

    ##Plotly panels
    dashboard["panels"].append(get_dram_roofline_panel(SuperTwin))
    dashboard["panels"].append(get_stream_scaling_panel(SuperTwin))
    dashboard["panels"].append(get_hpcg_scaling_panel(SuperTwin))

    
    json_dash_obj = utils.get_dashboard_json(dashboard, overwrite = False)
    url = utils.upload_to_grafana(json_dash_obj, server, token)

    return url

    
    
    
