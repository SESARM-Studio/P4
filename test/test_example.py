import pytest

def test_example():
    # Arrange
    x = 1
    y = 1

    # Act
    z = x + 1

    # Assert
    assert z > x, "fail message"
