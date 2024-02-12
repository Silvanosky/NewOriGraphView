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


def exp(it, r0, pond, i):
    return ["mm3d", "TestLib", "NO_SolInit_RndForest", ".*.tif",
            "OriCalib=CalibPerf", "SH=5Pts", "OriOut=BestInit" + str(i), "Nb=" + str(it), "R0=" + str(r0), "Pond=" + str(pond)]

def exec_(params, i):
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
    return micmacCmp(workingDir, "tif", refDir, "Ori-BestInit"+str(i)+"0")

def f(cmd, j):
    start = time.time()
    p = exec_(cmd, j)
    p.communicate()
    center, angles = verif(j)
    end = time.time()
    elapsedtime = end - start
    print("Center : " + str(center) + " Angle : " + str(angles) \
            + " on " + str(j) + " in " + str(elapsedtime))
    return center, angles, elapsedtime

def experiences(cmds, i = 0):
    print("Number of tests to try: " + str(len(cmds)) + " N times: " + str(i))
    csvfile = open('results.csv', 'w', newline='')
    fieldnames = ['N', 'R0', 'Pond', 'DistCenter', 'DistAngle', 'Time']
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
                center, angles, elapsedtime = res.get(timeout=10000)
                with csv_writer_lock:
                    writer.writerow({'N': cmds[c][0], 'R0': cmds[c][1], 'Pond':
                                 cmds[c][2], 'DistCenter': center, 'DistAngle':
                                     angles, 'Time': elapsedtime})
                    csvfile.flush()
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


listes_exp = []
for n in range(100, 5001, 100):
    listes_exp.append([n, 10, 1])
    listes_exp.append([n, 10, 0])
print(listes_exp)

experiences(listes_exp, 10)
