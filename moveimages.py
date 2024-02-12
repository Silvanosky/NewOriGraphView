import glob
import shutil
import os

k = 0
for i in glob.glob("./20*.png"):
    if k % 2 != 0:
        print(i)
        shutil.move(i, 'ignored/'+i)
    k += 1
