import os
from .manifest import Manifest


def bagcheck(args):
    ''' Check inventory contents against relpaths & checksums of a bag manifest.
    
    '''

    # create sets represnting the two asset manifests
    print(f"Reading asset inventory at {args.inventory}...")
    inventory = Manifest(args.inventory)
    print(f" => {len(inventory)} assets in batch.")

    print(f"Inspecting BagIt bag at {args.bag}...")
    with open(os.path.join(args.bag, 'manifest-sha256.txt')) as bag_manifest:
        bag = set([tuple(line.strip().split(None, 1)) for line in bag_manifest])
    print(f" => {len(bag)} items in bag manifest.")

    print(f"Confirming all inventory files are present in bag...")
    assets_to_check = set(
        [(a.sha256, os.path.join('data', a.relpath)) for a in inventory]
        )

    # find differences between the two sets
    missing = list(sorted(assets_to_check - bag))
    extra = list(sorted(bag - assets_to_check))

    # reports the results
    if missing:
        print(f" => {len(missing)} files not found in bag:")
        for n, file in enumerate(missing, 1):
            print(f"    {n}. {file}")
    else:
        print(f" => All files accounted for in bag!")

    if extra:
        print(f" => {len(extra)} extra files found in bag:")
        for n, file in enumerate(extra, 1):
            print(f"    {n}. {file}")
    else:
        print(f" => No extra files found in bag!")
