import re


old_pattern = r"^([a-z]+?)-(\d+?)-\d+?\.\w+?$"
new_pattern = r"^([a-z]+?)-(\d+?)[-_][^.]+?\.\S+?$"


def test_pattern():

    # Example files from this ticket:
    # https://umd-dit.atlassian.net/browse/LIBITD-2238
    file1 = 'scpa-081931-0001.mov.md5'
    file2 = 'scpa-081986_PBCore.xml'

    # File with a bunch of extensions
    file3 = 'blah-123456-1234.a.bunch.of.file.extensions.txt'

    # File with numbers after underscore
    file4 = 'scpa-081986_1234.xml'

    # The old pattern shouldn't match these
    assert re.match(old_pattern, file1) is None
    assert re.match(old_pattern, file2) is None
    assert re.match(old_pattern, file3) is None
    assert re.match(old_pattern, file4) is None

    # The new pattern should
    assert re.match(new_pattern, file1) is not None
    assert re.match(new_pattern, file2) is not None
    assert re.match(new_pattern, file3) is not None
    assert re.match(new_pattern, file4) is not None
