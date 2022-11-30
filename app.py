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

Gfinal = pdv.AGraph(projectDir + "/final.dot")
Gtotal = pdv.AGraph(projectDir + "/total.dot")

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
visualize_graph_3d(Gfinal, ids, final, filename="final.html",  title="3D visualization")
#visualize_graph_3d(Gtotal, ids, total, filename="total.html",  title="3D Visualization", cost=True)


#if __name__ == '__main__':
#    app.run_server(debug=True)
