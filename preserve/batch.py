#!/usr/bin/env python3


from .inventory import inventory as inventory
from .utils import human_readable as human_readable
from .__main__ import print_header as print_header
import os
import sys


INDIR = sys.argv[1]
OUTDIR = sys.argv[2]


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
                ))]
    pattern = '| {{{0}}} | {{{1}}} | {{{2}}} | {{{3}}} | {{{4}}} |'.format(*cols)
    header = pattern.format(n='N', d='DIRNAME', f='FILES', b='BYTES', h='HUMAN')
    border = '=' * len(header)
    table = [border, header, border]
    for num, dir in enumerate(results, 1):
        table.append(pattern.format(n=str(num).zfill(len(str(len(results)))), 
            d=dir.dirname, f=dir.filecount, b=dir.bytecount, h=dir.humanread
            ))
    table.extend([border, '\n'])
    return '\n'.join(table)


class Directory():

    '''Class representing a directory to be scanned in a batch process'''

    def __init__(self, path):
        self.path = path
        self.dirname = os.path.basename(path)
        self.filecount, self.bytecount = self.summarize()
        self.humanread = ' '.join([str(i) for i in human_readable(self.bytecount)])

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


def main():

    class CommandArgs():
        '''A simple class to create a stand-in for the argparse namespace object'''
        def __init__(self, kwargs):
            self.__dict__.update(kwargs)

    print_header('batch inventory')
    print()

    # Scan the batch directory and create summary of batch
    sys.stderr.write(f'Checking {INDIR} ...\n')
    if not os.path.exists(OUTDIR):
        os.makedirs(OUTDIR)
        sys.stderr.write(f'Creating {OUTDIR} ...\n')
    sys.stderr.write(f'Writing to {OUTDIR} ...\n')
    results = list()    
    for entry in os.listdir(INDIR):
        path = os.path.join(INDIR, entry)
        if os.path.isdir(path):
            results.append(Directory(path))

    # Print the summary in table format
    sys.stderr.write(f'\nBatch contains the following {len(results)} directories:\n')
    sys.stderr.write(table_format(results))

    # Process each directory in the batch
    for result in results:
        args = CommandArgs({'path': os.path.join(INDIR, result.dirname),
                            'outfile': None,
                            'existing': None,
                            'algorithms': 'md5'
                            })
        outpath = os.path.join(OUTDIR, result.dirname + '.csv')
        if os.path.isfile(outpath):
            args.existing = outpath
        else:
            args.outfile = outpath

        # Call the inventory subcommand generated args
        result = inventory(args)
        if result:
            sys.stderr.write(result + '\n')


if __name__ == "__main__":
    main()
