import plotly.graph_objects as go

hehe = ["#0cc0aa", "#194f46", "#bfdad4", "#9f2114", "#c7e11f", "#754643", "#f8a395", "#729890"]

fig = go.Figure()

fig.add_trace(go.Indicator(
    mode = "number+delta",
    value = 200,
    domain = {'x': [0, 0.5], 'y': [0, 0.5]},
    delta = {'reference': 400, 'relative': True, 'position' : "top"}))

fig.add_trace(go.Indicator(
    mode = "number+delta",
    value = 350,
    delta = {'reference': 400, 'relative': True},
    domain = {'x': [0, 0.5], 'y': [0.5, 1]}))

fig.add_trace(go.Indicator(
    mode = "number",
    value = 32,
    number = {"prefix": "", "suffix": "kB"},
    title = {"text": "L1 Cache Size<br><span style='font-size:0.8em;color:gray'>"},
    #delta = {'reference': 400, 'relative': True},
    domain = {'x': [0.6, 1], 'y': [0, 1]}))

fig.show()
