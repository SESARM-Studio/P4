from pathlib import Path

from exceptions.preprocessor_exception import PreprocessorException
from preprocessor.prepro import preprocessor
from preprocessor.source_map import SourceMap
from parser.gsl_parser import *
from parser.ast_builder import *
from exceptions.parser_exception import ParseException

def IntegratedASTBuilder(inp_file):
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
    return tree

def test_bellman_ford_AST_builder_integration():
    # Arrange
    input_file_path = Path("tests/integration_tests/integration_test_files/bellman_ford.gsl")

    # Act
    abstract_syntax_tree = IntegratedASTBuilder(input_file_path)

    # Assert
    assert abstract_syntax_tree.token == "Program"
    assert len(abstract_syntax_tree.children) == 4
    assert isinstance(abstract_syntax_tree.children[0], GraphDecl)
    assert isinstance(abstract_syntax_tree.children[1], Algorithm)
    assert isinstance(abstract_syntax_tree.children[2], DeclarationInit)
    assert isinstance(abstract_syntax_tree.children[3], ASTNode) # EOF $ object