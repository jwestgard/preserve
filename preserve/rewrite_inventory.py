#!/usr/bin/env python3

import sys
import os

def inventory(file1, file2):
    
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
    all_files = list_files(SEARCHROOT)
    print("Checking path: {0}".format(SEARCHROOT))
    
    if OUTFILE:
        print("Writing inventory to file {0}".format(OUTFILE))
        # check whether output file exists, and if so read it and resume job
        try:
            complete_list = read_inventory(OUTFILE)
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
        metadata = get_metadata(f)
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

inventory(sys.argv[1], sys.argv[2])
