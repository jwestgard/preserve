import csv
import os
import sys

from .manifest import Manifest
from .asset import Asset

ALGS = ['md5', 'sha1', 'sha256']
FIELDNAMES = ['BATCH', 'PATH', 'DIRECTORY', 'RELPATH', 'FILENAME', 'EXTENSION', 
              'BYTES', 'MTIME', 'MODDATE', 'MD5', 'SHA1', 'SHA256']


def read_csv(filepath):
    '''Read asset data from CSV file'''
    with open(filepath) as handle:
        reader = csv.DictReader(handle)
        return [row for row in reader]


def scan_filesystem(root):
    '''Create lookup of filepaths by filname in asset directory'''
    result = {}
    for currentdir, subdirs, files in os.walk(root):
        for file in files:
            result.setdefault(file, []).append(os.path.join(currentdir, file))
    return result


def annotate(args):
    '''Read CSV and scan filesystem to fill in blanks in the data'''

    sys.stderr.write(f" => CSV to annotate: {args.inventory}\n")
    sys.stderr.write(f" => Root to search:  {args.root}\n")
    sys.stderr.write(f" => File to write:  {args.output}\n\n")

    spreadsheet = read_csv(args.inventory)
    file_index = scan_filesystem(args.root)

    for row in spreadsheet:
        filename = row['FILENAME']
        if row['PATH'] is '':
            sys.stderr.write(f"Searching for a local path to {filename} ... ")
            if filename in file_index:
                for path in file_index[filename]:
                    a = Asset().from_filesystem(path, args.root, *ALGS)
                    if a.md5 == row['MD5']:
                        sys.stderr.write("Match!\n")
                        sys.stderr.write(f" => {a.md5} == {row['MD5']}\n")
                        row['PATH'] = path
                        break
                    else:
                        sys.stderr.write("No match!\n")
                        sys.stderr.write(f" => {a.md5} != {row['MD5']}\n")

    with open(args.output, 'w') as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES)
        writer.writeheader()
        for row in spreadsheet:
            writer.writerow(row)