from datetime import datetime as dt
import hashlib
import os

class Asset():
    '''Class representing the key characteristics of a digital asset'''

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            # Catch non-standard keys used in File Analyzer inventories
            if key == 'Size':
                setattr(self, 'bytes', value)
            elif key == 'Type':
                setattr(self, 'extension', value)
            else:
                setattr(self, key.lower(), value)
        if not hasattr(self, 'path'):
            self.path = os.path.join(self.directory, self.filename)

    # Generate asset dictionary by examining file on disk
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
