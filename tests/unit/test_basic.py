"""
Basic tests to verify testing framework
"""
import pytest


def test_basic_math():
    """Test basic math operations."""
    assert 1 + 1 == 2
    assert 2 * 3 == 6
    assert 10 / 2 == 5


def test_string_operations():
    """Test string operations."""
    text = "Hello, World!"
    assert text.upper() == "HELLO, WORLD!"
    assert text.lower() == "hello, world!"
    assert "World" in text


def test_list_operations():
    """Test list operations."""
    items = [1, 2, 3, 4, 5]
    assert len(items) == 5
    assert items[0] == 1
    assert items[-1] == 5
    assert 3 in items


class TestBasicClass:
    """Test class-based test organization."""

    def test_class_method(self):
        """Test method within a class."""
        assert True

    def test_another_method(self):
        """Another test method."""
        data = {"key": "value", "number": 42}
        assert data["key"] == "value"
        assert data["number"] == 42
