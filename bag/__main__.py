#!/usr/bin/env python3

import argparse
import bagit
import json
import os
import sys


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
        action='store'
        )

    parser.add_argument(
        '-v', '--version',
        action='version',
        help='Print version number and exit',
        version='%(prog)s 0.1'
        )

    return parser.parse_args()


def main():

    try:
        print(f"\n================")
        print(f"|              |")
        print(f"| Bagging Tool |")
        print(f"|              |")
        print(f"================\n")

        """ (1) Parse args """
        args = parse_args()
        print(f"Running with the following arguments:")
        width = max([len(k) for k in args.__dict__])
        for k in args.__dict__:
            print(f"  {k:>{width}} : {getattr(args, k)}")

        """ (2) Read configuration """
        if args.config:
            with open(args.config) as handle:
                config = json.load(handle)

        """ (3) Create bag """
        bag = bagit.make_bag(args.path, checksums=['md5', 'sha256'])
        for tagfile, tags in config.items():
            if tagfile == 'bag-info.txt':
                for k, v in tags.items():
                    bag.info[k] = v
            else:
                tagfilepath = os.path.join(args.path, tagfile)
                with open(tagfilepath, 'w') as handle:
                    for k, v in tags.items():
                        handle.write(f"{k}: {v}\n")
        bag.save()

        """ (4) Summarize results """
        print("Bagging complete.")

    except Exception as err:
        print(f"ERROR: {err}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
