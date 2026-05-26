from pathlib import Path

from preprocessor.prepro import preprocessor
from preprocessor.prepro import preprocessor, SourceMap
from parser.gsl_parser import gsl_parser
from typesystem.type_checker import TypeChecker
from parser.ast_builder import AbstractSyntaxTreeBuilder
from preprocessor.source_map import SourceMap
from exceptions.parser_exception import ParseException
from exceptions.preprocessor_exception import PreprocessorException
from exceptions.evaluator_exception import EvaluatorException
from evaluator.evaluator import traverse_program
import sys

######### Integration of typesystem

def IntegratedEvaluator(inp_file: str) -> bool:
    source_map = SourceMap()
    try:
        preprocessed_contents = preprocessor(inp_file, source_map)
    except PreprocessorException as pe:
        source_map.print_error(pe.message, pe.span[0], pe.span[1], processed=False)
        sys.exit(1)

    tree_builder = gsl_parser.ParseTreeBuilder()
    parser = gsl_parser(preprocessed_contents, tree_builder)
    ast = AbstractSyntaxTreeBuilder(preprocessed_contents)

    try:
        parser.parse_Program()
        tree = ast.build_tree(tree_builder.stack)
        type_checker = TypeChecker(tree, source_map)
        type_checker.check()

        program_result = traverse_program(tree)
    except ParseException as pe:
        source_map.print_error(parser.getErrorMessage(pe), pe.getBegin(), pe.getEnd())
        sys.exit(1)
    except EvaluatorException as ee:
        source_map.print_error(ee.message, ee.span[0], ee.span[1], error_type="Evaluator")
        sys.exit(1)
    
    return program_result

######### (Helper function)

INPUT_FILES = "tests/typesystem_integration/"

def test_bellman_ford_evaluator_integration(): # tmp:path is from pytest that creates a tmp path for the test run
    ## Arrange
    input_file_path = Path("tests/integration_tests/integration_test_files/bellman_ford.gsl")

    ## Act
    store, env_var, env_algo, env_graph, v, loc = IntegratedEvaluator(input_file_path)

    ## Assert
    # Check Bellman-Ford returns true (result is correct)
    location = env_var.get("result")
    assert store.get(location) == True, "Bellman-Ford does not return true!"

def test_algorithm(tmp_path):
    ## Arrange
    input_file_path = Path("tests/integration_tests/integration_test_files/algorithm_integration.gsl")

    ## Act
    store, env_var, env_algo, env_graph, v, loc = IntegratedEvaluator(input_file_path)

    ## Assert
    # Check that declared variables and algorithms exists
    assert "s" in env_var
    assert "x_times" in env_graph
    assert "helper" in env_algo
    assert "t" in env_var
    assert "another_one" in env_algo

    # Check local list does not exist in global scope
    assert "y" not in env_var

