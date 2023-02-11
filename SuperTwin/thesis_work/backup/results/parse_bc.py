import sys
import pandas as pd
import plotly.graph_objects as go


#import plotly.io as pio
#pio.templates


#colors_4 = ["rgb(82,239,153)", "rgb(7,92,98)", "rgb(147,208,226)", "rgb(29,109,31)"]
colors_4 = ["rgb(33,240,182)", "rgb(38,85,130)", "rgb(187,226,114)", "rgb(27,81,29)"]



if __name__ == "__main__":

    _file = sys.argv[1]
    data = pd.read_csv(_file, index_col=False)

    #print("data:", data)
    #print(data["alias"])

    
    xx =["1", "1/2", "1/4", "1/8", "1/16"]

    #s_10 = data.loc["alias":"luna10"]
    
    s_20 = data.loc[data["alias"] == "luna50"]
    
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

    
    
    trace1 = go.Bar(name="pmcd",
               x=xx,
               y=pmcd_cpu,
               error_y = dict(type='data', array=pmcd_cpu_err),
               marker_color = colors_4[0])
        
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
    
    fig = make_subplots(rows=1, cols=3, column_widths=[0.7, 0.2, 0.1])
    fig.append(trace1, 1,1)
    fig.append(trace2, 1,1)
    fig.append(trace3, 1,1)
    fig.append(trace4, 1,1)
    #fig.update_traces(texttemplate='%{y:.2f}', textposition='auto')
    fig.update_layout(legend=dict(yanchor="top",y=0.99,xanchor="left",x=0.01,orientation="h"))
    fig.update_traces(marker_line_color='rgb(0,0,0)',marker_line_width=1, opacity=0.9)
    fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide', barmode='group',
                      template="simple_white")
                      #legend = {"orientation":"h"})
                      
    
    fig.update_yaxes(type="log", dtick=0.30102999566, fontsize="25")
    fig.update_layout(barmode='group')
    fig.show()
