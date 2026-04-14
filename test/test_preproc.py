import pytest

from Preprocessor.prepro import preprocessor

INPUT_FILES = "test/input_files/"
OUTPUT_FILES = "output_files"

def test_comments(tmp_path):
    # Arrange
    expected = "x in int := 1 @NEWLINE\n$"
    input_file = INPUT_FILES + "comments.gsl"

    output_dir = tmp_path / OUTPUT_FILES
    output_dir.mkdir()
    output_file = output_dir / "comments_out.gsl"

    # Act
    preprocessor(input_file, output_file)

    data = ""
    with open(output_file, "r") as out:
        data = out.read()

    # Assert
    assert expected == data, f"expected: {expected} actual: {data}"

def test_indents(tmp_path):
    # Arrange
    expected = \
    """graph G @NEWLINE
@INDENT node a, b, c @NEWLINE
a --> c weight integer 3 @NEWLINE
@DEDENT repeat || G . nodes || - 1 times @NEWLINE
@INDENT for each x1 <-- x2 with weight w in G @NEWLINE
@INDENT relax (x1, x2, w) @NEWLINE
@DEDENT for each x1 --> x2 with weight w in G @NEWLINE
@INDENT if w > 5 then @NEWLINE
@INDENT return false @NEWLINE
@DEDENT return true @NEWLINE
@DEDENT @DEDENT $"""

    input_file = INPUT_FILES + "indents.gsl"

    output_dir = tmp_path / OUTPUT_FILES
    output_dir.mkdir()
    output_file = output_dir / "indents_out.gsl"

    # Act
    preprocessor(input_file, output_file)

    data = ""
    with open(output_file, "r") as out:
        data = out.read()

    # Assert
    assert expected == data, f"expected: {expected} actual: {data}"

def test_newlines(tmp_path):
    # Arrange
    expected = \
    """x in int := 4 @NEWLINE
repeat x times @NEWLINE
@INDENT x := x + 1 @NEWLINE
@DEDENT y in real := 3.14 @NEWLINE
v in real := 2 @NEWLINE
o in real := y^2 * v @NEWLINE
$"""

    input_file = INPUT_FILES + "newlines.gsl"

    output_dir = tmp_path / OUTPUT_FILES
    output_dir.mkdir()
    output_file = output_dir / "newlines_out.gsl"

    # Act
    preprocessor(input_file, output_file)

    data = ""
    with open(output_file, "r") as out:
        data = out.read()

    # Assert
    assert expected == data, f"expected: {expected} actual: {data}"
