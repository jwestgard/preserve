#=== SUBCOMMAND =============================================================
#         NAME: bytecount
#  DESCRIPTION: count files by extention and sum their sizes
#============================================================================

def bytecount(args):
    '''Sum the bytes in an inventory file or a directory tree, reporting total 
       bytes and number of files broken down by extension.'''
    print_header(args.func.__name__)

    print("Loading data from specified path...")
    PATH = args.path
    all_files = get_inventory(PATH)

    if not all_files:
        print(
            "ERROR: Could not read inventory data from the specified path.\n"
            )
        sys.exit()

    extensions = {}
    totalbytes = 0

    # Handle different keys in inventory files
    if {'BYTES','EXTENSION'}.issubset([k.upper() for k in all_files[0].keys()]):
        byte_key = 'Bytes'
        ext_key = 'Extension'
    elif {'SIZE','TYPE'}.issubset([k.upper() for k in all_files[0].keys()]):
        byte_key = 'Size'
        ext_key = 'Type'
    else:
        print("ERROR: Cannot interpret this inventory file.\n")
        sys.exit()

    # Iterate over the rows of the inventory
    for f in all_files:
        totalbytes += int(f[byte_key])
        ext = f[ext_key]
        if ext in extensions:
            extensions[ext] += 1
        else:
            extensions[ext] = 1

    exts_summary = [
        "{0}:{1}".format(type, num) for (type, num) in extensions.items()
        ]

    # Convert bytes to human-readable if requested and report results
    if args.human and totalbytes >= 1024:
        count_num, count_units = human_readable(totalbytes)
        print('{0} bytes ({1} {2}) for {3} files.'.format(
            str(totalbytes), count_num, count_units, len(all_files)
            ))       
    else:
        print('{0} bytes for {1} files.'.format(
            str(totalbytes), len(all_files)
            ))

    print('({0})'.format(", ".join(exts_summary)))
    print('')
