#!/usr/bin/env python3

import re, sys, os, csv

def extract(data):
    rawlines = [line.strip('\n') for line in data]
    result = []
    if rawlines[0] == "IBM Tivoli Storage Manager":
        print("Parsing Tivoli output file...")
        p = re.compile('\\\\\\\\.+\\\\(.+) \[Sent\]')
        for l in rawlines:
            if l.startswith('Normal File-->'):
                m = p.search(l)
                if m:
                    result.append(m.group(1))
    elif "Key" in rawlines[0] or "Filename" in rawlines[0]:
        print("Parsing File Analyzer file...")
        reader = csv.DictReader(rawlines, delimiter="\t")
        filenamecol = "Key" if "Key" in rawlines[0] else "Filename"
        for l in reader:
            result.append(l[filenamecol])
    else:
        print("Unrecognized file type ...")
        return
    return result

def compare(**kwargs):
    all_lists = [set(kwargs[k]) for k in kwargs]
    common = set.intersection(*all_lists)
    print("{} values are common to all the supplied files.".format(len(common)))
    for n, k in enumerate(kwargs):
        unique = set(kwargs[k]).difference(common)
        print(" • File {0}: {1} values are unique to {2}".format(n+1, len(unique), k))
        if unique is not None:
            sorted_files = sorted(unique)
            for fnum, fname in enumerate(sorted_files):
                print("\t({0}) {1}".format(fnum+1, fname))

def main():
    print("")
    print("preserve.py file checker")
    print("="*24)
    filelists = {}
    for filepath in sys.argv[1:]:
        with open(filepath, 'r') as f:
            rawdata = f.readlines()
            filelist = extract(rawdata)
            if filelist:
                filelists[filepath] = filelist
                print(" >", filepath, ":", len(filelist), "files")
            else:
                print(" > File", filepath, "has not been parsed.")
    compare(**filelists)
    
if __name__ == "__main__":
    main()
