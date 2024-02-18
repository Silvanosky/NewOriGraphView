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
imageExt = sys.argv[2]

#testDir = sys.argv[2]

path = Path(refDir)
workingDir = path.parent.absolute()
print(workingDir)

from basculed import *


def exp(it, r0, r1, pond, opti, i, oriname):
    return ["mm3d", "TestLib", "NO_SolInit_RndForest", ".*."+str(imageExt),
            "OriCalib=CalibPerf", "SH=5Pts", "OriOut=" + oriname, "Nb=" +
            str(it), "R0=" + str(r0), "R1=" + str(r1), "Pond=" + str(pond), "Opti=" + str(opti)]

def exec_(params, oriname, i):
    cmd = exp(params[0], params[1], params[2],  params[3], params[4], i, oriname)

    print(cmd)
    log = open("/dev/null", "w")
    process = subprocess.Popen(cmd, stdout=log, stderr=log)
    #stdout, stderr = process.communicate()
    #process.wait()
    #print(stdout)
    return process

def verif(oriname):
    ori = "Ori-" + oriname+"0"
    if not os.path.isdir(ori):
        return -1,-1

    micmacBascule(workingDir, refDir, ori)
    return micmacCmp(workingDir, imageExt, refDir, ori)

def verifH(oriname):
    ori = "Ori-" + oriname+"0Hierarchique"
    if not os.path.isdir(ori):
        return -1,-1

    micmacBascule(workingDir, refDir, ori)
    return micmacCmp(workingDir, imageExt, refDir, ori)


def f(cmd, j):
    oriname = "Exp-N" + str(cmd[0]) + "-R" + str(cmd[1]) + \
        "-R" + str(cmd[2]) + "-P" + str(cmd[3]) + "-" + str(j)
    start = time.time()
    p = exec_(cmd, oriname, j)
    p.communicate()
    center1, angles1 = verif(oriname)
    center2, angles2 = verifH(oriname)
    end = time.time()
    elapsedtime = end - start
    print("Center : " + str(center1) + " Angle : " + str(angles1) \
            + " on " + str(j) + " in " + str(elapsedtime))
    return cmd, center1, angles1, center2, angles2, elapsedtime

def experiences(cmds, i = 0):
    print("Number of tests to try: " + str(len(cmds)) + " N times: " + str(i))
    csvfile = open('results.csv', 'w', newline='')
    fieldnames = ['N', 'R0', 'R1', 'Pond', 'DistCenter', 'DistAngle', 'DistHCenter',
                  'DistHAngle', 'Time']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    csv_writer_lock = threading.Lock()

    with Pool(processes=10) as pool:
        multiple_results = [pool.apply_async(f, (cmds[j//i], j%i)) for j in
                            range(len(cmds) * i)]
        for res in multiple_results:
            cmd, center1, angles1, center2, angles2, elapsedtime = res.get(timeout=10000)
            with csv_writer_lock:
                writer.writerow({'N': cmd[0],
                                     'R0': cmd[1],
                                     'R1': cmd[2],
                                     'Pond': cmd[3],
                                     'DistCenter': center1,
                                     'DistAngle': angles1,
                                     'DistHCenter': center2,
                                     'DistHAngle': angles2,
                                     'Time': elapsedtime})
                csvfile.flush()

#        print("-------------------------------")
#        print("         Result for :          ")
#        print(cmds[c])
#        print("---")
#        print(results_center)
#        print(results_angles)
#        print("---")
#        print(str(np.mean(results_center)) + " - " + str(np.std(results_center)) + " - " + str(np.var(results_center)))
#        print(str(np.mean(results_angles)) + " - " + str(np.std(results_angles)) + " - " + str(np.var(results_angles)))
#        print("-------------------------------")


listes_exp = []
for r0 in np.arange(0., 5, 0.2):
    for r1 in np.arange(0., 5, 0.2):
        listes_exp.append([1000, r0, r1, 1, 0])
print(listes_exp)

experiences(listes_exp, 1)
