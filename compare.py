#!/bin/python
import sys, os
import lxml.objectify
import xml.etree.ElementTree as ET
from lxml import etree
import glob
import numpy as np
from pathlib import Path
import shutil
import random
import subprocess
from parse import compile
import time
from concurrent.futures import ThreadPoolExecutor
from multiprocessing import Process
from multiprocessing import Pool, TimeoutError
import plotly.express as px
import plotly.graph_objects as go
import csv
import sys, os
from plotly.offline import plot as offpy
import glob


from basculed import *

nArg = len(sys.argv)
refDir = sys.argv[1]
testDir = sys.argv[2]

path = Path(refDir)
workingDir = path.parent.absolute()
print(workingDir)

def find_extension(r):
    files = glob.glob(r + "/Orientation-*.xml")
    extension = files[0].split('.')[-2]
    print("Images extensions: " + extension)
    return extension


image_extension = find_extension(refDir)

# Morito utiliser que 3 images au lieu de toutes les images
def f(t):
    start = time.time()
    micmacBascule(workingDir, refDir, t)
    center, angles = micmacCmp(workingDir, image_extension, refDir, t)
    end = time.time()
    #print("Center : " + str(center) + " Angle : " + str(angles) \
    #        + " in " + str(end - start))
    return center, angles

print(testDir)
if testDir.find('*') != -1:
    directories = glob.glob(testDir)
    csv_log = open("differences.csv", "w")
    results_center = []
    results_angles = []
    with Pool(processes=10) as pool:
        multiple_results = []
        for t in directories:
            if not "Basculed" in t:
                multiple_results.append((pool.apply_async(f, (t, )), t))
        for res, d in multiple_results:
            center, angles = res.get(timeout=10000)
            results_center.append(center)
            results_angles.append(angles)
            csv_log.write(d + "," + str(center) + "," + str(angles))

    print("-------------------------------")
    print("         Results :          ")
    print(results_center)
    print(results_angles)
    print("---")
    print(str(np.mean(results_center)) + " - " + str(np.std(results_center)) + " - " + str(np.var(results_center)))
    print(str(np.mean(results_angles)) + " - " + str(np.std(results_angles)) + " - " + str(np.var(results_angles)))
    print("-------------------------------")

    fg = go.Figure()
    fg.add_trace(go.Histogram(x=results_center,
                        name='Centers'))
    fg.add_trace(go.Histogram(x=results_angles,
                        name='Angles'))
    offpy(fg, filename="triplets.html", auto_open=True, show_link=True)

    csv_log.close()
else:
    micmacBascule(workingDir, refDir, testDir)
    micmacCmp(workingDir, image_extension, refDir, testDir)


#basculeDir = workingDir / "Ori-TMPBascule"

#def createBasculeOri():
#    for f in glob.glob(refDir + "/AutoCal*"):
#        shutil.copy(f, workingDir / "Ori-TMPBascule")
#    for f in glob.glob(refDir + "/Orientation*"):
#        shutil.copy(f, workingDir / "Ori-TMPBascule")
#    return
#
#    ori = glob.glob(refDir + "/Orientation*")
#    shutil.copy(ori[0],workingDir / "Ori-TMPBascule")
#    shutil.copy(ori[-1], workingDir/ "Ori-TMPBascule")

#shutil.rmtree(basculeDir, ignore_errors=True)
#os.mkdir(basculeDir)
#createBasculeOri()


quit(0)

finaltestDir = workingDir / "Ori-Basculed"

def loadOrientation(path):
    views = {}
    orientations = glob.glob(path + "/Orientation-*.xml")
    for ori in orientations:
        name = os.path.basename(ori)
        imagename = name.removeprefix("Orientation-").removesuffix(".xml")
        #print(imagename)
        img = {}
        tree = etree.parse(ori)
        for center in tree.xpath("/OrientationConique/Externe/Centre"):
            #print(center.text)
            pos = []
            for n in center.text.split(" "):
                pos.append(float(n))
            img["position"] = pos
        a = []
        for angles in tree.xpath("/OrientationConique/Externe/ParamRotation/CodageMatr/*"):
            #print(angles.text)
            l = []
            for n in angles.text.split(" "):
                l.append(float(n))
            a.append(l)
        img["angle"] = a
        views[str(imagename)] = img
    #print(views)
    return views

ref = loadOrientation(refDir)
test = loadOrientation(finaltestDir.as_posix())

for keys in test.keys():
    if not keys in ref.keys():
        print("Missing view in ref: " + str(keys))
        quit(1)

errors = []
for key in test.keys():
    pos_ref = np.array(ref[key]["position"])
    pos_test = np.array(test[key]["position"])
    # calculating Euclidean distance
    # using linalg.norm()
    diff = pos_ref - pos_test
    dist = np.linalg.norm(diff)
    # printing Euclidean distance
    #print(key + " - " + str(dist) + " - " + str(diff))
    errors.append(dist)
print ("Error : " + str(np.mean(errors)) + " - " + str(np.var(errors)))

# Faire la bascule avec morito






