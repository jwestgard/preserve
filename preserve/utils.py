import csv
import os
import sys

from .asset import Asset


def header(title):
    '''Generate a title header box for console output.'''
    length = len(title) + 4
    lines = [f"\n{'=' * length}",
             f"|{' ' * (length-2)}|",
             f"| {title} |",
             f"|{' ' * (length-2)}|",
             f"{'=' * length}\n\n"]
    return "\n".join(lines)


def file_size(size: int) -> str:
    if size >= 2**40:
        return f"{round(size/2**40, 2)} TiB"
    elif size >= 2**30:
        return f"{round(size/2**30, 2)} GiB"
    elif size >= 2**20:
        return f"{round(size/2**20, 2)} MiB"
    elif size >= 2**10:
        return f"{round(size/2**10, 2)} KiB"
    else:
        return f"{size} Bytes"


def subheader(title):
    '''Format and print header for a subcommand.'''
    return f'{title.capitalize()}\n{"-" * len(title)}\n'


def human_readable(bytes):
    '''Return human-readable version of a given number of bytes plus the units,
       rounding to two decimal places for scales in KiB and larger.'''
    orders_mag = [
        'bytes', 'KiB', 'MiB', 'GiB', 'TiB', 'PiB', 'EiB', 'ZiB', 'YiB'
        ]
    for n in range(len(orders_mag)):
        scaled = bytes / (2**(10 * n))
        if scaled >= 0 and scaled < 1024:
            if orders_mag[n] == 'bytes':
                scaled = int(scaled)
            else:
                scaled = round(scaled, 2)
            return (scaled, orders_mag[n])
    return False


def list_files(dir_path):
    '''Return a list of files in a directory tree, pruning out the
       hidden files & dirs (i.e. those that begin with dot).'''
    result = []
    for root, dirs, files in os.walk(dir_path):
        # prune directories beginning with dot
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        # prune files beginning with dot
        files[:] = [f for f in files if not f.startswith('.')]
        result.extend([os.path.join(root, f) for f in files])
    return result


def get_inventory(path, label, mount):
    '''Given a path to a file or directory, return list of inventory metadata
       based on reading the inventory, or scanning the directory's files.'''
    if os.path.isfile(path):
        print("  => {0} is a file.".format(path))
        with open(path, 'r') as infile:
            dialect = csv.Sniffer().sniff(infile.readline())
            infile.seek(0)
            result = []
            for row in csv.DictReader(infile, dialect=dialect):
                a = Asset().from_csv(**row)
                result.append(a)
        print("  => read {0} lines from file.".format(len(result)))
        return result
    elif os.path.isdir(path):
        print("  => {0} is a directory.".format(path))
        result = []
        for n, f in enumerate(list_files(path)):
            print("  => found {0} files.".format(n+1), end='\r')
            a = Asset.from_filesystem(f, path, label, mount)
            result.append(a)
        print()
        return result
    else:
        sys.exit("  => {0} could not be found!".format(path))
