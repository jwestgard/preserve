from .asset import Asset
import csv

class Manifest(list):
    '''Class representing a set of Asset objects in a particular 
       storage location'''
    def __init__(self, *args):
        for k,v in kwargs.items():
            setattr(self, k, v)

    @classmethod
    def from_tsm_report(cls, path):
        '''Alternate constructor for reading data from Tivoli 
           Storage Manager Report'''
        with open(path, 'r') as handle:
            
        for k, v in kwargs.items():
            values[k.lower()] = v
        if not hasattr(values, 'path'):
            values['path'] = os.path.join(values['directory'],
                                          values['filename'])
        return cls(**values)

    @classmethod
    def from_inventory_csv(cls, path):
        '''Alternate constructor for reading data from csv'''
        with open(path, 'r') as handle:
            reader = csv.DictReader(handle)
            for row in reader:
            values[k.lower()] = v
        if not hasattr(values, 'path'):
            values['path'] = os.path.join(values['directory'],
                                          values['filename'])
        return cls(**values)

'''     with open(filepath, 'r') as f:
            rawlines = [line.strip('\n') for line in f.readlines()]
            if rawlines[0] == "IBM Tivoli Storage Manager":
                print("Parsing Tivoli output file...")
                p = re.compile(r"([^\\]+) \[Sent\]")
                for line in rawlines:
                    if 'Normal File-->' in line:
                        m = p.search(line)
                        if m:
                            result.append(m.group(1))
            elif any(marker in rawlines[0] for marker in markers):
                print("Parsing DPI inventory file... ", end='')
                for marker in markers:
                    if marker in rawlines[0]:
                        filenamecol = marker
                        if marker.isupper():
                            dircol = "DIRECTORY"
                        else:
                            dircol = "Directory"
                        break
                if '\t' in rawlines[0]:
                    print('tab delimited:')
                    delimiter = '\t'
                else:
                    print('comma delimited:')
                    delimiter = ','
                reader = csv.DictReader(rawlines, delimiter=delimiter)
                for row in reader:
                    result.append(os.path.join(row[dircol], row[filenamecol]))
            else:
                print("Unrecognized file type ...")
            if result:
                filelists[filepath] = result
                print(" => {0}: {1} files".format(filepath, len(result)))
            else:
                print(" => File {0} has not been parsed.".format(filepath))
'''
