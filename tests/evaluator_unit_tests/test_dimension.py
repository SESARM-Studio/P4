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

def make_term(arg):
    term = Term('Term')
    term.type = 'NATURAL_NUMBER'
    term.value = arg

    return term

# Declaration list
def test_1d_list_declaration():
    # Arrange
    dim = make_term(1)
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
    assert len(ret) == 0 # A 1D array should return [], so this assert makes sure the inner array is empty


def test_3d_list_declaration():
    # Arrange
    dim = make_term(3)
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
    assert len(ret[0][0]) == 0 # A 3D array should return [[[]]], so this assert makes sure the inner array is empty

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

def test_no_dim_declaration():
    # Arrange
    dec = make_list_declaration(["x"], "int")
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
    assert len(ret) == 0 # A 1D array should return [], so this assert makes sure the inner array is empty

