#!/usr/bin/env python3
import argparse
import csv
import logging
import os
import shutil
import sys
from pathlib import Path

from preserve.utils import file_size, header

from .classes import FileSet
from .exceptions import ConfigError, DuplicateFileError

logging.basicConfig(format='%(message)s',
                    level="INFO")

PARTITIONING_PATTERN = r"^([a-z]+?)-(\d+?)[-_][^.]+?\.\S+?$"

CSV_FIELDS = ['relpath_old', 'relpath_new']


def parse_args():
    ''' Parse command line arguments '''

    parser = argparse.ArgumentParser(
        description='Partition a tree of files based on various schemes'
        )

    parser.add_argument(
        'source',
        help='Root directory to be partitioned',
        action='store'
        )

    parser.add_argument(
        'destination',
        help='Output directory (if exists, must be empty)',
        action='store'
        )

    parser.add_argument(
        '-m', '--mode',
        choices=['copy', 'move', 'dryrun'],
        help='Dryrun, move, or copy files to destination',
        action='store',
        default='dryrun'
        )

    parser.add_argument(
        '-o', '--output',
        default=None,
        action='store',
        help='Path to csv file',
        )

    parser.add_argument(
        '-v', '--version',
        action='version',
        help='Print version number and exit',
        version='%(prog)s 0.1'
        )

    return parser.parse_args()


def check_args(args):
    ''' Validate the provided arguments '''

    if not os.path.isdir(args.source):
        raise ConfigError("Source directory not found")

    if os.path.isdir(args.destination) and len(os.listdir(args.destination)) > 0:
        raise ConfigError("Destination directory is not empty")


def has_duplicates(mapping):
    all_dest = dict()
    for source, destination in mapping.items():
        all_dest.setdefault(destination, []).append(source)
    duplicates = [tuple(all_dest[d]) for d in all_dest if len(all_dest[d]) > 1]
    if duplicates:
        return duplicates
    else:
        return False


def write_relpaths(relpaths=None, file=sys.stdout):
    if relpaths is None:
        relpaths = []

    csv_writer = csv.writer(file)
    csv_writer.writerow(CSV_FIELDS)

    for row in relpaths:
        csv_writer.writerow(row)


def main():

    try:
        logging.info(header("Partition Tool"))

        """ (1) Parse args """
        args = parse_args()

        """ (2) Validate the provided arguments """
        check_args(args)
        logging.info(f"Running with the following arguments:")
        width = max([len(k) for k in args.__dict__])
        for k in args.__dict__:
            logging.info(f"  {k:>{width}} : {getattr(args, k)}")

        """ (3) Create FileSet """
        fileset = FileSet.from_filesystem(args.source)
        logging.info(f"\nAnalyzing files: {len(fileset)} files, " +
                     file_size(fileset.bytes))

        """ (4) Create partition map """
        logging.info(f"Creating mapping to partitioned tree...")
        mapping = fileset.partition_by(PARTITIONING_PATTERN, args.destination)

        """ (5) Check for duplicate files """
        duplicates = has_duplicates(mapping)
        if duplicates:
            raise DuplicateFileError(f"Duplicate filenames detected: {duplicates}")
        else:
            logging.info("Destination paths are all confirmed to be unique...")

        """ (5) Move, copy, or print """
        relpaths = []
        logging.info(f"Partitioning files ({args.mode} mode)...")
        for n, (source, destination) in enumerate(mapping.items(), 1):
            logging.info(f"  {n}. {source} -> {destination}")
            if args.mode == 'dryrun':
                continue
            else:
                os.makedirs(os.path.dirname(destination), exist_ok=True)
                if args.mode == 'copy':
                    shutil.copyfile(source, destination)
                elif args.mode == 'move':
                    shutil.move(source, destination)
            relpaths.append((source, destination))
        
        logging.info("Partitioning complete.\n")

        """ (6) Record results """
        if args.output is not None:
            with open(args.output, 'w') as csv_file:
                write_relpaths(relpaths=relpaths, file=csv_file)
        else:
            write_relpaths(relpaths=relpaths)

    except Exception as err:
        logging.error(f"{err}")
        sys.exit(1)


if __name__ == "__main__":
    main()
