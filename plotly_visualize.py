from os import name
from colour import color_scale
from networkx import link_analysis
from numpy import double
from plotly.graph_objs import *
import plotly.graph_objects as go
from plotly.offline import plot as offpy
import numpy as np

def getRGBfromI(RGBint):
    blue =  RGBint & 255
    green = (RGBint >> 8) & 255
    red =   (RGBint >> 16) & 255
    return red, green, blue


def get_node_pos(G, offset = [0,0,0], scale=[1,1,1]):
    pos = {}
    for node in G.nodes():
        if "pos" in node.attr:
            s = node.attr['pos'].replace("!", "").replace("\"", "")
            t = [float(i) for i in s.split(",")]
            pos[node] = t
        else:
            pos[node] = [0,0,0]

        pos[node][0] += offset[0]
        pos[node][1] += offset[1]
        pos[node][2] += offset[2]

        pos[node][0] *= scale[0]
        pos[node][1] *= scale[1]
        pos[node][2] *= scale[2]

    #pos = { node[0] : [node[1]['pos'].replace("!", "").split(",")]
    #       for node in G.nodes(data=True)}
    return pos

def get_node_labels(G):
    t = []
    for node in G.nodes():
        t.append(node.attr['label'] if "label" in node.attr else node)
    return t

allpos = {}

offsetbar = [0.]

def visualize_graph_layer(G, fig, color, weight=[], text=[], name="", offset = [0,0,0],
                          scale=[1,1,1], colorscale="Viridis", size=5, symbol = "circle", edge=True):
    positions = get_node_pos(G, offset=offset, scale=scale)
    node_size = len(G.nodes())
    node_x = [0]*node_size
    node_y = [0]*node_size
    node_z = [0]*node_size

    node_colors = [0] * node_size
    #nodesc = {}
    for i, node in enumerate(G.nodes()):
        print(node)
        x, y, z = positions[node]
        node_x[i], node_y[i], node_z[i] = x, y, z
        #c = getRGBfromI(int(node))
        #node_colors[i] = f'rgb({c[0]}, {c[1]}, {c[2]})'
        #nodesc[node] = f'rgb({c[0]}, {c[1]}, {c[2]})'
    for node in positions:
        allpos[node] = positions[node]

    node_trace = Scatter3d(x=node_x,
                           y=node_y,
                           z=node_z,
                           mode='markers',
                           marker=dict(symbol=symbol,
                                       size=size,
                                       #color=color,
                                       color=weight,
                                       colorscale=colorscale,  # 'Viridis',
                                       colorbar=dict(
                                           thickness=15,
                                           title='Residue',
                                           xanchor='left',
                                           titleside='right',
                                           x=offsetbar[0]
                                       ),
                                       line=Line(
                                           color='rgb(50,50,50)', width=0.5)
                                       ),
                           name=name,
                           text=text,
                           hoverinfo='text'
                           )
    fig.add_trace(node_trace)
    offsetbar[0] += 0.02

    if not edge:
        return

    edge_size = len(G.edges())
    edge_x = [0, 0, None]*edge_size
    edge_y = [0, 0, None]*edge_size
    edge_z = [0, 0, None]*edge_size

    #edge_colors = [''] * edge_size
    for i, edge in enumerate(G.edges()):
        x0, y0, z0 = positions[edge[0]]
        x1, y1, z1 = positions[edge[1]]
        edge_x[i*3], edge_x[i*3+1] = [x0, x1]
        edge_y[i*3], edge_y[i*3+1] = [y0, y1]
        edge_z[i*3], edge_z[i*3+1] = [z0, z1]
        #edge_colors[i] = nodesc[edge[0]]

    edge_trace = Scatter3d(x=edge_x,
                       y=edge_y,
                       z=edge_z,
                       mode='lines',
                        name=name,
                       #line=Line(color='rgba(136, 136, 136, .8)', width=1),
                       line=Line(color=color, width=1),
                       hoverinfo='none'
                       )
    fig.add_trace(edge_trace)

def visualize_graph_interlayer(G, fig, color, name="", offsetZ = 0):
    edge_size = len(G.edges())
    edge_x = [0, 0, None]*edge_size
    edge_y = [0, 0, None]*edge_size
    edge_z = [0, 0, None]*edge_size

    #edge_colors = [''] * edge_size
    for i, edge in enumerate(G.edges()):
        x0, y0, z0 = allpos[edge[0]]
        x1, y1, z1 = allpos[edge[1]]
        edge_x[i*3], edge_x[i*3+1] = [x0, x1]
        edge_y[i*3], edge_y[i*3+1] = [y0, y1]
        edge_z[i*3], edge_z[i*3+1] = [z0+offsetZ, z1 + offsetZ]
        #edge_colors[i] = nodesc[edge[0]]

    edge_trace = Scatter3d(x=edge_x,
                       y=edge_y,
                       z=edge_z,
                       mode='lines',
                       #line=Line(color='rgba(136, 136, 136, .8)', width=1),
                       line=Line(color=color, width=1),
                       hoverinfo='none',
                           name=name
                       )
    fig.add_trace(edge_trace)

def genHoverTextT(G, ids, final, cost=False):
    labels = get_node_labels(G)
    nodesize = len(G.nodes())
    texts = [''] * nodesize
    for i in range(nodesize):
        name = ids.at[int(G.nodes()[i]),'labels']
        #name = G.nodes()[i]
        texts[i] += "Name: " + name + "<br>"
        texts[i] += "Id: "+ G.nodes()[i] + "<br>"
        texts[i] += "R_moy: " + str(final.iloc[i].Residue) + "<br>"
        texts[i] += "R_med: " + str(final.iloc[i].ResidueMedian) + "<br>"
        texts[i] += "R_score: " + str(final.iloc[i].Score) + "<br>"

    return texts

def genHoverText(G, ids, final):
    labels = get_node_labels(G)
    nodesize = len(G.nodes())
    texts = [''] * nodesize
    for i in range(nodesize):
        texts[i] += "Name: "+ G.nodes()[i] + "<br>"
        texts[i] += "D: " + str(labels[i])
    return texts

def visualize_graph_3d(G, ids, final, filename, title="3d", cost=False):
    Gt = G.get_subgraph("triplets")
    Gv = G.get_subgraph("views")
    Ge = G.get_subgraph("triplets_views")

    fig = go.Figure()
    if cost:
        weight = final["ResidueMedian"]
    else:
        weight = final["Residue"]
    weight = final["Score"]
    #weight += [1]*len(weight)
    #weight = np.log10(weight)

    visualize_graph_layer(Gt, fig, weight=weight,
                          text=genHoverTextT(Gt, ids, final, cost),
                          color=f'rgb(0, 255, 0)', colorscale="Viridis", name="triplets",
                          size=3,
                          offset=[0, 0, 0], symbol="square", edge=False)

    labels = get_node_labels(Gv)
    w = []
    for i in range(len(labels)):
        w.append(int(labels[i]))

    visualize_graph_layer(Gv, fig, weight=w,
                          text=genHoverText(Gv, ids, final),
                          color=f'rgb(255, 0, 0)', colorscale="inferno",
                          symbol="circle",
                          name="views")

    visualize_graph_interlayer(Ge, fig, color=f'rgb(0, 0, 255)',
                               name="inter")
    mi = 9999999
    ma = -9999999
    for e in allpos.values():
        for ee in e:
            if ee > ma:
                ma = ee
            if ee < mi:
                mi = ee
    print(mi)
    print(ma)

    axis = dict(showbackground=True,
                showline=True,
                zeroline=True,
                showgrid=True,
                showticklabels=False,
                range = [mi-1,ma+1]
                )

    layout = Layout(
        title=title,
#        width=1000,
#        height=1000,
        showlegend=True,
        scene=Scene(
            xaxis=XAxis(axis),
            yaxis=YAxis(axis),
            zaxis=ZAxis(axis),
            aspectratio=dict(x=1, y=1, z=1)
        ),
        margin=Margin(
            t=10
        ),
        hovermode='closest',
        annotations=Annotations([
            Annotation(
                showarrow=False,
                text="",
                xref='paper',
                yref='paper',
                x=0,
                y=10,
                xanchor='left',
                yanchor='bottom',
            )
        ]), )

    fig.update_layout(layout)
    offpy(fig, filename=filename, auto_open=True, show_link=True)


