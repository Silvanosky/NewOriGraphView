import glob
import shutil
import os
import sys
import parse

folder = sys.argv[1]
ignore = sys.argv[2]

print("Search: " + folder + "/Orientation-*.xml")

images = set()

for i in glob.glob(folder + "/Orientation-*.xml"):
    name = parse.parse(folder + "/Orientation-{}.xml", i)[0]
    print(name)
    images.add(name)

k = 0
for i in glob.glob("20*.png"):
    print(i)
    if i not in images:
        print(i)
        shutil.move(i, ignore+"/"+i)
        k += 1

print("Number of images:" + str(k))
