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

outputFile = sys.argv[1]
inputFilename = sys.argv[2]

G = pdv.AGraph(inputFilename)
#print(G.get_subgraph("triplets").nodes())
#print(G.get_subgraph("views").nodes())

#from pprint import pprint
#pprint(vars(G.get_subgraph("triplets").nodes()))

#node_sizes = get_node_sizes(graph)
#edge_weights = get_edge_weights(G)
#filename= "outputs/"+outputFile+".html"
filename=outputFile
visualize_graph_3d(G, filename=filename,  title="3D visualization")


#if __name__ == '__main__':
#    app.run_server(debug=True)
