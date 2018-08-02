import csv
from datetime import datetime as dt
import hashlib
import os
import re
import sys


class Asset():

    '''    # Handle different keys in inventory files
    all_keys_upper = [k.upper() for k in all_files[0].__dict__.keys()]
    if {'BYTES','EXTENSION'}.issubset(all_keys_upper):
        byte_key = 'Bytes'
        ext_key = 'Extension'
    elif {'SIZE','TYPE'}.issubset(all_keys_upper):
        byte_key = 'Size'
        ext_key = 'Type'
    else:
        print("ERROR: Cannot interpret this inventory file.\n")
        sys.exit()'''

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key.lower(), value)
        if not hasattr(self, 'path'):
            self.path = os.path.join(self.directory, self.filename)

    @classmethod
    def from_filesystem(cls, path, hash_algs=['md5']):
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
                hash = getattr(hashlib, algorithm)()
                with open(values['path'], 'rb') as f:
                    while True:
                        data = f.read(8192)
                        if not data:
                            break
                        else:
                            hash.update(data)
                values[algorithm] = hash.hexdigest()
            return cls(**values)
