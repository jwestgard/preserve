import pytest

from partition.__main__ import PARTITIONING_PATTERN, has_duplicates
from partition.classes import Asset, FileSet


@pytest.mark.parametrize(
    ('filename'),
    [
        # Example files from this ticket:
        # https://umd-dit.atlassian.net/browse/LIBITD-2238
        ('scpa-081931-0001.mov.md5'),
        ('scpa-081986_PBCore.xml'),
        # File with a bunch of extensions
        ('blah-123456-1234.a.bunch.of.file.extensions.txt'),
        # File with numbers after underscore
        ('scpa-081986_1234.xml')
    ]
)
def test_partition_by(filename):
    # 'd41d8cd98f00b204e9800998ecf8427e' is the MD5 of an empty file
    asset = Asset(filename=filename, md5='d41d8cd98f00b204e9800998ecf8427e', bytes=0)
    # '8ddd8be4b179a529afa5f2ffae4b9858' is the MD5 of a file with just the line 'Hello World!'
    asset2 = Asset(filename=f'{filename}.different.file', md5='8ddd8be4b179a529afa5f2ffae4b9858', bytes=13)
    path = f'/input/{filename}'
    path2 = f'/input/{filename}.extra'

    # This shouldn't have any duplicates because only one
    fileset = FileSet({
        path: asset
    })
    mapping = fileset.partition_by(PARTITIONING_PATTERN, '/output')
    duplicates = has_duplicates(mapping)
    assert duplicates is False

    # This should have duplicates because same filename
    fileset = FileSet({
        path: asset,
        path2: asset
    })
    mapping = fileset.partition_by(PARTITIONING_PATTERN, '/output')
    duplicates = has_duplicates(mapping)
    assert duplicates

    # This shouldn't have duplicates because different filenames
    fileset = FileSet({
        path: asset,
        path2: asset2
    })
    mapping = fileset.partition_by(PARTITIONING_PATTERN, '/output')
    duplicates = has_duplicates(mapping)
    assert duplicates is False
