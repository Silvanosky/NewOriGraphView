#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import dash
import sys, os
from dash import dcc
from dash import html
import plotly.graph_objs as go

import networkx as nx
import pandas as pd
from colour import Color
from datetime import datetime
from textwrap import dedent as d
from lxml import etree

import pygraphviz as pdv
from plotly_visualize import visualize_graph_3d

projectDir = sys.argv[1]
if len(sys.argv) > 2:
    projectZoom = float(sys.argv[2])
    print("Zoom " + str(projectZoom))
else:
    projectZoom = 1

bonusfile = ""
if len(sys.argv) > 3:
    bonusfile = sys.argv[3]


Gfinal = pdv.AGraph(projectDir + "/final.dot")
Gtotal = pdv.AGraph(projectDir + "/total.dot")

Gbonus = None
if bonusfile != "":
    Gbonus = pdv.AGraph(projectDir + "/" + bonusfile)

ids = pd.read_csv(projectDir + "/logs/all.csv", parse_dates=True, index_col=0)
final = pd.read_csv(projectDir + "/logs/final.csv", parse_dates=True)
total = pd.read_csv(projectDir + "/logs/total.csv", parse_dates=True)

ids['labels'] = ids.Image1
for idx, row in ids.iterrows():
    ids.at[idx,'labels'] = row.Image1 +' / '+ row.Image2 +' / '+ row.Image3

ids = ids.sort_values(by=['Id'])


print(ids.head())
print(final.head())


#print(G.get_subgraph("triplets").nodes())
#print(G.get_subgraph("views").nodes())

#from pprint import pprint
#pprint(vars(G.get_subgraph("triplets").nodes()))

#node_sizes = get_node_sizes(graph)
#edge_weights = get_edge_weights(G)
#filename= "outputs/"+outputFile+".html"

camera = dict(
            up=dict(x=0, y=1, z=0),
            center=dict(x=-0.2, y=0.2, z=0),
            eye=dict(x=-0.2, y=0.2, z=0.7)
        )
if not Gbonus is None:
    visualize_graph_3d(Gbonus, ids, final, camera=camera, filename="bonus.html",  title="3D \
                   visualization", zoom=projectZoom)
else:
    visualize_graph_3d(Gfinal, ids, final, camera=camera, filename="final.html",  title="3D \
                   visualization", zoom=projectZoom)
    visualize_graph_3d(Gtotal, ids, total, camera=camera, filename="total.html",  title="3D "\
                    "Visualization", zoom=projectZoom,cost=True)

#if __name__ == '__main__':
#    app.run_server(debug=True)
