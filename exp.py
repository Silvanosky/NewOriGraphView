#!/bin/python

import sys, os
import xml.etree.ElementTree as ET
import lxml.objectify
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
import csv
import threading

nArg = len(sys.argv)
refDir = sys.argv[1]
#testDir = sys.argv[2]

path = Path(refDir)
workingDir = path.parent.absolute()
print(workingDir)

from basculed import *


def exp(it, r0, pond, opti, i):
    return ["mm3d", "TestLib", "NO_SolInit_RndForest", ".*.tif",
            "OriCalib=CalibPerf", "SH=5Pts", "OriOut=BestInit" + str(i), "Nb=" +
            str(it), "R0=" + str(r0), "Pond=" + str(pond), "Opti=" + str(opti)]

def exec_(params, i):
    cmd = exp(params[0], params[1], params[2], params[3], i)

    print(cmd)
    log = open("/dev/null", "w")
    process = subprocess.Popen(cmd, stdout=log, stderr=log)
    #stdout, stderr = process.communicate()
    #process.wait()
    #print(stdout)
    return process

def verif(i):
    ori = "Ori-BestInit"+str(i)+"0"
    if not os.path.isdir(ori):
        return -1,-1

    micmacBascule(workingDir, refDir, ori)
    return micmacCmp(workingDir, "tif", refDir, ori)

def verifH(i):
    ori = "Ori-BestInit"+str(i)+"0Hierarchique"
    if not os.path.isdir(ori):
        return -1,-1

    micmacBascule(workingDir, refDir, ori)
    return micmacCmp(workingDir, "tif", refDir, ori)


def f(cmd, j):
    start = time.time()
    p = exec_(cmd, j)
    p.communicate()
    center1, angles1 = verif(j)
    center2, angles2 = verifH(j)
    end = time.time()
    elapsedtime = end - start
    print("Center : " + str(center1) + " Angle : " + str(angles1) \
            + " on " + str(j) + " in " + str(elapsedtime))
    return center1, angles1, center2, angles2, elapsedtime

def experiences(cmds, i = 0):
    print("Number of tests to try: " + str(len(cmds)) + " N times: " + str(i))
    csvfile = open('results.csv', 'w', newline='')
    fieldnames = ['N', 'R0', 'Pond', 'DistCenter', 'DistAngle', 'DistHCenter',
                  'DistHAngle', 'Time']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    csv_writer_lock = threading.Lock()

    processes = []
    for c in range(len(cmds)):
        results_center = []
        results_angles = []
        with Pool(processes=10) as pool:
            multiple_results = [pool.apply_async(f, (cmds[c], j)) for j in range(i)]
            for res in multiple_results:
                center1, angles1, center2, angles2, elapsedtime = res.get(timeout=10000)
                with csv_writer_lock:
                    writer.writerow({'N': cmds[c][0], 'R0': cmds[c][1], 'Pond':
                                     cmds[c][2], 'DistCenter': center1, 'DistAngle':
                                     angles1, 'DistHCenter': center2,
                                     'DistHAngle': angles2, 'Time': elapsedtime})
                    csvfile.flush()
                results_center.append(center1)
                results_angles.append(angles1)

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


listes_exp = []
for n in np.arange(0.1, 2, 0.1):
    listes_exp.append([500, n, 1, 0])
print(listes_exp)

experiences(listes_exp, 10)
