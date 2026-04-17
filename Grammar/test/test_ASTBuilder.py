import pytest

import ASTBuilder
from gslParser import *
from ASTBuilder import *

def test_base_case_recursive():
    # Arrange
    input_string = "Grandfather Father Son Grandson"
    terminal = gslParser.Terminal("Granddad", 0,11)
    ast = AbstractSyntaxTreeBuilder(input_string)
    stack = [terminal]
    expected_type = ASTNode

    # Act
    return_node = ast.build_tree(stack)

    # Assert
    assert isinstance(return_node, expected_type), f"expected: {expected_type} actual: {return_node.__class__.__name__}"
    assert terminal.name == return_node.token
    assert ast.characters(terminal.getBegin(), terminal.getEnd()) == return_node.value
    assert len(return_node.children) == 0

def test_skipped_words():
    # Arrange
    input_string = "Grandfather Son Daughter Stepson"
    terminal1 = gslParser.Terminal("Son", 12, 14)
    terminal2 = gslParser.Terminal("Daughter", 16, 23)
    terminal3 = gslParser.Terminal("Stepson", 25, 31)
    nonterminal = gslParser.Nonterminal("Granddad", 0, 10, [terminal1, terminal2, terminal3])

    ast = AbstractSyntaxTreeBuilder(input_string)
    stack = [nonterminal]
    expected_type = ASTNode

    # Act
    return_node = ast.build_tree(stack)

    # Assert
    assert isinstance(return_node, expected_type), f"expected: {expected_type} actual: {return_node.__class__.__name__}"
    assert len(return_node.children) == 3