#!/bin/python
import sys, os
import lxml.objectify
import xml.etree.ElementTree as ET
from lxml import etree
import glob
import numpy as np

nArg = len(sys.argv)
refDir = sys.argv[1]
testDir = sys.argv[2]

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
    print(views)
    return views

ref = loadOrientation(refDir)
test = loadOrientation(testDir)

for keys in test.keys():
    if not keys in ref.keys():
        print("Missing view in ref: " + str(keys))
print("ok")

errors = 0
n = 0

for key in test.keys():
    pos_ref = np.array(ref[key]["position"])
    pos_test = np.array(test[key]["position"])
    # calculating Euclidean distance
    # using linalg.norm()
    diff = pos_ref - pos_test
    dist = np.linalg.norm(diff)
    # printing Euclidean distance
    print(str(dist) + " - " + str(diff))
    errors += dist
    n += 1
print ("Mean error : " + str(errors/n))





