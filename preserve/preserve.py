#!/usr/bin/env python3
#-*- coding: utf-8 -*-

import argparse
import csv
from datetime import datetime as dt
import hashlib
import os
import re
import sys
import time


#============================================================================
# HELPER FUNCTIONS 
#============================================================================

def print_header(subcommand):
    '''Common header formatting for each subcommand.'''
    title = 'preserve.py {0}'.format(subcommand)
    bar = '=' * len(title)
    print('')
    print(title)
    print(bar)


def md5sum(filepath):
    '''For a given file path, return the md5 checksum for that file.'''
    # TODO: if a path to a directory is passed instead of a file path
    # gracefully handle the error.
    with open(filepath, 'rb') as f:
        m = hashlib.md5()
        while True:
            data = f.read(8192)
            if not data:
                break
            m.update(data)
        return m.hexdigest()


def list_files(dir_path):
    '''Return a list of files in a directory tree, pruning out the 
       hidden files & dirs (i.e. those that begin with dot).'''
    # TODO: When a file is specified instead of a directory, 
    # read the file contents instead if the file is not a text file, abort and
    # provide a useful error message
    result = []
    for root, dirs, files in os.walk(dir_path):
        # prune directories beginning with dot
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        # prune files beginning with dot
        files[:] = [f for f in files if not f.startswith('.')]
        result.extend([os.path.join(root, f) for f in files])
    return result


def read_file(file_path):
    '''Return list of dictionaries representing contents of an inventory 
        file.'''
    with open(file_path, 'r') as f:
        return [row for row in csv.DictReader(f)]


def get_metadata(file_path):
    '''Given a path to a file, return a dictionary representing the 
       metadata for that file.'''
    tstamp = int(os.path.getmtime(file_path))
    metadata = {'Directory': os.path.dirname(os.path.abspath(file_path)),
                'Filename': os.path.basename(file_path),
                'MTime': tstamp,
                'Moddate': dt.fromtimestamp(tstamp).strftime(
                    '%Y-%m-%dT%H:%M:%S'),
                'Extension': os.path.splitext(file_path)[1].lstrip('.').upper(),
                'Bytes': os.path.getsize(file_path),
                'MD5': md5sum(file_path)
                }
    return metadata


def get_inventory(path):
    '''Given a path to a file or directory, return list of inventory metadata
       based on reading the inventory, or scanning the directory's files.'''
    if os.path.isfile(path):
        print("  > {0} is a file.".format(path))
        return read_file(path)
    elif os.path.isdir(path):
        print("  > {0} is a directory.".format(path))
        return [get_metadata(f) for f in list_files(path)]
    else:
        print("  > {0} could not be found!".format(path))
        return False


#=== SUBCOMMAND =============================================================
#         NAME: compare
#  DESCRIPTION: check for the presence of files in inventories of various
#               formats (TSM backup, file analyzer, this script)
#============================================================================

def compare(args):

    print_header('compare')
    filelists = {}
    all_files = [args.first] + args.other 
    
    for filepath in all_files:
        result = []
        with open(filepath, 'r') as f:
            rawlines = [line.strip('\n') for line in f.readlines()]
            
            if rawlines[0] == "IBM Tivoli Storage Manager":
                print("Parsing Tivoli output file...")
                p = re.compile(r"([^\\]+) \[Sent\]")
                for line in rawlines:
                    if 'Normal File-->' in line:
                        m = p.search(line)
                        if m:
                            result.append(m.group(1))

            elif "Key" in rawlines[0] or "Filename" in rawlines[0]:
                print("Parsing DPI inventory file... ", end='')
                if '\t' in rawlines[0]:
                    print('tab delimited:')
                    delimiter = '\t'
                else:
                    print('comma delimited:')
                    delimiter = ','
                reader = csv.DictReader(rawlines, delimiter=delimiter)
                filenamecol = "Key" if "Key" in rawlines[0] else "Filename"
                for l in reader:
                    result.append(l[filenamecol])
            
            else:
                print("Unrecognized file type ...")
            
            if result:
                filelists[filepath] = result
                print(" => {0}: {1} files".format(filepath, len(result)))
            else:
                print(" => File {0} has not been parsed.".format(filepath))
    
    all_lists = [set(filelists[filelist]) for filelist in filelists]
    common = set.intersection(*all_lists)
    print("{} values are common to all the supplied files:".format(len(common)))

    for n, filelist in enumerate(filelists):
        unique = set(filelists[filelist]).difference(common)
        print(" => File {0}: {1} values are unique to {2}".format(
                n+1, len(unique), filelist)
            )
        if unique is not None:
            sorted_files = sorted(unique)
            for fnum, fname in enumerate(sorted_files):
                print("     ({0}) {1}".format(fnum+1, fname))
    print('')


#=== SUBCOMMAND =============================================================
#         NAME: bytecount
#  DESCRIPTION: count files by extention and sum their sizes
#============================================================================

def bytecount(args):
    
    # work for file as well as directory
    
    print_header('bytecount')
    all_files = list_files(args.path)
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
    
    if args.outfile is not None:
        OUTFILE = os.path.abspath(args.outfile)
    else:
        OUTFILE = None
    SEARCHROOT = os.path.abspath(args.path)
    FIELDNAMES = ['Directory', 'Filename', 'Extension', 'Bytes', 'MTime', 
                  'Moddate', 'MD5']
    
    # Get a list of all files in the search path.
    all_files = list_files(SEARCHROOT)
    total = len(all_files)
    count = 0
    files_to_check = all_files  # will be overriden if outfile specified
    files_done = []             # will be overriden if outfile specified
    existing_entries = []       # will be overriden if outfile specified

    # TODO: better handling of output file options:
    #   - output file specified?
    #       - YES: check for resume flag?
    #           - YES: check if outfile exists and can be read
    #               - YES: resume and write to file
    #               - NO: raise exception file cannot be read
    #           - NO: check if outfile exists
    #               - YES: raise exception
    #               - NO: write to outfile
    #       - NO: write to stdout
    
    if OUTFILE:
        print_header('inventory')
        print("Checking path: {0}".format(SEARCHROOT))
        print("Writing to file: {0}".format(OUTFILE))
        # check whether output file exists; if so, read it and resume the job.
        if os.path.isfile(OUTFILE):
            # TODO: add exceptions to handle outfile that is malformed
            existing_entries = read_inventory_file(OUTFILE)
            files_done = [os.path.join(f['Directory'], f['Filename']) \
                for f in existing_entries]
            # TODO: add exceptions for presence of files in inventory that
            # are no longer on disk
            files_to_check = set(all_files).difference(files_done)
            # TODO: add handling for output file that is already complete
        else:   
            # If the output file doesn't exist, use defaults.
            print("Inaccessible output file, inventorying everything...")
        fh = open(OUTFILE, 'w+')
    else:
        # if no output file has been specified, write to stdout
        fh = sys.stdout
    

    writer = csv.DictWriter(fh, fieldnames=FIELDNAMES)
    writer.writeheader()
    # Write the existing portion of the inventory to the output file
    if OUTFILE:
        for entry in existing_entries:
            writer.writerow(entry)
            count += 1

    # check each (remaining) file and generate metadata
    for f in files_to_check:
        metadata = get_metadata(f)
        writer.writerow(metadata)
        count += 1
            
        if OUTFILE:
            # display running counter
            print("Files checked: {0}/{1}".format(count, total), end='\r')

    if OUTFILE:
        fh.close()
        # clear counter
        print('')
        # report successful completion
        print('Inventory complete!')
        print('')


#=== SUBCOMMAND =============================================================
#         NAME: verify
#  DESCRIPTION: verify two sets of files (on disk or as recorded in CSV file) 
#               by comparing their checksums, size, timestamp
#============================================================================

def verify(args):
    print_header('verify')
    
    print("1. Loading data from 1st path...")
    dict_a = {f['Filename']: f['MD5'] for f in get_inventory(args.first)}
    print("2. Loading data from 2nd path...")
    dict_b = {f['Filename']: f['MD5'] for f in get_inventory(args.second)}
    all_keys = set().union(dict_a.keys(), dict_b.keys())
    not_a = []
    not_b = []
    changed = {}
    verified = 0
    total = len(all_keys)
    
    # iterate over union of both dicts
    for n,k in enumerate(all_keys):
        if not k in dict_a:
            not_a.append(k)
        elif not k in dict_b:
            not_b.append(k)
        elif not dict_a[k] == dict_b[k]:
            changed[k] = (dict_a[k], dict_b[k])
        else:
            verified += 1
        print("Checked {0}/{1} files.".format(n+1, total), end='\r')

    # clear counter
    print('')
    
    # report results
    if all([not_a is None, not_b is None, changed is None]):
        print("Success! No differences found.")
    else:
        print("Possible problems were found.")
    print("{0} files are in 1 but not 2.".format(len(not_b)))
    print("{0} files are in 2 but not 1.".format(len(not_a)))
    print("{0} files show a checksum mismatch.".format(len(changed)))
    print("Verified {0}/{1} files.".format(verified, total))

    print('')


#============================================================================
# MAIN LOOP
#============================================================================
'''Parse args and set the chosen sub-command as the default function.'''

def main():

    # main parser for command line arguments
    parser = argparse.ArgumentParser(
                            description='Digital preservation utilities.'
                            )
                            
    subparsers = parser.add_subparsers(
                            title='subcommands', 
                            description='valid subcommands', 
                            help='-h additional help', 
                            metavar='{bc,inv,comp,ver}',
                            dest='cmd'
                            )
                            
    subparsers.required = True
    
    # parser for the "bytecount" sub-command
    bc_parser = subparsers.add_parser(
                            'bytecount', aliases=['bc'], 
                            help='Count files and sizes in bytes',
                            description='Count files by type and sum bytes.'
                            )
                            
    bc_parser.add_argument( 'path',
                            help='path to search',
                            action='store'
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
                            action='store'
                            )
    
    inv_parser.add_argument('-o', '--outfile',
                            help='path to an output file',
                            action='store'
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
                            help='one or more files to compare'
                            )
                            
    comp_parser.set_defaults(func=compare)


    # parser for the "verify" sub-command
    comp_parser = subparsers.add_parser(
                            'verify', aliases=['ver'],
                            help='Verify checksums for two sets of files',
                            description='Verify checksums.'
                            )
                            
    comp_parser.add_argument('first', 
                            help='first file or path'
                            )
                            
    comp_parser.add_argument('second', 
                            help='second file or path'
                            )
                            
    comp_parser.set_defaults(func=verify)


    # parse the args and call the default sub-command function
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()



