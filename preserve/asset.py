from datetime import datetime as dt
import hashlib
import os

GB = 1024 ** 3
CHUNK_SIZE = 4 * GB


def calculate_etag(path, chunk_size):
    """
    Calculate the AWS etag: either the md5 hash, or for files larger than
    the specified chunk size, the hash of all the chunk hashes concatenated
    together, followed by the number of chunks.
    """
    file_size = os.path.getsize(path)
    if file_size == 0:
        # for zero byte files, just return the MD5 sum of an empty string
        return hashlib.md5(b'').hexdigest()
    else:
        md5s = []
        with open(path, 'rb') as handle:
            if chunk_size < GB:
                for data in chunked(handle, chunk_size):
                    md5s.append(hashlib.md5(data))
            else:
                # Python doesn't like reading more than 1GB from a file at a time.
                # To get around this, read 1GB at a time and assemble the portions
                # into the final md5sum.
                if chunk_size % GB != 0:
                    raise ConfigException('Chunk sizes >1GB must be multiples of 1GB')
                portions_per_chunk = chunk_size // GB
                md5sum = None
                for i, data in enumerate(chunked(handle, GB), 1):
                    if md5sum is None:
                        md5sum = hashlib.md5()
                    md5sum.update(data)
                    if i % portions_per_chunk == 0:
                        md5s.append(md5sum)
                        md5sum = None
                else:
                    # check to see if we have a pending md5sum
                    # after the last iteration of the loop
                    if md5sum is not None:
                        md5s.append(md5sum)

        if len(md5s) == 1:
            return md5s[0].hexdigest()
        else:
            digests = hashlib.md5(b''.join(m.digest() for m in md5s))
            return f'{digests.hexdigest()}-{len(md5s)}'


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


def chunked(handle, chunk_size):
    # based on https://stackoverflow.com/a/54989668/5124907
    return iter(lambda: handle.read(chunk_size), b'')


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
    def from_filesystem(cls, path, base_path, *args):
        '''Alternate constructor for reading attributes from file'''
        if not os.path.isfile(path):
            raise TypeError
        else:
            reldir = ''
            filepath = os.path.dirname(path)
            if filepath != str(base_path):
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
            if values['md5'] and (values['bytes'] <= CHUNK_SIZE):
                values['etag'] = values['md5']
            else:
                values['etag'] = calculate_etag(path, CHUNK_SIZE)
        return cls(**values)
