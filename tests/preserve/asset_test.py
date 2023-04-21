from preserve.asset import Asset
from tests.utils import create_temp_file


def test_relpath_for_file_in_base_path_should_simply_be_filename(tmp_path):
    filename = 'relpath_test.txt'
    temp_file = create_temp_file(tmp_path, filename, "Test relpath")

    asset = Asset.from_filesystem(temp_file, tmp_path, 'test label', *['md5', 'sha1', 'sha256'])
    assert filename == asset.relpath
