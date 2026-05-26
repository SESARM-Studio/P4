from pathlib import Path

from preprocessor.prepro import preprocessor
from parser.ast_builder import AbstractSyntaxTreeBuilder
from parser.gsl_parser import gsl_parser
from typesystem.type_checker import TypeChecker
from preprocessor.source_map import SourceMap
from exceptions.parser_exception import ParseException
from exceptions.preprocessor_exception import PreprocessorException
import sys

######### Integration of typesystem

def IntegratedTypesystem(inp_file: str) -> bool:
    source_map = SourceMap()
    try:
        preprocessed_contents = preprocessor(inp_file, source_map)
    except PreprocessorException as pe:
        source_map.print_error(pe.message, pe.span[0], pe.span[1], processed=False)
        sys.exit(1)

    tree_builder = gsl_parser.ParseTreeBuilder()
    parser = gsl_parser(preprocessed_contents, tree_builder)
    try:
        parser.parse_Program()
    except ParseException as pe:
            source_map.print_error(parser.getErrorMessage(pe), pe.getBegin(), pe.getEnd())
            sys.exit(1)
    ast_builder = AbstractSyntaxTreeBuilder(preprocessed_contents)
    tree = ast_builder.build_tree(tree_builder.stack)

    type_checker = TypeChecker(ast=tree, source_map=source_map)
    return type_checker.check()

######### (Helper function)

def test_bellman_ford():
    # Arrange
    input_file_path = Path("tests/integration_tests/integration_test_files/bellman_ford.gsl")

    # Act
    well_formed_program = IntegratedTypesystem(input_file_path)

    # Assert
    assert well_formed_program == True, "Program was not well formed"


def test_lists(tmp_path):
    # Arrange
    input_file_path = Path("tests/integration_tests/integration_test_files/typesystem_lists_integration.gsl")

    # Act
    well_formed_program = IntegratedTypesystem(input_file_path)

    # Assert
    assert well_formed_program == True, "Program was not well formed"

def test_algorithm(tmp_path):
    # Arrange
    input_file_path = Path("tests/integration_tests/integration_test_files/algorithm_integration.gsl")

    # Act
    well_formed_program = IntegratedTypesystem(input_file_path)

    # Assert
    assert well_formed_program == True, "Program was not well formed"
