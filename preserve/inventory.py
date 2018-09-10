import csv
import os
import sys
from .asset import Asset
from .functions import get_inventory
from .functions import list_files


#=== SUBCOMMAND =============================================================
#         NAME: inventory
#  DESCRIPTION: Generates a file listing with checksum, file size, timestamp
#============================================================================

def inventory(args):
    '''Create a CSV inventory of file metadata for files in 
       a specified path.'''  
    if args.outfile:
        OUTFILE = os.path.abspath(args.outfile)
        if os.path.isfile(OUTFILE):
            print("ERROR: The output file exists.",
                  "Use the -e flag to resume the job.\n")
            sys.exit()
        elif os.path.isdir(OUTFILE):
            print("ERROR: The specified output path is a directory.\n")
            sys.exit()
    elif args.existing:
        OUTFILE = os.path.abspath(args.existing)
        if not os.path.isfile(OUTFILE):
            print("ERROR: Must specify the path to an existing",
                  "inventory file.\n")
            sys.exit()
    else:
        OUTFILE = None

    if os.path.exists(args.path):
        PATH = os.path.abspath(args.path)
    else:
        print("ERROR: The specified search path does not exist.\n")
        sys.exit()

    FIELDNAMES = ['PATH', 'DIRECTORY', 'FILENAME', 
                  'EXTENSION', 'BYTES', 'MTIME', 
                  'MODDATE', 'MD5', 'SHA1', 'SHA256'
                  ]

    # Get a list of all files in the search path.
    all_files = list_files(PATH)
    total = len(all_files)
    files_to_check = all_files  # overriden if outfile specified
    existing_entries = []       # overriden if outfile specified
    count = 0

    if OUTFILE:
        print("Checking path: {0}".format(PATH))
        print("Writing to file: {0}".format(OUTFILE))

        # If the output file exists, read it and resume the job.
        if os.path.isfile(OUTFILE):
            existing_entries = get_inventory(OUTFILE)
            all_keys = set().union(
                *(e.__dict__.keys() for e in existing_entries)
                )

            # if the CSV file conforms to the pattern
            if all_keys.issubset([fname.lower() for fname in FIELDNAMES]):
                files_done = [os.path.join(
                                f.directory, f.filename
                                ) for f in existing_entries]

                # Handle various problem cases
                if files_done == files_to_check:
                    print("Inventory is already complete.\n")
                    sys.exit()
                elif set(files_done).difference(files_to_check):
                    print("ERROR: Existing file contains references",
                          "to files that are not found in the path",
                          "being inventoried.\n")
                    sys.exit()

                files_to_check = set(all_files).difference(files_done)

            # Handle non-conforming CSV file
            else:
                print("ERROR: The specified output file is not a correctly",
                      "formatted inventory CSV.\n")
                sys.exit()

        buffer = 1
        fh = open(OUTFILE, 'w+', buffer)

    # If no output file has been specified, write to stdout
    else:
        fh = sys.stdout

    writer = csv.DictWriter(fh, fieldnames=FIELDNAMES)
    writer.writeheader()
    # Write the existing portion of the inventory to the output file
    if OUTFILE:
        for entry in existing_entries:
            writer.writerow({k.upper():v for (k,v) in entry.__dict__.items()})
            count += 1

    # check each (remaining) file and generate metadata
    for f in files_to_check:
        a = Asset().from_filesystem(f)
        writer.writerow({k.upper(): v for k, v in a.__dict__.items()})
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

