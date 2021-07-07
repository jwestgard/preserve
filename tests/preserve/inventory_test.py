import argparse
import csv
import os
from datetime import datetime
from preserve.inventory import inventory
from preserve.asset import calculate_hashes


def test_inventory_stdout(capsys, tmp_path):
    '''
    Simple "happy path" test of the "inventory" command, with a single file
    with output to stdout.
    '''
    subdirectory = "subdir"
    filename = "test_file.txt"
    temp_file_path = tmp_path / subdirectory

    temp_file = create_temp_file(temp_file_path, filename, "Test File1234")
    expected = generate_expected_values(temp_file)

    batch = "TEST_BATCH"
    inventory_args = argparse.Namespace(batch=batch, outfile=None, existing=None, path=str(tmp_path), algorithms=None)
    inventory(inventory_args)

    captured = capsys.readouterr()

    expected_rel_path = os.path.join(subdirectory, filename)
    expected_header = 'BATCH,PATH,DIRECTORY,RELPATH,FILENAME,EXTENSION,BYTES,MTIME,MODDATE,MD5,SHA1,SHA256'
    expected_file_line = f"{batch},{expected['path']},{expected['directory']},{expected_rel_path}," +\
                         f"{expected['filename']},{expected['extension']},{expected['bytes']},{expected['mtime']}," +\
                         f"{expected['moddate']},{expected['md5']},{expected['sha1']},{expected['sha256']}"
    stdout_lines = captured.out.split(csv.Dialect.lineterminator)
    assert stdout_lines[0] == expected_header
    assert stdout_lines[1] == expected_file_line


def create_temp_file(temp_file_path, filename, contents):
    '''
    Creates a temporary file in the given path
    '''
    temp_file_path.mkdir()

    temp_file = temp_file_path / filename

    temp_file.write_text(contents)
    return temp_file


def generate_expected_values(temp_file):
    '''
    Generates the expected values for the given file
    '''
    mtime = int(os.path.getmtime(temp_file))
    hashes = calculate_hashes(temp_file, ['md5', 'sha1', 'sha256'])

    expected_values = {
        "path": str(temp_file),
        "directory": temp_file.parent,
        "filename": temp_file.name,
        "extension": temp_file.suffix.upper()[1:],  # drop period from suffix
        "bytes": os.path.getsize(temp_file),
        "mtime": mtime,
        "moddate": datetime.fromtimestamp(mtime).strftime('%Y-%m-%dT%H:%M:%S'),
        "md5": hashes['md5'],
        "sha1":  hashes['sha1'],
        "sha256":  hashes['sha256']
    }

    return expected_values
