import pytest

from parser.ast_builder import *

from copy import deepcopy

from evaluator.categories.statement import execute_statement
from evaluator.categories.expression import execute_expression
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

def make_declaration(identifiers: list[str], _type: str, is_list=False, dimension =None, token="Declaration"):
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

def reapeat_statement(repeat_expression=None, repeat_statements=[], token="RepeatStatement"):
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
    condition_expression_arg2 = make_term("NATURAL_NUMBER","100")
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
    assert store.get(env_var.get("i")) == 100
    

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
    
    # Act

    # Assert
    
    pass
def test_repeat_statement():
    # Arrange
   
    # Act

    # Assert
    
    pass