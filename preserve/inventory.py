import csv
import os
import sys
from .asset import Asset
from .utils import get_inventory
from .utils import list_files


# === SUBCOMMAND =============================================================
#         NAME: inventory
#  DESCRIPTION: Generates a file listing with checksum, file size, timestamp
# ============================================================================

def inventory(args):

    '''Create a CSV inventory of file metadata for files in
       a specified path.'''

    FIELDNAMES = ['BATCH', 'PATH', 'DIRECTORY', 'RELPATH', 'FILENAME',
                  'EXTENSION', 'BYTES', 'MTIME',
                  'MODDATE', 'MD5', 'SHA1', 'SHA256'
                  ]
    BATCH = args.batch

    # Handle errors in the user-supplied paths
    if args.outfile:
        OUTFILE = os.path.abspath(args.outfile)
        if os.path.isfile(OUTFILE):
            return (
                "ERROR: The output file exists. " +
                "Use the -e flag to resume the job.\n"
                )
        elif os.path.isdir(OUTFILE):
            return (
                "ERROR: The specified output path is a directory.\n"
                )
    elif args.existing:
        OUTFILE = os.path.abspath(args.existing)
        if not os.path.isfile(OUTFILE):
            return (
                "ERROR: Must specify the path " +
                "to an existing inventory file.\n"
                )
    else:
        OUTFILE = None

    # Ensure that the path to be checked is valid
    if os.path.exists(args.path):
        PATH = os.path.abspath(args.path)
    else:
        return (
            "ERROR: The specified search path does not exist.\n"
            )

    # Get a list of all files in the search path.
    all_files = list_files(PATH)
    total = len(all_files)
    files_to_check = all_files  # overriden if OUTFILE specified
    existing_entries = []       # overriden if OUTFILE specified
    count = 0
    sys.stderr.write("Checking path: {0}\n".format(PATH))
    if OUTFILE:
        sys.stderr.write("Writing to file: {0}\n".format(OUTFILE))
        # If the output file exists, read it and resume the job.
        if os.path.isfile(OUTFILE):
            existing_entries = get_inventory(OUTFILE)
            all_keys = set().union(
                *(e.__dict__.keys() for e in existing_entries)
                )
            # if the CSV file conforms to the pattern
            all_keys.discard('relpath')
            if all_keys.issubset([fname.lower() for fname in FIELDNAMES]):
                files_done = [
                    os.path.join(f.directory, f.filename) for f in existing_entries
                    ]
                # Handle a complete inventory ...
                if files_done == files_to_check:
                    return (
                        "Inventory is already complete.\n"
                        )
                # or an erroneous partial inventory
                elif set(files_done).difference(files_to_check):
                    return (
                        "ERROR: Existing file contains references " +
                        "to files that are not found in the path " +
                        "being inventoried.\n"
                        )
                # Create the set of remaining files to be checked
                files_to_check = set(all_files).difference(files_done)
            # Handle non-conforming CSV file
            else:
                return (
                    "ERROR: The specified output file is not a correctly " +
                    "formatted inventory CSV.\n"
                    )
        # open line-buffered file handle
        fh = open(OUTFILE, 'w+', 1)

    # If no output file has been specified, write to stdout
    else:
        sys.stderr.write("Piping inventory to stdout\n")
        fh = sys.stdout

    writer = csv.DictWriter(fh, fieldnames=FIELDNAMES)
    writer.writeheader()
    # Write the existing portion of the inventory to the output file
    if OUTFILE:
        for entry in existing_entries:
            write_entry(writer, BATCH, entry, FIELDNAMES)
            count += 1

    # Determine the set of hash algorithms to run
    known_algs = ['md5', 'sha1', 'sha256']
    if args.algorithms:
        algs_to_run = args.algorithms.split(',')
        if any([alg not in known_algs for alg in algs_to_run]):
            return (
                "ERROR: Unknown hash algorithm specified.\n\n"
                )
    else:
        algs_to_run = known_algs
    # Check each (remaining) file and generate metadata
    for f in files_to_check:
        a = Asset().from_filesystem(f, PATH, *algs_to_run)
        write_entry(writer, BATCH, a, FIELDNAMES)

        count += 1
        # Display a running counter
        sys.stderr.write(
            "\rFiles checked: {0}/{1}".format(count, total)
            )

    # Clear the counter, report results, and close file handle (it not stdout)
    sys.stderr.write('\nInventory complete!\n\n')
    if fh != sys.stdout:
        fh.close()


def write_entry(writer, batch, entry, fieldnames):
    '''
    Write out an entry to the file using the supplied writer
    '''
    # Ensure that the entry include the "batch" field
    entry.batch = batch
    writer.writerow({k.upper(): v for k, v in entry.__dict__.items() if k.upper() in fieldnames})
