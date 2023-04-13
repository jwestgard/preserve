import pytest

from partition.__main__ import PARTITIONING_PATTERN, has_duplicates
from partition.classes import Asset, FileSet


@pytest.mark.parametrize(
    ('filename', 'dest_dir'),
    [
        # Example files from this ticket:
        # https://umd-dit.atlassian.net/browse/LIBITD-2238
        ('scpa-081931-0001.mov.md5', 'scpa-081931'),
        ('scpa-081986_PBCore.xml', 'scpa-081986'),
        # File with a bunch of extensions
        ('blah-123456-1234.a.bunch.of.file.extensions.txt', 'blah-123456'),
        # File with numbers after underscore
        ('scpa-081986_1234.xml', 'scpa-081986')
    ]
)
def test_partition_by(filename, dest_dir):
    # 'd41d8cd98f00b204e9800998ecf8427e' is the MD5 of an empty file
    asset = Asset(filename=filename, md5='d41d8cd98f00b204e9800998ecf8427e', bytes=0)
    path = f'/input/{filename}'
    path2 = f'/input/{filename}.extra'

    # This shouldn't have any duplicates
    fileset = FileSet({
        path: asset
    })
    mapping = fileset.partition_by(PARTITIONING_PATTERN, '/output')
    duplicates = has_duplicates(mapping)
    assert duplicates is False

    # This should have duplicates
    fileset = FileSet({
        path: asset,
        path2: asset
    })

    mapping = fileset.partition_by(PARTITIONING_PATTERN, '/output')
    duplicates = has_duplicates(mapping)
    assert duplicates
