import os

import sys

sys.path.append("../")
sys.path.append("../probing/benchmarks")
sys.path.append("pmu_mappings")

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
import pmu_grafana_utils
import pmu_mapping_utils
import math


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
vis_map_threads = {}  ##This is where markings will be added


# colors = ["#75eab6", "#2d747a", "#20d8fd", "#c0583d", "#bccd97", "#b1e632", "#57832e", "#efaa79"]
# colors = ["#56ebd3", "#528e8c", "#c5df72", "#194f46", "#b4ddd4", "#9f5553"] ##This is, SO BEAUTIFUL
colors = [
    "#399283",
    "#9f1845",
    "#4cf32c",
    "#3c5472",
    "#cadba5",
    "#02531d",
    "#56ebd3",
    "#b4ddd4",
    "#a0e85b",
    "#3163d8",
    "#b3d9fa",
    "#82400f",
    "#ef8ead",
    "#31a62e",
    "#ff0087",
    "#809b31",
    "#399283",
    "#9f1845",
    "#4cf32c",
    "#3c5472",
    "#cadba5",
    "#02531d",
    "#56ebd3",
    "#b4ddd4",
    "#a0e85b",
    "#3163d8",
    "#b3d9fa",
    "#82400f",
    "#ef8ead",
    "#31a62e",
    "#ff0087",
    "#809b31",
]

chosen_thread_colors = {}

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
            # print("item:", item)
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
            if 2**i >= number:
                return 2**i
    else:
        return 1


def carm_eq(ai, bw, fp):
    # print("Returning:", np.minimum(ai*bw, fp))
    return np.minimum(ai * bw, fp)


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
        "line": {"color": color, "dash": dash, "width": 4},
        "mode": "lines",
        "name": name,
        "type": "scatter",
        "x": ai,
        "y": eq,
    }

    return line


def line_spec(color, dash):

    line = {}

    if dash != "":
        line = {"color": color, "dash": dash, "width": 2}

    else:
        line = {"color": color, "width": 2}

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

    for_one_L1 = carm_eq(
        ai,
        data["threads"][thread][index]["L1"],
        data["threads"][thread][index]["FP"],
    )
    _id1 = get_eid()

    for_one_L2 = carm_eq(
        ai,
        data["threads"][thread][index]["L2"],
        data["threads"][thread][index]["FP"],
    )
    _id2 = get_eid()

    for_one_L3 = carm_eq(
        ai,
        data["threads"][thread][index]["L3"],
        data["threads"][thread][index]["FP"],
    )
    _id3 = get_eid()

    for_one_DRAM = carm_eq(
        ai,
        data["threads"][thread][index]["DRAM"],
        data["threads"][thread][index]["FP"],
    )
    _id4 = get_eid()

    this_keys = data["threads"][thread][index].keys()
    name = thread + "thr"

    if data["threads"][thread][index]["interleaved"] != 0:
        name += " interleaved"

    if "binding" in this_keys:
        name += " "
        name += data["threads"][thread][index]["binding"].split(" ")[3]

    if thread in vis_threads.keys():
        vis_threads[thread] += [True] * 4
    else:
        vis_threads[thread] = []
        vis_threads[thread] += [False] * len(vis_all)
        vis_threads[thread] += [True] * 4

    if (
        data["threads"][thread][index]["interleaved"] != 0
        or "binding" in this_keys
    ):
        vis_all += [False] * 4
        vis_L1s += [False] * 4
        vis_L2s += [False] * 4
        vis_L3s += [False] * 4
        vis_DRAMs += [False] * 4
    else:
        vis_all += [True] * 4
        vis_L1s += [True, False, False, False]
        vis_L2s += [False, True, False, False]
        vis_L3s += [False, False, True, False]
        vis_DRAMs += [False, False, False, True]

    if thread not in vis_map_all.keys():
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

    global chosen_thread_colors

    thread_lines = []
    print("data[threads]:", data["threads"])
    for i in range(len(data["threads"][thread])):
        thread_lines = return_subtraces(data, ai, thread, i)
        name_postfix = thread_lines[4]
        gc = get_next_color()
        fig.add_trace(
            go.Scatter(
                x=ai_list,
                y=thread_lines[0].tolist(),
                mode="lines",
                name="L1 - " + name_postfix,
                line=line_spec(gc, ""),
            )
        )
        fig.add_trace(
            go.Scatter(
                x=ai_list,
                y=thread_lines[1].tolist(),
                mode="lines",
                name="L2 - " + name_postfix,
                line=line_spec(gc, "dash"),
            )
        )
        fig.add_trace(
            go.Scatter(
                x=ai_list,
                y=thread_lines[2].tolist(),
                mode="lines",
                name="L3 - " + name_postfix,
                line=line_spec(gc, ""),
            )
        )
        fig.add_trace(
            go.Scatter(
                x=ai_list,
                y=thread_lines[3].tolist(),
                mode="lines",
                name="DRAM - " + name_postfix,
                line=line_spec(gc, "dashdot"),
            )
        )

        if thread not in chosen_thread_colors.keys():
            chosen_thread_colors[thread] = gc
        if thread == "32":  ##Will change anyway
            chosen_thread_colors[thread] = gc

    return fig


def fill_carm_res_dict(carm_res, result):

    threads = str(result["@threads"])
    modifier = ""

    if "@modifier" in result.keys():
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

    # for idx, item in enumerate(result["@local_parameters"]):
    # print("idx:", idx, "item:", item)

    _dict = {}
    _dict["inst"] = inst
    _dict["isa"] = isa
    _dict["precision"] = precision
    _dict["ldstratio"] = ldstratio
    _dict["onlyld"] = onlyld
    _dict["interleaved"] = interleaved
    _dict["numops"] = numops
    _dict["drambytes"] = drambytes
    if modifier != "":
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

    td = utils.get_twin_description(SuperTwin)  ##Twin description

    carm_res = {}
    carm_res["threads"] = {}
    for key in td:
        if key.find("system") != -1:
            for content in td[key]["contents"]:
                if (
                    content["@type"] == "benchmark"
                    and content["@name"] == "CARM"
                ):
                    results = content["@contents"]

                    for result in results:
                        # print("one_res:", result)
                        carm_res = fill_carm_res_dict(carm_res, result)

    return carm_res


def get_hpcg_marks(hpcg_res):

    hpcg_marks = {}

    for key in hpcg_res:
        for _res in hpcg_res[key]:
            for thr in _res:
                try:
                    hpcg_marks[thr].append((key, _res[thr]))
                except:
                    hpcg_marks[thr] = []
                    hpcg_marks[thr].append((key, _res[thr]))

    return hpcg_marks


##colors needs to be related with number of threads
##I need various different color sets for various different result sets

##This visibility thing; should keep indices, then generate, true false arrays from it
##For returning a roofline dashboard for observations; it should levitate these indices
##For buttons; probably shouldnt exist
##When there is no buttons, legend automatically comes back which is nice
#Possibly deprecated now
def generate_carm_roofline(
    SuperTwin,
):  ##THREADS as a parameter to redraw for observations

    global vis_map_all
    global vis_map_L1s
    global vis_map_L2s
    global vis_map_L3s
    global vis_map_DRAMs
    global vis_map_threads

    global next_color
    global chosen_thread_colors

    td = utils.get_twin_description(SuperTwin)  ##Twin description

    # empty_dash = obs.template_dict(SuperTwin.name + " Roofline-" + str(uuid.uuid4()))
    # empty_dash["panels"] = []

    ai = np.linspace(0.00390625, 2048, num=10000)
    # data = adcarm_benchmark.parse_adcarm_bench()
    data = adcarm_benchmark.parse_adcarm_bench(
        SuperTwin
    )  ##This is not good coding
    ###

    fig = go.Figure(layout={})
    ai_list = ai.tolist()

    # carm_res = adcarm_benchmark.parse_adcarm_bench()
    # print("carm res:", carm_res.keys())
    # print("###############")
    carm_res = get_carm_res_from_dt(SuperTwin)
    print("carm res:", carm_res.keys())

    
    for idx, key in enumerate(carm_res["threads"].keys()):
        fig = thread_groups(fig, key, colors[idx], carm_res, ai, ai_list)

    # print("##########")
    print("all:", vis_map_all)
    print("L1s:", vis_map_L1s)
    print("L2s:", vis_map_L2s)
    print("L3s:", vis_map_L3s)
    print("DRAMS:", vis_map_DRAMs)
    print("Threads:", vis_map_threads)
    # print("##########")

    ##hpcg marks
    hpcg_res = get_hpcg_bench_data(td)
    hpcg_marks = get_hpcg_marks(hpcg_res)
    print("hpcg marks:", hpcg_marks)
    ##hpcg marks

    marker_symbols = {
        "spmv": "cross-open",
        "ddot": "x-open",
        "waxpby": "hash-open",
    }

    hpcg_ai = {"spmv": 0.25, "waxpby": 0.125, "ddot": 0.125}

    next_color = -1

    for _threads in hpcg_marks:
        for _tuple in hpcg_marks[_threads]:
            _this_mark_id = get_eid()
            _name = _tuple[0]
            _res = _tuple[1]
            fig.add_trace(
                go.Scatter(
                    x=[hpcg_ai[_name]],
                    y=[_res],
                    mode="markers",
                    name=_name,
                    marker_symbol=marker_symbols[_name],
                    marker_color=chosen_thread_colors[_threads],
                    marker_size=14,
                    marker_line_width=2,
                )
            )
            vis_map_all[_threads].append(_this_mark_id)
            vis_map_threads[_threads].append(_this_mark_id)

    vis_map_all = dict(sorted(vis_map_all.items(), key=lambda t: int(t[0])))
    vis_map_L1s = dict(sorted(vis_map_L1s.items(), key=lambda t: int(t[0])))
    vis_map_L2s = dict(sorted(vis_map_L2s.items(), key=lambda t: int(t[0])))
    vis_map_L3s = dict(sorted(vis_map_L3s.items(), key=lambda t: int(t[0])))
    vis_map_DRAMs = dict(
        sorted(vis_map_DRAMs.items(), key=lambda t: int(t[0]))
    )
    vis_map_threads = dict(
        sorted(vis_map_threads.items(), key=lambda t: int(t[0]))
    )

    buttons = [
        {
            "label": "All",
            "method": "restyle",
            "args": ["visible", generate_visibility_sequence(vis_map_all)],
        },
        {
            "label": "L1s",
            "method": "restyle",
            "args": ["visible", generate_visibility_sequence(vis_map_L1s)],
        },
        {
            "label": "L2s",
            "method": "restyle",
            "args": ["visible", generate_visibility_sequence(vis_map_L2s)],
        },
        {
            "label": "L3s",
            "method": "restyle",
            "args": ["visible", generate_visibility_sequence(vis_map_L3s)],
        },
        {
            "label": "DRAMs",
            "method": "restyle",
            "args": ["visible", generate_visibility_sequence(vis_map_DRAMs)],
        },
    ]

    buttons2 = []
    for thread in vis_map_threads.keys():
        buttons2.append(
            {
                "label": thread + " thr",
                "method": "restyle",
                "args": [
                    "visible",
                    generate_visibility_sequence_from_list(
                        vis_map_threads[thread]
                    ),
                ],
            }
        )

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
                pad={"r": 4, "t": 4, "l": 0, "b": 0},  ##b?
                showactive=True,
                x=0.1,
                xanchor="left",
                y=1.15,
                yanchor="top",
            ),
            dict(
                type="buttons",
                direction="right",
                buttons=buttons2,
                pad={"r": 4, "t": 4, "l": 0, "b": 0},  ##b?
                showactive=True,
                x=0.1,
                xanchor="left",
                y=1.25,
                yanchor="top",
            ),
        ]
    )

    fig = rdp.grafana_layout(fig)  ##return this, ##parameterise this

    return fig


def get_indicator_fields(_string):

    value = -1
    prefix = ""
    suffix = ""
    for idx, char in enumerate(_string):
        if char.isdigit():
            value = int(_string[idx])
            prefix = _string[0 : idx - 1]
            suffix = _string[idx + 1 :]

    return value, prefix, suffix


def get_indicator_fields_vector(_array):

    value = -1
    prefix = ""
    suffix = ""

    _string = ""
    for idx, item in enumerate(_array):
        _string += item
        _string += " "
        if (
            idx == 3 and len(_array) >= 6
        ):  ##Just aesthetical, change the values and see
            _string += "<br>"
    _string = _string[:-1]

    for idx, char in enumerate(_string):
        if char.isdigit():
            value = int(_string[idx])
            prefix = _string[0:idx]
            suffix = _string[idx + 1 :]
            break

    print("vps:", value, prefix, suffix)
    return value, prefix, suffix


def generate_info_panel(SuperTwin):

    td = utils.get_twin_description(SuperTwin)  ##Twin description
    data = utils.fill_data(td, SuperTwin.name, SuperTwin.addr)

    number_size = 24
    title_size = 18

    fig = go.Figure(layout={})

    value, prefix, suffix = get_indicator_fields(data["cpu_model"])
    fig.add_trace(
        go.Indicator(
            mode="number",
            value=value,
            number={
                "font": {"color": "black", "size": number_size},
                "prefix": prefix,
                "suffix": suffix,
            },
            title={
                "text": "CPU",
                "font": {"color": "gray", "size": title_size},
            },
            domain={"row": 0, "column": 1},
        )
    )

    number_size = 36
    ##Don't need to do split prefix suffix thing if value is simply a number
    fig.add_trace(
        go.Indicator(
            mode="number",
            value=int(data["system_no_numa_nodes"]),
            number={
                "font": {"color": "black", "size": number_size},
                "prefix": "",
                "suffix": "",
            },
            title={
                "text": "Numa Nodes",
                "font": {"color": "gray", "size": title_size},
            },
            domain={"row": 1, "column": 0},
        )
    )

    fig.add_trace(
        go.Indicator(
            mode="number",
            value=int(data["cpu_cores"]),
            number={
                "font": {"color": "black", "size": number_size},
                "prefix": "",
                "suffix": "",
            },
            title={
                "text": "Core Per Node",
                "font": {"color": "gray", "size": title_size},
            },
            domain={"row": 1, "column": 1},
        )
    )

    fig.add_trace(
        go.Indicator(
            mode="number",
            value=int(data["cpu_threads_per_core"]),
            number={
                "font": {"color": "black", "size": number_size},
                "prefix": "",
                "suffix": "",
            },
            title={
                "text": "Thread Per Core",
                "font": {"color": "gray", "size": title_size},
            },
            domain={"row": 1, "column": 2},
        )
    )

    fig.add_trace(
        go.Indicator(
            mode="number",
            value=int(data["l1dcache_size"].strip(" kB")),
            number={
                "font": {"color": "black", "size": number_size},
                "prefix": "",
                "suffix": "kB",
            },
            title={
                "text": "L1D Cache Size",
                "font": {"color": "gray", "size": title_size},
            },
            domain={"row": 2, "column": 0},
        )
    )

    l2mb = False
    strip = ""
    suffix = ""
    if data["l2cache_size"].find("MB") != -1:
        l2mb = True
    if l2mb:
        strip = " MB"
        suffix = "MB"
    else:
        strip = " kB"
        suffix = " kB"

    fig.add_trace(
        go.Indicator(
            mode="number",
            value=int(data["l2cache_size"].strip(strip)),
            number={
                "font": {"color": "black", "size": number_size},
                "prefix": "",
                "suffix": suffix,
            },
            title={
                "text": "L2 Cache Size",
                "font": {"color": "gray", "size": title_size},
            },
            domain={"row": 2, "column": 1},
        )
    )

    fig.add_trace(
        go.Indicator(
            mode="number",
            value=float(data["l3cache_size"].strip(" MB")),
            number={
                "font": {"color": "black", "size": number_size},
                "prefix": "",
                "suffix": "MB",
            },
            title={
                "text": "L3 Cache Size",
                "font": {"color": "gray", "size": title_size},
            },
            domain={"row": 2, "column": 2},
        )
    )

    fig.add_trace(
        go.Indicator(
            mode="number",
            value=int(data["l1dcache_associativity"]),
            number={
                "font": {"color": "black", "size": number_size},
                "prefix": "",
                "suffix": "",
            },
            title={
                "text": "L1D Association",
                "font": {"color": "gray", "size": title_size},
            },
            domain={"row": 3, "column": 0},
        )
    )

    fig.add_trace(
        go.Indicator(
            mode="number",
            value=int(data["l1dcache_linesize"]),
            number={
                "font": {"color": "black", "size": number_size},
                "prefix": "",
                "suffix": "",
            },
            title={
                "text": "L1D Cacheline Size",
                "font": {"color": "gray", "size": title_size},
            },
            domain={"row": 3, "column": 1},
        )
    )

    fig.add_trace(
        go.Indicator(
            mode="number",
            value=int(data["l1dcache_nosets"]),
            number={
                "font": {"color": "black", "size": number_size},
                "prefix": "",
                "suffix": "",
            },
            title={
                "text": "L1D No Sets",
                "font": {"color": "gray", "size": title_size},
            },
            domain={"row": 3, "column": 2},
        )
    )

    fig.add_trace(
        go.Indicator(
            mode="number",
            value=int(data["l2cache_associativity"]),
            number={
                "font": {"color": "black", "size": number_size},
                "prefix": "",
                "suffix": "",
            },
            title={
                "text": "L2 Association",
                "font": {"color": "gray", "size": title_size},
            },
            domain={"row": 4, "column": 0},
        )
    )

    fig.add_trace(
        go.Indicator(
            mode="number",
            value=int(data["l2cache_linesize"]),
            number={
                "font": {"color": "black", "size": number_size},
                "prefix": "",
                "suffix": "",
            },
            title={
                "text": "L2 Cacheline Size",
                "font": {"color": "gray", "size": title_size},
            },
            domain={"row": 4, "column": 1},
        )
    )

    fig.add_trace(
        go.Indicator(
            mode="number",
            value=int(data["l2cache_nosets"]),
            number={
                "font": {"color": "black", "size": number_size},
                "prefix": "",
                "suffix": "",
            },
            title={
                "text": "L2 No Sets",
                "font": {"color": "gray", "size": title_size},
            },
            domain={"row": 4, "column": 2},
        )
    )

    fig.add_trace(
        go.Indicator(
            mode="number",
            value=int(data["l3cache_associativity"]),
            number={
                "font": {"color": "black", "size": number_size},
                "prefix": "",
                "suffix": "",
            },
            title={
                "text": "L3 Association",
                "font": {"color": "gray", "size": title_size},
            },
            domain={"row": 5, "column": 0},
        )
    )

    fig.add_trace(
        go.Indicator(
            mode="number",
            value=int(data["l3cache_linesize"]),
            number={
                "font": {"color": "black", "size": number_size},
                "prefix": "",
                "suffix": "",
            },
            title={
                "text": "L3 Cacheline Size",
                "font": {"color": "gray", "size": title_size},
            },
            domain={"row": 5, "column": 1},
        )
    )

    fig.add_trace(
        go.Indicator(
            mode="number",
            value=int(data["l3cache_nosets"]),
            number={
                "font": {"color": "black", "size": number_size},
                "prefix": "",
                "suffix": "",
            },
            title={
                "text": "L3 No Sets",
                "font": {"color": "gray", "size": title_size},
            },
            domain={"row": 5, "column": 2},
        )
    )

    number_size = 24
    value, prefix, suffix = get_indicator_fields_vector(data["sse_vector"])
    fig.add_trace(
        go.Indicator(
            mode="number",
            value=value,
            number={
                "font": {"color": "black", "size": number_size},
                "prefix": prefix,
                "suffix": suffix,
            },
            title={
                "text": "Supported SSE Instructions",
                "font": {"color": "gray", "size": title_size},
            },
            domain={"row": 6, "column": 1},
        )
    )

    value, prefix, suffix = get_indicator_fields_vector(data["avx_vector"])
    fig.add_trace(
        go.Indicator(
            mode="number",
            value=value,
            number={
                "font": {"color": "black", "size": number_size},
                "prefix": prefix,
                "suffix": suffix,
            },
            title={
                "text": "Supported AVX Instructions",
                "font": {"color": "gray", "size": title_size},
            },
            domain={"row": 7, "column": 1},
        )
    )

    fig = rdp.grafana_layout_2(fig)
    fig.update_layout(grid={"rows": 8, "columns": 3, "pattern": "independent"})
    return fig


def get_stream_bench_data(td):

    stream_res = {}

    for key in td:
        if key.find("system") != -1:
            for content in td[key]["contents"]:
                if (
                    content["@type"] == "benchmark"
                    and content["@name"] == "STREAM"
                ):
                    results = content["@contents"]
                    results = sorted(results, key=lambda d: d["@threads"])
                    # print("results:", results)

                    for result in results:
                        name = result["@field"]
                        threads = str(result["@threads"])
                        affinity = ""
                        try:
                            affinity = result["@modifier"][1].split(" ")[-1]
                            # name += " numa bind"
                        except:
                            pass
                        _res = float(result["@result"]) / 1024
                        # print("Name:", name, "threads:", threads, "affinity:", affinity, "_res:", _res)
                        if name.find("Max_Thr") == -1:
                            try:
                                stream_res[name].append({threads: _res})
                            except:
                                stream_res[name] = []
                                stream_res[name].append({threads: _res})

    return stream_res


def generate_x(stream_res):

    x = []
    keys = list(stream_res.keys())
    # print("keys:", keys)
    for item in stream_res[keys[0]]:
        to_app = int(list(item.items())[0][0])
        x.append(to_app)

    return x


def generate_y(stream_res_key):

    y = []
    for item in stream_res_key:
        y.append(list(item.items())[0][1])

    return y


def generate_stream_panel(SuperTwin):

    td = utils.get_twin_description(SuperTwin)
    fig = go.Figure(layout={})

    stream_res = get_stream_bench_data(td)
    x = generate_x(stream_res)

    for key in stream_res:
        gc = get_next_color()
        fig.add_trace(
            go.Scatter(
                x=x,
                y=generate_y(stream_res[key]),
                mode="lines",
                name=key,
                line=line_spec(gc, ""),
            )
        )

    xtickvals = [str(xx) for xx in x]
    fig.update_layout(font_size=16)
    fig.update_xaxes(showspikes=True)
    fig.update_yaxes(showspikes=True)
    fig.update_traces(hovertemplate="%{y}")
    fig.update_layout(hovermode="x")
    fig = rdp.grafana_layout_3(
        fig, xtickvals, "GB/s"
    )  ##return this, ##parameterise this
    print("Returning")
    return fig


def get_hpcg_bench_data(td):

    hpcg_res = {}

    for key in td:
        if key.find("system") != -1:
            for content in td[key]["contents"]:
                if (
                    content["@type"] == "benchmark"
                    and content["@name"] == "HPCG"
                ):
                    results = content["@contents"]
                    results = sorted(results, key=lambda d: d["@threads"])

                    for result in results:
                        name = result["@field"]
                        threads = str(result["@threads"])
                        affinity = ""
                        try:
                            affinity = result["@modifier"][1].split(" ")[-1]
                            # name += " numa bind" ## This may change later
                        except:
                            pass
                        _res = float(result["@result"])
                        # print("Name:", name, "threads:", threads, "affinity:", affinity, "_res:", _res)
                        if name.find("Max_Thr") == -1:
                            try:
                                hpcg_res[name].append({threads: _res})
                            except:
                                hpcg_res[name] = []
                                hpcg_res[name].append({threads: _res})

    print("hpcg_res:", hpcg_res)
    return hpcg_res


def generate_hpcg_panel(
    SuperTwin,
):  ##Tricky part is marking results on the roofline

    td = utils.get_twin_description(
        SuperTwin
    )  ##This line keeps repeating because we may call
    fig = go.Figure(layout={})  ##these generate panel functions on their own

    hpcg_res = get_hpcg_bench_data(td)
    ##hpcg_marks = get_hpcg_bench_marks() ##Make this global, and let roofline call it

    x = generate_x(hpcg_res)

    for key in hpcg_res:
        gc = get_next_color()
        fig.add_trace(
            go.Scatter(
                x=x,
                y=generate_y(hpcg_res[key]),
                mode="lines",
                name=key,
                line=line_spec(gc, ""),
            )
        )

    xtickvals = [str(xx) for xx in x]
    fig.update_layout(font_size=16)
    fig.update_xaxes(showspikes=True)
    fig.update_yaxes(showspikes=True)
    fig.update_traces(hovertemplate="%{y}")
    fig.update_layout(hovermode="x")
    fig = rdp.grafana_layout_3(
        fig, xtickvals, "GFLOP/s"
    )  ##return this, ##parameterise this
    print("Returning")
    return fig

#Function that returns the thread_set used by the various benchmarks
def get_thread_set(SuperTwin):
    
    td = utils.get_twin_description(SuperTwin)  ##Twin description
    mt_info = utils.get_multithreading_info(td)
    no_cores_per_socket = mt_info["no_cores_per_socket"]
    no_threads_per_socket = mt_info["no_threads_per_socket"]
    total_cores = mt_info["total_cores"]
    total_threads = mt_info["total_threads"]
    thread_set = []
    thr = 1

    while(thr < total_threads):
        thread_set.append(thr)
        thr = thr * 2

    if no_cores_per_socket not in thread_set:
        thread_set.append(no_cores_per_socket)

    if no_threads_per_socket not in thread_set:
        thread_set.append(no_threads_per_socket)

    if total_cores not in thread_set:
        thread_set.append(total_cores)

    if total_threads not in thread_set:
        thread_set.append(total_threads)

    #thread_set = [16] ## for debug purposes
    thread_set = list(sorted(thread_set))

    print(thread_set)

    return thread_set

#Function that generates the rooflinecontrol dashboard variable, based on number of threads of the cpu
def generate_dashboard_variable(thread_set, number):

    
    tester = {}
    tester["current"] = {}
    tester["current"]["selected"] = True
    if (number == 1):
        tester["current"]["text"] = "1"
        tester["current"]["value"] = "1"
        tester["label"] = "Live Cache Aware Roofline Model Thread Count"
        tester["name"] = "rooflinecontrol"
        tester["description"] = "Select the static Roofline results for a particular number of threads"
    elif (number == 2):
        tester["current"]["text"] = "None"
        tester["current"]["value"] = "None"
        tester["label"] = "Live Cache Aware Roofline Model Thread Count 2"
        tester["name"] = "rooflinecontrol2"
        tester["description"] = "Select the static Roofline results for a particular number of threads"
        
    elif (number == 3):
        tester["current"]["text"] = "None"
        tester["current"]["value"] = "None"
        tester["label"] = "Display Benchmark"
        tester["name"] = "benchmarkcontrol"
        tester["description"] = "Display Benchmarks to be plotted in the CARM graph."

    tester["includeAll"] = False
    tester["hide"] = 0
    tester["multi"] = False

    tester["options"] = []


    if(number == 1 or number == 2):
        if (number == 2):
            tester["options"].append({
                "selected": False,
                "text": "None",
                "value": "None"
            },)
        for thread in thread_set:
            tester["options"].append({
                "selected": False,
                "text": str(thread),
                "value": str(thread)
            },)
    
        query_numbers = ', '.join(str(thread) for thread in thread_set)
        if (number == 1):
            tester_query = f"{query_numbers}"
        elif (number == 2):
            tester_query = f"None, {query_numbers}"
    elif (number == 3):
        tester["options"].append({
                "selected": False,
                "text": "None",
                "value": "None"
            },)
        tester["options"].append({
                "selected": False,
                "text": "spmv",
                "value": "spmv"
            },)
        tester["options"].append({
                "selected": False,
                "text": "ddot",
                "value": "ddot"
            },)
        tester["options"].append({
                "selected": False,
                "text": "waxpby",
                "value": "waxpby"
            },)
        tester["options"].append({
                "selected": False,
                "text": "All",
                "value": "All"
            },)
        tester_query = f"None, spmv, ddot, waxpby, All"
        

    tester["querry"] = tester_query
    tester["queryValue"] = ""
    tester["skipUrlSync"] = False
    tester["type"] = "custom"

    return  tester

#function that auto generates the script part of the live-carm graph, based on thread number of the machine
def generate_live_carm_script(thread_set, SuperTwin):

    data = get_carm_res_from_dt(SuperTwin)
    td = utils.get_twin_description(SuperTwin)

    panelMaxY = 0

    results = {}

    ai = np.linspace(0.00390625, 256, num=200000)

    script = ''

    script += f'let timestamps = data.series[0].fields[0].values;\nlet ai = data.series[0].fields[1].values;\nlet gflops = data.series[0].fields[2].values;\n\n'
    script += f"// Format timestamps into human-readable dates\nlet formattedTimestamps = timestamps.map(timestamp => {{\n  let date = new Date(timestamp);\n  let hours = date.getHours().toString().padStart(2, '0');\n  let minutes = date.getMinutes().toString().padStart(2, '0');\n  let seconds = date.getSeconds().toString().padStart(2, '0');\n  let day = date.getDate().toString().padStart(2, '0');\n  let month = (date.getMonth() + 1).toString().padStart(2, '0'); // Months are 0-based, so add 1\n  let year = date.getFullYear();\n  return `${{hours}}:${{minutes}}:${{seconds}} ${{day}}-${{month}}-${{year}}`;\n}});\n\n"
    script += f"let trace0 = {{\n  x: ai,\n  y: gflops,\n  name : \"CARM\",\n  text: formattedTimestamps,\n  mode: 'markers', // Specify marker mode for scatter plot\n  type: 'scatter', // Specify trace type as scatter plot\n  marker: {{\n    size: 10, // Set marker size as needed\n    color: timestamps // Set marker color as needed\n  }}\n}};\n"

    for cpu in thread_set:
        thread_number = str(cpu)

        if thread_number in data["threads"]:
            
            values_for_thread = data["threads"][thread_number]
            # Now, values_for_thread contains the list of dictionaries for the specified thread number

            # You can access specific values from this list of dictionaries
            for item in values_for_thread:
                ai = np.linspace(0.00390625, 256, num=200000)
                L1_eq = carm_eq(ai, item["L1"], item['FP'])
                L2_eq = carm_eq(ai, item['L2'], item['FP'])
                L3_eq = carm_eq(ai, item['L3'], item['FP'])
                DRAM_eq = carm_eq(ai, item['DRAM'], item['FP'])

                ai_list = ai.tolist()
                L1_eq_list = L1_eq.tolist()
                L2_eq_list = L2_eq.tolist()
                L3_eq_list = L3_eq.tolist()
                DRAM_eq_list = DRAM_eq.tolist()

                results["L1sx"] = float(ai_list[0])
                results["L1sy"] = float(L1_eq_list[0])
                results["L2sy"] = float(L2_eq_list[0])
                results["L3sy"] = float(L3_eq_list[0])
                results["DRAMsy"] = float(DRAM_eq_list[0])

                for i in range(1, len(L1_eq_list)):
                    if(L1_eq_list[i-1] == L1_eq_list[i]):
                        results["L1mx"] = float(ai[i])
                        results["L1my"] = float(L1_eq_list[i])
                        if(float(results["L1my"]) > panelMaxY):
                            panelMaxY = results["L1my"]
                        break
                for i in range(1, len(L2_eq_list)):
                    if(L2_eq_list[i-1] == L2_eq_list[i]):
                        results["L2mx"] = float(ai[i])
                        break
                for i in range(1, len(L3_eq_list)):
                    if(L3_eq_list[i-1] == L3_eq_list[i]):
                        results["L3mx"] = float(ai[i])
                        break
                for i in range(1, len(DRAM_eq_list)):
                    if(DRAM_eq_list[i-1] == DRAM_eq_list[i]):
                        results["DRAMmx"] = float(ai[i])
                        break

                script += f'let l1x{cpu} = [0, {results["L1sx"]}, {results["L1mx"]}, 8192];\n'
                script += f'let l1y{cpu} = [0, {results["L1sy"]}, {results["L1my"]}, {results["L1my"]}];\n'
                script += f'let l2x{cpu} = [0, {results["L1sx"]}, {results["L2mx"]}];\n'
                script += f'let l2y{cpu} = [0, {results["L2sy"]}, {results["L1my"]}];\n'
                script += f'let l3x{cpu} = [0, {results["L1sx"]}, {results["L3mx"]}];\n'
                script += f'let l3y{cpu} = [0, {results["L3sy"]}, {results["L1my"]}];\n'
                script += f'let dramx{cpu} = [0, {results["L1sx"]}, {results["DRAMmx"]}];\n'
                script += f'let dramy{cpu} = [0, {results["DRAMsy"]}, {results["L1my"]}];\n\n'

            else:
                print(f"No data found for thread number {thread_number}")
       
    # Add the threadNumber variable at the end
    script += 'let threadNumber = variables.rooflinecontrol;\nlet threadNumber2 = variables.rooflinecontrol2;\nlet benchmarkcontrol = variables.benchmarkcontrol;\n\n'

    trace_names = ["DRAM", "L1", "L2", "L3"]

    # Define the template for the trace
    trace_template = """
    let trace{index} = {{
    x: {type}x{thread},
    y: {type}y{thread},
    order: "natural",
    name: "{name}",
    type: 'scatter',
    mode: 'lines+markers',
    marker: {{
        size: 2,
        symbol: 'square',
        color: "{color}"
    }},
    line: {{
        "color": "{color}",
        "dash": "{dash}",
        "shape": "linear",
        "width": 3
    }},
    }};
    """

    # Loop to generate the code for each thread and change names accordingly
    total = 0
    for cpu in thread_set:
        gc = get_next_color()
        if cpu not in chosen_thread_colors.keys():
            chosen_thread_colors[cpu] = gc
        for i in range (1, 5):
            name = trace_names[i % 4]
            dash = "solid" 
            if i % 4 == 2:
                dash = "dash" 
            elif i % 4 == 3:
                dash = "dashdot" 
            elif i % 4 == 0:
                dash = "dot"
            total += 1
           
            script += trace_template.format(index=total, color=gc, thread=cpu, name=name, type=name.lower(), dash=dash)
            
    
    hpcg_res = get_hpcg_bench_data(td)
    hpcg_marks = get_hpcg_marks(hpcg_res)
    print("hpcg marks:", hpcg_marks)
    ##hpcg marks
    print(chosen_thread_colors)

    marker_symbols = {
        "spmv": "cross-open",
        "ddot": "x-open",
        "waxpby": "hash-open",
    }

    hpcg_ai = {"spmv": 0.25, "waxpby": 0.125, "ddot": 0.125}

    # Define the template for the trace
    trace_template2 = """
    let {name}{index} = {{
    x: [{ai}],
    y: [{result}],
    order: "natural",
    name: "{name}",
    type: 'scatter',
    mode: 'markers',
    marker: {{
        size: 15,
        symbol: "{symbol}",
        color: "{color}"
    }},}};
    """

    for _threads in hpcg_marks:
        #gc = get_next_color()
        for _tuple in hpcg_marks[_threads]:
            
            _name = _tuple[0]
            _res = _tuple[1]
            total += 1
           
            script += trace_template2.format(index=_threads, ai=hpcg_ai[_name],color=chosen_thread_colors[int(_threads)], thread=cpu, result=_res, name=_name, type=name.lower(), symbol=marker_symbols[_name])

    
    
    # Define the base trace
    base_trace = "trace0"

    # Initialize an empty list for each group of traces
    traces = []

    total = 1
    # Loop to generate the code
    for i in thread_set:
        # Create traces for the current group
        
        group_traces = [f"trace{total + j}" for j in range(4)]
        total += 4

        # Combine the base trace and group traces into a data array
        data_array = [base_trace] + group_traces

        # Append the JavaScript code for this threadNumber
        script += f'else if (threadNumber == {i})' + '{\n'
        script += f'data = [{", ".join(data_array)}]\n'
        if(hpcg_marks != None):
            script += "if (benchmarkcontrol == 'spmv'){"
            script += f'data = data.concat([{"spmv"+str(i)}])\n'
            script += '}'
            script += "else if (benchmarkcontrol == 'ddot'){"
            script += f'data = data.concat([{"ddot"+str(i)}])\n'
            script += '}'
            script += "else if (benchmarkcontrol == 'waxpby'){"
            script += f'data = data.concat([{"waxpby"+str(i)}])\n'
            script += '}'
            script += "else if (benchmarkcontrol == 'All'){"
            script += f'data = data.concat([{"spmv"+str(i)}, {"ddot"+str(i)}, {"waxpby"+str(i)}])\n'
            script += '}'
        #script += f'    return {{ data: [{", ".join(data_array)}] }};\n'
        script += '}'

        # Extend the list of all traces
        traces.extend(group_traces)

    # Remove the leading 'else' from the first condition
    script = script.replace('else if (threadNumber == 1)', '\n\nif (threadNumber == 1)')

    #script += f'else if (threadNumber == \"1 + Max\"){{\n return {{ data: [trace0, trace1, trace2, trace3, trace4, trace{total-4}, trace{total-3}, trace{total-2}, trace{total-1}] }};\n}}else {{return {{ data: [trace0]}}}};\n'
    script += f'else {{data = [trace0]}};\n'

    traces = []

    total = 1
    # Loop to generate the code
    for i in thread_set:
        # Create traces for the current group
        
        group_traces = [f"trace{total + j}" for j in range(4)]
        total += 4

        # Combine the base trace and group traces into a data array
        data_array = group_traces

        # Append the JavaScript code for this threadNumber
        script += f'else if (threadNumber2 == {i})' + '{\n'
        script += f'data = data.concat([{", ".join(data_array)}])\n'
        if(hpcg_marks != None):
            script += "if (benchmarkcontrol == 'spmv'){"
            script += f'data = data.concat([{"spmv"+str(i)}])\n'
            script += '}'
            script += "else if (benchmarkcontrol == 'ddot'){"
            script += f'data = data.concat([{"ddot"+str(i)}])\n'
            script += '}'
            script += "else if (benchmarkcontrol == 'waxpby'){"
            script += f'data = data.concat([{"waxpby"+str(i)}])\n'
            script += '}'
            script += "else if (benchmarkcontrol == 'All'){"
            script += f'data = data.concat([{"spmv"+str(i)}, {"ddot"+str(i)}, {"waxpby"+str(i)}])\n'
            script += '}'
        #script += f'    return {{ data: [{", ".join(data_array)}] }};\n'
        script += '}'

        # Extend the list of all traces
        traces.extend(group_traces)

    # Remove the leading 'else' from the first condition
    script = script.replace('else if (threadNumber2 == 1)', '\n\nif (threadNumber2 == 1)')

    

    #script += f'else if (threadNumber == \"1 + Max\"){{\n return {{ data: [trace0, trace1, trace2, trace3, trace4, trace{total-4}, trace{total-3}, trace{total-2}, trace{total-1}] }};\n}}else {{return {{ data: [trace0]}}}};\n'
    #script += f'else {{data = [trace0]}};\n'

    
    script += f'\n\nreturn {{data}};'

    return script, panelMaxY

def next_power_of_2(n):
    # Use bitwise left shift to find the next power of 2
    if n <= 0:
        return 1
    else:
        return 2**(int(n) - 1).bit_length()


def generate_roofline_dashboard(SuperTwin):
    global next_color

    td = utils.get_twin_description(SuperTwin)  ##Twin description
    data = utils.fill_data(td, SuperTwin.name, SuperTwin.addr)
    cpu_count = int(data["cpu_cores"] * data["cpu_threads_per_core"]) # * data[socket_count]

    thread_set = get_thread_set(SuperTwin)

    empty_dash = obs.template_dict(
        SuperTwin.name + " Roofline-" + str(uuid.uuid4())
    )
    
    #Generating the dashboard variables, used by the live-CARM graph
    empty_dash["templating"]["list"].append(generate_dashboard_variable(thread_set, 1))
    empty_dash["templating"]["list"].append(generate_dashboard_variable(thread_set, 2))
    empty_dash["templating"]["list"].append(generate_dashboard_variable(thread_set, 3))

    empty_dash["panels"] = []

    #roofline_fig = generate_carm_roofline(SuperTwin)
    next_color = -1
    info_fig = generate_info_panel(SuperTwin)
    next_color = -1
    stream_bench_fig = generate_stream_panel(SuperTwin)
    hpcg_bench_fig = generate_hpcg_panel(SuperTwin)
    next_color = -1

    #dict_roofline_fig = obs.json.loads(io.to_json(roofline_fig))
    #empty_dash["panels"].append(
    #    rdp.two_templates_one(
    #        dict_roofline_fig["data"], dict_roofline_fig["layout"], SuperTwin.grafana_datasource
    #    )
    #)

    dict_info_fig = obs.json.loads(io.to_json(info_fig))
    empty_dash["panels"].append(
        rdp.two_templates_two(dict_info_fig["data"], dict_info_fig["layout"], SuperTwin.grafana_datasource)
    )

    for pmu_name in SuperTwin.pmu_metrics.keys():
        for pmu_generic_event in pmu_mapping_utils._DEFAULT_GENERIC_PMU_EVENTS:
            formula = [
                pmu_event
                for pmu_event in pmu_mapping_utils.get(
                    pmu_name, pmu_generic_event
                )
                if pmu_event.isupper()
            ]
            if len(formula) == 0:
                continue
            
            if pmu_generic_event == "CARM":

                script, maxY = generate_live_carm_script(thread_set, SuperTwin)

                print (script)

                empty_dash["panels"].append(
                    pmu_grafana_utils.dashboard_livecarm_table(
                        pmu_name,
                        SuperTwin.grafana_datasource,
                        "Live Cache Aware Roofline Model",
                        cpu_count, # * data[socket_count]
                        formula,
                        script,
                        math.log10(next_power_of_2(maxY))+0.02
                    )
                ) 

    dict_stream_bench_fig = obs.json.loads(io.to_json(stream_bench_fig))
    empty_dash["panels"].append(rdp.two_templates_three(dict_stream_bench_fig["data"],
                                                        dict_stream_bench_fig["layout"],
                                                        8, 8 , 0, 16, SuperTwin.grafana_datasource, "STREAM Benchmark", 442))

    
    dict_hpcg_bench_fig = obs.json.loads(io.to_json(hpcg_bench_fig))
    empty_dash["panels"].append(rdp.two_templates_three(dict_hpcg_bench_fig["data"],
                                                        dict_hpcg_bench_fig["layout"],
                                                        8, 8, 8, 16, SuperTwin.grafana_datasource, "HPCG Benchmark", 443))
    
    ## Add pmu events
    for pmu_name in SuperTwin.pmu_metrics.keys():
        for pmu_generic_event in pmu_mapping_utils._DEFAULT_GENERIC_PMU_EVENTS:
            formula = [
                pmu_event
                for pmu_event in pmu_mapping_utils.get(
                    pmu_name, pmu_generic_event
                )
                if pmu_event.isupper()
            ]
            if len(formula) == 0:
                continue

            if pmu_generic_event != "CARM":
                empty_dash["panels"].append(
                    pmu_grafana_utils.dashboard_pmu_table(
                        SuperTwin.grafana_datasource,
                        pmu_generic_event,
                        cpu_count,  # * data[socket_count]
                        formula,
                    )
                )
                empty_dash["panels"].append(
                    pmu_grafana_utils.dashboard_pmu_table_total(
                        SuperTwin.grafana_datasource,
                        pmu_generic_event,
                        cpu_count, # * data[socket_count]
                        formula,
                    )
                )

    print("Upload?")
    ###
    json_dash_obj = obs.get_dashboard_json(empty_dash, overwrite=False)
    g_url = obs.upload_to_grafana(
        json_dash_obj, SuperTwin.grafana_addr, SuperTwin.grafana_token
    )
    print("Generated:", g_url)
    return g_url["url"]
