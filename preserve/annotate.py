import csv
import os
import sys

from .asset import Asset
from .manifest import Manifest

ALGS = ['md5', 'sha1', 'sha256']

FIELDNAMES = ['BATCH', 'PATH', 'DIRECTORY', 'RELPATH', 'FILENAME', 'EXTENSION',
              'BYTES', 'MTIME', 'MODDATE', 'MD5', 'SHA1', 'SHA256', 'storageprovider',
              'storagepath']


def read_csv(filepath):
    '''Read asset data from CSV file'''
    result = []
    with open(filepath) as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            row.setdefault('storagepath', '')
            row.setdefault('storageprovider', '')
            result.append(row)
    return result


def scan_filesystem(root):
    '''Create lookup of filepaths by filname in asset directory'''
    result = {}
    for currentdir, subdirs, files in os.walk(root):
        for file in files:
            result.setdefault(file, []).append(os.path.join(currentdir, file))
    return result


def examine_matching_file(filename, root, row, file_index):
    '''Locate file match in the index and annotate the spreadsheet row'''
    updated = row
    for path in file_index.get(filename, []):
        asset = Asset().from_filesystem(path, root, *ALGS)
        for algorithm in ALGS:
            storedhash = row[algorithm.upper()]
            calculated = getattr(asset, algorithm)
            if storedhash == '':
                updated[algorithm.upper()] = calculated
            elif calculated != storedhash:
                break
            else:
                sys.stderr.write(f" => {storedhash} == {calculated}\n")
                continue
        sys.stderr.write(" => Match!\n")
        updated['PATH'] = path
        return updated
    sys.stderr.write("No match!\n")
    return row


def annotate(args):
    '''Read CSV and scan filesystem to fill in blanks in the data'''
    sys.stderr.write(f"Running with the following arguments:\n")
    sys.stderr.write(f" - CSV to annotate:     {args.inventory}\n")
    sys.stderr.write(f" - Directory to search: {args.root}\n")
    sys.stderr.write(f" - Write results to:    {args.output}\n\n")

    spreadsheet = read_csv(args.inventory)
    sys.stderr.write(f"Read {len(spreadsheet)} lines from CSV\n")

    file_index = scan_filesystem(args.root)
    sys.stderr.write(f"Created index of {len(file_index)} filenames\n")

    handle = open(args.output, 'w', 1)
    writer = csv.DictWriter(handle, fieldnames=FIELDNAMES, extrasaction='ignore')
    writer.writeheader()

    for n, row in enumerate(spreadsheet, 1):
        filename = row['FILENAME']
        if row['PATH'] != '' or row['storagepath'] != '':
            sys.stderr.write(f"{n}. Skipping completed row for {filename}\n")
            # writer.writerow(row)
        else:
            sys.stderr.write(f"{n}. Searching for a local path to {filename} ...\n")
            annotated = examine_matching_file(filename, args.root, row, file_index)
            writer.writerow(annotated)

    handle.close()
