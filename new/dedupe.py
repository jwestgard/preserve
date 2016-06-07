#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
import os, sys, hashlib
from subprocess import call

BLOCKSIZE = 65536

def count_by_ext(files):
    result = {}
    for f in files:
        ext = os.path.splitext(f)[1][1:]
        if ext in result.keys():
            result[ext] += 1
        else:
            result[ext] = 1
    return result

def filter_by_ext(files, ext):
    result = []
    for f in files:
        if f.endswith(ext):
            result.append(f)
        else:
            pass
    return result

def human_readable_size(b):
    bytes = int(b)
    if bytes >= 2**40:
        return "{0} TB".format(round(bytes / 2**40), 2)
    elif bytes >= 2**30:
        return "{0} GB".format(round(bytes / 2**30), 2)
    elif bytes >= 2**20:
        return "{0} MB".format(round(bytes / 2**20), 2)
    else:
        return "{0} KB".format(round(bytes / 2**10), 2)

def listfiles(path):
    result = []
    for root, dirs, files in os.walk(path):
        print("\n", root)
        # prune directories beginning with dot
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        # prune files beginning with dot
        files[:] = [f for f in files if not f.startswith('.')]
        try:
            files = filter_by_ext(files, sys.argv[2])
        except IndexError:
            pass
        for f in files:
            path = os.path.join(root, f)
            if os.path.islink(path):
                print("! skipping link ->", path)
            else:
                print("  •", f)
                bytes = os.path.getsize(path)
                result.append((path, bytes))
    return result
        
def total_bytes(files):
    return sum(f[1] for f in files)
    
def md5_check(path_to_file):
    hasher = hashlib.md5()
    with open(path_to_file, 'rb') as f:
        buf = f.read(BLOCKSIZE)
        while len(buf) > 0:
            hasher.update(buf)
            buf = f.read(BLOCKSIZE)
        return hasher.hexdigest()
    
def md5_compare(files_grouped_by_size):
    result = {}
    for byte_size in files_grouped_by_size.keys():
        for path in files_grouped_by_size[byte_size]:
            h = md5_check(path)
            if h in result:
                result[h].append(path)
            else:
                result[h] = [path]
    return result
    
def print_report(dupes_by_hash):
    print("{0} Sets of Possible Duplicate Files:".format(len(dupes_by_hash)))
    for n, d in enumerate(dupes_by_hash):
        print("\n{0}. {1}".format(n+1, d))
        for f in dupes_by_hash[d]:
            print("\t{0}".format(f))
    print("\n***END OF REPORT***\n")

def group_by_bytes(filelist):
    byte_match_dict = {}
    for path, bytes in filelist:
        if bytes in byte_match_dict:
            byte_match_dict[bytes].append(path)
        else:
            byte_match_dict[bytes] = [path]
    result = { k: v for k, v in byte_match_dict.items() if len(v) > 1 }
    return result

def main():
    searchroot = os.path.dirname(sys.argv[1])
    print("\n\n*** FILE REPORTER ***")
    print("\nChecking the following directory: {0} ...".format(searchroot))
    filelist = listfiles(searchroot)
    total = total_bytes(filelist)
    print("\nTotal: {0} bytes, or {1} for {2} files.".format(
        total, human_readable_size(total), len(filelist)))
    counts = count_by_ext([f[0] for f in filelist])
    count_display = ", ".join(".{0} ({1})".format(
        k, counts[k]) for k in sorted(counts.keys()))
    print("Extensions: {0}\n".format(count_display))
    possible_matches = group_by_bytes(filelist)
    print("{0} file-groups match by size".format(len(possible_matches)))
    hash_matches = md5_compare(possible_matches)
    print_report({ k: v for k, v in hash_matches.items() if len(v) > 1 })

if __name__ == "__main__":
    main()
