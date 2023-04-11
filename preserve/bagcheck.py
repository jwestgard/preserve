import os
import tarfile

from .manifest import Manifest


def inspect(bag: str) -> set:
    '''
    Checks the given bag. If the bag is a directory, it
    will open the bag and then open the manifest file.
    Otherwise it will treat the bag as a tar or tar.gz file and open
    the manifest file in the archive.
    '''
    if os.path.isdir(bag):
        with open(os.path.join(bag, 'manifest-md5.txt')) as bag_manifest:
            return {tuple(line.strip().split(None, 1)) for line in bag_manifest}

    else:
        directory_name = bag.split('/')[-1].split('.')[0]
        tar = tarfile.open(bag, 'r') if bag.endswith('.tar') else tarfile.open(bag, 'r:gz')

        with tar.extractfile(f'{directory_name}/manifest-md5.txt') as bag_manifest:
            return {tuple(line.strip().split(None, 1)) for line in bag_manifest}


def bagcheck(args):
    '''
    Check inventory contents against relpaths & checksums of a bag manifest.
    '''

    # create sets represnting the two asset manifests
    print(f"Reading asset inventory at {args.inventory}...")
    inventory = Manifest(args.inventory)
    print(f" => {len(inventory)} assets in batch.")

    print(f"Inspecting BagIt bag at {args.bag}...")
    bag = inspect(args.bag)
    print(f" => {len(bag)} items in bag manifest.")

    print(f"Confirming all inventory files are present in bag...")
    assets_to_check = {(a.sha256, os.path.join('data', a.relpath)) for a in inventory}

    # find differences between the two sets
    missing = sorted(assets_to_check - bag)
    extra = sorted(bag - assets_to_check)

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
