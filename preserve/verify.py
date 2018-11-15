import os
import re
from .utils import get_inventory
from .manifest import Manifest

#=== SUBCOMMAND =============================================================
#         NAME: verify
#  DESCRIPTION: verify two sets of files (on disk or as recorded in CSV file) 
#               by comparing filenames, relative paths, and checksums
#============================================================================

def verify(args):
    '''Verify the identity of two inventories (either stored or created on 
       the fly), by checking for the presence of all files and comparing the 
       checksums of each one.'''
    print(f"1. Loading data from {args.first}...")
    A = Manifest(args.first)
    print(f"2. Loading data from {args.second}...")
    B = Manifest(args.second)

    all_diffs = []
    
    # compare by specified criteria, default to checksum/bytes verification
    if not any([args.filenames, args.relpaths, args.checksums]):
        args.checksums = True
        print(" => No verification criteria specified...")
        print(" => Defaulting to checksum verification...")

    if args.filenames:
        print(" => Verifying by filenames...")
        a_filenames = [asset.filename for asset in A]
        b_filenames = [asset.filename for asset in B]
        not_a_filenames = [f for f in a_filenames if f not in b_filenames]
        not_b_filenames = [f for f in b_filenames if f not in a_filenames]
        all_diffs.extend([not_a_filenames, not_b_filenames])

    if args.relpaths:
        print(" => Verifying by relative paths...")
        a_relpaths = [re.sub(A.root, '', asset.path) for asset in A]
        b_relpaths = [re.sub(B.root, '', asset.path) for asset in B]
        not_a_relpaths = [path for path in a_relpaths if path not in b_relpaths]
        not_b_relpaths = [path for path in b_relpaths if path not in a_relpaths]
        all_diffs.extend([not_a_relpaths, not_b_relpaths])

    if args.checksums:
        print(" => Verifying by md5 and length...")
        a_checksums = set([(asset.md5, asset.bytes) for asset in A])
        b_checksums = set([(asset.md5, asset.bytes) for asset in B])
        not_a_checksums = a_checksums.difference(b_checksums)
        not_b_checksums = b_checksums.difference(a_checksums)
        all_diffs.extend([not_a_checksums, not_b_checksums])

    # Report success or failure of verification criteria
    if not any(all_diffs):
        print("RESULT: Success! No differences found.")
    else:
        print("RESULT: Possible problems were found.")
        if not_a_filenames or not_b_filenames:
            print(f" => {len(not_a_filenames)} filenames in #1 are not in #2")
            for n, diff in enumerate(not_a_filenames, 1):
                print(f"     ({n}) {diff}")
            print(f" => {len(not_b_filenames)} filenames in #2 are not in #1")
            for n, diff in enumerate(not_b_filenames, 1):
                print(f"     ({n}) {diff}")
        if not_a_relpaths or not_b_relpaths:
            print(f" => {len(not_a_relpaths)} paths in #1 are not in #2")
            for n, diff in enumerate(not_a_relpaths, 1):
                print(f"     ({n}) {diff}")
            print(f" => {len(not_b_relpaths)} paths in #2 are not in #1")
            for n, diff in enumerate(not_b_relpaths, 1):
                print(f"     ({n}) {diff}")
        if not_a_checksums or not_b_checksums:
            print(f" => {len(not_a_checksums)} checksums in #1 are not in #2")
            for n, diff in enumerate(not_a_checksums, 1):
                filename = [a.filename for a in A if (a.md5, a.bytes) == diff]
                print(f"     ({n}) {diff}: {filename}")
            print(f" => {len(not_b_checksums)} checksums in #2 are not in #1")
            for n, diff in enumerate(not_b_checksums, 1):
                filename = [a.filename for a in B if (a.md5, a.bytes) == diff]
                print(f"     ({n}) {diff}: {filename}")
print()
