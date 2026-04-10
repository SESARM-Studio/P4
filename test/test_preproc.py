from Preprocessor.prepro import preprocessor

import pytest

def test_comments():
    # Arrange
    expected = "x in int := 1 @NEWLINE\n$"
    output_file = "test/output_files/rasmus.gsl"

    # Act
    preprocessor(inp="test/input_files/comments.gsl", outp=output_file)

    data = ""
    with open(output_file, "r") as out:
        data = out.read()

    # Assert
    assert expected == data, f"expected: {expected} actual: {data}"