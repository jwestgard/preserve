import csv
import os
import pathlib
import re
from .asset import Asset
from .utils import list_files

class Manifest(list):
    '''Class representing a set of Asset objects in a particular 
       storage location'''
    CSV_MARKERS = ["Key", "Filename", "KEY", "FILENAME"]
    def __init__(self, path):
        self.path = path
        if os.path.isdir(self.path):
            self.source = "directory"
            self.read_from_dir()
        elif os.path.isfile(self.path):
            self.source = "file"
            self.read_from_file()
        self.root = os.path.commonprefix([a.path for a in self])

    def read_from_file(self):
        '''Examine input file and call appropriate parser'''
        with open(self.path, 'r') as f:
            self.rawlines = [line.strip('\n') for line in f]
            headline = self.rawlines[0]
            if headline == "IBM Tivoli Storage Manager":
                self.format = "TSM"
                self.parse_tsm()
            elif any([m in headline for m in self.CSV_MARKERS]):
                if '\t' in headline:
                    self.format = "TSV"
                    self.delimiter = '\t'
                else:
                    self.format = "CSV"
                    self.delimiter = ','
                self.parse_csv()

    def read_from_dir(self):
        '''Read files on disk and populate manifest'''
        for f in list_files(self.path):
            self.append(Asset().from_filesystem(f))

    def parse_tsm(self):
        '''Data parser function for reading data from Tivoli 
           Storage Manager Report'''
        r = r"^Normal File-->\W+([\d,]+)\W(\\{2}[^ ]+\$\\)([^ ]+)\W\[Sent\]$"
        p = re.compile(r)
        results = []
        for line in self.rawlines:
            m = p.search(line)
            if m:
                bytes = int(m.group(1).replace(',', ''))
                path = m.group(3).replace('\\', '/')
                self.append(Asset(path=path, bytes=bytes))

    def parse_csv(self):
        '''Data parser for reading data from csv'''
        for marker in self.CSV_MARKERS:
            if marker in self.rawlines[0]:
                filenamecol = marker
                dircol = "DIRECTORY" if marker.isupper() else "Directory"
                break
        for row in csv.DictReader(self.rawlines, delimiter=self.delimiter):
            self.append(Asset().from_csv(**row))
