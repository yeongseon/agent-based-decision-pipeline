def test_abdp_has_expected_version() -> None:
    from abdp import __version__

    assert __version__ == "0.3.0"


def test_get_version_returns_public_version() -> None:
    from abdp import __version__, get_version

    assert get_version() == "0.3.0"
    assert get_version() == __version__
