from datetime import datetime as dt
import hashlib
import os

def calculate_hash(path, alg):
    hash = getattr(hashlib, alg)()
    with open(path, 'rb') as f:
        while True:
            data = f.read(8192)
            if not data:
                break
            else:
                hash.update(data)
        return hash.hexdigest()

class Asset(dict):
    def __init__(self, **kwargs):
        for k,v in kwargs.items():
            setattr(self, k, v)

    @classmethod
    def from_csv(cls, **kwargs):
        '''alternate constructor for reading data from inventory csv'''
        values = {}
        for k, v in kwargs.items():
            values[k.lower()] = v
        if not hasattr(values, 'path'):
            values['path'] = os.path.join(values['directory'],
                                          values['filename'])
        return cls(**values)

    # Generate asset dictionary by examining file on disk
    @classmethod
    def from_filesystem(cls, path, hash_algs=['md5','sha1','sha256']):
        '''alternate constructory for reading attributes from file'''
        if not os.path.isfile(path):
            raise TypeError
        else:
            values = {
                'path':      os.path.abspath(path),
                'mtime':     int(os.path.getmtime(path)),
                'directory': os.path.dirname(path),
                'filename':  os.path.basename(path),
                'bytes':     os.path.getsize(path),
                'extension': os.path.splitext(path)[1].lstrip('.').upper()
                }
            values['moddate'] = dt.fromtimestamp(values['mtime']).strftime(
                                                           '%Y-%m-%dT%H:%M:%S')
            for algorithm in hash_algs:
                values[algorithm] = calculate_hash(path, algorithm)
        return cls(**values)
