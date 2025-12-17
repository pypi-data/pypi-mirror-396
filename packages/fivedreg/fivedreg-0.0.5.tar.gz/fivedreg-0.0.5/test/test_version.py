"""
Tests for fivedreg version information
"""
import fivedreg


def test_version_exists():
    """Test that __version__ attribute exists."""
    assert hasattr(fivedreg, '__version__')
    assert isinstance(fivedreg.__version__, str)
    assert len(fivedreg.__version__) > 0


def test_version_format():
    """Test that version follows expected format."""
    version = fivedreg.__version__
    # Version should contain at least a number
    assert any(char.isdigit() for char in version)



