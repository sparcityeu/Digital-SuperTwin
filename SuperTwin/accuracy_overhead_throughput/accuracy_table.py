import sys
import pandas as pd
import plotly.graph_objects as go

from plotly.subplots import make_subplots                                                           
import plotly.io as pio

import statistics


def ret_list(df, no_metric, freq):

    df = df.loc[(df["no_metric"] == no_metric) & (df["frequency"] == freq)]
    df = df["error"]
    return list(df)
    

def ret_metric(df, metric, no_metric, freq):

    df = df.loc[df["metric"] == metric]
    df = ret_list(df, no_metric, freq)

    df = [abs(x) for x in df]
    
    return statistics.mean(df)

deren_colors_4 = ["rgb(182,156,253)", "rgb(149,38,92)", "rgb(183,200,226)", "rgb(66,65,117)", "rgb(247,94,240)"] 
dolap_colors_4 = ["rgb(6,150,104)", "rgb(195,222,155)", "rgb(52,75,70)", "rgb(121,235,153)", "rgb(101,139,131)"]
poseidon_colors_4 = ["rgb(240,210,126)", "rgb(139,18,58)", "rgb(212,212,212)", "rgb(208,100,64)", "rgb(93,62,71)"]
luna_colors_4 = ["rgb(57,146,131)", "rgb(180,221,212)", "rgb(52,75,70)", "rgb(54,237,211)", "rgb(26,167,238)"]
seven_colors = ["rgb(86,235,211)", "rgb(17,93,82)", "rgb(197,216,221)", "rgb(88,157,144)", "rgb(197,223,114)", "rgb(200,105,73)", "rgb(116,238,101)"]


_deren_file = "deren_cstress_accuracy.csv"
_dolap_file = "dolap_cstress_accuracy.csv"
_luna_file = "luna_cstress_accuracy.csv"
_poseidon_file = "poseidon_cstress_accuracy.csv"

_deren_data = pd.read_csv(_deren_file, index_col = False)
_dolap_data = pd.read_csv(_dolap_file, index_col = False)
_luna_data = pd.read_csv(_luna_file, index_col = False)
_poseidon_data = pd.read_csv(_poseidon_file, index_col = False)



deren_24_1 = _deren_data.loc[(_deren_data["no_metric"] == 24) & (_deren_data["frequency"] == 16)]
dolap_24_1 = _dolap_data.loc[(_dolap_data["no_metric"] == 24) & (_dolap_data["frequency"] == 16)]
luna_24_1 = _luna_data.loc[(_luna_data["no_metric"] == 24) & (_luna_data["frequency"] == 16)]
poseidon_24_1 = _poseidon_data.loc[(_poseidon_data["no_metric"] == 24) & (_poseidon_data["frequency"] == 16)]

pd.set_option('display.float_format', lambda x: '%.2E' % x)
    
print("dolap24", dolap_24_1)
#print("deren24", deren_24_1)
#print("luna24", luna_24_1)
#print("poseidon24", poseidon_24_1)


    
print(ret_list(_dolap_data, 24, 16))
print(ret_metric(_dolap_data, "fp_arith_scalar_double_err", 24, 8))
print(ret_metric(_dolap_data, "l1_bw", 24, 8))

#metrics = [1,4,8,12,16,20,24]
metrics = [8,16,24]
freqs = [1,2,4,8,16,32]

xx = ["1", "1/2", "1/4", "1/8", "1/16", "1/32"]

fig = go.Figure()
fig = make_subplots(rows=2, cols=2, column_widths=[0.5,0.5], row_heights=[0.5, 0.5], horizontal_spacing=0.1, shared_xaxes=True)
for idx, metric in enumerate(metrics):
    line = []
    for freq in freqs:
        line.append(ret_metric(_dolap_data, "fp_arith_scalar_double_err", metric, freq))
        
    trace1 = (go.Scatter(x=xx, y=line,
                             mode='lines',
                             name=str(metric) + " metric",
                             line=dict(color=seven_colors[6-idx], width=2)))
    

    fig.append_trace(trace1, row=1, col=1)

'''
fig = go.Figure()
metrics = [4,8,12,16,20,24]

for metric in metrics:
    line = []
    for freq in freqs:
        line.append(ret_metric(_dolap_data, "l1_bw", metric, freq))
        trace2 = (go.Scatter(x=xx, y=line,
                             mode='lines',
                             name=str(metric) + " metric",
                             line=dict(color=seven_colors, width=2)))
    
    
fig.show()

fig = go.Figure()
metrics = [4,8,12,16,20,24]

for metric in metrics:
    line = []
    for freq in freqs:
        line.append(ret_metric(_dolap_data, "instruction_retired_err", metric, freq))
    fig.add_trace(go.Scatter(x=xx, y=line,
                             mode='lines',
                             name=str(metric) + " metric",
                             line=dict(color=luna_colors_4, width=2)))
    
    
fig.show()

fig = go.Figure()
metrics = [8,12,16,20,24]

for metric in metrics:
    line = []
    for freq in freqs:
        line.append(ret_metric(_dolap_data, "unhalted_reference_cycles_err", metric, freq))
    fig.add_trace(go.Scatter(x=xx, y=line,
                             mode='lines',
                             name=str(metric) + " metric",
                             line=dict(color=poseidon_colors_4, width=2)))
    
fig.show()


fig = go.Figure()
for metric in metrics:
    line = []
    for freq in freqs:
        line.append(ret_metric(_dolap_data, "uops_retired_any_err", metric, freq))
    fig.add_trace(go.Scatter(x=xx, y=line,
                             mode='lines',
                             name=str(metric) + " metric"))
    
fig.show()
'''

fig.update_layout(template="simple_white")
fig.update_layout(legend=dict(yanchor="top",y=1.075,xanchor="left",x=0.01,orientation="h"))

fig.update_layout(                                                                              
    title="Error in measurement",               
    font=dict(                                                                                  
        family="Courier New, monospace",                                                        
        size=32,                                                                                
        color="black"                                                                           
    ),
    yaxis={'tickformat':'.0e','ticks': 'outside'}
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
                'yshift': -50,                                                                  
                
                "font": dict(                                                                   
                    family="Courier New, monospace",                                            
                    size=32,                                                                    
                    color="black"                                                               
                ),                                                                              
                
            })                                                                                  
    ]                                                                                           
)
fig.show()
