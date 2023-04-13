from .manifest import Manifest

# === SUBCOMMAND =============================================================
#         NAME: verify
#  DESCRIPTION: Verify two sets of files (on disk or as recorded in CSV file)
#               by comparing number of files, relative paths, and a file
#               signature consisting of checksum + byte length. Attempt to
#               reason about the nature of the differences and print a report
#               about them to the console.
# ============================================================================


def verify(args):
    '''Verify the identity of two inventories (either stored or created on
       the fly), by checking for the presence of all files and comparing the
       checksums of each one.'''

    # Create dictionary from each manifest with key = path and val = signature
    print(f"A. Loading data from {args.first}...")
    A = {asset.relpath: asset for asset in Manifest(args.first)}
    a_paths = set(A.keys())
    a_unique = set([(asset.md5, asset.bytes) for asset in A.values()])
    print(f"   - A has {len(A)} assets, {len(a_unique)} of which are unique")

    print(f"B. Loading data from {args.second}...")
    B = {asset.relpath: asset for asset in Manifest(args.second)}
    b_paths = set(B.keys())
    b_unique = set([(asset.md5, asset.bytes) for asset in B.values()])
    print(f"   - B has {len(B)} assets, {len(b_unique)} of which are unique")

    # Sort all asset paths into their respective sets
    relpaths_both = a_paths.intersection(b_paths)
    relpaths_only_a = a_paths.difference(b_paths)
    relpaths_only_b = b_paths.difference(a_paths)

    # Check identity of paths present in both manifests
    unchanged = {p for p in relpaths_both if A[p] == B[p]}
    modified = {p for p in relpaths_both if A[p] != B[p]}

    # Examine asset paths present in one or the other, but not both, manifests
    moved = {}
    added = []
    deleted = []
    differences = []

    for p in relpaths_only_a:
        signature = (A[p].md5, A[p].bytes)
        if signature not in b_unique:
            deleted.append(p)
        else:
            moved.setdefault(signature, []).append(p)

    for p in relpaths_only_b:
        signature = (B[p].md5, B[p].bytes)
        if signature not in a_unique:
            added.append(p)
        else:
            moved.setdefault(signature, []).append(p)

    # create a summary of all possible issues
    if modified:
        differences.append(("asset(s) changed in place", modified))
    if added:
        differences.append(("asset(s) added to B", added))
    if deleted:
        differences.append(("asset(s) removed from A", deleted))
    if moved:
        differences.append(("asset(s) moved but unchanged", moved))

    # Report results, sorting assets by nature of detected difference
    if unchanged == relpaths_both and not any(differences):
        print("=> SUCCESS! No differences found.")
    else:
        print("=> Check complete! But possible problems were found.")
        for diff in differences:
            print(f"=> {len(diff[1])} {diff[0]}:")
            for n, asset in enumerate(sorted(diff[1]), 1):
                print(f"   ({n}) {asset}")
                if type(diff[1]) == dict:
                    print(f"       {' --> '.join(diff[1][asset])}")
