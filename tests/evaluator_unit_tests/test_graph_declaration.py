from parser.ast_builder import *
from evaluator.helpers import *
import networkx as nx
from typesystem.data_types import *
import evaluator.categories.graph_declaration

### AST tree helpers ###
def make_term(_type=None, value=None, children=None, token="Term"):
    term = Term(token)
    term.type = _type
    term.value = value
    term.children = children
    return term

def make_expression(operator=None, arg1=None, arg2=None, token="Expression"):
    expr = Expression(token)
    expr.operator = operator
    expr.arg1 = arg1
    expr.arg2 = arg2
    return expr

########################


def test_graph_declaration_graph(): #(dGraph1)
    ## Arrange
    env_graph = dict()
    env_var = dict()
    env_algo = dict()
    loc = Location()
    graph_object = Graph()
    store = dict()

    # Creating a undirectional graph G node
    decl_graph = GraphDecl("GraphDecl")
    decl_graph.graph_type = TypeEnum.GRAPH
    decl_graph.identifier = "G"
    decl_graph.nodes = []
    decl_graph.edges = []

    ## Act
    env_graph, store = evaluator.categories.graph_declaration.execute_graph_decl(decl_graph, env_var, env_algo, loc, env_graph, graph_object, store)

    ## Assert
    assert decl_graph.identifier in env_graph
    assert isinstance(env_graph.get(decl_graph.identifier).graph, nx.Graph)


def test_graph_declaration_digraph(): #(dGraph1)
    ## Arrange
    env_graph = dict()
    env_var = dict()
    env_algo = dict()
    loc = Location()
    graph_object = Graph()
    store = dict()

    # Creating a directional graph G node
    decl_graph = GraphDecl("GraphDecl")
    decl_graph.graph_type = "digraph"
    decl_graph.identifier = "G"
    decl_graph.nodes = []
    decl_graph.edges = []

    ## Act
    env_graph, store = evaluator.categories.graph_declaration.execute_graph_decl(decl_graph, env_var, env_algo, loc, env_graph, graph_object, store)

    ## Assert
    assert decl_graph.identifier in env_graph
    assert isinstance(env_graph.get(decl_graph.identifier).graph, nx.DiGraph)


def test_graph_declaration_tree(): #(dGraph1)
    ## Arrange
    env_graph = dict()
    env_var = dict()
    env_algo = dict()
    loc = Location()
    graph_object = Graph()
    store = dict()

    # Creating a tree G node
    decl_graph = GraphDecl("GraphDecl")
    decl_graph.graph_type = "tree"
    decl_graph.identifier = "G"
    decl_graph.nodes = []
    decl_graph.edges = []

    ## Act
    env_graph, store = evaluator.categories.graph_declaration.execute_graph_decl(decl_graph, env_var, env_algo, loc, env_graph, graph_object, store)

    ## Assert
    assert decl_graph.identifier in env_graph
    assert isinstance(env_graph.get(decl_graph.identifier).graph, nx.Graph)


def test_graph_declaration_graph_weight(): #(dGraph2)
    ## Arrange
    env_graph = dict()
    env_var = dict()
    env_algo = dict()
    loc = Location()
    graph_object = Graph()
    store = dict()

    # Creating a undirectional graph G node
    decl_graph = GraphDecl("GraphDecl")
    decl_graph.graph_type = TypeEnum.GRAPH
    decl_graph.identifier = "G"
    decl_graph.weight_type = TypeEnum.NAT
    decl_graph.nodes = []
    decl_graph.edges = []

    ## Act
    env_graph, store = evaluator.categories.graph_declaration.execute_graph_decl(decl_graph, env_var, env_algo, loc, env_graph, graph_object, store)

    ## Assert
    # Graph declarations do not utilize weight type other than to determine between graphs, trees and directional graphs.
    assert decl_graph.identifier in env_graph
    assert isinstance(env_graph.get(decl_graph.identifier).graph, nx.Graph)


def test_graph_declaration_graph_body(): #(dGraph3)
    ## Arrange
    env_graph = dict()
    env_var = dict()
    env_algo = dict()
    loc = Location()
    graph_object = Graph()
    store = dict()

    decl_edge = EdgeDecl("EdgeDecl")
    decl_edge.initial_node = 'a'
    decl_edge.nodes = ['b', 'c']
    decl_edge.direction = "---"

    decl_nodes = NodeDecl("NodeDecl")
    decl_nodes.type = TypeEnum.NODE
    decl_nodes.identifiers = ['a', 'b', 'c']
    decl_nodes.is_list = False

    # Creating a undirectional graph G node
    decl_graph = GraphDecl("GraphDecl")
    decl_graph.graph_type = TypeEnum.GRAPH
    decl_graph.identifier = "G"
    decl_graph.nodes = [decl_nodes]
    decl_graph.edges = [decl_edge]

    ## Act
    env_graph, store = evaluator.categories.graph_declaration.execute_graph_decl(decl_graph, env_var, env_algo, loc, env_graph, graph_object, store)

    ## Assert
    assert decl_graph.identifier in env_graph

    graph_object = env_graph.get(decl_graph.identifier)
    assert isinstance(graph_object.graph, nx.Graph)

    assert 'a' in graph_object.get_nodes()
    assert 'b' in graph_object.get_nodes()
    assert 'c' in graph_object.get_nodes()

    assert ('a', 'b') in graph_object.get_edges()
    assert ('a', 'c') in graph_object.get_edges()


def test_graph_declaration_graph_weight_body(): #(dGraph4)
    ## Arrange
    env_graph = dict()
    env_var = dict()
    env_algo = dict()
    loc = Location()
    graph_object = Graph()
    store = dict()

    decl_edge = EdgeDecl("EdgeDecl")
    decl_edge.initial_node = 'a'
    decl_edge.nodes = ['b', 'c']
    decl_edge.direction = "---"
    decl_edge.weight = [
        make_expression(arg1=make_term(TypeEnum.NAT, "3")),
        make_expression(arg1=make_term(TypeEnum.NAT, "4"))
    ]

    decl_nodes = NodeDecl("NodeDecl")
    decl_nodes.type = TypeEnum.NODE
    decl_nodes.identifiers = ['a', 'b', 'c']
    decl_nodes.is_list = False

    # Creating a undirectional graph G node
    decl_graph = GraphDecl("GraphDecl")
    decl_graph.graph_type = TypeEnum.GRAPH
    decl_graph.identifier = "G"
    decl_graph.weight_type = TypeEnum.NAT
    decl_graph.nodes = [decl_nodes]
    decl_graph.edges = [decl_edge]

    ## Act
    env_graph, store = evaluator.categories.graph_declaration.execute_graph_decl(decl_graph, env_var, env_algo, loc, env_graph, graph_object, store)

    ## Assert
    assert decl_graph.identifier in env_graph

    graph_object = env_graph.get(decl_graph.identifier)
    assert isinstance(graph_object.graph, nx.Graph)

    assert 'a' in graph_object.get_nodes()
    assert 'b' in graph_object.get_nodes()
    assert 'c' in graph_object.get_nodes()

    assert ('a', 'b') in graph_object.get_edges()
    assert ('a', 'c') in graph_object.get_edges()

    edge_weight = graph_object.get_edge_data('a', 'b').get("weight")
    assert edge_weight == 3

    edge_weight = graph_object.get_edge_data('a', 'c').get("weight")
    assert edge_weight == 4



