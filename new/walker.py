#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
import os, sys
from subprocess import call

def count_by_ext(files):
    result = {}
    for f in files:
        ext = os.path.splitext(f)[1][1:]
        if ext in result.keys():
            result[ext] += 1
        else:
            result[ext] = 1
    return result

def exec_shell_command(files):
    for f in files:
        print(f)
        call(['exiftool', '-*resolution*', f])

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
            print("  •", f)
            path = os.path.join(root, f)
            bytes = os.path.getsize(path)
            result.append((path, bytes))
    return result

def pretty_print(table):
    number_cols = max([len(line) for line in table])
    column_width = max([len(cell) for row in table for cell in row])
    for row in table:
        print("".join(cell.ljust(column_width) for cell in row))
        
    #    for col in range[:numcols]:
    #        if col:
    #            cell = col + (" " * 3)
    #        else:
    #            cell = " - "
    #        print("| {0} |".format(cell))
    #                
    #longest = max(len(l[0]) for l in lines)

def total_bytes(files):
    return sum(f[1] for f in files)

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
    exec_shell_command([f[0] for f in filelist])

if __name__ == "__main__":
    main()