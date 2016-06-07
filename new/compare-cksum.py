#!/usr/bin/env python3
#-*- coding: utf-8 -*-

import csv
import sys

with open(sys.argv[1], 'r') as f1:
    reader1 = csv.DictReader(f1)
    files1 = {f['File']: f for f in reader1}
    
with open(sys.argv[2], 'r') as f2:
    reader2 = csv.DictReader(f2, delimiter="\t")
    files2 = {f['Filename']: f for f in reader2}


k1 = set(files1.keys())
k2 = set(files2.keys())

allfiles = k1.union(k2)

for n, f in enumerate(allfiles):
    try:
        md51 = files1[f]['MD5']
    except KeyError:
        md51 = "n/a"
    try:
        md52 = files2[f]['Other']
    except KeyError:
        md52 = "n/a"
    
    if md51 == md52:
        comparison = "Match"
    else:
        comparison = "NO MATCH!"
    
    print("{0},{1},{2},{3},{4}".format(n+1, f, md51, md52, comparison))
