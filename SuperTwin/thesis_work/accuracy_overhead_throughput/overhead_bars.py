import sys
import pandas as pd
import plotly.graph_objects as go

from plotly.subplots import make_subplots                                                           
import plotly.io as pio

import statistics

xx = ["1", "1/2", "1/4", "1/8", "1/16", "1/32"]
xx_inner = ["1", "8", "24"]
#xx_inner = ["1", "1/8", "1/24"]

def ret_list(df, no_metric, freq):

    df = df.loc[(df["no_metric"] == no_metric) & (df["frequency"] == freq)]
    #print("no_metric:", no_metric, "freq:", freq)
    #print("df there:", df)
    df = df["error"]
    #print("last df:", df)
    return list(df)
    

def ret_metric(df, metric, no_metric, freq):

    df = df.loc[df["metric"] == metric]
    #print("df here:", df)
    df = ret_list(df, no_metric, freq)
    
    df = [abs(x) for x in df]
    
    
    return statistics.mean(df)

def ret_trace_list(df, freq):

    df_1 = df.loc[(df["freq"] == freq) & (df["metric"] == 1)]
    df_8 = df.loc[(df["freq"] == freq) & (df["metric"] == 8)]
    df_24 = df.loc[(df["freq"] == freq) & (df["metric"] == 24)]

    df_1 = list(df_1["overhead"])
    df_1 = statistics.mean(df_1)
    df_1 = (df_1 * 100) - 100
    
    df_8 = list(df_8["overhead"])
    df_8 = statistics.mean(df_8)
    df_8 = (df_8 * 100) - 100

    df_24 = list(df_24["overhead"])
    df_24 = statistics.mean(df_24)
    df_24 = (df_24 * 100) - 100

    #return [abs(df_1), abs(df_8), abs(df_24)]
    return [df_1,df_8,df_24]


def ret_trace(_data, metric, no_metrics, freq, name, colors, sl):

    global xx
    
    line = []
    for freq in freqs:
        line.append(ret_metric(_data, metric, no_metrics, freq))
        
        trace1 = (go.Scatter(x=xx, y=line,
                             mode='lines',
                             name=name,
                             showlegend=sl,
                             #legendgroup='1',
                             line=dict(color=colors[4], width=8)))

    return trace1

def ret_trace_dash(_data, metric, no_metrics, freq, name, colors, sl):

    global xx
    
    line = []
    for freq in freqs:
        line.append(ret_metric(_data, metric, no_metrics, freq))
        
        trace1 = (go.Scatter(x=xx, y=line,
                             mode='lines',
                             name=name,
                             showlegend=sl,
                             #legendgroup='2',
                             line=dict(color=colors[4], width=8, dash="dash")))

    return trace1

def ret_trace_dot(_data, metric, no_metrics, freq, name, colors, sl):

    global xx
    
    line = []
    for freq in freqs:
        line.append(ret_metric(_data, metric, no_metrics, freq))
        
        trace1 = (go.Scatter(x=xx, y=line,
                             mode='lines',
                             name=name,
                             showlegend=sl,
                             #legendgroup='3',
                             line=dict(color=colors[4], width=8, dash="dot")))

    return trace1

def ret_trace_dashdot(_data, metric, no_metrics, freq, name, colors):

    global xx
    
    line = []
    for freq in freqs:
        line.append(ret_metric(_data, metric, no_metrics, freq))
        
        trace1 = (go.Scatter(x=xx, y=line,
                             mode='lines',
                             name=name,
                             line=dict(color=colors[4], width=4, dash="dashdot")))

    return trace1


def one_trace(t_list, name, colors, sl):

    global xx_inner
    
    trace = go.Bar(name=name,
                   x=xx_inner,
                   y=t_list,
                   showlegend=sl,
                   marker_color=colors[2])

    return trace


def one_trace_luna(t_list, name, colors, i, sl):

    global xx_inner
    t_list = [-1*x for x in t_list]
    
    trace = go.Bar(name=name,
                   x=xx_inner,
                   y=t_list,
                   showlegend=sl,
                   marker_color=colors[i])

    return trace
    
    
deren_colors_4 = ["rgb(182,156,253)", "rgb(149,38,92)", "rgb(183,200,226)", "rgb(66,65,117)", "rgb(247,94,240)"] 
dolap_colors_4 = ["rgb(6,150,104)", "rgb(195,222,155)", "rgb(52,75,70)", "rgb(121,235,153)", "rgb(101,139,131)"]
poseidon_colors_4 = ["rgb(240,210,126)", "rgb(139,18,58)", "rgb(212,212,212)", "rgb(208,100,64)", "rgb(93,62,71)"]
luna_colors_4 = ["rgb(57,146,131)", "rgb(180,221,212)", "rgb(52,75,70)", "rgb(54,237,211)", "rgb(26,167,238)"]
seven_colors = ["rgb(86,235,211)", "rgb(17,93,82)", "rgb(197,216,221)", "rgb(88,157,144)", "rgb(197,223,114)", "rgb(200,105,73)", "rgb(116,238,101)"]


_deren_file = "deren_cstress_overhead.csv"
_dolap_file = "dolap_cstress_overhead.csv"
_luna_file = "luna_cstress_overhead.csv"
_poseidon_file = "poseidon_cstress_overhead.csv"

_deren_data = pd.read_csv(_deren_file, index_col = False)
_dolap_data = pd.read_csv(_dolap_file, index_col = False)
_luna_data = pd.read_csv(_luna_file, index_col = False)
_poseidon_data = pd.read_csv(_poseidon_file, index_col = False)




fig = make_subplots(rows=1, cols=6, column_widths = [0.15,0.15,0.15,0.15,0.15,0.1], horizontal_spacing=0.05, vertical_spacing=0.05, shared_xaxes=True)


trace1 = ret_trace_list(_dolap_data, 1) ##freq = 1, metrics=1,8,24
fig.append_trace(one_trace(trace1, "dolap", dolap_colors_4, True), row=1, col=1)
print("trace1:", trace1)
trace1 = ret_trace_list(_dolap_data, 2) ##freq = 1, metrics=1,8,24
fig.append_trace(one_trace(trace1, "dolap", dolap_colors_4, False), row=1, col=2)
print("trace1:", trace1)
trace1 = ret_trace_list(_dolap_data, 4) ##freq = 1, metrics=1,8,24
fig.append_trace(one_trace(trace1, "dolap", dolap_colors_4, False), row=1, col=3)
print("trace1:", trace1)
trace1 = ret_trace_list(_dolap_data, 8) ##freq = 1, metrics=1,8,24
fig.append_trace(one_trace(trace1, "dolap", dolap_colors_4, False), row=1, col=4)
print("trace1:", trace1)
trace1 = ret_trace_list(_dolap_data, 16) ##freq = 1, metrics=1,8,24
fig.append_trace(one_trace(trace1, "dolap", dolap_colors_4, False), row=1, col=5)
print("trace1:", trace1)
###################################################################################
trace1 = ret_trace_list(_deren_data, 1) ##freq = 1, metrics=1,8,24
fig.append_trace(one_trace(trace1, "deren", deren_colors_4, True), row=1, col=1)
print("trace1:", trace1)
trace1 = ret_trace_list(_deren_data, 2) ##freq = 1, metrics=1,8,24
fig.append_trace(one_trace(trace1, "deren", deren_colors_4, False), row=1, col=2)
print("trace1:", trace1)
trace1 = ret_trace_list(_deren_data, 4) ##freq = 1, metrics=1,8,24
fig.append_trace(one_trace(trace1, "deren", deren_colors_4, False), row=1, col=3)
print("trace1:", trace1)
trace1 = ret_trace_list(_deren_data, 8) ##freq = 1, metrics=1,8,24
fig.append_trace(one_trace(trace1, "deren", deren_colors_4, False), row=1, col=4)
print("trace1:", trace1)
trace1 = ret_trace_list(_deren_data, 16) ##freq = 1, metrics=1,8,24
fig.append_trace(one_trace(trace1, "deren", deren_colors_4, False), row=1, col=5)
print("trace1:", trace1)
###################################################################################
trace1 = ret_trace_list(_poseidon_data, 1) ##freq = 1, metrics=1,8,24
fig.append_trace(one_trace(trace1, "poseidon", poseidon_colors_4, True), row=1, col=1)
print("trace1:", trace1)
trace1 = ret_trace_list(_poseidon_data, 2) ##freq = 1, metrics=1,8,24
fig.append_trace(one_trace(trace1, "poseidon", poseidon_colors_4, False), row=1, col=2)
print("trace1:", trace1)
trace1 = ret_trace_list(_poseidon_data, 4) ##freq = 1, metrics=1,8,24
fig.append_trace(one_trace(trace1, "poseidon", poseidon_colors_4, False), row=1, col=3)
print("trace1:", trace1)
trace1 = ret_trace_list(_poseidon_data, 8) ##freq = 1, metrics=1,8,24
fig.append_trace(one_trace(trace1, "poseidon", poseidon_colors_4, False), row=1, col=4)
print("trace1:", trace1)
trace1 = ret_trace_list(_poseidon_data, 16) ##freq = 1, metrics=1,8,24
fig.append_trace(one_trace(trace1, "poseidon", poseidon_colors_4, False), row=1, col=5)
print("trace1:", trace1)
###################################################################################
trace1 = ret_trace_list(_luna_data, 1) ##freq = 1, metrics=1,8,24
fig.append_trace(one_trace_luna(trace1, "luna-1", luna_colors_4, 0, True), row=1, col=6)
print("trace1:", trace1)
trace1 = ret_trace_list(_luna_data, 2) ##freq = 1, metrics=1,8,24
fig.append_trace(one_trace_luna(trace1, "luna-1/2", luna_colors_4, 1, True), row=1, col=6)
print("trace1:", trace1)
trace1 = ret_trace_list(_luna_data, 4) ##freq = 1, metrics=1,8,24
fig.append_trace(one_trace_luna(trace1, "luna-1/4", luna_colors_4, 2, True), row=1, col=6)
print("trace1:", trace1)
trace1 = ret_trace_list(_luna_data, 8) ##freq = 1, metrics=1,8,24
fig.append_trace(one_trace_luna(trace1, "luna-1/8", luna_colors_4, 3, True), row=1, col=6)
print("trace1:", trace1)
trace1 = ret_trace_list(_luna_data, 16) ##freq = 1, metrics=1,8,24
fig.append_trace(one_trace_luna(trace1, "luna-1/16", luna_colors_4, 4, True), row=1, col=6)
print("trace1:", trace1)

#fig.update_yaxes(type="log", dtick=0.30102999566)
fig.update_layout(uniformtext_minsize=16, uniformtext_mode='hide', template="simple_white")
fig.update_traces(marker_line_color='rgb(0,0,0)',marker_line_width=1, opacity=1)


fig.update_layout(                                                                              
    #title="Sampling Overhead",               
        font=dict(                                                                                  
            family="Courier New, monospace",                                                        
            size=32,                                                                                
            color="black"                                                                           
        )                                                                                           
    )                                                                                               
fig.update_layout(                                                                              
        annotations=[                                                                               
            go.layout.Annotation(                                                                   
                {                                                                                   
                    'showarrow': False,                                                             
                    'text': 'Number of metrics - Frequency',
                    'x': 0.5,                                                                       
                    'xanchor': 'center',                                                            
                    'xref': 'paper',                                                                
                    'y': 0,
                    'yanchor': 'top',                                                               
                    'yref': 'paper',                                                                
                    'yshift': -30,                                                                  
                                                                                                    
                    "font": dict(                                                                   
                        family="Courier New, monospace",                                            
                        size=32,                                                                    
                        color="black"                                                               
                    ),                                                                              
                                                                                                    
                })                                                                                  
        ]                                                                                           
    )


fig.update_layout(legend=dict(yanchor="top",y=1.075,xanchor="left",x=0.01,orientation="h"))
fig.layout['yaxis1'].update(title="% overhead")
fig.layout['xaxis1'].update(title="1/s")
fig.layout['xaxis2'].update(title="2/s")
fig.layout['xaxis3'].update(title="4/s")
fig.layout['xaxis4'].update(title="8/s")
fig.layout['xaxis5'].update(title="16/s")
'''
fig.update_xaxes(
        tickangle = 90,
        title_text = "s/8",
        title_font = {"size": 32},
        title_standoff = 25)
'''
# make room to display double x-axes
fig.update_layout(yaxis1=dict(domain=[0.1, 1]),
                  yaxis2=dict(domain=[0.1, 1]),
                  yaxis3=dict(domain=[0.1, 1]),
                  yaxis4=dict(domain=[0.1, 1]),
                  yaxis5=dict(domain=[0.1, 1]),
                  yaxis6=dict(domain=[0.1, 1]),
                 )

# not critical, but just to put a little air in there
#fig.update_layout(xaxis1=dict(domain=[0.0, 0.4]),
#                  xaxis2=dict(domain=[0.6, 1]),
#                 )

print(fig.layout)
fig.show()
