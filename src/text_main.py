import unittest
from main import *

def test_extract_title():
    # Test with valid H1 header
    assert extract_title("# Hello") == "Hello"
    # Test with whitespace
    assert extract_title("# Hello World  ") == "Hello World"
    # Test with exception
    try:
        extract_title("No H1 here")
        assert False, "Should have raised an exception"
    except ValueError:
        pass