#!/usr/bin/env python3

from ..inventory import inventory as inventory
from ..utils import human_readable as human_readable
from ..__main__ import print_header as print_header
import csv
import os
import sys
import yaml


def table_format(results):

    '''Generate summary list of directories formatted as a table'''

    cols = ['n:>{width}'.format(width=len(str(len(results)))),
            'd:<{width}'.format(width=max(
                [len(r.dirname) for r in results] + [len('DIRNAME')]
                )),
            'f:>{width}'.format(width=max(
                [len(str(r.filecount)) for r in results] + [len('FILES')]
                )),
            'b:>{width}'.format(width=max(
                [len(str(r.bytecount)) for r in results] + [len('BYTES')]
                )),
            'h:>{width}'.format(width=max(
                [len(str(r.humanread)) for r in results] + [len('HUMAN')]
                )),
            's:>8'
            ]
    template = '| {{{0}}} | {{{1}}} | {{{2}}} | {{{3}}} | {{{4}}} | {{{5}}} |'
    pattern = template.format(*cols)
    header = pattern.format(
        n='N', d='DIRNAME', f='FILES', b='BYTES', h='HUMAN', s='STATUS'
        )
    border = '=' * len(header)
    table = [border, header, border]
    for num, dir in enumerate(results, 1):
        table.append(pattern.format(n=str(num).zfill(len(str(len(results)))),
            d=dir.dirname, f=dir.filecount, b=dir.bytecount, h=dir.humanread,
            s=dir.status
            ))
    table.extend([border, '\n'])
    return '\n'.join(table)


class Directory():

    '''Class representing a directory to be scanned in a batch process'''

    def __init__(self, path, dirname=None, filecount=None, bytecount=None,
                humanread=None, status=None):
        self.path = path
        self.status = status or 'ToDo'
        self.dirname = dirname or os.path.basename(path)
        if filecount and bytecount:
            self.filecount = filecount
            self.bytecount = bytecount
        else:
            self.filecount, self.bytecount = self.summarize()
        if humanread:
            self.humanread = humanread
        else:
            self.humanread = ' '.join(
                [str(i) for i in human_readable(self.bytecount)]
                )

    def summarize(self):
        filecount = 0
        bytecount = 0
        for (dir, subdirs, files) in os.walk(self.path):
            files = [f for f in files if not f.startswith('.')]
            subdirs[:] = [d for d in subdirs if not d.startswith('.')]
            filecount += len(files)
            for file in files:
                path = os.path.join(dir, file)
                bytecount += os.path.getsize(path)
        return filecount, bytecount


class CommandArgs():

    '''A simple class to create a stand-in for the argparse namespace object'''

    def __init__(self, kwargs):
        self.__dict__.update(kwargs)


def main():

    with open(sys.argv[1]) as handle:
        config = yaml.safe_load(handle)

    INDIR    = os.path.abspath(config['INPUT_ROOT'])
    OUTDIR   = os.path.abspath(config['OUTPUT_ROOT'])
    EXCLUDES = config['EXCLUDES']
    MANIFEST = config['MANIFEST']

    print_header('batch inventory')
    print()

    # check input path; exit if not exists
    if not os.path.exists(INDIR):
        sys.exit(f'{INDIR} does not exist; exiting.')
    else:
        sys.stderr.write(f'Checking {INDIR} ...\n')

    # check output path; create if not exists
    if not os.path.exists(OUTDIR):
        os.makedirs(OUTDIR)
        sys.stderr.write(f'Creating {OUTDIR} ...\n')
    sys.stderr.write(f'Writing to {OUTDIR} ...\n')

    # check manifest file; resume batch if exists else scan and create
    if os.path.exists(MANIFEST):
        with open(MANIFEST) as manifest_handle:
            reader = csv.DictReader(manifest_handle)
            batchdirs = [Directory(**row) for row in reader]
    else:
        batchdirs = list()
        for entry in os.listdir(INDIR):
            path = os.path.join(INDIR, entry)
            if os.path.isdir(path):
                dir = Directory(path)
                if dir.dirname in EXCLUDES:
                    dir.status = 'Exclude'
                batchdirs.append(dir)

    # Print the summary in table format
    sys.stderr.write(
        f'\nBatch contains the following {len(batchdirs)} directories:\n'
        )
    sys.stderr.write(table_format(batchdirs))

    # Write out the manifest file, summarizing the batch
    with open(MANIFEST, 'w') as handle:
        fieldnames = ['path', 'dirname', 'filecount', 'bytecount',
                      'humanread', 'status']
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for dir in batchdirs:
            writer.writerow({'path': dir.path,
                             'dirname': dir.dirname,
                             'filecount': dir.filecount,
                             'bytecount': dir.bytecount,
                             'humanread': dir.humanread,
                             'status': dir.status
                             })

    # Process each directory in the batch
    for dir in batchdirs:
        if dir.status == 'Exclude':
            continue
        args = CommandArgs({'path': os.path.join(INDIR, dir.dirname),
                            'outfile': None,
                            'existing': None,
                            'algorithms': 'md5'
                            })
        outpath = os.path.join(OUTDIR, dir.dirname + '.csv')
        if os.path.isfile(outpath):
            args.existing = outpath
        else:
            args.outfile = outpath

        # Call the inventory subcommand generated args
        result = inventory(args)

        if result:
            sys.stderr.write(result + '\n')
            dir.status = 'Complete'
            sys.stderr.write(table_format(batchdirs))


if __name__ == "__main__":
    main()
