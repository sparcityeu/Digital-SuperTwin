import sys
import pandas as pd
import plotly.graph_objects as go

from plotly.subplots import make_subplots                                                           
import plotly.io as pio

import statistics


deren_colors_4 = ["rgb(182,156,253)", "rgb(149,38,92)", "rgb(183,200,226)", "rgb(66,65,117)", "rgb(247,94,240)"] 
dolap_colors_4 = ["rgb(6,150,104)", "rgb(195,222,155)", "rgb(52,75,70)", "rgb(121,235,153)", "rgb(101,139,131)"]
poseidon_colors_4 = ["rgb(240,210,126)", "rgb(139,18,58)", "rgb(212,212,212)", "rgb(208,100,64)", "rgb(93,62,71)"]
luna_colors_4 = ["rgb(57,146,131)", "rgb(180,221,212)", "rgb(52,75,70)", "rgb(54,237,211)", "rgb(26,167,238)"]


_deren_file = "deren_cstress_accuracy.csv"
_dolap_file = "dolap_cstress_accuracy.csv"
_luna_file = "luna_cstress_accuracy.csv"
_poseidon_file = "poseidon_cstress_accuracy.csv"

_deren_data = pd.read_csv(_deren_file, index_col = False)
_dolap_data = pd.read_csv(_dolap_file, index_col = False)
_luna_data = pd.read_csv(_luna_file, index_col = False)
print("luna_data:", _luna_data)
_poseidon_data = pd.read_csv(_poseidon_file, index_col = False)

deren_24_1 = _deren_data.loc[(_deren_data["no_metric"] == 24) & (_deren_data["frequency"] == 1) & (_deren_data["metric"] == "fp_arith_scalar_double_err")]
deren_24_1 = list(deren_24_1["error"])
deren_24_1 = [abs(x) for x in deren_24_1]
deren_24_1 = statistics.mean(deren_24_1)
dolap_24_1 = _dolap_data.loc[(_dolap_data["no_metric"] == 24) & (_dolap_data["frequency"] == 1) & (_dolap_data["metric"] == "fp_arith_scalar_double_err")]
dolap_24_1 = list(dolap_24_1["error"])
dolap_24_1 = [abs(x) for x in dolap_24_1]
dolap_24_1 = statistics.mean(dolap_24_1)
luna_24_1 = _luna_data.loc[(_luna_data["no_metric"] == 24) & (_luna_data["frequency"] == 1) & (_luna_data["metric"] == "fp_arith_scalar_double_err")]
luna_24_1 = list(luna_24_1["error"])
luna_24_1 = [abs(x) for x in luna_24_1]
luna_24_1 = statistics.mean(luna_24_1)
poseidon_24_1 = _poseidon_data.loc[(_poseidon_data["no_metric"] == 24) & (_poseidon_data["frequency"] == 1) & (_poseidon_data["metric"] == "fp_arith_scalar_double_err")]
poseidon_24_1 = list(poseidon_24_1["error"])
poseidon_24_1 = [abs(x) for x in poseidon_24_1]
poseidon_24_1 = statistics.mean(poseidon_24_1)

#xx = ["triad", "sum", "stream", "peakflops", "daxpy", "ddot"]
xx = ["dolap, deren, poseidon, luna"]
#xx = ["fp", "cycles", "inst", "uops", "l1bw"]

print("deren_24_1:", deren_24_1)

#######
#######

##cpus and errs

trace1 = go.Bar(name="dolap",
                x=xx,
                y=[dolap_24_1],
                marker_color = dolap_colors_4[0])
    
trace2 = go.Bar(name="deren",
                x=xx,
                y=[deren_24_1],
                marker_color = deren_colors_4[0])

trace3 = go.Bar(name="poseidon",
                x=xx,
                y=[poseidon_24_1],
                marker_color = poseidon_colors_4[0])

trace4 = go.Bar(name="luna",
                x=xx,
                y=[luna_24_1],
                marker_color = luna_colors_4[1])


##cpus and errs

fig = make_subplots(rows=1, cols=6, column_widths=[0.15, 0.15, 0.15, 0.15, 0.15, 0.15], horizontal_spacing=0.1, shared_xaxes=True)
fig.append_trace(trace1, 1,1)
fig.append_trace(trace2, 1,1)
fig.append_trace(trace3, 1,1)
fig.append_trace(trace4, 1,1)

#fig.update_traces(texttemplate='%{y:.2f}', textposition='auto')
fig.update_layout(legend=dict(yanchor="top",y=1.075,xanchor="left",x=0.01,orientation="h"))
fig.update_traces(marker_line_color='rgb(0,0,0)',marker_line_width=1, opacity=1)
fig.update_layout(uniformtext_minsize=16, uniformtext_mode='hide', template="simple_white")
#legend = {"orientation":"h"})

    
#fig.update_yaxes(type="log", dtick=0.30102999566)
#fig.layout['yaxis1'].update(type="log", dtick=0.30102999566, title="CPU [%]", tickvals=[0,0.125,0.25,0.5,1,2,4,8,16,32])
#fig.layout['yaxis2'].update(title="Memory [MBs]")
#fig.layout['yaxis3'].update(title="Network Traffic [MB/s]")
#fig.layout['xaxis'].update(title="Frequency [s]")
fig.update_xaxes(showticklabels=False)
fig.update_layout(
    title="Accuracy",
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
print("layout:", fig.layout)
#fig.write_image("try1.png")
fig.show()


