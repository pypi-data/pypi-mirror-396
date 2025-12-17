"""Tests for the example module."""
from treetops.example import hello


def test_hello_default():
    """Test hello() with default argument."""
    result = hello()
    assert result == "Hello, World!"


def test_hello_with_name():
    """Test hello() with a specific name."""
    result = hello("Alice")
    assert result == "Hello, Alice!"


def test_hello_with_different_names():
    """Test hello() with various names."""
    assert hello("Bob") == "Hello, Bob!"
    assert hello("Python") == "Hello, Python!"
    assert hello("") == "Hello, !"

