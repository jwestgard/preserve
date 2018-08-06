#=== SUBCOMMAND =============================================================
#         NAME: compare
#  DESCRIPTION: check for the presence of files in inventories of various
#               formats (TSM backup, file analyzer, this script)
#============================================================================

def compare(args):
    '''Compare lists of files derived from inventories in various formats,
       including archiving reports from TSM, tab-delimited File Analyzer
       reports, and inventories generated by this script.'''
    filelists = {}
    all_files = [args.first] + args.other 
    for filepath in all_files:
        result = []
        with open(filepath, 'r') as f:
            rawlines = [line.strip('\n') for line in f.readlines()]
            if rawlines[0] == "IBM Tivoli Storage Manager":
                print("Parsing Tivoli output file...")
                p = re.compile(r"([^\\]+) \[Sent\]")
                for line in rawlines:
                    if 'Normal File-->' in line:
                        m = p.search(line)
                        if m:
                            result.append(m.group(1))
            elif "Key" in rawlines[0] or "Filename" in rawlines[0]:
                print("Parsing DPI inventory file... ", end='')
                if '\t' in rawlines[0]:
                    print('tab delimited:')
                    delimiter = '\t'
                else:
                    print('comma delimited:')
                    delimiter = ','
                reader = csv.DictReader(rawlines, delimiter=delimiter)
                filenamecol = "Key" if "Key" in rawlines[0] else "Filename"
                dircol = "Directory"
                for l in reader:
                    result.append(os.path.join(l[filenamecol], l[dircol]))
            else:
                print("Unrecognized file type ...")
            if result:
                filelists[filepath] = result
                print(" => {0}: {1} files".format(filepath, len(result)))
            else:
                print(" => File {0} has not been parsed.".format(filepath))

    all_lists = [set(filelists[filelist]) for filelist in filelists]
    common = set.intersection(*all_lists)
    print("{} values are common to all the supplied files:".format(
            len(common)))

    for n, filelist in enumerate(filelists):
        unique = set(filelists[filelist]).difference(common)
        print(" => File {0}: {1} values are unique to {2}".format(
                n+1, len(unique), filelist))
        if unique is not None:
            sorted_files = sorted(unique)
            for fnum, fname in enumerate(sorted_files):
                print("     ({0}) {1}".format(fnum+1, fname))
    print('')

