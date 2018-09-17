from asset import Asset
import csv
import os
import re

class Manifest(list):
    '''Class representing a set of Asset objects in a particular 
       storage location'''
    def __init__(self, path):
        self.path = path
        with open(self.path, 'r') as f:
            self.rawlines = [line.strip('\n') for line in f.readlines()]
        markers = ["Key", "Filename", "KEY", "FILENAME"]
        if self.rawlines[0] == "IBM Tivoli Storage Manager":
            self.load_from_tsm()
        elif any([marker in rawlines[0] for marker in markers]):
            if '\t' in rawlines[0]:
                self.delimiter = '\t'
            else:
                self.delimiter = ','
        else:
            if result:
                filelists[filepath] = result
                print(" => {0}: {1} files".format(filepath, len(result)))
            else:
                print(" => File {0} has not been parsed.".format(filepath))

    def load_from_tsm(self):
        '''Data loading function for reading data from Tivoli 
           Storage Manager Report'''
        p = re.compile(r"^Normal File-->\W+([\d,]+)\W(\\{2}[^ ]+)\W\[Sent\]$")
        results = []
        for line in self.rawlines:
            m = p.search(line)
            if m:
                bytes = int(m.group(1).replace(',', ''))
                path = m.group(2)
                a = Asset(path=path, bytes=bytes)
                print(a)
                results.append(a)
        self.root = os.path.commonprefix([a.path for a in self])

    def load_from_csv(self):
        '''Alternate constructor for reading data from csv'''
        for marker in markers:
            if marker in rawlines[0]:
                filenamecol = marker
                if marker.isupper():
                    dircol = "DIRECTORY"
                else:
                    dircol = "Directory"
                break
        reader = csv.DictReader(rawlines, delimiter=self.delimiter)
        for row in reader:
            result.append(os.path.join(row[dircol], row[filenamecol]))

