#!/usr/bin/env python3

import argparse
import csv
import json
import os
import sys

import bagit

from preserve import version
from preserve.utils import header


def parse_args():
    ''' Parse command line arguments '''

    parser = argparse.ArgumentParser(
        description='Create APTrust-compatible BagIt bags'
        )

    parser.add_argument(
        'path',
        help='Root directory to be bagged',
        action='store'
        )

    parser.add_argument(
        '-c', '--config',
        help='Path to a config file containing tag info',
        action='store',
        required=True
        )

    parser.add_argument(
        '-b', '--batch',
        help='Batch identifier',
        action='store',
        required=True
        )

    parser.add_argument(
        '-e', '--exclude',
        help='Exclude hidden files and directories from the bag',
        action='store_true'
        )

    parser.add_argument(
        '-v', '--version',
        action='version',
        help='Print version number and exit',
        version=version
        )

    return parser.parse_args()


def main():

    try:
        sys.stderr.write(header("Bagging Tool"))

        """ (1) Parse args """
        args = parse_args()
        sys.stderr.write(f"Running with the following arguments:\n")
        width = max([len(k) for k in args.__dict__])
        for k in args.__dict__:
            sys.stderr.write(f"  {k:>{width}} : {getattr(args, k)}\n")
        sys.stderr.write('\n')

        if args.exclude:
            for dir, subdirs, files in os.walk(args.path):
                for f in files:
                    if f.startswith('.'):
                        os.remove(os.path.join(dir, f))

        """ (2) Read configuration """
        with open(args.config) as handle:
            sys.stderr.write("Reading tags from config file...\n")
            reader = csv.DictReader(handle)
            for row in reader:
                if row['Internal-Sender-Description'] == args.batch:
                    tags = row

        """ (3) Create bag """
        sys.stderr.write("Analyzing files in bag...\n")
        bag = bagit.make_bag(args.path, checksums=['md5', 'sha256'])
        for key in ['Internal-Sender-Identifier',
                    'Internal-Sender-Description',
                    'Source-Organization'
                    ]:
            bag.info[key] = tags[key]

        sys.stderr.write("Generating aptrust-info.txt...\n")
        apt_tagfile_path = os.path.join(args.path, 'aptrust-info.txt')
        with open(apt_tagfile_path, 'w') as handle:
            for key in ['Access', 'Description', 'Storage-Option', 'Title']:
                handle.write(f"{key}: {tags[key]}\n")

        bag.save()

        """ (4) Summarize results """
        sys.stderr.write("Bagging complete.\n")

    except Exception as err:
        sys.stderr.write(f"ERROR: {err}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
