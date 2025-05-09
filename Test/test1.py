#test1.py

from MyFuncs import *
import unittest

def test_addition():
    assert add(2, 3) == 5, "Should be 5"
    assert add(-1, 1) == 0, "Should be 0"
    assert add(0, 0) == 0, "Should be 0"

def test_multiplication():
    assert multiply(2, 3) == 6, "Should be 6"
    assert multiply(-1, 1) == -1, "Should be -1"
    assert multiply(0, 5) == 0, "Should be 0"

def test_add():
    x = 1.1
    y = 2.2


if __name__ == "__main__":
    test_addition()
    test_multiplication()
    print("All tests passed!")
    unittest.main()
    # Test the add function
