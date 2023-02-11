import sys
import pandas as pd
import plotly.graph_objects as go
#from plotly import tools
from plotly.subplots import make_subplots
import plotly.io as pio
#pio.templates

#pio.kaleido.scope.default_width = 1200
#pio.kaleido.scope.default_heigth = 500
colors_4 = ["rgb(6,150,104)", "rgb(195,222,155)", "rgb(52,75,70)", "rgb(121,235,153)", "rgb(101,139,131)"]

def one_size(metrics, alias):
    
    _file = sys.argv[1]
    data = pd.read_csv(_file, index_col=False)

    print("_file:", _file)
    print("metrics:", metrics)
    print("alias:", alias)
    
    print("data:", data)
    #print(data["alias"])

    xx =["1", "1/2", "1/4", "1/8", "1/16"]

    #s_10 = data.loc["alias":"luna10"]
    metrics = metrics 
    s_20 = data.loc[data["alias"] == alias]
    
    pmcd_cpu = s_20.loc[s_20["component"] == "pmcd"]
    pmcd_cpu = list(pmcd_cpu["cpu_use_mean"])
    pmcd_cpu_err = s_20.loc[s_20["component"] == "pmcd"]
    pmcd_cpu_err = list(pmcd_cpu_err["cpu_use_std"])

    linux_cpu = s_20.loc[s_20["component"] == "pmdalinux"]
    linux_cpu = list(linux_cpu["cpu_use_mean"])
    linux_cpu_err = s_20.loc[s_20["component"] == "pmdalinux"]
    linux_cpu_err = list(linux_cpu_err["cpu_use_std"])

    proc_cpu = s_20.loc[s_20["component"] == "pmdaproc"]
    proc_cpu = list(proc_cpu["cpu_use_mean"])
    proc_cpu_err = s_20.loc[s_20["component"] == "pmdaproc"]
    proc_cpu_err = list(proc_cpu_err["cpu_use_std"])

    perfevent_cpu = s_20.loc[s_20["component"] == "pmdaperfevent"]
    perfevent_cpu = list(perfevent_cpu["cpu_use_mean"])
    perfevent_cpu_err = s_20.loc[s_20["component"] == "pmdaperfevent"]
    perfevent_cpu_err = list(perfevent_cpu_err["cpu_use_std"])

    total = []
    for i in range(len(linux_cpu)):
        total.append(linux_cpu[i] + pmcd_cpu[i] + proc_cpu[i] + perfevent_cpu[i])
    

    print(s_20)
    print(linux_cpu)
    print(pmcd_cpu)
    print(proc_cpu)
    print(perfevent_cpu)
    print(total)

    
    ##cpus and errs
    trace1 = go.Bar(name="pmcd",
                    x=xx,
                    y=pmcd_cpu,
                    error_y = dict(type='data', array=pmcd_cpu_err),
                    marker_color = colors_4[0])
    #update_yaxes(type="log", dtick=0.30102999566, fontsize="25")
    trace2 = go.Bar(name="pmdaperfevent",
                    x=xx,
                    y=perfevent_cpu,
                    error_y = dict(type='data', array=perfevent_cpu_err),
                    marker_color = colors_4[1])
        
    trace3 = go.Bar(name="pmdalinux",
                    x=xx,
                    y=linux_cpu,
                    error_y = dict(type='data', array=linux_cpu_err),
                    marker_color = colors_4[2])
    
    trace4 = go.Bar(name="pmdaproc",
                    x=xx,
                    y=proc_cpu,
                    error_y = dict(type='data', array=proc_cpu_err),
                    marker_color = colors_4[3])
    ##cpus and errs

    ##mem
    pmcd_mem = s_20.loc[s_20["component"] == "pmcd"]
    pmcd_mem = list(pmcd_mem["mem_use_mean"])
    
    linux_mem = s_20.loc[s_20["component"] == "pmdalinux"]
    linux_mem = list(linux_mem["mem_use_mean"])
    
    proc_mem = s_20.loc[s_20["component"] == "pmdaproc"]
    proc_mem = list(proc_mem["mem_use_mean"])
    
    perfevent_mem = s_20.loc[s_20["component"] == "pmdaperfevent"]
    perfevent_mem = list(perfevent_mem["mem_use_mean"])

    trace5 = go.Bar(name="pmcd",
                     x=xx,
                     y=pmcd_mem,
                     offsetgroup=0,
                    marker_color = colors_4[0],
                    showlegend=False)
    
    trace6 = go.Bar(name="perfevent",
                     x=xx,
                     y=perfevent_mem,
                     offsetgroup=0,
                     base=pmcd_mem,
                    marker_color = colors_4[1],
                    showlegend=False)

    base = [sum(x) for x in zip(pmcd_mem,perfevent_mem)]
    trace7 = go.Bar(name="linux",
                    x=xx,
                    y=linux_mem,
                    offsetgroup=0,
                    base=base,
                    marker_color = colors_4[2],
                    showlegend=False)
    
    base = [sum(x) for x in zip(pmcd_mem,perfevent_mem,linux_mem)]
    trace8 = go.Bar(name="proc",
                     x=xx,
                     y=proc_mem,
                     offsetgroup=0,
                     base=base,
                    marker_color = colors_4[3],
                    showlegend=False)

    ##network and elements
    net = s_20.loc[s_20["component"] == "network"]
    net = list(net["net_use_mean"])
    net_err = s_20.loc[s_20["component"] == "network"]
    net_err = list(net_err["net_use_std"])

    net = [x/1024 for x in net]
    net_err = [x/1024 for x in net_err]
    
    datapoints = s_20.loc[s_20["component"] == "datapoints"]
    datapoints = list(datapoints["total_datapoints"])
    print("datapoints:", datapoints)

    trace9 = go.Bar(name = "network",
                    x = xx,
                    y = net,
                    error_y = dict(type='data', array=net_err),
                    marker_color = colors_4[4])
                    


    #trace9 = go.Bar(name = "datapoints",
    #                x = xx,
    #                y = datapoints,
    #                yaxis = 'y4')
    
    ##network and elements
    
    fig = make_subplots(rows=1, cols=3, column_widths=[0.7, 0.2, 0.1], horizontal_spacing=0.075, shared_xaxes=True)
    fig.append_trace(trace1, 1,1)
    fig.append_trace(trace2, 1,1)
    fig.append_trace(trace3, 1,1)
    fig.append_trace(trace4, 1,1)
    fig.append_trace(trace5, 1,2)
    fig.append_trace(trace6, 1,2)
    fig.append_trace(trace7, 1,2)
    fig.append_trace(trace8, 1,2)
    fig.append_trace(trace9, 1,3)
    
    fig.update_traces(texttemplate='  %{y:.2f}', textposition='auto')
    fig.update_layout(legend=dict(yanchor="top",y=1.025,xanchor="left",x=0.01,orientation="h"))
    fig.update_traces(marker_line_color='rgb(0,0,0)',marker_line_width=1, opacity=1)
    fig.update_layout(uniformtext_minsize=8, uniformtext_mode='show', template="simple_white")
    #legend = {"orientation":"h"})
        
    
    #fig.update_yaxes(type="log", dtick=0.30102999566, fontsize="25")
    fig.layout['yaxis1'].update(type="log", dtick=0.30102999566, title="CPU [%]", tickvals=[0,1,2,4,8,16,32])
    fig.layout['yaxis2'].update(title="Memory [MB/s]")
    fig.layout['yaxis3'].update(title="Network Traffic [MB/s]")
    #fig.layout['xaxis'].update(title="Frequency [s]")
    #fig.update_xaxes(title_text="Frequency [s]")
    fig.update_layout(
        title="Dolap, " + metrics + " metrics " + str(datapoints[0]) + " datapoints",
        font=dict(
            family="Courier New, monospace",
            size=18,
            color="black"
        )
    )
    fig.update_layout(
        annotations=[
            go.layout.Annotation(
                {
                    'showarrow': False,
                    'text': 'Frequency [s]',
                    'x': 0.5,
                    'xanchor': 'center',
                    'xref': 'paper',
                    'y': 0,
                    'yanchor': 'top',
                    'yref': 'paper',
                    'yshift': -30,
                    
                    "font": dict(
                        family="Courier New, monospace",
                        size=21,
                        color="black"
                    ),
                    
                })
        ]
    )
    print("layout:", fig.layout)
    #fig.write_image("try1.png")
    fig.show()


if __name__ == "__main__":
    
    one_size("10" ,"dolap10")
    one_size("20" ,"dolap20")
    one_size("30" ,"dolap30")
    one_size("40" ,"dolap40")
    one_size("50" ,"dolap50")
    
