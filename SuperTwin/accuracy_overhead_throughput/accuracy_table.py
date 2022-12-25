import sys
import pandas as pd
import plotly.graph_objects as go

from plotly.subplots import make_subplots                                                           
import plotly.io as pio

import statistics

xx = ["1", "1/2", "1/4", "1/8", "1/16", "1/32"]

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

def ret_trace(_data, metric, no_metrics, freq, name, colors, sl):

    global xx
    
    line = []
    for freq in freqs:
        line.append(ret_metric(_data, metric, no_metrics, freq))
        
        trace1 = (go.Scatter(x=xx, y=line,
                             mode='lines',
                             name=name,
                             showlegend=sl,
                             line=dict(color=colors[0], width=4)))

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
                             line=dict(color=colors[1], width=4, dash="dash")))

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
                             line=dict(color=colors[4], width=4, dash="dot")))

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
    
#print("dolap24", dolap_24_1)
#print("deren24", deren_24_1)
#print("luna24", luna_24_1)
#print("poseidon24", poseidon_24_1)


    
#print(ret_list(_dolap_data, 24, 16))
#print(ret_metric(_dolap_data, "fp_arith_scalar_double_err", 24, 8))
#print(ret_metric(_dolap_data, "l1_bw", 24, 8))

#metrics = [1,4,8,12,16,20,24]
metrics = [8,16,24]
freqs = [1,2,4,8,16]

xx = ["1", "1/2", "1/4", "1/8", "1/16"]

fig = go.Figure()
fig = make_subplots(rows=2, cols=2, column_widths=[0.5,0.5], row_heights=[0.5, 0.5], horizontal_spacing=0.1, vertical_spacing=0.1, shared_xaxes=True, subplot_titles=("FP_ARITH_SCALAR_DOBLE", "MEM_LOAD_UOPS", "UNHALTED_REFERENCE_CYCLES", "INSTRUCTIONS_RETIRED"))


#line = []
#for freq in freqs:
#    line.append(ret_metric(_dolap_data, "fp_arith_scalar_double_err", 8, freq))
        
#    trace1 = (go.Scatter(x=xx, y=line,
#                         mode='lines',
#                         name="Dolap-8",
#                         line=dict(color=dolap_colors_4[0], width=4)))
    

#######################
trace1 = ret_trace(_dolap_data, "fp_arith_scalar_double_err", 8, 1, "Dolap-8", dolap_colors_4, True)
fig.append_trace(trace1, row=1, col=1)

trace1 = ret_trace_dash(_dolap_data, "fp_arith_scalar_double_err", 16, 1, "Dolap-16", dolap_colors_4, True)
fig.append_trace(trace1, row=1, col=1)

trace1 = ret_trace_dot(_dolap_data, "fp_arith_scalar_double_err", 24, 1, "Dolap-24", dolap_colors_4, True)
fig.append_trace(trace1, row=1, col=1)
##
trace1 = ret_trace(_poseidon_data, "fp_arith_scalar_double_err", 8, 1, "Poseidon-8", poseidon_colors_4, True)
fig.append_trace(trace1, row=1, col=1)

trace1 = ret_trace_dash(_poseidon_data, "fp_arith_scalar_double_err", 16, 1, "Poseidon-16", poseidon_colors_4, True)
fig.append_trace(trace1, row=1, col=1)

trace1 = ret_trace_dot(_poseidon_data, "fp_arith_scalar_double_err", 24, 1, "Poseidon-24", poseidon_colors_4, True)
fig.append_trace(trace1, row=1, col=1)
##
trace1 = ret_trace(_deren_data, "fp_arith_scalar_double_err", 8, 1, "Deren-8", deren_colors_4, True)
fig.append_trace(trace1, row=1, col=1)

trace1 = ret_trace_dash(_deren_data, "fp_arith_scalar_double_err", 16, 1, "Deren-16", deren_colors_4, True)
fig.append_trace(trace1, row=1, col=1)

trace1 = ret_trace_dot(_deren_data, "fp_arith_scalar_double_err", 24, 1, "Deren-24", deren_colors_4, True)
fig.append_trace(trace1, row=1, col=1)
##########################
##########################
trace1 = ret_trace(_dolap_data, "l1_bw", 8, 1, "Dolap-8", dolap_colors_4, False)
fig.append_trace(trace1, row=1, col=2)

trace1 = ret_trace_dash(_dolap_data, "l1_bw", 16, 1, "Dolap-16", dolap_colors_4, False)
fig.append_trace(trace1, row=1, col=2)

trace1 = ret_trace_dot(_dolap_data, "l1_bw", 24, 1, "Dolap-24", dolap_colors_4, False)
fig.append_trace(trace1, row=1, col=2)
##
trace1 = ret_trace(_poseidon_data, "l1_bw", 8, 1, "Poseidon-8", poseidon_colors_4, False)
fig.append_trace(trace1, row=1, col=2)

trace1 = ret_trace_dash(_poseidon_data, "l1_bw", 16, 1, "Poseidon-16", poseidon_colors_4, False)
fig.append_trace(trace1, row=1, col=2)

trace1 = ret_trace_dot(_poseidon_data, "l1_bw", 24, 1, "Poseidon-24", poseidon_colors_4, False)
fig.append_trace(trace1, row=1, col=2)
##
trace1 = ret_trace(_deren_data, "l1_bw", 8, 1, "Deren-8", deren_colors_4, False)
fig.append_trace(trace1, row=1, col=2)

trace1 = ret_trace_dash(_deren_data, "l1_bw", 16, 1, "Deren-16", deren_colors_4, False)
fig.append_trace(trace1, row=1, col=2)

trace1 = ret_trace_dot(_deren_data, "l1_bw", 24, 1, "Deren-24", deren_colors_4, False)
fig.append_trace(trace1, row=1, col=2)
##
trace1 = ret_trace(_luna_data, "l1_bw", 8, 1, "Luna-8", luna_colors_4, True)
fig.append_trace(trace1, row=1, col=2)

trace1 = ret_trace_dash(_luna_data, "l1_bw", 16, 1, "Luna-16", luna_colors_4, True)
fig.append_trace(trace1, row=1, col=2)

trace1 = ret_trace_dot(_luna_data, "l1_bw", 24, 1, "Luna-24", luna_colors_4, True)
fig.append_trace(trace1, row=1, col=2)
##########################
##########################
trace1 = ret_trace(_dolap_data, "unhalted_reference_cycles_err", 8, 1, "Dolap-8", dolap_colors_4, False)
fig.append_trace(trace1, row=2, col=1)

trace1 = ret_trace_dash(_dolap_data, "unhalted_reference_cycles_err", 16, 1, "Dolap-16", dolap_colors_4, False)
fig.append_trace(trace1, row=2, col=1)

trace1 = ret_trace_dot(_dolap_data, "unhalted_reference_cycles_err", 24, 1, "Dolap-24", dolap_colors_4, False)
fig.append_trace(trace1, row=2, col=1)
##
trace1 = ret_trace(_poseidon_data, "unhalted_reference_cycles_err", 8, 1, "Poseidon-8", poseidon_colors_4, False)
fig.append_trace(trace1, row=2, col=1)

trace1 = ret_trace_dash(_poseidon_data, "unhalted_reference_cycles_err", 16, 1, "Poseidon-16", poseidon_colors_4, False)
fig.append_trace(trace1, row=2, col=1)

trace1 = ret_trace_dot(_poseidon_data, "unhalted_reference_cycles_err", 24, 1, "Poseidon-24", poseidon_colors_4, False)
fig.append_trace(trace1, row=2, col=1)
##
trace1 = ret_trace(_deren_data, "unhalted_reference_cycles_err", 8, 1, "Deren-8", deren_colors_4, False)
fig.append_trace(trace1, row=2, col=1)

trace1 = ret_trace_dash(_deren_data, "unhalted_reference_cycles_err", 16, 1, "Deren-16", deren_colors_4, False)
fig.append_trace(trace1, row=2, col=1)

trace1 = ret_trace_dot(_deren_data, "unhalted_reference_cycles_err", 24, 1, "Deren-24", deren_colors_4, False)
fig.append_trace(trace1, row=2, col=1)
##
trace1 = ret_trace(_luna_data, "unhalted_reference_cycles_err", 8, 1, "Luna-8", luna_colors_4, False)
fig.append_trace(trace1, row=2, col=1)

trace1 = ret_trace_dash(_luna_data, "unhalted_reference_cycles_err", 16, 1, "Luna-16", luna_colors_4, False)
fig.append_trace(trace1, row=2, col=1)

trace1 = ret_trace_dot(_luna_data, "unhalted_reference_cycles_err", 24, 1, "Luna-24", luna_colors_4, False)
fig.append_trace(trace1, row=2, col=1)
###################################
###################################
trace1 = ret_trace(_dolap_data, "instruction_retired_err", 8, 1, "Dolap-8", dolap_colors_4, False)
fig.append_trace(trace1, row=2, col=2)

trace1 = ret_trace_dash(_dolap_data, "instruction_retired_err", 16, 1, "Dolap-16", dolap_colors_4, False)
fig.append_trace(trace1, row=2, col=2)

trace1 = ret_trace_dot(_dolap_data, "instruction_retired_err", 24, 1, "Dolap-24", dolap_colors_4, False)
fig.append_trace(trace1, row=2, col=2)
##
trace1 = ret_trace(_poseidon_data, "instruction_retired_err", 8, 1, "Poseidon-8", poseidon_colors_4, False)
fig.append_trace(trace1, row=2, col=2)

trace1 = ret_trace_dash(_poseidon_data, "instruction_retired_err", 16, 1, "Poseidon-16", poseidon_colors_4, False)
fig.append_trace(trace1, row=2, col=2)

trace1 = ret_trace_dot(_poseidon_data, "instruction_retired_err", 24, 1, "Poseidon-24", poseidon_colors_4, False)
fig.append_trace(trace1, row=2, col=2)
##
trace1 = ret_trace(_deren_data, "instruction_retired_err", 8, 1, "Deren-8", deren_colors_4, False)
fig.append_trace(trace1, row=2, col=2)

trace1 = ret_trace_dash(_deren_data, "instruction_retired_err", 16, 1, "Deren-16", deren_colors_4, False)
fig.append_trace(trace1, row=2, col=2)

trace1 = ret_trace_dot(_deren_data, "instruction_retired_err", 24, 1, "Deren-24", deren_colors_4, False)
fig.append_trace(trace1, row=2, col=2)
##
trace1 = ret_trace(_luna_data, "instruction_retired_err", 8, 1, "Luna-8", luna_colors_4, False)
fig.append_trace(trace1, row=2, col=2)

trace1 = ret_trace_dash(_luna_data, "instruction_retired_err", 16, 1, "Luna-16", luna_colors_4, False)
fig.append_trace(trace1, row=2, col=2)

trace1 = ret_trace_dot(_luna_data, "instruction_retired_err", 24, 1, "Luna-24", luna_colors_4, False)
fig.append_trace(trace1, row=2, col=2)
###############################
###############################



############################################################################################
############################################################################################
############################################################################################
fig.update_layout(template="simple_white")
fig.update_layout(legend=dict(yanchor="top",y=1.2,xanchor="left",x=0.01,orientation="h"))


fig.update_layout(                                                                              
    #title="Error in measurement",               
    font=dict(                                                                                  
        family="Courier New, monospace",                                                        
        size=32,                                                                                
        color="black"                                                                           
    ),
    yaxis={'tickformat':'.1e','ticks': 'outside'},
    yaxis2={'tickformat':'.1e','ticks': 'outside'},
    yaxis3={'tickformat':'.1e','ticks': 'outside'},
    yaxis4={'tickformat':'.1e','ticks': 'outside'})
    #xaxis4={'title_text':'Frequency [s]',})

fig.update_layout(                                                                              
    annotations=[ 
        go.layout.Annotation(                                                                   
            {                                                                                   
                'showarrow': False,                                                             
                #'text': 'Frequency [s]',                                                        
                #'x': 0.5,                                                                       
                #'xanchor': 'center',                                                            
                #'xref': 'paper',                                                                
                #'y': 0,                                                                         
                #'yanchor': 'top',                                                               
                #'yref': 'paper',                                                                
                #'yshift': -50,                                                                  
                
                "font": dict(                                                                   
                    family="Courier New, monospace",                                            
                    size=32,                                                                    
                    color="black"                                                               
                ),                                                                              
                
            })                                                                                  
    ]                                                                                           
)

'''
fig['layout'].update(
    annotations=[
    dict(
        x=0, y=0, # annotation point
        xref='x4', 
        yref='y4',
        text='dict Text',
        showarrow=False,
        ax=0,
        ay=0,
        font = dict(                                                                   
                        family="Courier New, monospace",                                            
                        size=32,                                                                    
                        color="black"                                                               
                    )
    )])
'''
fig['layout'].update(height=2160, width=2160)
print(fig.layout["annotations"])
fig.show()
