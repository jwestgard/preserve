from datetime import datetime as dt
import hashlib
import os


def calculate_hashes(path, algorithms):
    '''Given a path to a file and a list of hash algorithms, calculate and
       return a dictionary of the requested digests of the file'''
    hashes = [(alg, getattr(hashlib, alg)()) for alg in algorithms]
    with open(path, 'rb') as f:
        while True:
            data = f.read(8192)
            if not data:
                break
            else:
                [hash.update(data) for (alg, hash) in hashes]
    return {alg: hash.hexdigest() for (alg, hash) in hashes}


class Asset():
    '''Class representing the metadata pertaining to an instance of
       a particular digital asset'''
    def __init__(self, **kwargs):
        self.relpath = None
        for k, v in kwargs.items():
            setattr(self, k, v)

    def __eq__(self, other):
        if all([(self.md5 == other.md5),
                (self.bytes == other.bytes),
                (self.filename == other.filename),
                (self.relpath == other.relpath)]):
            return True
        else:
            return False

    @classmethod
    def from_csv(cls, sha1=None, sha256=None, **kwargs):
        '''Alternate constructor for reading data from inventory csv'''
        values = {}
        mapping = {
            'Other': 'md5',
            'Data': 'md5',
            'Key': 'filename',
            'Size': 'bytes',
            'Type': 'extension'
            }
        for k, v in kwargs.items():
            if k in mapping:
                values[mapping[k].lower()] = v
            else:
                values[k.lower()] = v
        if not hasattr(values, 'path'):
            values['path'] = os.path.join(values.get('directory', ''),
                                          values.get('filename'))
        return cls(**values)

    @classmethod
    def from_filesystem(cls, path, base_path='/', *args):
        '''Alternate constructor for reading attributes from file'''
        if not os.path.isfile(path):
            raise TypeError
        else:
            reldir = os.path.relpath(os.path.dirname(path), base_path)
            filename = os.path.basename(path)
            relpath = os.path.join(reldir, filename)

            values = {
                'path':      os.path.abspath(path),
                'mtime':     int(os.path.getmtime(path)),
                'directory': os.path.dirname(path),
                'relpath':   relpath,
                'filename':  filename,
                'bytes':     os.path.getsize(path),
                'extension': os.path.splitext(path)[1].lstrip('.').upper()
                }
            values['moddate'] = dt.fromtimestamp(values['mtime']).strftime(
                                                           '%Y-%m-%dT%H:%M:%S')
            for algorithm, hash in calculate_hashes(path, args).items():
                values[algorithm] = hash
        return cls(**values)
