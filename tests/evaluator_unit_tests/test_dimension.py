import pytest

from evaluator.functions import Location, Graph
from parser.ast_builder import *
from evaluator.categories.dimension import execute_dimension

def make_list_declaration(identifiers: list[str], _type: str, dimension_expression =None, token="Declaration"):
    declaration = Declaration(token)
    declaration.type = _type
    declaration.identifiers = identifiers
    declaration.is_list = True
    declaration.dimension = dimension_expression


    return declaration

def make_node_list_declaration(identifiers: list[str], dimension_expression=None, token="NodeDecl"):
    declaration = NodeDecl(token)
    declaration.identifiers = identifiers
    declaration.is_list = True
    declaration.dimension = dimension_expression

    return declaration

def make_term(arg):
    term = Term('Term')
    term.type = 'NATURAL_NUMBER'
    term.value = arg

    return term

def make_arit_expression(arg1, arg2, operator, token):
    exp = Expression(token)
    exp.operator = operator
    exp.arg1 = arg1 if isinstance(arg1, Expression) else make_term(arg1)
    exp.arg2 = arg2 if isinstance(arg2, Expression) else make_term(arg2)

    return exp

# Declaration list
def test_int_2d_list_declaration():
    # Arrange
    dim = make_term(2)
    dec = make_list_declaration(["x"], "int", dim)
    env_graph = dict()
    env_var = dict()
    env_algo = dict()
    loc = Location()
    graph_object = Graph()
    store = dict()

    # Act
    ret = execute_dimension(dec, env_graph, env_var, env_algo, loc, graph_object, store)
    expected_type = list

    # Assert
    assert isinstance(ret, expected_type)
    assert len(ret[0]) == 0

# NodeDecl list
def test_node_3d_list_declaration():
    # Arrange
    dim = make_arit_expression(2, 1, '+', 'ExprPlus')
    dec = make_list_declaration(["x"], "int", dim)
    env_graph = dict()
    env_var = dict()
    env_algo = dict()
    loc = Location()
    graph_object = Graph()
    store = dict()

    # Act
    ret = execute_dimension(dec, env_graph, env_var, env_algo, loc, graph_object, store)
    expected_type = list

    # Assert
    assert isinstance(ret, expected_type)
    assert len(ret[0][0]) == 0

# List with expression

def test_exp_4d_list_declaration():
    # Arrange
    exp1 = make_arit_expression(3, 2, '*', 'ExprMult')
    exp2 = make_arit_expression(4, 2, '/', 'ExprMult')

    dim = make_arit_expression(exp1, exp2, '-', 'ExpPlus')
    dec = make_list_declaration(["x"], "int", dim)

    env_graph = dict()
    env_var = dict()
    env_algo = dict()
    loc = Location()
    graph_object = Graph()
    store = dict()

    # Act
    ret = execute_dimension(dec, env_graph, env_var, env_algo, loc, graph_object, store)
    expected_type = list

    # Assert
    assert isinstance(ret, expected_type)
    assert len(ret[0][0][0]) == 0

def test_0d_list_declaration():

    dim = make_term(0)
    dec = make_list_declaration(["x"], "int", dim)

    env_graph = dict()
    env_var = dict()
    env_algo = dict()
    loc = Location()
    graph_object = Graph()
    store = dict()

    # Act + Assert
    with pytest.raises(RuntimeError):
        execute_dimension(dec, env_graph, env_var, env_algo, loc, graph_object, store)
