import pytest
from pathlib import Path
from P4.preprocessor.preprocessor import preprocessor
from preprocessor.source_map import SourceMap
from exceptions.preprocessor_exception import PreprocessorException

INPUT_FILES = Path("tests/preprocessor_unit_tests/input_files/")
OUTPUT_FILES = "output_files"

def test_comments(tmp_path):
    # Arrange
    expected = "x in int := 1 @NEWLINE\n"
    input_file = INPUT_FILES / "comments.gsl"

    output_dir = tmp_path / OUTPUT_FILES
    output_dir.mkdir()
    output_file = output_dir / "comments_out.gsl"

    # Act
    sm = SourceMap()
    print("Test file: ",input_file)
    preprocessor(input_file,sm, True, output_file)

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
@DEDENT @DEDENT """

    input_file = INPUT_FILES / "indents.gsl"

    output_dir = tmp_path / OUTPUT_FILES
    output_dir.mkdir()
    output_file = output_dir / "indents_out.gsl"

    # Act
    sm = SourceMap()
    preprocessor(input_file,sm, True, output_file)

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
o in real := y^2 * v @NEWLINE\n"""

    input_file = INPUT_FILES / "newlines.gsl"

    output_dir = tmp_path / OUTPUT_FILES
    output_dir.mkdir()
    output_file = output_dir / "newlines_out.gsl"

    # Act
    sm = SourceMap()
    preprocessor(input_file,sm, True, output_file)

    data = ""
    with open(output_file, "r") as out:
        data = out.read()

    # Assert
    assert expected == data, f"expected: {expected} actual: {data}"

def test_code_after_comment_error(tmp_path):
    # Arrange
    expected = "No code must follow a multi-line comment"

    input_file = INPUT_FILES / "codeAfterCommentError.gsl"

    output_dir = tmp_path / OUTPUT_FILES
    output_dir.mkdir()
    output_file = output_dir / "codeAfterCommentError.gsl"

    # Act
    sm = SourceMap()
    with pytest.raises(PreprocessorException) as exit_info:
        preprocessor(input_file, sm,True, output_file)

    # Assert
    assert expected == exit_info.value.message, f"expected: {expected} actual: {exit_info.value.message}"

def test_mismatch_indent_error(tmp_path):
    # Arrange
    expected = "Inconsistent use of spaces"

    input_file = INPUT_FILES / "mismatchIndentError.gsl"

    output_dir = tmp_path / OUTPUT_FILES
    output_dir.mkdir()
    output_file = output_dir / "mismatchIndentError.gsl"

    # Act
    sm = SourceMap()
    with pytest.raises(PreprocessorException) as exit_info:
        preprocessor(input_file, sm,True, output_file)

    # Assert
    assert expected == exit_info.value.message, f"expected: {expected} actual: {exit_info.value.message}"

def test_start_indent_error(tmp_path):
    # Arrange
    expected = "Unexpected indentation"

    input_file = INPUT_FILES / "startIndentError.gsl"

    output_dir = tmp_path / OUTPUT_FILES
    output_dir.mkdir()
    output_file = output_dir / "startIndentError.gsl"

    # Act
    sm = SourceMap()
    with pytest.raises(PreprocessorException) as exit_info:
        preprocessor(input_file, sm,True, output_file)

    # Assert
    assert expected == exit_info.value.message, f"expected: {expected} actual: {exit_info.value.message}"

def test_comment_sl_in_text_type(tmp_path):
    # Arrange
    expected = "text a := \"This is text type with a comment // This should be here\" @NEWLINE\n"

    input_file = INPUT_FILES / "commentSLInTextType.gsl"

    output_dir = tmp_path / OUTPUT_FILES
    output_dir.mkdir()
    output_file = output_dir / "commentSLInTextType.gsl"

    # Act
    sm = SourceMap()
    preprocessor(input_file,sm, True, output_file)

    data = ""
    with open(output_file, "r") as out:
        data = out.read()

    # Assert
    assert expected == data, f"expected: {expected} actual: {data}"

def test_comment_sl_in_text_type_and_after(tmp_path):
    # Arrange
    expected = "text testing := \"This is a test text // This is cool\"  @NEWLINE\n"

    input_file = INPUT_FILES / "commentSLInTextTypeAndAfter.gsl"

    output_dir = tmp_path / OUTPUT_FILES
    output_dir.mkdir()
    output_file = output_dir / "commentSLInTextTypeAndAfter.gsl"

    # Act
    sm = SourceMap()
    preprocessor(input_file,sm, True, output_file)

    data = ""
    with open(output_file, "r") as out:
        data = out.read()

    # Assert
    assert expected == data, f"expected: {expected} actual: {data}"

def test_comment_ml_in_text_type(tmp_path):
    # Arrange
    expected = "text something := \"I love something /* Multiline comment wow */\" @NEWLINE\n"

    input_file = INPUT_FILES / "commentMLInTextType.gsl"

    output_dir = tmp_path / OUTPUT_FILES
    output_dir.mkdir()
    output_file = output_dir / "commentSLInTextType.gsl"

    # Act
    sm = SourceMap()
    preprocessor(input_file,sm, True, output_file)

    data = ""
    with open(output_file, "r") as out:
        data = out.read()

    # Assert
    assert expected == data, f"expected: {expected} actual: {data}"

def test_comment_ml_in_text_type_and_after(tmp_path):
    # Arrange
    expected = "text blabla := \"Cool text /* Multiline comment */\"  @NEWLINE\n"

    input_file = INPUT_FILES / "commentMLInTextTypeAndAfter.gsl"

    output_dir = tmp_path / OUTPUT_FILES
    output_dir.mkdir()
    output_file = output_dir / "commentMLInTextTypeAndAfter.gsl"

    # Act
    sm = SourceMap()
    preprocessor(input_file,sm, True, output_file)

    data = ""
    with open(output_file, "r") as out:
        data = out.read()

    # Assert
    assert expected == data, f"expected: {expected} actual: {data}"

def test_comment_in_expression_error(tmp_path):
    # Arrange
    expected = "No code must follow a multi-line comment"

    input_file = INPUT_FILES / "commentInExpressionError.gsl"

    output_dir = tmp_path / OUTPUT_FILES
    output_dir.mkdir()
    output_file = output_dir / "commentInExpressionError.gsl"

    # Act
    sm = SourceMap()
    with pytest.raises(PreprocessorException) as exit_info:
        preprocessor(input_file, sm,True, output_file)

    # Assert
    assert expected == exit_info.value.message, f"expected: {expected} actual: {exit_info.value.message}"

def test_multiple_ml_comments(tmp_path):
    # Arrange
    expected = "a in int := 5  @NEWLINE\n"

    input_file = INPUT_FILES / "multipleMLComments.gsl"

    output_dir = tmp_path / OUTPUT_FILES
    output_dir.mkdir()
    output_file = output_dir / "multipleMLComments.gsl"

    # Act
    sm = SourceMap()
    preprocessor(input_file,sm, True, output_file)

    data = ""
    with open(output_file, "r") as out:
        data = out.read()

    # Assert
    assert expected == data, f"expected: {expected} actual: {data}"

def test_ml_comment_after_sl_comment(tmp_path):
    # Arrange
    expected = \
        """number in real := 0.1  @NEWLINE
This is a comment @NEWLINE
*/ @NEWLINE\n"""

    input_file = INPUT_FILES / "MLCommentAfterSLComment.gsl"

    output_dir = tmp_path / OUTPUT_FILES
    output_dir.mkdir()
    output_file = output_dir / "MLCommentAfterSLComment.gsl"

    # Act
    sm = SourceMap()
    preprocessor(input_file,sm, True, output_file)

    data = ""
    with open(output_file, "r") as out:
        data = out.read()

    # Assert
    assert expected == data, f"expected: {expected} actual: {data}"

def test_sl_comment_after_ml_comment_error(tmp_path):
    # Arrange
    expected = "No code must follow a multi-line comment"

    input_file = INPUT_FILES / "SLCommentAfterMLCommentError.gsl"

    output_dir = tmp_path / OUTPUT_FILES
    output_dir.mkdir()
    output_file = output_dir / "SLCommentAfterMLCommentError.gsl"

    # Act
    sm = SourceMap()
    with pytest.raises(PreprocessorException) as exit_info:
        preprocessor(input_file, sm,True, output_file)

    # Assert
    assert expected == exit_info.value.message, f"expected: {expected} actual: {exit_info.value.message}"

def test_multiple_ml_comments_after_each_other(tmp_path):
    # Arrange
    expected = "a in nat := 1  @NEWLINE\n"

    input_file = INPUT_FILES / "multipleMLCommentsAfterEachother.gsl"

    output_dir = tmp_path / OUTPUT_FILES
    output_dir.mkdir()
    output_file = output_dir / "multipleMLCommentsAfterEachother.gsl"

    # Act
    sm = SourceMap()
    preprocessor(input_file,sm, True, output_file)

    data = ""
    with open(output_file, "r") as out:
        data = out.read()

    # Assert
    assert expected == data, f"expected: {expected} actual: {data}"

