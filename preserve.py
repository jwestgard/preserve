#!/usr/bin/env python3
#-*- coding: utf-8 -*-

import argparse
import csv
from datetime import datetime as dt
import hashlib
import os
import sys
import time


'''
====================
| HELPER FUNCTIONS |
====================

'''


def md5sum(filepath):
    '''For a given path, return the md5 checksum for that file.'''
    with open(filepath, 'rb') as f:
        m = hashlib.md5()
        while True:
            data = f.read(8192)
            if not data:
                break
            m.update(data)
        return m.hexdigest()


def listfiles(path):
    '''Return a list of files in a directory tree, 
       but pruning out the hidden files'''
    result = []
    for root, dirs, files in os.walk(path):
        # prune directories beginning with dot
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        # prune files beginning with dot
        files[:] = [f for f in files if not f.startswith('.')]
        result.extend([os.path.join(root, f) for f in files])
    return result


def resume_job(path):
    '''Return a list of file paths keyed to file metadata read
        from a file listing '''
    with open(path, 'r') as f:
        reader = csv.DictReader(f)
        result = {}
        for row in reader:
            filepath = os.path.join(row['Directory'], row['File'])
            result[filepath] = row
    return result


#=== SUBCOMMAND =============================================================
#         NAME: compare
#  DESCRIPTION: 
#============================================================================

def compare(args):

    print("")
    print("preserve.py file checker")
    print("="*24)
    
    filelists = {}
    
    for filepath in args.files:
        result = []
        with open(filepath, 'r') as f:
            rawlines = [line.strip('\n') for line in f.readlines()]
            
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
                reader = csv.DictReader(rawlines, delimiter=",")
                filenamecol = "Key" if "Key" in rawlines[0] else "Filename"
                for l in reader:
                    result.append(l[filenamecol])
            
            else:
                print("Unrecognized file type ...")
            
            if result:
                filelists[filepath] = result
                print(" >", filepath, ":", len(result), "files")
            else:
                print(" > File", filepath, "has not been parsed.")
    
    all_lists = [set(filelists[filelist]) for filelist in filelists]
    common = set.intersection(*all_lists)
    print("{} values are common to all the supplied files.".format(len(common)))

    for n, filelist in enumerate(filelists):
        unique = set(filelists[filelist]).difference(common)
        print(" • File {0}: {1} values are unique to {2}".format(n+1, 
                                                                 len(unique), 
                                                                 filelist)
             )
        if unique is not None:
            sorted_files = sorted(unique)
            for fnum, fname in enumerate(sorted_files):
                print("\t({0}) {1}".format(fnum+1, fname))


#=== SUBCOMMAND =============================================================
#         NAME: bytecount
#  DESCRIPTION: 
#============================================================================

def bytecount(args):
    
    extensions = {}
    totalbytes = 0
    all_files = listfiles(args.path)
    
    for f in all_files:
        totalbytes += os.path.getsize(f)
        ext = os.path.splitext(f)[1].lstrip('.').upper()
        if ext in extensions:
            extensions[ext] += 1
        else:
            extensions[ext] = 1
            
    print("{0} bytes for {1} files".format(totalbytes, 
                                           len(all_files)
                                           ))
    print(extensions.items())



#=== SUBCOMMAND =============================================================
#         NAME: inventory
#  DESCRIPTION: generate a file listing with checksums, size, timestamp
#============================================================================

def inventory(args):

    DIR = args.directory
    OUTFILE = args.outfile
    FIELDNAMES = [  'Directory', 
                    'Filename', 
                    'Extension', 
                    'Bytes', 
                    'MTime', 
                    'Moddate',
                    'MD5'
                    ]

    all_files = listfiles(DIR)

    # check whether output file exists, and if so read it and resume job
    try:
        complete = resume_job(OUTFILE)
        files_to_check = set(all_files).difference([key for key in complete])
        
    except FileNotFoundError:
        complete = []
        files_to_check = all_files

    # set up output headers and counter
    with open(OUTFILE, 'w+') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=FIELDNAMES)
        writer.writeheader()
        count = 0
        total = len(all_files)
        
        # write out already completed items
        for cf in complete:
            writer.writerow(complete[cf])
            count += 1
        
        # check each remaining file and generate metadata
        for f in files_to_check:
            tstamp = int(os.path.getmtime(f))
            metadata = {'Directory': os.path.dirname(os.path.abspath(f)),
                        'Filename': os.path.basename(f),
                        'MTime': tstamp,
                        'Moddate': dt.fromtimestamp(tstamp).strftime(
                            '%Y-%m-%dT%H:%M:%S'),
                        'Extension': os.path.splitext(f)[1].lstrip('.').upper(),
                        'Bytes': os.path.getsize(f),
                        'MD5': md5sum(f)
                        }
            writer.writerow(metadata)
            
            # display running counter
            count += 1
            print("Files checked: {0}/{1}".format(count, total), end='\r')

        # clear counter
        print('')


'''
=============
| MAIN LOOP |
=============

This is the main loop, parsing args and setting the default function based
on the sub-command.

'''

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
    bc_parser = subparsers.add_parser(
                            'bytecount', aliases=['bc'], 
                            help='count files and sizes in bytes',
                            description='help for bytecount subcommand'
                            )
                            
    bc_parser.add_argument('path', help='path to files')
    
    bc_parser.add_argument('-r', '--recursive', 
                            help='recurse through subdirectories',
                            action='store_true'
                            )
                            
    bc_parser.set_defaults(func=bytecount)
    
    
    # parser for the inventory sub-command
    inv_parser = subparsers.add_parser(
                            'inventory', 
                            help='create inventory of files and checksums',
                            aliases=['inv']
                            )
                            
    inv_parser.add_argument('-r', '--recursive',
                            help='recurse through subdirectories',
                            action='store_true'
                            )

    inv_parser.add_argument('-d', '--directory',
                            help='directory to inventory',
                            action='store'
                            )
    
    inv_parser.add_argument('-o', '--outfile',
                            help='path to output file'
                            )
    
    inv_parser.set_defaults(func=inventory)
    
    
    # parser for the compare sub-command
    comp_parser = subparsers.add_parser(
                            'compare', 
                            help='compare and verify inventories',
                            aliases=['comp']
                            )
                            
    comp_parser.add_argument(
                            'files', nargs='+',
                            help='two or more files to compare'
                            )
                            
    comp_parser.set_defaults(func=compare)


    # parse the args and call the default sub-command function
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()



