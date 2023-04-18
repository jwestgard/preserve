from partition.__main__ import clobbering


def test_clobbering(tmp_path):
    (tmp_path / 'exdir').mkdir()
    (tmp_path / 'exdir/example').touch()
    (tmp_path / 'exdir/files').touch()
    (tmp_path / 'exdir/for').touch()
    (tmp_path / 'exdir/testing').touch()
    (tmp_path / 'exdir/clobbering').touch()

    # Only one of these files should exist
    mapping = {
        "asdf": tmp_path / "exdir/notanexistingfile",
        "fdsa": tmp_path / "exdir/anotherfilethatdoesntexist",
        "dsfa": tmp_path / "exdir/example"
    }

    clobbered = clobbering(mapping=mapping)
    assert len(clobbered) == 1
    assert clobbered[0] == tmp_path / "exdir/example"
