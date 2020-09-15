import pytest
import random

def test_print():
    print("This is a simple test")

def test_that_fails():
    raise Exception("This a test that will fail")

def test_random():
    value = random.randint(1, 2)
    if value == 1:
        raise Exception("Random fail")