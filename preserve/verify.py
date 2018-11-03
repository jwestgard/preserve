import os
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

    print(" => Verifying by filenames...")
    a_filenames = [asset.filename for asset in A]
    b_filenames = [asset.filename for asset in B]
    not_a_filenames = [f for f in a_filenames if f not in b_filenames]
    not_b_filenames = [f for f in b_filenames if f not in a_filenames]

    print(" => Verifying by relative paths...")
    a_relpaths = [os.path.relpath(asset.path, A.root) for asset in A]
    b_relpaths = [os.path.relpath(asset.path, B.root) for asset in B]
    not_a_relpaths = [path for path in a_relpaths if path not in b_relpaths]
    not_b_relpaths = [path for path in b_relpaths if path not in a_relpaths]

    print(" => Verifying by md5 and length...")
    a_hashes = set([(asset.md5, asset.bytes) for asset in A])
    b_hashes = set([(asset.md5, asset.bytes) for asset in B])
    not_a_hashes = a_hashes.difference(b_hashes)
    not_b_hashes = b_hashes.difference(a_hashes)

    # Report success or failure of verification
    all_diffs = [not_a_filenames, not_b_filenames, not_a_relpaths, 
                 not_b_relpaths, not_a_hashes, not_b_hashes]

    if not any(all_diffs):
        print("\nRESULT: Success! No differences found.")
    else:
        print("\nRESULT: Possible problems were found.")
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
        if not_a_hashes or not_b_hashes:
            print(f" => {len(not_a_hashes)} hashes in #1 are not in #2")
            for n, diff in enumerate(not_a_hashes, 1):
                filename = [a.filename for a in A if (a.md5, a.bytes) == diff]
                print(f"     ({n}) {diff}: {filename}")
            print(f" => {len(not_b_hashes)} hashes in #2 are not in #1")
            for n, diff in enumerate(not_b_hashes, 1):
                filename = [a.filename for a in B if (a.md5, a.bytes) == diff]
                print(f"     ({n}) {diff}: {filename}")
print()
