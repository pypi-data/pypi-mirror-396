"""Test that the package imports correctly."""

def test_import():
    """Test package import."""
    import pyseter
    assert pyseter is not None

def test_version():
    """Test that version is defined."""
    import pyseter
    assert hasattr(pyseter, '__version__')
    assert isinstance(pyseter.__version__, str)