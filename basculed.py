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

def micmacBascule(wDir, rDir, tDir, Debug=False):
    cwd = os.getcwd()
    os.chdir(wDir)
    cmd_morito = ["mm3d", "Morito",\
                os.path.split(rDir)[1] + "/Orientation-.*.xml",
                os.path.split(tDir)[1] + "/Orientation-.*.xml", \
                os.path.split(tDir)[1].removeprefix("Ori-") + "Basculed", \
                "FUO=2"]
    print(cmd_morito)

    ex = subprocess.Popen(cmd_morito, stdout=subprocess.PIPE, \
                                 stderr=subprocess.PIPE)
    stdout, stderr = ex.communicate()
    if Debug:
        print(stdout)
    #print(stdout.decode('utf-8'))
    os.chdir(cwd)

def micmacCmp(wDir, rDir, tDir):
    cwd = os.getcwd()
    os.chdir(wDir)
    cmd_cmpori = ["mm3d", "CmpOri", ".*.tif", os.path.split(rDir)[1], \
            os.path.split(tDir)[1] + "Basculed", "CSV=diff.csv"]
    print(cmd_cmpori)
    ex_cmpori = subprocess.Popen(cmd_cmpori, stdout=subprocess.PIPE, \
                                 stderr=subprocess.PIPE)
    stdout, stderr = ex_cmpori.communicate()
    p = compile("Aver;  DistCenter= {} DistMatrix= {} DistMatrixAng= not calculated")
    output = stdout.decode('utf-8')
    #print (output.splitlines()[-1])
    parsed = p.parse(output.splitlines()[-1])
    print("Center Distance : " + parsed[0] + " Angle Distance : " + parsed[1])
    os.chdir(cwd)
    return (float(parsed[0]), float(parsed[1]))


