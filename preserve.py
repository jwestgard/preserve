#!/usr/bin/env python3
#-*- coding: utf-8 -*-

import argparse
import csv
from datetime import datetime as dt
import hashlib
import os
import sys
import time


def compare(args):
    for n,f in enumerate(args.files):
        print("file {0}: {1}".format(n,f))


def bytecount(args):
    print(args)


def inventory(args):
    print(args)


def main():

    # main parser for command line arguments
    parser = argparse.ArgumentParser(
        description='Digital preservation utilities.'
        )
    subparsers = parser.add_subparsers(
        title='subcommands', 
        description='valid subcommands', 
        help='-h additional help', 
        metavar='{bc,inv,comp}'
        )
    
    # parser for the bytecount sub-command
    bytecount_parser = subparsers.add_parser(
        'bytecount', aliases=['bc'], 
        help='count files and sizes in bytes',
        description='help for bytecount subcommand'
        )
    bytecount_parser.add_argument('path', help='path to files')
    bytecount_parser.add_argument(
        '-r', '--recursive', 
        help='recurse through subdirectories',
        action='store_true'
        )
    bytecount_parser.set_defaults(func=bytecount)
    
    # parser for the inventory sub-command
    inventory_parser = subparsers.add_parser(
        'inventory', 
        help='create inventory of files and checksums',
        aliases=['inv']
        )
    inventory_parser.add_argument(
        '-r', '--recursive',
        help='recurse through subdirectories',
        action='store_true'
        )
    inventory_parser.add_argument('path', help='path to files')
    inventory_parser.set_defaults(func=inventory)
    
    # parser for the compare sub-command
    compare_parser = subparsers.add_parser(
        'compare', 
        help='compare and verify inventories',
        aliases=['comp']
        )
    compare_parser.add_argument(
        'files', nargs='*',
        help='two or more files to compare'
        )
    compare_parser.set_defaults(func=compare)

    # parse the args and call the default sub-command function
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()



'''

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


'''
