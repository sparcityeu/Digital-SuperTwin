import os

import sys
sys.path.append("../")
sys.path.append("../probing/benchmarks")

import utils
import stream_benchmark
import adcarm_benchmark
import hpcg_benchmark

import observation_standard as obs
import roofline_dashboard_panels as rdp

import json
import requests

from grafanalib.core import Dashboard
from grafanalib._gen import DashboardEncoder
import uuid
import numpy as np

import plotly.graph_objects as go
import plotly.io as io
import matplotlib.colors as mc
import colorsys



vis_all = []
vis_L1s = []
vis_L2s = []
vis_L3s = []
vis_DRAMs = []
vis_threads = {}

vis_map_all = {}
vis_map_L1s = {}
vis_map_L2s = {}
vis_map_L3s = {}
vis_map_DRAMs = {}
vis_map_threads = {} ##This is where markings will be added


#colors = ["#75eab6", "#2d747a", "#20d8fd", "#c0583d", "#bccd97", "#b1e632", "#57832e", "#efaa79"]
#colors = ["#56ebd3", "#528e8c", "#c5df72", "#194f46", "#b4ddd4", "#9f5553"] ##This is, SO BEAUTIFUL
colors = ["#399283", "#9f1845", "#4cf32c", "#3c5472", "#cadba5", "#02531d", "#56ebd3", "#d11f0b", "#a0e85b", "#3163d8", "#b3d9fa", "#82400f", "#ef8ead", "#31a62e", "#ff0087", "#809b31"]

next_color = -1
next_element_id = -1

def get_eid():
    global next_element_id

    next_element_id += 1

    return next_element_id

def show_eid():
    global next_element_id
    
    return next_element_id



def generate_visibility_sequence(vis_dict):

    visibility = [False for i in range(show_eid() + 1)]
    
    for key in vis_dict.keys():
        for item in vis_dict[key]:
            #print("item:", item)
            visibility[item] = True

    return visibility

def generate_visibility_sequence_from_list(vis_list):

    visibility = [False for i in range(show_eid() + 1)]

    for item in vis_list:
        visibility[item] = True

    return visibility


def get_next_color():
    global next_color
    
    next_color += 1

    return colors[next_color]

def round_power_of_2(number):
    if number > 1:
        for i in range(1, int(number)):
            if (2 ** i >= number):
                return 2 ** i
    else:
        return 1

def carm_eq(ai, bw, fp):
    #print("Returning:", np.minimum(ai*bw, fp))
    return np.minimum(ai*bw, fp)


glob_y = -7
glob_panel_id = 1

glob_id = 80

def next_y():
    global glob_y
    glob_y += 7
    
    return glob_y

def next_panel_id():
    global glob_panel_id
    glob_panel_id += 1

    return glob_panel_id

def next_dash_id():
    global glob_id

    glob_id += 1

    return glob_id

def return_line(ai, eq, name, color, dash):

    line = {
                    "line": {
                        "color": color,
                        "dash": dash,
                        "width": 4
                    },
                    "mode": "lines",
                    "name": name,
                    "type": "scatter",
                    "x": ai,
                    "y": eq
                }

    return line

def line_spec(color, dash):

    line = {}
    
    if(dash != ""):
        line = {
            "color": color,
            "dash": dash,
            "width": 2
        }
        
    else:
        line = {"color": color,
                "width": 2
        }
    
    return line

def return_subtraces(data, ai, thread, index):

    global vis_all
    global vis_L1s
    global vis_L2s
    global vis_L3s
    global vis_DRAMs
    global vis_threads

    global vis_map_all
    global vis_map_L1s
    global vis_map_L2s
    global vis_map_L3s
    global vis_map_DRAMs
    global vis_map_threads

    
    for_one_L1 = carm_eq(ai, data["threads"][thread][index]["L1"], data["threads"][thread][index]["FP"])
    _id1 = get_eid()
    
    for_one_L2 = carm_eq(ai, data["threads"][thread][index]["L2"], data["threads"][thread][index]["FP"])
    _id2 = get_eid()
    
    for_one_L3 = carm_eq(ai, data["threads"][thread][index]["L3"], data["threads"][thread][index]["FP"])
    _id3 = get_eid()
    
    for_one_DRAM = carm_eq(ai, data["threads"][thread][index]["DRAM"], data["threads"][thread][index]["FP"])
    _id4 = get_eid()
    

    this_keys = data["threads"][thread][index].keys()
    name = thread + "thr"
        
    if(data["threads"][thread][index]["interleaved"] != 0):
        name += " interleaved"

    if("binding" in this_keys):
        name += " "
        name += data["threads"][thread][index]["binding"].split(" ")[3]

    if(thread in vis_threads.keys()):
        vis_threads[thread] += [True]*4
    else:
        vis_threads[thread] = []
        vis_threads[thread] += [False]*len(vis_all)
        vis_threads[thread] += [True]*4
        
    if(data["threads"][thread][index]["interleaved"] != 0 or "binding" in this_keys):
        vis_all += [False]*4
        vis_L1s += [False]*4
        vis_L2s += [False]*4
        vis_L3s += [False]*4
        vis_DRAMs += [False]*4
    else:
        vis_all += [True]*4
        vis_L1s += [True, False, False, False]
        vis_L2s += [False, True, False, False]
        vis_L3s += [False, False, True, False]
        vis_DRAMs += [False, False, False, True]

        
    if(thread not in vis_map_all.keys()):
        vis_map_all[thread] = []
        vis_map_L1s[thread] = []
        vis_map_L2s[thread] = []
        vis_map_L3s[thread] = []
        vis_map_DRAMs[thread] = []
        vis_map_threads[thread] = []

    vis_map_all[thread] += [_id1, _id2, _id3, _id4]
    vis_map_threads[thread] += [_id1, _id2, _id3, _id4]
    vis_map_L1s[thread].append(_id1)
    vis_map_L2s[thread].append(_id2)
    vis_map_L3s[thread].append(_id3)
    vis_map_DRAMs[thread].append(_id4)
        

    return [for_one_L1, for_one_L2, for_one_L3, for_one_DRAM, name]


def thread_groups(fig, thread, color, data, ai, ai_list):

    thread_lines = []
    print(data["threads"])
    for i in range(len(data["threads"][thread])):
        thread_lines = return_subtraces(data, ai, thread, i)
        name_postfix = thread_lines[4]
        gc = get_next_color()
        fig.add_trace(go.Scatter(x=ai_list, y=thread_lines[0].tolist(),
                      mode = "lines", name="L1 - "+ name_postfix, line=line_spec(gc, "")))
        fig.add_trace(go.Scatter(x=ai_list, y=thread_lines[1].tolist(),
                      mode = "lines", name="L2 - "+ name_postfix, line=line_spec(gc, "dash")))
        fig.add_trace(go.Scatter(x=ai_list, y=thread_lines[2].tolist(),
                      mode = "lines", name="L3 - "+ name_postfix, line=line_spec(gc, "")))
        fig.add_trace(go.Scatter(x=ai_list, y=thread_lines[3].tolist(),
                      mode = "lines", name="DRAM - "+ name_postfix, line=line_spec(gc, "dashdot")))

    return fig


def fill_res_dict(carm_res, result):

    threads = str(result["@threads"])
    modifier = ""

    if("@modifier" in result.keys()):
        modifier = result["@modifier"]

    inst = result["@local_parameters"][0]["inst"]
    isa = result["@local_parameters"][1]["isa"]
    precision = result["@local_parameters"][2]["precision"]
    ldstratio = result["@local_parameters"][3]["ld_st_ratio"]
    onlyld = result["@local_parameters"][4]["only_ld"]
    interleaved = result["@local_parameters"][5]["interleaved"]
    numops = result["@local_parameters"][6]["numops"]
    drambytes = result["@local_parameters"][7]["dram_bytes"]
    L1 = result["@result"][0]["L1"]
    L2 = result["@result"][1]["L2"]
    L3 = result["@result"][2]["L3"]
    DRAM = result["@result"][3]["DRAM"]
    FP = result["@result"][4]["FP"]
    
    #for idx, item in enumerate(result["@local_parameters"]):
        #print("idx:", idx, "item:", item)
        
    _dict = {}
    _dict["inst"] = inst
    _dict["isa"] = isa
    _dict["precision"] = precision
    _dict["ldstratio"] = ldstratio
    _dict["onlyld"] = onlyld
    _dict["interleaved"] = interleaved
    _dict["numops"] = numops
    _dict["drambytes"] = drambytes
    if(modifier != ""):
        _dict["binding"] = modifier
    _dict["L1"] = L1
    _dict["L2"] = L2
    _dict["L3"] = L3
    _dict["DRAM"] = DRAM
    _dict["FP"] = FP


    try:
        carm_res["threads"][threads].append(_dict)
    except:
        carm_res["threads"][threads] = []
        carm_res["threads"][threads].append(_dict)
    
    return carm_res

def get_carm_res_from_dt(SuperTwin):

    td = utils.get_twin_description(SuperTwin) ##Twin description

    carm_res = {}
    carm_res["threads"] = {}
    for key in td:
        if(key.find("system") != -1):
            for content in td[key]["contents"]:
                if(content["@type"] == "benchmark" and content["@name"] == "CARM"):
                    results = content["@contents"]

                    for result in results:
                        #print("one_res:", result)
                        carm_res = fill_res_dict(carm_res, result)

    return carm_res

##This visibility thing; should keep indices, then generate, true false arrays from it
##For returning a roofline dashboard for observations; it should levitate these indices
##For buttons; probably shouldnt exist
##When there is no buttons, legend automatically comes back which is nice
def generate_carm_roofline(SuperTwin): ##THREADS as a parameter to redraw for observations

    global vis_map_all
    global vis_map_L1s
    global vis_map_L2s
    global vis_map_L3s
    global vis_map_DRAMs
    global vis_map_threads

    td = utils.get_twin_description(SuperTwin) ##Twin description

    empty_dash = obs.template_dict(SuperTwin.name + " Roofline-" + str(uuid.uuid4()))
    empty_dash["panels"] = []

    ai = np.linspace(0.00390625, 2048, num=1000)
    data = adcarm_benchmark.parse_adcarm_bench()

    empty_dash = obs.template_dict(SuperTwin.name + " Monitor-" + str(uuid.uuid4()))
    empty_dash["panels"] = []
    ###
    
    fig = go.Figure(layout={})
    ai_list = ai.tolist()

    #carm_res = adcarm_benchmark.parse_adcarm_bench()
    #print("carm res:", carm_res.keys())
    #print("###############")
    carm_res = get_carm_res_from_dt(SuperTwin)
    #print("carm res:", carm_res.keys())
    
    
    print("carm_res:", carm_res.keys())
    for idx, key in enumerate(carm_res["threads"].keys()):
        fig = thread_groups(fig, key, colors[idx], carm_res, ai, ai_list)

        
    #print("##########")
    print("all:", vis_map_all)
    print("L1s:", vis_map_L1s)
    print("L2s:", vis_map_L2s)
    print("L3s:",vis_map_L3s)
    print("DRAMS:", vis_map_DRAMs)
    print("Threads:", vis_map_threads)
    #print("##########")
    
    vis_map_all = dict(sorted(vis_map_all.items(), key=lambda t: int(t[0])))
    vis_map_L1s = dict(sorted(vis_map_L1s.items(), key=lambda t: int(t[0])))
    vis_map_L2s = dict(sorted(vis_map_L2s.items(), key=lambda t: int(t[0])))
    vis_map_L3s = dict(sorted(vis_map_L3s.items(), key=lambda t: int(t[0])))
    vis_map_DRAMs = dict(sorted(vis_map_DRAMs.items(), key=lambda t: int(t[0])))
    vis_map_threads = dict(sorted(vis_map_threads.items(), key=lambda t: int(t[0])))
    
    
    buttons = [{"label": "All",
                "method": "restyle",
                "args": ["visible", generate_visibility_sequence(vis_map_all)]},
               {"label": "L1s",
                "method": "restyle",
                "args": ["visible", generate_visibility_sequence(vis_map_L1s)]},
               {"label": "L2s",
                "method": "restyle",
                "args": ["visible", generate_visibility_sequence(vis_map_L2s)]},
               {"label": "L3s",
                "method": "restyle",
                "args": ["visible", generate_visibility_sequence(vis_map_L3s)]},
               {"label": "DRAMs",
                "method": "restyle",
                "args": ["visible", generate_visibility_sequence(vis_map_DRAMs)]}]

    buttons2 = []
    for thread in vis_map_threads.keys():
        buttons2.append({"label": thread +" thr",
                                         "method": "restyle",
                                         "args": ["visible",
                                                  generate_visibility_sequence_from_list(vis_map_threads[thread])]})


    fig.update_layout(showlegend=False)
    fig.update_layout(font_size=16)
    fig.update_xaxes(showspikes=True)
    fig.update_yaxes(showspikes=True)
    fig.update_traces(hovertemplate="%{y}")
    fig.update_layout(hovermode="x")

    ##update layout with buttons
    fig.update_layout(
        updatemenus=[
            dict(
                type="buttons",
                direction="right",
                buttons=buttons,
                pad={"r": 4, "t": 4, "l": 0, "b": 0}, ##b?
                showactive=True,
                x=0.1,
                xanchor="left",
                y=1.15,
                yanchor="top"),
            dict(
                type="buttons",
                direction="right",
                buttons=buttons2,
                pad={"r": 4, "t": 4, "l": 0, "b": 0}, ##b?
                showactive=True,
                x=0.1,
                xanchor="left",
                y=1.25,
                yanchor="top")])
            
    
    fig = rdp.grafana_layout(fig)
    dict_fig = obs.json.loads(io.to_json(fig))
    empty_dash["panels"].append(rdp.two_templates_one(dict_fig["data"], dict_fig["layout"]))
    ###
    json_dash_obj = obs.get_dashboard_json(empty_dash, overwrite = False)
    g_url = obs.upload_to_grafana(json_dash_obj, SuperTwin.grafana_addr, SuperTwin.grafana_token)
    print("Generated:", g_url)


    
def generate_roofline_dashboard(SuperTwin):

    generate_carm_roofline(SuperTwin)
