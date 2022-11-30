#!/bin/python
from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import sys, os
import glob
import pandas as pd

app = Dash(__name__)

nArg = len(sys.argv)
curDir = sys.argv[1]

def loadTriplets():
    print("Load triplets")
    files = glob.glob(curDir + "/triplets/*.csv")
    data = {}
    for f in files:
        triplet = os.path.basename(f).split(".")[0]
        data[triplet] = pd.read_csv(f, parse_dates=True)
    return data

total = pd.read_csv(curDir + "/total.csv", parse_dates=True)
data = loadTriplets()
print(len(data))

def getTripletCat(cat):
    print("Load triplets cat: " + str(cat))
    r = {}
    c = total[total["Category"] == cat]
    for key, t in data.items():
        if key in c["Id"]:
            r[key] = t
    return r

def histogram(data, key):
    cat0 = data[data["Category"] == 0]
    cat1 = data[data["Category"] == 1]
    cat2 = data[data["Category"] == 2]

    fg = go.Figure()
    fg.add_trace(go.Histogram(x=data[key],
                        name='Sum',
                        marker_color=f'rgb(128, 128, 128)'))

    fg.add_trace(go.Histogram(x=cat0[key],
                    name='Cat0 - bad',
                    marker_color=f'rgb(255, 0, 0)'))

    fg.add_trace(go.Histogram(x=cat1[key],
                    name='Cat1 - good',
                    marker_color=f'rgb(0, 255, 0)'))
    return fg

app.layout = html.Div([
    html.H4('Score triplets computation'),
    html.Div([
        html.H1(children='Residue'),
        dcc.Graph(
            id='Residue',
            figure=histogram(total, "Residue")
        ),
    ]),
    html.Div([
        html.H1(children='ResidueMedian'),
        dcc.Graph(
            id='ResidueMedian',
            figure=histogram(total, "ResidueMedian")
        ),
    ]),

    html.Div([
        html.H4(children='R/(R+D+R0)'),
        dcc.Graph(id="graph"),
        html.P("R0:"),
        dcc.Slider(id="R0", min=0, max=500, step=1, value=100,
                   marks=None,
                   tooltip={"placement": "bottom", "always_visible": True}),
        dcc.Slider(id="D0", min=0, max=12, step=1, value=5,
                   marks=None,
                   tooltip={"placement": "bottom", "always_visible": True}),

    ])
   ])


def computeScoreTriplet(key, d, r0, d0):
    #s = 0
    #i = 0
    d["inter"] = d["Residue"] / (d["Residue"] + d["Distance"] + r0)
    #for idx, row in d.iterrows():
    #    s += row.Residue / (row.Residue + row.Distance + r0)
    #    i += 1
    #rs = s / i
    total.loc[int(key), 'Score'] = d["inter"].mean()

@app.callback(
    Output("graph", "figure"),
    Input("R0", "value"),
    Input("D0", "value"))
def display_color(r0, d0):
    print("Compute scores for: " + str(r0))
    for key, t in data.items():
        computeScoreTriplet(key, t, r0, d0)

    cat0 = total[total["Category"] == 0]
    cat1 = total[total["Category"] == 1]

    fig = go.Figure()
    fig.add_trace(go.Histogram(x=total['Score'],
                        name='Sum',
                        marker_color=f'rgb(128, 128, 128)'))

    fig.add_trace(go.Histogram(x=cat0['Score'],
                    name='Cat0 - bad',
                    marker_color=f'rgb(255, 0, 0)'))

    fig.add_trace(go.Histogram(x=cat1['Score'],
                    name='Cat1 - good',
                    marker_color=f'rgb(0, 255, 0)'))

    print("Updated")
    return fig

app.run_server(debug=True)
