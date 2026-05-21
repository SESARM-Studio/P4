from parser.ast_builder import *
from evaluator.functions import *

import evaluator.categories.statement
import evaluator.categories.graph_statement


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


# Tests only done using undirected graph. 

def test_graph_statement_add_node():
## Arrange
    env_graph = dict()
    env_var = dict()
    env_algo = dict()
    loc = Location()
    graph_object = Graph()
    store = dict()

    # Creating a undirectional graph G with nodes a,b,c and edges a---b, a---c
    decl_edge1 = EdgeDecl("EdgeDecl")
    decl_edge1.initial_node = 'a'
    decl_edge1.nodes = ['b', 'c']
    decl_edge1.direction = "---"

    decl_nodes = NodeDecl("NodeDecl")
    decl_nodes.type = "node"
    decl_nodes.identifiers = ['a', 'b', 'c']
    decl_nodes.is_list = False

    decl_graph = GraphDecl("GraphDecl")
    decl_graph.graph_type = "graph"
    decl_graph.identifier = "G"
    decl_graph.nodes = [decl_nodes]
    decl_graph.edges = [decl_edge1]

    # Creating the graph statement node
    declaration_node = Declaration("Declaration")
    declaration_node.identifiers = ['d']
    declaration_node.type = "node"
    declaration_node.is_list = False

    graph_statement = GraphStatement("GraphStatement")
    graph_statement.graph_identifier = "G"
    graph_statement.operator = "add"
    graph_statement.argument = declaration_node

    ## Act
    # Evaluate graph declaration
    store, env_var, env_algo, env_graph, v, loc = evaluator.categories.statement.execute_statement(decl_graph, loc, graph_object, store, env_var, env_algo, env_graph)

    # Evaluate node expression
    evaluator.categories.graph_statement.execute_graph_statement(graph_statement, env_graph, env_var, env_algo, loc, graph_object, store)

    ## Assert
    graph_object = env_graph.get(decl_graph.identifier)
    assert 'd' in graph_object.get_nodes()


def test_graph_statement_add_edge():
## Arrange
    env_graph = dict()
    env_var = dict()
    env_algo = dict()
    loc = Location()
    graph_object = Graph()
    store = dict()

    # Creating a undirectional graph G with nodes a,b,c and edges a---b, a---c
    decl_edge1 = EdgeDecl("EdgeDecl")
    decl_edge1.initial_node = 'a'
    decl_edge1.nodes = ['b', 'c']
    decl_edge1.direction = "---"

    decl_nodes = NodeDecl("NodeDecl")
    decl_nodes.type = "node"
    decl_nodes.identifiers = ['a', 'b', 'c']
    decl_nodes.is_list = False

    decl_graph = GraphDecl("GraphDecl")
    decl_graph.graph_type = "graph"
    decl_graph.identifier = "G"
    decl_graph.nodes = [decl_nodes]
    decl_graph.edges = [decl_edge1]

    # Creating the graph statement node
    declaration_edge = EdgeDecl("EdgeDecl")
    declaration_edge.initial_node = 'b'
    declaration_edge.nodes = ['c']
    declaration_edge.direction = "---"

    graph_statement = GraphStatement("GraphStatement")
    graph_statement.graph_identifier = "G"
    graph_statement.operator = "add"
    graph_statement.argument = declaration_edge

    ## Act
    # Evaluate graph declaration
    store, env_var, env_algo, env_graph, v, loc = evaluator.categories.statement.execute_statement(decl_graph, loc, graph_object, store, env_var, env_algo, env_graph)

    # Evaluate node expression
    evaluator.categories.graph_statement.execute_graph_statement(graph_statement, env_graph, env_var, env_algo, loc, graph_object, store)

    ## Assert
    graph_object = env_graph.get(decl_graph.identifier)
    assert ('b', 'c') in graph_object.get_edges()


def test_graph_statement_add_edge_weight():
## Arrange
    env_graph = dict()
    env_var = dict()
    env_algo = dict()
    loc = Location()
    graph_object = Graph()
    store = dict()

    # Creating a undirectional graph G with nodes a,b,c and edges a---b, a---c
    decl_edge1 = EdgeDecl("EdgeDecl")
    decl_edge1.initial_node = 'a'
    decl_edge1.nodes = ['b', 'c']
    decl_edge1.direction = "---"

    decl_nodes = NodeDecl("NodeDecl")
    decl_nodes.type = "node"
    decl_nodes.identifiers = ['a', 'b', 'c']
    decl_nodes.is_list = False

    decl_graph = GraphDecl("GraphDecl")
    decl_graph.graph_type = "graph"
    decl_graph.identifier = "G"
    decl_graph.nodes = [decl_nodes]
    decl_graph.edges = [decl_edge1]

    # Creating the graph statement node
    decl_edge2 = EdgeDecl("EdgeDecl")
    decl_edge2.initial_node = 'b'
    decl_edge2.nodes = ['c']
    decl_edge2.direction = "---"
    decl_edge2.weight = [
        make_expression(arg1=make_term("NATURAL_NUMBER", "3"))
    ]

    graph_statement = GraphStatement("GraphStatement")
    graph_statement.graph_identifier = "G"
    graph_statement.operator = "add"
    graph_statement.argument = decl_edge2

    ## Act
    # Evaluate graph declaration
    store, env_var, env_algo, env_graph, v, loc = evaluator.categories.statement.execute_statement(decl_graph, loc, graph_object, store, env_var, env_algo, env_graph)

    # Evaluate node expression
    evaluator.categories.graph_statement.execute_graph_statement(graph_statement, env_graph, env_var, env_algo, loc, graph_object, store)

    ## Assert
    # Checking existance of added edge
    graph_object = env_graph.get(decl_graph.identifier)
    assert ('b', 'c') in graph_object.get_edges()

    # Checking weight of added edge
    edge_data = graph_object.get_edge_data('b', 'c')
    assert edge_data.get("weight") == 3


def test_graph_statement_remove_node():
## Arrange
    env_graph = dict()
    env_var = dict()
    env_algo = dict()
    loc = Location()
    graph_object = Graph()
    store = dict()

    # Creating a undirectional graph G with nodes a,b,c and edges a---b, a---c
    decl_edge1 = EdgeDecl("EdgeDecl")
    decl_edge1.initial_node = 'a'
    decl_edge1.nodes = ['b', 'c']
    decl_edge1.direction = "---"

    decl_nodes = NodeDecl("NodeDecl")
    decl_nodes.type = "node"
    decl_nodes.identifiers = ['a', 'b', 'c']
    decl_nodes.is_list = False

    decl_graph = GraphDecl("GraphDecl")
    decl_graph.graph_type = "graph"
    decl_graph.identifier = "G"
    decl_graph.nodes = [decl_nodes]
    decl_graph.edges = [decl_edge1]

    # Creating the graph statement node
    declaration_node = Declaration("Declaration")
    declaration_node.identifiers = ['b']
    declaration_node.type = "node"
    declaration_node.is_list = False

    graph_statement = GraphStatement("GraphStatement")
    graph_statement.graph_identifier = "G"
    graph_statement.operator = "remove"
    graph_statement.argument = declaration_node

    ## Act
    # Evaluate graph declaration
    store, env_var, env_algo, env_graph, v, loc = evaluator.categories.statement.execute_statement(decl_graph, loc, graph_object, store, env_var, env_algo, env_graph)

    # Evaluate node expression
    evaluator.categories.graph_statement.execute_graph_statement(graph_statement, env_graph, env_var, env_algo, loc, graph_object, store)

    ## Assert
    graph_object = env_graph.get(decl_graph.identifier)
    assert 'b' not in graph_object.get_nodes()


def test_graph_statement_remove_edge():
## Arrange
    env_graph = dict()
    env_var = dict()
    env_algo = dict()
    loc = Location()
    graph_object = Graph()
    store = dict()

    # Creating a undirectional graph G with nodes a,b,c and edges a---b, a---c
    decl_edge1 = EdgeDecl("EdgeDecl")
    decl_edge1.initial_node = 'a'
    decl_edge1.nodes = ['b', 'c']
    decl_edge1.direction = "---"

    decl_nodes = NodeDecl("NodeDecl")
    decl_nodes.type = "node"
    decl_nodes.identifiers = ['a', 'b', 'c']
    decl_nodes.is_list = False

    decl_graph = GraphDecl("GraphDecl")
    decl_graph.graph_type = "graph"
    decl_graph.identifier = "G"
    decl_graph.nodes = [decl_nodes]
    decl_graph.edges = [decl_edge1]

    # Creating the graph statement node
    declaration_edge = EdgeDecl("EdgeDecl")
    declaration_edge.initial_node = 'a'
    declaration_edge.nodes = ['c']
    declaration_edge.direction = "---"

    graph_statement = GraphStatement("GraphStatement")
    graph_statement.graph_identifier = "G"
    graph_statement.operator = "remove"
    graph_statement.argument = declaration_edge

    ## Act
    # Evaluate graph declaration
    store, env_var, env_algo, env_graph, v, loc = evaluator.categories.statement.execute_statement(decl_graph, loc, graph_object, store, env_var, env_algo, env_graph)

    # Evaluate node expression
    evaluator.categories.graph_statement.execute_graph_statement(graph_statement, env_graph, env_var, env_algo, loc, graph_object, store)

    ## Assert
    graph_object = env_graph.get(decl_graph.identifier)
    assert ('a', 'c') not in graph_object.get_edges()

