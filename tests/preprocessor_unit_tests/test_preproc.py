import pytest

from preprocessor.prepro import preprocessor

INPUT_FILES = "tests/preprocessor_unit_tests/input_files/"
OUTPUT_FILES = "output_files"

def test_comments(tmp_path):
    # Arrange
    expected = "x in int := 1 @NEWLINE\n$"
    input_file = INPUT_FILES + "comments.gsl"

    output_dir = tmp_path / OUTPUT_FILES
    output_dir.mkdir()
    output_file = output_dir / "comments_out.gsl"

    # Act
    preprocessor(input_file, True, output_file)

    data = ""
    with open(output_file, "r") as out:
        data = out.read()

    # Assert
    assert expected == data, f"expected: {expected} actual: {data}"

def test_indents(tmp_path):
    # Arrange
    expected = \
    """graph G with int weight @NEWLINE
@INDENT node a, b, c @NEWLINE
edge a --> c weight 3 @NEWLINE
@DEDENT repeat || G.nodes || - 1 times @NEWLINE
@INDENT for each edge x1 <-- x2 with weight w in G @NEWLINE
@INDENT relax (x1, x2, w) @NEWLINE
@DEDENT for each edge x1 --> x2 with weight w in G @NEWLINE
@INDENT if w > 5 then @NEWLINE
@INDENT return false @NEWLINE
@DEDENT return true @NEWLINE
@DEDENT @DEDENT $"""

    input_file = INPUT_FILES + "indents.gsl"

    output_dir = tmp_path / OUTPUT_FILES
    output_dir.mkdir()
    output_file = output_dir / "indents_out.gsl"

    # Act
    preprocessor(input_file, True, output_file)

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
    preprocessor(input_file, True, output_file)

    data = ""
    with open(output_file, "r") as out:
        data = out.read()

    # Assert
    assert expected == data, f"expected: {expected} actual: {data}"

def test_codeAfterCommentError(tmp_path):
    # Arrange
    expected = "ERROR LINE 6: No code must follow a multi-line comment"

    input_file = INPUT_FILES + "codeAfterCommentError.gsl"

    output_dir = tmp_path / OUTPUT_FILES
    output_dir.mkdir()
    output_file = output_dir / "codeAfterCommentError.gsl"

    # Act
    with pytest.raises(SystemExit) as exit_info:
        preprocessor(input_file, True, output_file)   

    # Assert
    assert expected == exit_info.value.code, f"expected: {expected} actual: {exit_info.value.code}"

def test_mismatchIndentError(tmp_path):
    # Arrange
    expected = "ERROR LINE 3: Inconsistent use of spaces"

    input_file = INPUT_FILES + "mismatchIndentError.gsl"

    output_dir = tmp_path / OUTPUT_FILES
    output_dir.mkdir()
    output_file = output_dir / "mismatchIndentError.gsl"

    # Act
    with pytest.raises(SystemExit) as exit_info:
        preprocessor(input_file, True, output_file)   

    # Assert
    assert expected == exit_info.value.code, f"expected: {expected} actual: {exit_info.value.code}"

def test_startIndentError(tmp_path):
    # Arrange
    expected = "ERROR LINE 1: Unexpected indentation"

    input_file = INPUT_FILES + "startIndentError.gsl"

    output_dir = tmp_path / OUTPUT_FILES
    output_dir.mkdir()
    output_file = output_dir / "startIndentError.gsl"

    # Act
    with pytest.raises(SystemExit) as exit_info:
        preprocessor(input_file, True, output_file)   

    # Assert
    assert expected == exit_info.value.code, f"expected: {expected} actual: {exit_info.value.code}"

def test_commentSLInTextType(tmp_path):
    # Arrange
    expected = "text a := \"This is text type with a comment // This should be here\" @NEWLINE\n$"

    input_file = INPUT_FILES + "commentSLInTextType.gsl"

    output_dir = tmp_path / OUTPUT_FILES
    output_dir.mkdir()
    output_file = output_dir / "commentSLInTextType.gsl"

    # Act
    preprocessor(input_file, True, output_file)

    data = ""
    with open(output_file, "r") as out:
        data = out.read()

    # Assert
    assert expected == data, f"expected: {expected} actual: {data}"

def test_commentSLInTextTypeAndAfter(tmp_path):
    # Arrange
    expected = "text testing := \"This is a test text // This is cool\"  @NEWLINE\n$"

    input_file = INPUT_FILES + "commentSLInTextTypeAndAfter.gsl"

    output_dir = tmp_path / OUTPUT_FILES
    output_dir.mkdir()
    output_file = output_dir / "commentSLInTextTypeAndAfter.gsl"

    # Act
    preprocessor(input_file, True, output_file)

    data = ""
    with open(output_file, "r") as out:
        data = out.read()

    # Assert
    assert expected == data, f"expected: {expected} actual: {data}"

def test_commentMLInTextType(tmp_path):
    # Arrange
    expected = "text something := \"I love something /* Multiline comment wow */\" @NEWLINE\n$"

    input_file = INPUT_FILES + "commentMLInTextType.gsl"

    output_dir = tmp_path / OUTPUT_FILES
    output_dir.mkdir()
    output_file = output_dir / "commentSLInTextType.gsl"

    # Act
    preprocessor(input_file, True, output_file)

    data = ""
    with open(output_file, "r") as out:
        data = out.read()

    # Assert
    assert expected == data, f"expected: {expected} actual: {data}"

def test_commentMLInTextTypeAndAfter(tmp_path):
    # Arrange
    expected = "text blabla := \"Cool text /* Multiline comment */\"  @NEWLINE\n$"

    input_file = INPUT_FILES + "commentMLInTextTypeAndAfter.gsl"

    output_dir = tmp_path / OUTPUT_FILES
    output_dir.mkdir()
    output_file = output_dir / "commentMLInTextTypeAndAfter.gsl"

    # Act
    preprocessor(input_file, True, output_file)

    data = ""
    with open(output_file, "r") as out:
        data = out.read()

    # Assert
    assert expected == data, f"expected: {expected} actual: {data}"

def test_commentInExpressionError(tmp_path):
    # Arrange
    expected = "ERROR LINE 1: No code must follow a multi-line comment"

    input_file = INPUT_FILES + "commentInExpressionError.gsl"

    output_dir = tmp_path / OUTPUT_FILES
    output_dir.mkdir()
    output_file = output_dir / "commentInExpressionError.gsl"

    # Act
    with pytest.raises(SystemExit) as exit_info:
        preprocessor(input_file, True, output_file)   

    # Assert
    assert expected == exit_info.value.code, f"expected: {expected} actual: {exit_info.value.code}"

def test_multipleMLComments(tmp_path):
    # Arrange
    expected = "a in int := 5  @NEWLINE\n$"

    input_file = INPUT_FILES + "multipleMLComments.gsl"

    output_dir = tmp_path / OUTPUT_FILES
    output_dir.mkdir()
    output_file = output_dir / "multipleMLComments.gsl"

    # Act
    preprocessor(input_file, True, output_file)

    data = ""
    with open(output_file, "r") as out:
        data = out.read()

    # Assert
    assert expected == data, f"expected: {expected} actual: {data}"

def test_MLCommentAfterSLComment(tmp_path):
    # Arrange
    expected = \
        """number in real := 0.1  @NEWLINE
This is a comment @NEWLINE
*/ @NEWLINE
$"""

    input_file = INPUT_FILES + "MLCommentAfterSLComment.gsl"

    output_dir = tmp_path / OUTPUT_FILES
    output_dir.mkdir()
    output_file = output_dir / "MLCommentAfterSLComment.gsl"

    # Act
    preprocessor(input_file, True, output_file)

    data = ""
    with open(output_file, "r") as out:
        data = out.read()

    # Assert
    assert expected == data, f"expected: {expected} actual: {data}"

def test_SLCommentAfterMLCommentError(tmp_path):
    # Arrange
    expected = "ERROR LINE 3: No code must follow a multi-line comment"

    input_file = INPUT_FILES + "SLCommentAfterMLCommentError.gsl"

    output_dir = tmp_path / OUTPUT_FILES
    output_dir.mkdir()
    output_file = output_dir / "SLCommentAfterMLCommentError.gsl"

    # Act
    with pytest.raises(SystemExit) as exit_info:
        preprocessor(input_file, True, output_file)   

    # Assert
    assert expected == exit_info.value.code, f"expected: {expected} actual: {exit_info.value.code}"

def test_multipleMLCommentsAfterEachother(tmp_path):
    # Arrange
    expected = "a in nat := 1  @NEWLINE\n$"

    input_file = INPUT_FILES + "multipleMLCommentsAfterEachother.gsl"

    output_dir = tmp_path / OUTPUT_FILES
    output_dir.mkdir()
    output_file = output_dir / "multipleMLCommentsAfterEachother.gsl"

    # Act
    preprocessor(input_file, True, output_file)

    data = ""
    with open(output_file, "r") as out:
        data = out.read()

    # Assert
    assert expected == data, f"expected: {expected} actual: {data}"

