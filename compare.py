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

nArg = len(sys.argv)
refDir = sys.argv[1]
testDir = sys.argv[2]

path = Path(refDir)
workingDir = path.parent.absolute()
print(workingDir)

basculeDir = workingDir / "Ori-TMPBascule"

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


cwd = os.getcwd()
os.chdir(workingDir)
os.system("mm3d Morito \""+os.path.split(refDir)[1] +"/Orientation-.*.xml\" \"" + \
          os.path.split(testDir)[1] + "/Orientation-.*.xml\" Basculed")

os.system("mm3d CmpOri \".*.tif\" \""+os.path.split(refDir)[1] + "/\" \"Ori-Basculed/\"")

os.chdir(cwd)

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






