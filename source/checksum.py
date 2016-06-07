#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import csv
from datetime import datetime as dt
import hashlib
import os
import sys
import time


def md5sum(filepath):
    with open(filepath, 'rb') as f:
        m = hashlib.md5()
        while True:
            data = f.read(8192)
            if not data:
                break
            m.update(data)
        return m.hexdigest()


def listfiles(path):
    result = []
    for root, dirs, files in os.walk(path):
        # prune directories beginning with dot
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        # prune files beginning with dot
        files[:] = [f for f in files if not f.startswith('.')]
        result.extend([os.path.join(root, f) for f in files])
    return result


def resume_job(path):
    with open(path, 'r') as f:
        reader = csv.DictReader(f)
        result = {}
        for row in reader:
            filepath = os.path.join(row['Directory'], row['File'])
            result[filepath] = row
    return result


def main():
    allfiles = listfiles(sys.argv[1])

    # check whether output file exists, and if so read it and resume job
    try:
        complete = resume_job(sys.argv[2])
        files_to_check = set(allfiles).difference([key for key in complete])
    except FileNotFoundError:
        files_to_check = allfiles
        complete = []

    fieldnames = ['Directory', 'File', 'Extension', 'Bytes', 'MTime', 'Moddate',
                    'MD5']

    with open(sys.argv[2], 'w+') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        count = 0
        total = len(allfiles)
        
        for cf in complete:
            writer.writerow(complete[cf])
            count += 1
            
        for f in files_to_check:
            tstamp = int(os.path.getmtime(f))
            metadata = {'Directory': os.path.dirname(os.path.abspath(f)),
                        'File': os.path.basename(f),
                        'MTime': tstamp,
                        'Moddate': dt.fromtimestamp(tstamp).strftime(
                            '%Y-%m-%dT%H:%M:%S'),
                        'Extension': os.path.splitext(f)[1].lstrip('.').upper(),
                        'Bytes': os.path.getsize(f),
                        'MD5': md5sum(f)}
            writer.writerow(metadata)
            count += 1
            print("Files checked: {0}/{1}".format(count, total), end='\r')

    print('')


main()

# parse args
# run main with options set



