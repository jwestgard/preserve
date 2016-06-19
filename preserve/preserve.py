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
def print_header(subcommand):
    '''Common output formatting.'''
    title = 'preserve.py {0}'.format(subcommand)
    bar = '=' * len(title)
    print('')
    print(title)
    print(bar)


def md5sum(filepath):
    '''For a given file path, return the md5 checksum for that file.'''
    with open(filepath, 'rb') as f:
        m = hashlib.md5()
        while True:
            data = f.read(8192)
            if not data:
                break
            m.update(data)
        return m.hexdigest()


def survey_files(path):
    '''Return a list of files in a directory tree, 
       pruning out the hidden files (i.e. those that begin with dot).'''
    result = []
    for root, dirs, files in os.walk(path):
        # prune directories beginning with dot
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        # prune files beginning with dot
        files[:] = [f for f in files if not f.startswith('.')]
        result.extend([os.path.join(root, f) for f in files])
    return result


def resume_job(path):
    '''Given a path to a directory listing file, return a dictionary of 
       the file metadata read from that file, where the keys are the file paths 
       and the values are the metadata as a dictionary.'''
    with open(path, 'r') as f:
        reader = csv.DictReader(f)
        result = {}
        for row in reader:
            filepath = os.path.join(row['Directory'], row['Filename'])
            result[filepath] = row
    return result


#=== SUBCOMMAND =============================================================
#         NAME: compare
#  DESCRIPTION: 
#============================================================================

def compare(args):

    print_header('file checker')
    filelists = {}
    all_files = [args.first] + args.other 
    
    for filepath in all_files:
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
        print(" • File {0}: {1} values are unique to {2}".format(
                                                    n+1, len(unique), filelist)
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
    
    print_header('bytecount')
    all_files = survey_files(args.path)
    extensions = {}
    totalbytes = 0
    
    for f in all_files:
        totalbytes += os.path.getsize(f)
        ext = os.path.splitext(f)[1].lstrip('.').upper()
        if ext in extensions:
            extensions[ext] += 1
        else:
            extensions[ext] = 1
            
    exts_summary = [
        "{0}:{1}".format(type, num) for (type, num) in extensions.items()
        ]
        
    print('{0} bytes for {1} files.'.format(totalbytes, len(all_files)))
    print('({0})'.format(", ".join(exts_summary)))
    print('')


#=== SUBCOMMAND =============================================================
#         NAME: inventory
#  DESCRIPTION: generate a file listing with checksums, size, timestamp
#============================================================================

def inventory(args):
    
    print_header('inventory')
    
    if args.outfile is not None:
        OUTFILE = os.path.abspath(args.outfile)
    else:
        OUTFILE = None
    
    SEARCHROOT = os.path.abspath(args.path)
    FIELDNAMES = [  'Directory', 
                    'Filename', 
                    'Extension', 
                    'Bytes', 
                    'MTime', 
                    'Moddate',
                    'MD5'
                    ]

    all_files = survey_files(SEARCHROOT)
    print("Checking path: {0}".format(SEARCHROOT))
    
    if OUTFILE:
        print("Writing inventory to file {0}".format(OUTFILE))

        # check whether output file exists, and if so read it and resume job
        try:
            complete_list = resume_job(OUTFILE)
            already_done = [item for item in complete_list]
            files_to_check = set(all_files).difference(already_done)
        
        except FileNotFoundError:
            complete_list = []
            files_to_check = all_files
            
        fh = open(OUTFILE, 'w+')

    else:
        print("Writing inventory to stdout")
        complete_list = []
        files_to_check = all_files
        fh = sys.stdout
    
    writer = csv.DictWriter(fh, fieldnames=FIELDNAMES)
    writer.writeheader()
    count = 0
    total = len(all_files)
        
    # write out already completed items
    for item in complete_list:
        writer.writerow(complete_list[item])
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

    if fh is not sys.stdout:
        fh.close()
    
    # clear counter
    print('')
    
    # report successful completion
    print('Inventory complete!')
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
    
    
    # parser for the "bytecount" sub-command
    bc_parser = subparsers.add_parser(
                            'bytecount', aliases=['bc'], 
                            help='Count files and sizes in bytes',
                            description='Count files by type and sum bytes.'
                            )
                            
    bc_parser.add_argument( 'path',
                            help='path to search',
                            action='store',
                            )
    
    bc_parser.add_argument( '-r', '--recursive', 
                            help='Recurse through subdirectories',
                            action='store_true'
                            )
                            
    bc_parser.set_defaults(func=bytecount)
    
    
    # parser for the "inventory" sub-command
    inv_parser = subparsers.add_parser(
                            'inventory', aliases=['inv'],
                            help='Create inventory of files with checksums',
                            description='Create dirlisting with file metadata.'
                            )
                            
    inv_parser.add_argument('path',
                            help='path to search',
                            action='store',
                            )
    
    inv_parser.add_argument('-o', '--outfile',
                            help='path to an output file (otherwise stdout)',
                            action='store',
                            )

    inv_parser.add_argument('-r', '--recursive',
                            help='recurse through subdirectories',
                            action='store_true'
                            )
    
    inv_parser.set_defaults(func=inventory)
    
    
    # parser for the "compare" sub-command
    comp_parser = subparsers.add_parser(
                            'compare', aliases=['comp'],
                            help='Compare two or more inventories',
                            description='Compare contents of file inventories.'
                            )
                            
    comp_parser.add_argument('first', 
                            help='first file'
                            )
                            
    comp_parser.add_argument('other', nargs='+',
                            help='one or more files to compare',
                            )
                            
    comp_parser.set_defaults(func=compare)


    # parse the args and call the default sub-command function
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()



