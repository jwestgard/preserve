from .utils import get_inventory

#=== SUBCOMMAND =============================================================
#         NAME: verify
#  DESCRIPTION: verify two sets of files (on disk or as recorded in CSV file) 
#               by comparing their checksums, size, timestamp
#============================================================================

def verify(args):
    '''Verify the identity of two inventories (either stored or created on 
       the fly), by checking for the presence of all files and comparing the 
       checksums of each one.'''
    print("1. Loading data from 1st path...")
    dict_a = {f.path: f.md5 for f in get_inventory(args.first)}
    print("2. Loading data from 2nd path...")
    dict_b = {f.path: f.md5 for f in get_inventory(args.second)}
    all_keys = set().union(dict_a.keys(), dict_b.keys())
    not_a = []
    not_b = []
    changed = {}
    verified = 0
    total = len(all_keys)

    # Iterate over union of both file inventories
    for n,k in enumerate(all_keys):
        if not k in dict_a:
            not_a.append(k)
        elif not k in dict_b:
            not_b.append(k)
        elif not dict_a[k] == dict_b[k]:
            changed[k] = (dict_a[k], dict_b[k])
        else:
            verified += 1
        print("Checked {0}/{1} files.".format(n+1, total), end='\r')

    # Clear counter
    print('')

    # Report success or failure of verification
    if not any([not_a, not_b, changed]):
        print("Success! No differences found.")
    else:
        print("Possible problems were found.")

    # Report details of the comparison
    print("  => {0} files are in 1 but not 2.".format(len(not_b)))
    print("  => {0} files are in 2 but not 1.".format(len(not_a)))
    print("  => {0} files show a checksum mismatch.".format(len(changed)))
    for k,v in changed.items():
        print("     - {0}: {1} != {2}".format(k, v[0], v[1]))
    print("  => Verified {0}/{1} files.".format(verified, total))
    print('')
