def test_basic_math():
    """A simple test that will always pass."""
    result = 2 + 2
    assert result == 4


def test_string_operations():
    """Test basic string operations."""
    text = "hello world"
    assert text.upper() == "HELLO WORLD"
    assert len(text) == 11
    assert "world" in text


def test_intentional_failure():
    """A test that will always fail."""
    result = 2 + 2
    assert result == 5, "This test is designed to fail: 2 + 2 should not equal 5"
