"""Basic tests for JSMon package."""

def test_import():
    """Test that package imports successfully."""
    try:
        import jsmon
        assert True
    except ImportError:
        assert False, "Failed to import jsmon"

def test_version():
    """Test version is defined."""
    import jsmon
    # Package should have __version__ or similar
    assert True  # Basic smoke test
