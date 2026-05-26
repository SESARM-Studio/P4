import pytest
from unittest.mock import patch
from types import SimpleNamespace

from parser.ast_builder import EdgeDecl, Term
from evaluator.helpers import Graph, Location
from evaluator.categories.edge_declaration import execute_edge_declaration

@pytest.fixture
def setup_env():
    graph_object = Graph()
    graph_object.create_graph("digraph")

    return {
        "env_graph": {},
        "env_var": {},
        "env_algo": {},
        "loc": Location(),
        "graph_object": graph_object,
        "store": {},
    }

def make_edge(direction, weighted=False):
    edge = EdgeDecl("EdgeDecl")
    edge.initial_node = "a"
    edge.nodes = ["b", "c"]
    edge.direction = direction

    if weighted:
        w1 = Term("Term")
        w1.type = "INTEGER_NUMBER"
        w1.value = "3"

        w2 = Term("Term")
        w2.type = "INTEGER_NUMBER"
        w2.value = "5"

        edge.weight = [w1, w2]
    else:
        edge.weight = []

    return edge

def test_unweighted_edge_undirected(setup_env):
    #arrange
    edge = make_edge("---")

    #act
    result, store = execute_edge_declaration(edge, **setup_env)

    #assert
    assert result == [("a", "b"), ("a", "c")]


def test_unweighted_edge_right(setup_env):
    #arrange
    edge = make_edge("-->")

    #act
    result, store = execute_edge_declaration(edge, **setup_env)

    #assert
    assert result == [("a", "b"), ("a", "c")]


def test_unweighted_edge_left(setup_env):
    #arrange
    edge = make_edge("<--")

    #act
    result, store = execute_edge_declaration(edge, **setup_env)

    #assert
    assert result == [("b", "a"), ("c", "a")]


def test_unweighted_edge_bidirectional(setup_env):
    #arrange
    edge = make_edge("<->")

    #act
    result, store = execute_edge_declaration(edge, **setup_env)

    #assert
    assert result == [
        ("a", "b"),
        ("a", "c"),
        ("b", "a"),
        ("c", "a"),
    ]


def test_weighted_edge_undirected(setup_env):
    #arrange
    edge = make_edge("---", weighted=True)

    with patch(
        "evaluator.categories.expression.execute_expression",
        side_effect=[
            SimpleNamespace(v=3, modified_store=None),
            SimpleNamespace(v=5, modified_store=None),
        ],
    ):
        #act
        result, store = execute_edge_declaration(edge, **setup_env)

    #assert
    assert result == [("a", "b", 3), ("a", "c", 5)]


def test_weighted_edge_right(setup_env):
    #arrange
    edge = make_edge("-->", weighted=True)

    with patch(
        "evaluator.categories.expression.execute_expression",
        side_effect=[
            SimpleNamespace(v=3, modified_store=None),
            SimpleNamespace(v=5, modified_store=None),
        ],
    ):
        #act
        result, store = execute_edge_declaration(edge, **setup_env)

    #assert
    assert result == [("a", "b", 3), ("a", "c", 5)]


def test_weighted_edge_left(setup_env):
    #arrange
    edge = make_edge("<--", weighted=True)

    with patch(
        "evaluator.categories.expression.execute_expression",
        side_effect=[
            SimpleNamespace(v=3, modified_store=None),
            SimpleNamespace(v=5, modified_store=None),
        ],
    ):
        #act
        result, store = execute_edge_declaration(edge, **setup_env)

    #assert
    assert result == [("b", "a", 3), ("c", "a", 5)]


def test_weighted_edge_bidirectional(setup_env):
    #arrange
    edge = make_edge("<->", weighted=True)

    with patch(
        "evaluator.categories.expression.execute_expression",
        side_effect=[
            SimpleNamespace(v=3, modified_store=None),
            SimpleNamespace(v=5, modified_store=None),
            SimpleNamespace(v=3, modified_store=None),
            SimpleNamespace(v=5, modified_store=None),
        ],
    ):
        #act
        result, store = execute_edge_declaration(edge, **setup_env)

    #assert
    assert result == [
        ("a", "b", 3),
        ("a", "c", 5),
        ("b", "a", 3),
        ("c", "a", 5),
    ]