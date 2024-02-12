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

nArg = len(sys.argv)
refDir = sys.argv[1]
#testDir = sys.argv[2]

path = Path(refDir)
workingDir = path.parent.absolute()
print(workingDir)

def micmacBascule(wDir, rDir, tDir, Debug=False):
    cwd = os.getcwd()
    os.chdir(wDir)
    cmd_morito = ["mm3d", "Morito", os.path.split(rDir)[1]
                  +"/Orientation-.*.xml", "" + \
            os.path.split(tDir)[1] + "/Orientation-.*.xml", \
                  os.path.split(tDir)[1].removeprefix("Ori-") + "Basculed"]
    #print(cmd_morito)

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
                  os.path.split(tDir)[1] + "Basculed"]
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


def exp(it, r0, pond, i):
    cmd = []
    cmd.append("mm3d")
    cmd.append("TestLib")
    cmd.append("NO_SolInit_RndForest")
    cmd.append(".*.tif")
    cmd.append("OriCalib=CalibPerf")
    cmd.append("OriOut=BestInit" + str(i))
    cmd.append("SH=5Pts")
    cmd.append("Nb=" + str(it))
    cmd.append("R0=" + str(r0))
    cmd.append("Pond=" + str(pond))
    return cmd

def exec(params, i):
    cmd = exp(params[0], params[1], params[2], i)
    #print(cmd)
    log = open("/dev/null", "w")
    process = subprocess.Popen(cmd, stdout=log, stderr=log)
    #stdout, stderr = process.communicate()
    #process.wait()
    #print(stdout)
    return process

def verif(i):
    micmacBascule(workingDir, refDir, "Ori-BestInit"+str(i)+"0")
    return micmacCmp(workingDir, refDir, "Ori-BestInit"+str(i)+"0")



def f(cmd, j):
    start = time.time()
    p = exec(cmd, j)
    p.communicate()
    center, angles = verif(j)
    end = time.time()
    print("Center : " + str(center) + " Angle : " + str(angles) \
            + " on " + str(j) + " in " + str(end - start))
    return center, angles

listes_exp = [ \
                [ 500, 10, 1], \
                [ 500, 10, 0], \
            ]

def experiences(cmds, i = 0):
    print("Number of tests to try: " + str(len(cmds)) + " N times: " + str(i))
    processes = []
    for c in range(len(cmds)):
        results_center = []
        results_angles = []
        with Pool(processes=10) as pool:
            multiple_results = [pool.apply_async(f, (cmds[c], j)) for j in range(i)]
            for res in multiple_results:
                center, angles = res.get(timeout=10000)
                results_center.append(center)
                results_angles.append(angles)

        print("-------------------------------")
        print("         Result for :          ")
        print(cmds[c])
        print("---")
        print(results_center)
        print(results_angles)
        print("---")
        print(str(np.mean(results_center)) + " - " + str(np.std(results_center)) + " - " + str(np.var(results_center)))
        print(str(np.mean(results_angles)) + " - " + str(np.std(results_angles)) + " - " + str(np.var(results_angles)))
        print("-------------------------------")

experiences(listes_exp, 50)
