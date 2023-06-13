import os
from pathlib import Path
import tarfile

from .manifest import Manifest


def inspect(bag: str) -> set:
    """
    Checks the given bag. If the bag is a directory, it will open the bag and then open
    the manifest file. If the bag is as a tar or tar.gz file, it will open the manifest
    file in the archive. Otherwise, raises a RuntimeError.
    """
    if os.path.isdir(bag):
        with open(os.path.join(bag, 'manifest-md5.txt')) as bag_manifest:
            return {tuple(line.strip().split(maxsplit=1)) for line in bag_manifest}

    elif tarfile.is_tarfile(bag):
        directory_name = bag.split('/')[-1].split('.')[0]
        tar = tarfile.open(bag, mode='r:*')

        with tar.extractfile(f'{directory_name}/manifest-md5.txt') as bag_manifest:
            return {tuple(line.strip().split(maxsplit=1)) for line in bag_manifest}

    else:
        raise RuntimeError(f'{bag} is neither a directory or a tar file')


def best_match_paths(manifest_set, bag_set):
    """
    Compares two sets of tuples in the form '(md5, path)' and attempts to align the paths
    by trimming directories from the set which may have extra leading directories,
    returning a new set with the paths trimmed to the degree that matches the largest
    number of paths in the other set.
    """
    best_trim = 0
    most_matches = 0
    manifest_paths = {t[1] for t in manifest_set}
    bag_paths = {t[1] for t in bag_set}
    max_trim = min([len(Path(p).parts) for p in bag_paths]) - 1

    print(f'Attempting to align the paths in the two sets...')
    for trim_length in range(max_trim):
        trimmed = [Path(p).parts[trim_length:] for p in bag_paths]
        joined = [str(Path(*p)) for p in trimmed]
        num_matches = len([p for p in joined if p in manifest_paths])
        print(f' => {trim_length} directories trimmed: {num_matches} paths match')
        if num_matches > most_matches:
            best_trim = trim_length

    return set([(md5, str(Path(*Path(p).parts[best_trim:]))) for (md5, p) in bag_set])


def bagcheck(args):
    """
    Check inventory contents against relpaths & checksums of a bag manifest.
    """

    # create sets representing the two asset manifests
    print(f"Reading asset inventory at {args.inventory}...")
    inventory = Manifest(args.inventory)
    print(f" => {len(inventory)} assets in batch.")

    print(f"Inspecting BagIt bag at {args.bag}...")
    bag = inspect(args.bag)
    print(f" => {len(bag)} items in bag manifest.")

    assets_to_check = set([(a.md5, a.relpath) for a in inventory])

    # create a new set that attempts to align the paths in the bag with the manifest
    trimmed_bag = best_match_paths(assets_to_check, bag)

    print(f"Confirming all inventory files are present in bag...")
    # find differences between the two sets
    missing = sorted(assets_to_check - trimmed_bag)
    extra = sorted(trimmed_bag - assets_to_check)

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