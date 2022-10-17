#!/bin/python
import pandas as pd
#import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
import csv
import sys, os

pd.options.plotting.backend = "plotly"

def pause():
    programPause = input("Press the <ENTER> key to continue...")

nArg = len(sys.argv)

curDir = sys.argv[1]
mode = sys.argv[2]
numberIter = int(sys.argv[3])
if nArg >= 5 :
    distN = int(sys.argv[4])
else:
    distN = -1


def loadRes(i, fig):
    file = curDir + "/triplets/" + str(i) + ".csv"
    if not os.path.exists(file):
        return
    data = pd.read_csv(file, parse_dates=True)
    data = data.sort_values(by=['Residue']).reset_index(drop=True)
    fig.add_trace(go.Scatter(x=data.index, y=data['Residue'],
                    mode='lines+markers',
                    name=str(i)))

def loadDist(i, fig):
    file = curDir + "/triplets/" + str(i) + ".csv"
    if not os.path.exists(file):
        return
    data = pd.read_csv(file, parse_dates=True)
    data = data.sort_values(by=['Distance']).reset_index(drop=True)
    #fig.add_trace(go.Scatter3d(x=data.index, y=data.Residue, z=data.Distance,
    #                           mode='markers'))
    fig.add_trace(go.Scatter(x=data.Distance, y=data.Residue,
                               mode='markers',
                             name=str(i)))

    #fig = data["Distance"].plot.hist(bins=20)
    #fig.show()

def loadDistN(N, i, fig):
    file = curDir + "/triplets/" + str(i) + ".csv"
    if not os.path.exists(file):
        return
    data = pd.read_csv(file, parse_dates=True)
    data = data.sort_values(by=['Residue']).reset_index(drop=True)
    filtDist = data[data['Distance']==N]
    filtDist = filtDist.sort_values(by=['Residue']).reset_index(drop=True)
    fig.add_trace(go.Scatter3d(x=data.index, y=data.Distance, z=data.Residue,
                               mode='markers',
                               name=str(i)))
    #fig.add_trace(go.Scatter(x=filtDist.index, y=filtDist.Residue,
    #                           mode='lines+markers',
    #                         name=str(i)))

    #fig = data["Distance"].plot.hist(bins=20)
    #fig.show()


#TODO Histogram pour la meme distance le residue de chaque triplet, cumulé ou
# ou pas

total = pd.read_csv(curDir + "/total.csv", parse_dates=True)
final = pd.read_csv(curDir + "/final.csv", parse_dates=True)
total = total.sort_values(by=['Residue']).reset_index(drop=True)
total['x1'] = total.index
#total = total.sort_values(by=['Cost']).reset_index(drop=True)
total['x2'] = total.index

#final = final.sort_values(by=['Residue']).reset_index(drop=True)
final['x1'] = final.index

for idx, row in final.iterrows():
    if row.Id:
        tr = total.loc[total['Id'] == row.Id]
        final.at[idx,'x1'] = int(tr.x2)

#s1 = pd.merge(total, final, how='inner', on=['Id'])
#print(s1.head())

print(total.head())
print(final.head())

#fig = px.scatter_3d(total, x='x1', y='Residue', z='Cost', size='Distance',
#                    size_max=18, opacity=0.7, log_y=True, log_z=True)
# tight layout
#fig.update_layout(margin=dict(l=0, r=0, b=0, t=0))
#fig.show()

# Create traces
fig = go.Figure()
fig.add_trace(go.Scatter(x=total['x1'], y=total['Residue'],
                    mode='lines+markers',
                    name='Residue'))
fig.add_trace(go.Scatter(x=total['x2'], y=total['Cost'],
                    mode='lines+markers',
                    name='Cost'))
fig.add_trace(go.Scatter(x=final['x1'], y=final['Residue'],
                    mode='markers', name='Final'))

fig.update_yaxes(type="log")
fig.show()

layout = {
  "scene": {
    "xaxis": {
      "title": "index"
    },
    "yaxis": {
#      "type": "log",
      "title": "Distance"
    },
    "zaxis": {
      "type": "log",
      "title": "Residue (px)"
    }
  },
  "title": "Distances",
  "margin": {
    "b": 40,
    "l": 60,
    "r": 10,
    "t": 25
  },
  "hovermode": "closest",
  "showlegend": False
}

fig2 = go.Figure()
fig3 = go.Figure(layout=layout)
if mode == "all":
#    plt.figure(num="Residue")
    for i in range(numberIter):
        loadRes(i, fig2)
#    plt.show(block=False)
#    plt.figure(num="Distance")
    for i in range(numberIter):
        if distN > 0:
            loadDistN(distN, i, fig3)
        else:
            loadDist(i, fig3)
#    plt.show(block=False)
elif mode == "one":
#    plt.figure(num="Residue")
    loadRes(numberIter,fig2)
#    plt.show(block=False)
#    plt.figure(num="Distance")
    if distN > 0:
        loadDistN(distN, i, fig3)
    else:
        loadDist(numberIter, fig3)
#    plt.show(block=False)

fig2.update_yaxes(type="log")
fig2.show()
fig3.update_yaxes(type="log")
fig3.show()

#pause()