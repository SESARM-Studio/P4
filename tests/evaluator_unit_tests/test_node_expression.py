from parser.ast_builder import *
from evaluator.functions import *

import evaluator.categories.node_expression
import evaluator.categories.statement

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



def test_node_expression_right():
    
    ## Arrange
    env_graph = dict()
    env_var = dict()
    env_algo = dict()
    loc = Location()
    graph_object = Graph()
    store = dict()

    # Creating a directional graph G with nodes a,b,c,d and edges a-->b, a-->c, c-->a, d-->a
    decl_edge1 = EdgeDecl("EdgeDecl")
    decl_edge1.initial_node = 'a'
    decl_edge1.nodes = ['b', 'c']
    decl_edge1.direction = "-->"

    decl_edge2 = EdgeDecl("EdgeDecl")
    decl_edge2.initial_node = 'c'
    decl_edge2.nodes = ['a']
    decl_edge2.direction = "-->"

    decl_edge3 = EdgeDecl("EdgeDecl")
    decl_edge3.initial_node = 'd'
    decl_edge3.nodes = ['a']
    decl_edge3.direction = "-->"

    decl_nodes = NodeDecl("NodeDecl")
    decl_nodes.type = "node"
    decl_nodes.identifiers = ['a', 'b', 'c', 'd']
    decl_nodes.is_list = False

    decl_graph = GraphDecl("GraphDecl")
    decl_graph.graph_type = "digraph"
    decl_graph.identifier = "G"
    decl_graph.nodes = [decl_nodes]
    decl_graph.edges = [decl_edge1, decl_edge2, decl_edge3]

    # Creating the node expression node
    identifier_access = IdentifierAccess("IdentifierAccess")
    identifier_access.identifiers = ['G', 'a']

    expression_inner = make_expression(arg1=identifier_access)

    expression_node = ExprNode("ExprNode")
    expression_node.expression = expression_inner
    expression_node.direction = "-->"

    ## Act
    # Evaluate graph declaration
    store, env_var, env_algo, env_graph, v, loc = evaluator.categories.statement.execute_statement(decl_graph, loc, graph_object, store, env_var, env_algo, env_graph)

    # Evaluate node expression
    nodes = evaluator.categories.node_expression.execute_node_expression(expression_node, env_graph, env_var, env_algo, loc, graph_object, store)

    ## Assert
    assert 'b' in nodes
    assert 'c' in nodes

def test_node_expression_left():
    
    ## Arrange
    env_graph = dict()
    env_var = dict()
    env_algo = dict()
    loc = Location()
    graph_object = Graph()
    store = dict()

    # Creating a directional graph G with nodes a,b,c,d and edges a-->b, a-->c, c-->a, d-->a
    decl_edge1 = EdgeDecl("EdgeDecl")
    decl_edge1.initial_node = 'a'
    decl_edge1.nodes = ['b', 'c']
    decl_edge1.direction = "-->"

    decl_edge2 = EdgeDecl("EdgeDecl")
    decl_edge2.initial_node = 'c'
    decl_edge2.nodes = ['a']
    decl_edge2.direction = "-->"

    decl_edge3 = EdgeDecl("EdgeDecl")
    decl_edge3.initial_node = 'd'
    decl_edge3.nodes = ['a']
    decl_edge3.direction = "-->"

    decl_nodes = NodeDecl("NodeDecl")
    decl_nodes.type = "node"
    decl_nodes.identifiers = ['a', 'b', 'c', 'd']
    decl_nodes.is_list = False

    decl_graph = GraphDecl("GraphDecl")
    decl_graph.graph_type = "digraph"
    decl_graph.identifier = "G"
    decl_graph.nodes = [decl_nodes]
    decl_graph.edges = [decl_edge1, decl_edge2, decl_edge3]

    # Creating the node expression node
    identifier_access = IdentifierAccess("IdentifierAccess")
    identifier_access.identifiers = ['G', 'a']

    expression_inner = make_expression(arg1=identifier_access)

    expression_node = ExprNode("ExprNode")
    expression_node.expression = expression_inner
    expression_node.direction = "<--"

    ## Act
    # Evaluate graph declaration
    store, env_var, env_algo, env_graph, v, loc = evaluator.categories.statement.execute_statement(decl_graph, loc, graph_object, store, env_var, env_algo, env_graph)

    # Evaluate node expression
    nodes = evaluator.categories.node_expression.execute_node_expression(expression_node, env_graph, env_var, env_algo, loc, graph_object, store)

    ## Assert
    assert 'c' in nodes
    assert 'd' in nodes

def test_node_expression_right_left():
    
    ## Arrange
    env_graph = dict()
    env_var = dict()
    env_algo = dict()
    loc = Location()
    graph_object = Graph()
    store = dict()

    # Creating a directional graph G with nodes a,b,c,d and edges a-->b, a-->c, c-->a, d-->a
    decl_edge1 = EdgeDecl("EdgeDecl")
    decl_edge1.initial_node = 'a'
    decl_edge1.nodes = ['b', 'c']
    decl_edge1.direction = "-->"

    decl_edge2 = EdgeDecl("EdgeDecl")
    decl_edge2.initial_node = 'c'
    decl_edge2.nodes = ['a']
    decl_edge2.direction = "-->"

    decl_edge3 = EdgeDecl("EdgeDecl")
    decl_edge3.initial_node = 'd'
    decl_edge3.nodes = ['a']
    decl_edge3.direction = "-->"

    decl_nodes = NodeDecl("NodeDecl")
    decl_nodes.type = "node"
    decl_nodes.identifiers = ['a', 'b', 'c', 'd']
    decl_nodes.is_list = False

    decl_graph = GraphDecl("GraphDecl")
    decl_graph.graph_type = "digraph"
    decl_graph.identifier = "G"
    decl_graph.nodes = [decl_nodes]
    decl_graph.edges = [decl_edge1, decl_edge2, decl_edge3]

    # Creating the node expression node
    identifier_access = IdentifierAccess("IdentifierAccess")
    identifier_access.identifiers = ['G', 'a']

    expression_inner = make_expression(arg1=identifier_access)

    expression_node = ExprNode("ExprNode")
    expression_node.expression = expression_inner
    expression_node.direction = "<->"

    ## Act
    # Evaluate graph declaration
    store, env_var, env_algo, env_graph, v, loc = evaluator.categories.statement.execute_statement(decl_graph, loc, graph_object, store, env_var, env_algo, env_graph)

    # Evaluate node expression
    nodes = evaluator.categories.node_expression.execute_node_expression(expression_node, env_graph, env_var, env_algo, loc, graph_object, store)

    ## Assert
    assert 'b' in nodes
    assert 'c' in nodes
    assert 'd' in nodes

def test_node_expression_undirected():
    
    ## Arrange
    env_graph = dict()
    env_var = dict()
    env_algo = dict()
    loc = Location()
    graph_object = Graph()
    store = dict()

    # Creating a undirectional graph G with nodes a,b,c,d and edges a---b, a---c, d---a
    decl_edge1 = EdgeDecl("EdgeDecl")
    decl_edge1.initial_node = 'a'
    decl_edge1.nodes = ['b', 'c']
    decl_edge1.direction = "---"

    decl_edge2 = EdgeDecl("EdgeDecl")
    decl_edge2.initial_node = 'd'
    decl_edge2.nodes = ['a']
    decl_edge2.direction = "---"

    decl_nodes = NodeDecl("NodeDecl")
    decl_nodes.type = "node"
    decl_nodes.identifiers = ['a', 'b', 'c', 'd']
    decl_nodes.is_list = False

    decl_graph = GraphDecl("GraphDecl")
    decl_graph.graph_type = "graph"
    decl_graph.identifier = "G"
    decl_graph.nodes = [decl_nodes]
    decl_graph.edges = [decl_edge1, decl_edge2]

    # Creating the node expression node
    identifier_access = IdentifierAccess("IdentifierAccess")
    identifier_access.identifiers = ['G', 'a']

    expression_inner = make_expression(arg1=identifier_access)

    expression_node = ExprNode("ExprNode")
    expression_node.expression = expression_inner
    expression_node.direction = "---"

    ## Act
    # Evaluate graph declaration
    store, env_var, env_algo, env_graph, v, loc = evaluator.categories.statement.execute_statement(decl_graph, loc, graph_object, store, env_var, env_algo, env_graph)

    # Evaluate node expression
    nodes = evaluator.categories.node_expression.execute_node_expression(expression_node, env_graph, env_var, env_algo, loc, graph_object, store)

    ## Assert
    assert 'b' in nodes
    assert 'c' in nodes
    assert 'd' in nodes
