import pytest

from parser.ast_builder import *

from copy import deepcopy

from evaluator.categories.statement import *
from evaluator.categories.expression import *
from evaluator.categories.graph_declaration import *
from evaluator.categories.declaration import *

from evaluator.functions import *


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

def make_list_expression(expressions: list, token="ListExpression"):
    list_expression = ListExpression(token)
    list_expression.expressions = expressions
    return list_expression

def make_assignment(identifiers: list, expression: Expression, token="Assignment"):
    assigment = Assignment(token)
    assigment.identifiers = identifiers
    assigment.expression = expression
    return assigment

def make_declaration(identifiers: list[str], _type: str, is_list=False, dimension=None, token="Declaration"):
    declaration = Declaration(token)
    declaration.type = _type
    declaration.identifiers = identifiers
    declaration.is_list = is_list
    if dimension:
        declaration.dimension = Term("Term")
        declaration.dimension.type = 'NATURAL_NUMBER'
        declaration.dimension.value = dimension
    return declaration

def make_node_declaration(identifiers: list[str], is_list=False, dimension=None, token="NodeDecl"):
    declaration = NodeDecl(token)
    declaration.identifiers = identifiers
    declaration.is_list = is_list
    if dimension:
        declaration.dimension = Term("Term")
        declaration.dimension.type = 'NATURAL_NUMBER'
        declaration.dimension.value = dimension
    return declaration

def make_edge_declaration(initial_node, nodes: list, direction, weight: list, token="EdgeDecl"):
    edge_decl = EdgeDecl(token)
    edge_decl.initial_node = initial_node
    edge_decl.nodes = nodes
    edge_decl.direction = direction
    edge_decl.weight = weight
    return edge_decl

def give_edge_declaration_int_weight(edge_decl):
    for i in range(0,len(edge_decl.nodes)):
        term = make_term("INTEGER_NUMBER",f"{i+1}")
        edge_decl.weight.append(make_expression(arg1=term))

def make_graph_decl(graph_type, identifier, weight_type, nodes: list, edges: list, token="GraphDecl"):
    graph_decl = GraphDecl(token)
    graph_decl.graph_type = graph_type
    graph_decl.identifier = identifier
    graph_decl.weight_type = weight_type
    graph_decl.nodes = nodes
    graph_decl.edges = edges
    return graph_decl

def make_graph_statement(graph_identifier, operator, argument, token="GraphStatement"):
    graph_statement = GraphStatement(token)
    graph_statement.graph_identifier = graph_identifier
    graph_statement.operator = operator
    graph_statement.argument = argument
    return graph_statement

def make_edge_loop(initial_node, last_node, direction, token="EdgeLoop"):
    edge_loop = EdgeLoop(token)
    edge_loop.initial_node = initial_node
    edge_loop.last_node = last_node
    edge_loop.direction = direction
    return edge_loop

def make_while_statement(condition: Expression, statements: list, token="WhileStatement"):
    while_statement = WhileStatement(token)
    while_statement.condition = condition
    while_statement.statements = statements
    return while_statement

def make_for_each_normal(loop_identifier, iterable, statements: list, token="ForEachNormal"):
    for_each_normal = ForEachNormal(token)
    for_each_normal.loop_identifier = loop_identifier
    for_each_normal.iterable = iterable
    for_each_normal.statements = statements
    return for_each_normal

def make_for_each_edge(edge, weight_identifier, graph_identifier, statements: list, token="ForEachEdge"):
    for_each_edge = ForEachEdge(token)
    for_each_edge.edge = edge
    for_each_edge.weight_identifier = weight_identifier
    for_each_edge.graph_identifier = graph_identifier
    for_each_edge.statements = statements
    return for_each_edge

def make_reapeat_statement(repeat_expression=None, repeat_statements=[], token="RepeatStatement"):
    repeat_statement = RepeatStatement(token)
    repeat_statement.repeat_expression = repeat_expression
    repeat_statement.repeat_statements = repeat_statements
    return repeat_statement

def test_while_statement():
    # Arrange
    env_graph = dict()
    env_var = dict()
    env_algo = dict()
    loc = Location()
    graph_object = Graph()
    store = dict()
    statements = []

    condition_expression_arg1 = make_term("IDENTIFIER","i")
    condition_expression_arg2 = make_term("NATURAL_NUMBER","6")
    condition_expression = make_expression("<", condition_expression_arg1, condition_expression_arg2)
    condition_expression = make_expression(arg1=condition_expression)
    env_var.update({"i": loc})
    store.update({loc: 1})
    loc = loc.next_location()
    
    assigment_expression_arg1 = make_term("NATURAL_NUMBER","1")
    assigment_expression_arg2 = make_term("IDENTIFIER","i")
    assigment_expression = make_expression("+", assigment_expression_arg1, assigment_expression_arg2)
    assigment_expression = make_expression(arg1=assigment_expression)
    assigment = make_assignment(["i"],assigment_expression)

    statements.append(assigment)

    while_statment = make_while_statement(condition_expression,statements)

    # Act
    store, env_var, env_algo, env_graph, value, loc = execute_statement(while_statment, loc, graph_object, store, env_var, env_algo, env_graph)

    # Assert
    assert store.get(env_var.get("i")) == 6
    

def test_for_each_normal():
    # Arrange
    env_graph = dict()
    env_var = dict()
    env_algo = dict()
    loc = Location()
    graph_object = Graph()
    store = dict()
    statements = []

  
    loop_identifier = "i"
    
    assigment_expression_arg1 = make_term("NATURAL_NUMBER","1")
    assigment_expression = make_expression(None, assigment_expression_arg1, None)
    assigment_expression = make_expression(arg1=assigment_expression)
    assigment = make_assignment(["i"],assigment_expression)

    statements.append(assigment)

    env_var.update({"array": loc})
    store.update({loc: [2,4,6,8,10]})
    loc = loc.next_location()
    iterable_arg1 = make_term("IDENTIFIER","array")
    iterable = make_expression(None, iterable_arg1, None)

    for_each_normal = make_for_each_normal(loop_identifier,iterable,statements)

    # Act
    store, env_var, env_algo, env_graph, value, loc = execute_statement(for_each_normal, loc, graph_object, store, env_var, env_algo, env_graph)

    # Assert
    assert store.get(env_var.get("i")) == None
    assert store.get(env_var.get("array")) == [2,4,6,8,10]
    
def test_for_each_edge():
    # Arrange
    env_graph = dict()
    env_var = dict()
    env_algo = dict()
    loc = Location()
    graph_object = Graph()
    store = dict()
    
    global_node_decl = make_node_declaration(['f'])
    store, env_var, env_algo, env_graph, v, loc = execute_statement(global_node_decl, loc, graph_object, store, env_var, env_algo, env_graph)

    node_decl = []
    node_decl_nodes = ['a', 'b,', 'c', 'd', 'e']
    node_decl.append(make_node_declaration(node_decl_nodes))
    
    edge_initial_node = 'a'
    edge_decl_nodes = ['b', 'c', 'd', 'e']
    edge_direction = '-->'
    temp_edge_decl = make_edge_declaration(edge_initial_node, edge_decl_nodes, edge_direction, [])
    give_edge_declaration_int_weight(temp_edge_decl)
    edge_decl = []
    edge_decl.append(temp_edge_decl)

    graph_decl_type = 'digraph'
    graph_decl_identifier = 'G'
    graph_decl_weight_type = 'int'
    graph_decl_nodes = node_decl
    graph_decl_edges = edge_decl
    graph_decl = make_graph_decl(graph_decl_type, graph_decl_identifier, graph_decl_weight_type, graph_decl_nodes, graph_decl_edges)
    store, env_var, env_algo, env_graph, value, loc = execute_statement(graph_decl, loc, graph_object, store, env_var, env_algo, env_graph)
    
    graph_statement1_edge_decl = make_edge_declaration('x', ['y'], '-->', [])
    graph_statement1 = make_graph_statement(graph_decl_identifier, 'remove', graph_statement1_edge_decl)

    graph_statement2_edge_decl = make_edge_declaration('y', ['f'], '-->', [make_expression(arg1=make_term('IDENTIFIER','w'))])
    graph_statement2 = make_graph_statement(graph_decl_identifier, 'add', graph_statement2_edge_decl)

    edge_loop = make_edge_loop('x', 'y', '-->')
    weight_identifier = 'w'
    graph_identifier = 'G'
    statements = []
    statements.append(graph_statement1)
    statements.append(graph_statement2)
    for_each_edge = make_for_each_edge(edge_loop, weight_identifier, graph_identifier, statements)

    # Act
    store, env_var, env_algo, env_graph, value, loc = execute_statement(for_each_edge, loc, graph_object, store, env_var, env_algo, env_graph)

    # Assert
    assert store.get(env_var.get("w")) == None
    assert store.get(env_var.get("x")) == None
    assert store.get(env_var.get("y")) == None
    assert env_graph.get(graph_identifier).get_edge_data('b', 'f')['weight'] == 1
    assert env_graph.get(graph_identifier).get_edge_data('c', 'f')['weight'] == 2
    assert env_graph.get(graph_identifier).get_edge_data('d', 'f')['weight'] == 3
    assert env_graph.get(graph_identifier).get_edge_data('e', 'f')['weight'] == 4
    assert env_graph.get(graph_identifier).get_edges() == [('b','f'),('c','f'),('d','f'),('e','f')]